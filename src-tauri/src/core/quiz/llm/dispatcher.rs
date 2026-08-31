use super::{AnswerItem, SYSTEM_PROMPT};
use crate::config::llm::{LLMProtocol, LLMProvider};
use crate::core::quiz::html::Question;

use anyhow::Result;
use std::sync::Arc;
use tokio::sync::Semaphore;

const CHUNK_SIZE: usize = 5;
const MAX_CONCURRENCY: usize = 10;

/// LLM 求解入口分发器
pub async fn solve(provider: &LLMProvider, questions: Vec<Question>) -> Result<Vec<AnswerItem>> {
    let chosen_model = provider
        .chosen_model
        .and_then(|idx| provider.models.get(idx))
        .ok_or_else(|| anyhow::anyhow!("未为提供商 [{}] 选择有效模型", provider.name))?;

    log::debug!(
        "将使用 [{}] 提供商模型 [{}] 进行推理 (题目总数: {}, 分组大小: {}, 最大并发: {})",
        provider.name,
        chosen_model,
        questions.len(),
        CHUNK_SIZE,
        MAX_CONCURRENCY
    );

    if questions.is_empty() {
        return Ok(Vec::new());
    }

    let client = reqwest::Client::new();
    let semaphore = Arc::new(Semaphore::new(MAX_CONCURRENCY));
    let mut handles = Vec::new();

    for chunk in questions.chunks(CHUNK_SIZE) {
        let client = client.clone();
        let provider = provider.clone();
        let model = chosen_model.to_string();
        let chunk = chunk.to_vec();
        let permit = semaphore.clone().acquire_owned().await?;

        handles.push(tokio::spawn(async move {
            let res = match provider.protocol {
                LLMProtocol::OpenAIChatCompletions => {
                    chat_completions(&client, &provider, &model, &chunk).await
                }
                LLMProtocol::OpenAIResponses => responses(&client, &provider, &model, &chunk).await,
                LLMProtocol::GoogleGemini => gemini(&client, &provider, &model, &chunk).await,
            };
            drop(permit);
            res
        }));
    }

    let mut all_answers = Vec::with_capacity(questions.len());
    for handle in handles {
        let chunk_answers = handle.await??;
        all_answers.extend(chunk_answers);
    }

    Ok(all_answers)
}

/// 发送 HTTP 请求，若遇到 429 (Too Many Requests) 则解析 Retry-After 头并使用指数退避自动重试
async fn send_with_retry<F>(build_req: F) -> Result<reqwest::Response>
where
    F: Fn() -> reqwest::RequestBuilder,
{
    const MAX_RETRIES: u32 = 3;

    for retry in 0..MAX_RETRIES {
        let res = build_req().send().await?;

        if res.status() == reqwest::StatusCode::TOO_MANY_REQUESTS {
            let delay = res
                .headers()
                .get("retry-after")
                .and_then(|h| h.to_str().ok()?.parse().ok())
                .map(std::time::Duration::from_secs)
                .unwrap_or_else(|| std::time::Duration::from_millis(1000 * (1 << retry)));

            log::warn!(
                "触发 API 限流 (429)，将在 {:?} 后进行第 {}/{} 次重试...",
                delay,
                retry + 1,
                MAX_RETRIES
            );
            tokio::time::sleep(delay).await;
            continue;
        }
        return Ok(res);
    }

    Ok(build_req().send().await?)
}

/// 通用 OpenAI ChatCompletions 接口处理
async fn chat_completions(
    client: &reqwest::Client,
    provider: &LLMProvider,
    model: &str,
    questions: &[Question],
) -> Result<Vec<AnswerItem>> {
    let mut request_body: serde_json::Value =
        serde_json::from_str(include_str!("./req_body/default.json"))?;
    request_body["model"] = serde_json::json!(model);
    request_body["messages"] = serde_json::json!([
        { "role": "system", "content": SYSTEM_PROMPT },
        { "role": "user", "content": serde_json::to_string(questions)? }
    ]);

    if let Some(extra) = &provider.extra_body {
        if let (Some(req_obj), Some(extra_obj)) = (request_body.as_object_mut(), extra.as_object())
        {
            for (k, v) in extra_obj {
                req_obj.insert(k.clone(), v.clone());
            }
        }
    }

    let response = send_with_retry(|| {
        let mut req = client.post(&provider.base_url);
        if let Some(key) = provider.api_key.as_ref().map(|key| key.expose()) {
            if !key.trim().is_empty() {
                req = req.header("Authorization", format!("Bearer {}", key));
            }
        }
        req.header("Content-Type", "application/json")
            .json(&request_body)
    })
    .await?;

    if !response.status().is_success() {
        anyhow::bail!(
            "{} API 错误 ({}): {}",
            provider.name,
            response.status(),
            response.text().await?
        );
    }

    let data: serde_json::Value = response.json().await?;
    let content = data
        .pointer("/choices/0/message/content")
        .or_else(|| data.pointer("/message/content"))
        .and_then(|v| v.as_str())
        .ok_or_else(|| {
            anyhow::anyhow!("无法从 {} 响应提取文本。原始响应: {}", provider.name, data)
        })?;

    serde_json::from_str(content).map_err(|e| {
        anyhow::anyhow!(
            "从 {} 响应解析答案 JSON 失败: {}。原始返回文本: {}",
            provider.name,
            e,
            content
        )
    })
}

