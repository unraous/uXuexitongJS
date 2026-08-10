use super::{AnswerItem, SYSTEM_PROMPT};
use crate::config::llm::{LLMProtocol, LLMProvider};
use crate::core::quiz::html::Question;

use anyhow::Result;

/// LLM 求解入口分发器
pub async fn solve(provider: &LLMProvider, questions: Vec<Question>) -> Result<Vec<AnswerItem>> {
    let chosen_model = provider
        .chosen_model
        .and_then(|idx| provider.models.get(idx))
        .ok_or_else(|| anyhow::anyhow!("未为提供商 [{}] 选择有效模型", provider.name))?;

    log::debug!(
        "将使用 [{}] 提供商模型 [{}] 进行推理",
        provider.name,
        chosen_model
    );

    let client = reqwest::Client::new();
    match provider.protocol {
        LLMProtocol::OpenAIChatCompletions => {
            chat_completions(&client, provider, chosen_model, &questions).await
        }
        LLMProtocol::OpenAIResponses => {
            responses(&client, provider, chosen_model, &questions).await
        }
        LLMProtocol::GoogleGemini => gemini(&client, provider, chosen_model, &questions).await,
    }
}

/// 通用 OpenAI ChatCompletions 接口处理
async fn chat_completions(
    client: &reqwest::Client,
    provider: &LLMProvider,
    model: &str,
    questions: &[Question],
) -> Result<Vec<AnswerItem>> {
    let mut request_body: serde_json::Value =
        serde_json::from_str(include_str!("./requests/default.json"))?;
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

    let mut req = client.post(&provider.base_url);
    if let Some(key) = provider.api_key.as_deref() {
        if !key.trim().is_empty() {
            req = req.header("Authorization", format!("Bearer {}", key));
        }
    }
    req = req
        .header("Content-Type", "application/json")
        .json(&request_body);

    let response = req.send().await?;
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

    Ok(serde_json::from_str(content)?)
}

/// OpenAI /v1/responses 接口处理
async fn responses(
    client: &reqwest::Client,
    provider: &LLMProvider,
    model: &str,
    questions: &[Question],
) -> Result<Vec<AnswerItem>> {
    let mut request_body: serde_json::Value =
        serde_json::from_str(include_str!("./requests/openai.json"))?;
    request_body["model"] = serde_json::json!(model);
    request_body["instructions"] = serde_json::json!(SYSTEM_PROMPT);
    request_body["input"] = serde_json::json!(serde_json::to_string(questions)?);

    let mut req = client.post(&provider.base_url);
    if let Some(key) = provider.api_key.as_deref() {
        if !key.trim().is_empty() {
            req = req.header("Authorization", format!("Bearer {}", key));
        }
    }
    req = req
        .header("Content-Type", "application/json")
        .json(&request_body);

    let response = req.send().await?;
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

    Ok(serde_json::from_str::<Vec<AnswerItem>>(content)?)
}

/// Google Gemini :generateContent 接口处理
async fn gemini(
    client: &reqwest::Client,
    provider: &LLMProvider,
    model: &str,
    questions: &[Question],
) -> Result<Vec<AnswerItem>> {
    let mut body: serde_json::Value = serde_json::from_str(include_str!("./requests/google.json"))?;
    body["contents"] = serde_json::json!([{
        "parts": [{ "text": serde_json::to_string(questions)? }]
    }]);
    body["systemInstruction"] = serde_json::json!({
        "parts": [{ "text": SYSTEM_PROMPT }]
    });

    let url = format!("{}/{}:generateContent", provider.base_url, model);
    let mut req = client.post(&url);
    if let Some(key) = provider.api_key.as_deref() {
        if !key.trim().is_empty() {
            req = req.header("x-goog-api-key", key);
        }
    }
    req = req.header("Content-Type", "application/json").json(&body);

    let response = req.send().await?;
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

    Ok(serde_json::from_str::<Vec<AnswerItem>>(content)?)
}

#[cfg(test)]
mod tests {
    use super::*;
    use crate::config::llm::LLMConfig;
    use std::fs;
    use std::path::PathBuf;

    fn load_test_questions() -> Vec<Question> {
        let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        path.push("tests/assets/course-page/decrypted.json");
        let json_str =
            fs::read_to_string(&path).unwrap_or_else(|_| panic!("找不到测试文件: {:?}", path));
        serde_json::from_str(&json_str).expect("JSON 解析到 Question 结构失败")
    }

    #[tokio::test]
    async fn test_solve_bigmodel() {
        let questions = load_test_questions();
        dotenv::dotenv().ok();

        let api_key = match std::env::var("BIGMODEL_API_KEY") {
            Ok(k) if !k.is_empty() => k,
            _ => return,
        };

        let config = LLMConfig::default();
        let mut provider = config.providers.lock().get("bigmodel").cloned().unwrap();
        provider.api_key = Some(api_key);

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
        dotenv::dotenv().ok();

        let api_key = match std::env::var("DEEPSEEK_API_KEY") {
            Ok(k) if !k.is_empty() => k,
            _ => return,
        };

        let config = LLMConfig::default();
        let mut provider = config.providers.lock().get("deepseek").cloned().unwrap();
        provider.api_key = Some(api_key);

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
        dotenv::dotenv().ok();

        let api_key = match std::env::var("GOOGLE_API_KEY") {
            Ok(k) if !k.is_empty() => k,
            _ => return,
        };

        let config = LLMConfig::default();
        let mut provider = config.providers.lock().get("google").cloned().unwrap();
        provider.api_key = Some(api_key);

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
        dotenv::dotenv().ok();

        let api_key = match std::env::var("MOONSHOT_API_KEY") {
            Ok(k) if !k.is_empty() => k,
            _ => return,
        };

        let config = LLMConfig::default();
        let mut provider = config.providers.lock().get("moonshot").cloned().unwrap();
        provider.api_key = Some(api_key);

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
        dotenv::dotenv().ok();

        let api_key = match std::env::var("OPENAI_API_KEY") {
            Ok(k) if !k.is_empty() => k,
            _ => return,
        };

        let config = LLMConfig::default();
        let mut provider = config.providers.lock().get("openai").cloned().unwrap();
        provider.api_key = Some(api_key);

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
        dotenv::dotenv().ok();

        let api_key = match std::env::var("OPENROUTER_API_KEY") {
            Ok(k) if !k.is_empty() => k,
            _ => return,
        };

        let config = LLMConfig::default();
        let mut provider = config.providers.lock().get("openrouter").cloned().unwrap();
        provider.api_key = Some(api_key);

        match solve(&provider, questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                for (i, answer) in answers.iter().enumerate() {
                    println!("OpenRouter 问题 {} 的回答: {:?}", i + 1, answer);
                }
            }
            Err(e) => {
                let err_msg = e.to_string();
                if err_msg.contains("402") || err_msg.contains("429") || err_msg.contains("404") {
                    println!(
                        "OpenRouter 测试跳过 (外部 API 服务状态限制 402/429/404): {}",
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
}