/// OpenAI /v1/responses 接口处理
async fn responses(
    client: &reqwest::Client,
    provider: &LLMProvider,
    model: &str,
    questions: &[Question],
) -> Result<Vec<AnswerItem>> {
    let mut request_body: serde_json::Value =
        serde_json::from_str(include_str!("./req_body/openai.json"))?;
    request_body["model"] = serde_json::json!(model);
    request_body["instructions"] = serde_json::json!(SYSTEM_PROMPT);
    request_body["input"] = serde_json::json!(serde_json::to_string(questions)?);

    let response = send_with_retry(|| {
        let mut req = client.post(&provider.base_url);
        if let Some(key) = provider.api_key.as_ref().map(|key| key.expose()) {
            if !key.trim().is_empty() {
                req = req.header("Authorization", format!("Bearer {}", key));
            }
        }
        req.header("Content-Type", "application/json")
            .json(&request_body)
    })
    .await?;

    if !response.status().is_success() {
        anyhow::bail!(
            "OpenAI API 错误 ({}): {}",
            response.status(),
            response.text().await?
        );
    }

    let data: serde_json::Value = response.json().await?;
    let content = data
        .pointer("/output/1/content/0/text")
        .and_then(|v| v.as_str())
        .or_else(|| {
            data["output"]
                .as_array()?
                .iter()
                .find(|o| o["type"] == "message")?
                .pointer("/content/0/text")?
                .as_str()
        })
        .ok_or_else(|| anyhow::anyhow!("无法从 OpenAI 响应提取文本。原始响应: {}", data))?;

    if let Ok(wrapper) = serde_json::from_str::<serde_json::Value>(content) {
        if let Some(answers) = wrapper.get("answers") {
            return Ok(serde_json::from_value(answers.clone())?);
        }
    }

    serde_json::from_str::<Vec<AnswerItem>>(content).map_err(|e| {
        anyhow::anyhow!(
            "从 OpenAI 响应解析答案 JSON 失败: {}。原始返回文本: {}",
            e,
            content
        )
    })
}

/// Google Gemini :generateContent 接口处理
async fn gemini(
    client: &reqwest::Client,
    provider: &LLMProvider,
    model: &str,
    questions: &[Question],
) -> Result<Vec<AnswerItem>> {
    let mut body: serde_json::Value = serde_json::from_str(include_str!("./req_body/google.json"))?;
    body["contents"] = serde_json::json!([{
        "parts": [{ "text": serde_json::to_string(questions)? }]
    }]);
    body["systemInstruction"] = serde_json::json!({
        "parts": [{ "text": SYSTEM_PROMPT }]
    });

    let url = format!("{}/{}:generateContent", provider.base_url, model);
    let response = send_with_retry(|| {
        let mut req = client.post(&url);
        if let Some(key) = provider.api_key.as_ref().map(|key| key.expose()) {
            if !key.trim().is_empty() {
                req = req.header("x-goog-api-key", key);
            }
        }
        req.header("Content-Type", "application/json").json(&body)
    })
    .await?;

    if !response.status().is_success() {
        anyhow::bail!(
            "Google API 错误 ({}): {}",
            response.status(),
            response.text().await?
        );
    }

    let data: serde_json::Value = response.json().await?;
    let content = data
        .pointer("/candidates/0/content/parts/0/text")
        .and_then(|v| v.as_str())
        .ok_or_else(|| anyhow::anyhow!("无法从 Google 响应提取文本。原始响应: {}", data))?;

    serde_json::from_str::<Vec<AnswerItem>>(content).map_err(|e| {
        anyhow::anyhow!(
            "从 Google 响应解析答案 JSON 失败: {}。原始返回文本: {}",
            e,
            content
        )
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::llm::LLMConfig;
    use std::fs;
    use std::path::PathBuf;

    fn load_questions_file(filename: &str) -> Vec<Question> {
        let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        path.push("tests/assets/course-page");
        path.push(filename);
        let json_str =
            fs::read_to_string(&path).unwrap_or_else(|_| panic!("找不到测试文件: {:?}", path));
        serde_json::from_str(&json_str).expect("JSON 解析到 Question 结构失败")
    }

    fn load_test_questions() -> Vec<Question> {
        load_questions_file("decrypted.json")
    }

    fn get_test_provider(provider_id: &str, env_var: &str) -> Option<LLMProvider> {
        dotenv::dotenv().ok();
        let api_key = std::env::var(env_var).ok().filter(|k| !k.is_empty())?;
        let config = LLMConfig::default();
        let mut provider = config.providers.lock().get(provider_id).cloned()?;
        provider.api_key = Some(crate::config::llm::ApiKey::new(api_key).unwrap());
        Some(provider)
    }

    #[tokio::test]
    async fn test_solve_bigmodel() {
        let questions = load_test_questions();
        let Some(provider) = get_test_provider("bigmodel", "BIGMODEL_API_KEY") else {
            return;
        };

        match solve(&provider, questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                for (i, answer) in answers.iter().enumerate() {
                    println!("BigModel 问题 {} 的回答: {:?}", i + 1, answer);
                }
            }
            Err(e) => panic!("BigModel 测试失败: {}", e),
        }
    }

    #[tokio::test]
    async fn test_solve_deepseek() {
        let questions = load_test_questions();
        let Some(provider) = get_test_provider("deepseek", "DEEPSEEK_API_KEY") else {
            return;
        };

        match solve(&provider, questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                println!("DeepSeek 收到回答，{:?}", answers);
            }
            Err(e) => panic!("DeepSeek 测试失败: {}", e),
        }
    }

    #[tokio::test]
    async fn test_solve_google() {
        let questions = load_test_questions();
        let Some(provider) = get_test_provider("google", "GOOGLE_API_KEY") else {
            return;
        };

        match solve(&provider, questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                for (i, answer) in answers.iter().enumerate() {
                    println!("Google 问题 {} 的回答: {:?}", i + 1, answer);
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if err_msg.contains("429") || err_msg.contains("RESOURCE_EXHAUSTED") {
                    println!("Google 测试跳过 (超出 API 免费频次限制 429): {}", err_msg);
                } else {
                    panic!("Google 测试失败: {}", e);
                }
            }
        }
    }

    #[tokio::test]
    async fn test_solve_moonshot() {
        let questions = load_test_questions();
        let Some(provider) = get_test_provider("moonshot", "MOONSHOT_API_KEY") else {
            return;
        };

        match solve(&provider, questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                for (i, answer) in answers.iter().enumerate() {
                    println!("Moonshot 问题 {} 的回答: {:?}", i + 1, answer);
                }
            }
            Err(e) => panic!("Moonshot 测试失败: {}", e),
        }
    }

    #[tokio::test]
    async fn test_solve_openai() {
        let questions = load_test_questions();
        let Some(provider) = get_test_provider("openai", "OPENAI_API_KEY") else {
            return;
        };

        match solve(&provider, questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                for (i, answer) in answers.iter().enumerate() {
                    println!("OpenAI 问题 {} 的回答: {:?}", i + 1, answer);
                }
            }
            Err(e) => panic!("OpenAI 测试失败: {}", e),
        }
    }

    #[tokio::test]
    async fn test_solve_openrouter() {
        let questions = load_test_questions();
        let Some(provider) = get_test_provider("openrouter", "OPENROUTER_API_KEY") else {
            return;
        };

        match solve(&provider, questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                for (i, answer) in answers.iter().enumerate() {
                    println!("OpenRouter 问题 {} 的回答: {:?}", i + 1, answer);
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if err_msg.contains("402")
                    || err_msg.contains("429")
                    || err_msg.contains("404")
                    || err_msg.contains("expected value")
                {
                    println!(
                        "OpenRouter 测试跳过 (外部 API 服务状态限制/格式异常): {}",
                        err_msg
                    );
                } else {
                    panic!("OpenRouter 测试失败: {}", e);
                }
            }
        }
    }

    #[tokio::test]
    async fn test_solve_ollama() {
        let questions = load_test_questions();
        let config = LLMConfig::default();
        let provider = config.providers.lock().get("ollama").cloned().unwrap();

        match solve(&provider, questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                println!("Ollama 收到回答，{:?}", answers);
            }
            Err(e) => {
                println!("Ollama 调用失败 (可能未启动本地 Ollama 服务): {}", e);
            }
        }
    }

    #[tokio::test]
    #[ignore]
    async fn test_solve_100_questions() {
        let questions = load_questions_file("questions_100.json");
        assert_eq!(questions.len(), 100);

        let Some(provider) = get_test_provider("deepseek", "DEEPSEEK_API_KEY") else {
            return;
        };

        let start = std::time::Instant::now();
        println!("🚀 开始进行 100 道题目的大长对话/并发性能基准测试...");
        match solve(&provider, questions).await {
            Ok(answers) => {
                let duration = start.elapsed();
                println!("✅ 100 道题求解完成！总耗时: {:?}", duration);
                println!("📊 平均单题耗时: {:?}", duration / 100);
                println!("解析到的答案总数: {}", answers.len());
                println!("\n📋 抽样 10 道题目的回答结果展示:");
                for (i, answer) in answers.iter().step_by(10).take(10).enumerate() {
                    println!(
                        "[抽样 {}] 题号: {:<3} | 答案: {:<6} | 解析: {}",
                        i + 1,
                        answer.index,
                        answer.content,
                        answer.explanation
                    );
                }
            }
            Err(e) => panic!("100 题性能测试失败: {}", e),
        }
    }
}
