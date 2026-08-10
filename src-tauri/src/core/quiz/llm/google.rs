use super::{AnswerItem, LLM, SYSTEM_PROMPT};

use crate::config::llm::GoogleConfig;
use crate::core::quiz::html::Question;

use anyhow::Result;
use async_trait::async_trait;
use serde_json::json;

#[async_trait]
impl LLM for GoogleConfig {
    fn api_key(&self) -> String {
        self.api_key.lock().clone()
    }
    fn set_key(&self, key: &str) {
        *self.api_key.lock() = key.to_string();
    }
    fn available_models(&self) -> Vec<String> {
        self.models.clone()
    }
    fn current_model(&self) -> String {
        self.chosen_model.lock().clone()
    }
    fn switch_model(&self, model: &str) {
        *self.chosen_model.lock() = model.to_string();
    }

    async fn solve(&self, question: Vec<Question>) -> Result<Vec<AnswerItem>> {
        log::debug!("将使用 Google 模型 {} 进行推理", *self.chosen_model.lock());
        // 参考 Gemini 官方 REST API 文档：https://ai.google.dev/gemini-api/docs/text-generation?hl=zh-cn#rest
        // 此处的 responseMimeType 需传入大写字符串常量 "APPLICATION_JSON"
        let mut body: serde_json::Value =
            serde_json::from_str(include_str!("./google-request.json"))?;
        body["contents"] = json!([{
            "parts": [{ "text": serde_json::to_string(&question)? }]
        }]);
        body["systemInstruction"] = json!({
            "parts": [{ "text": SYSTEM_PROMPT }]
        });

        let response = reqwest::Client::new()
            .post(format!(
                "https://generativelanguage.googleapis.com/v1beta/models/{}:generateContent",
                *self.chosen_model.lock()
            ))
            .header("x-goog-api-key", format!("{}", self.api_key.lock()))
            .header("Content-Type", "application/json")
            .json(&body)
            .send()
            .await?;

        if !response.status().is_success() {
            anyhow::bail!(
                "Google API 错误 ({}): {}",
                response.status().as_str(),
                response.text().await?
            )
        }

        let data: serde_json::Value = response.json().await?;
        let content = data
            .pointer("/candidates/0/content/parts/0/text")
            .and_then(|v| v.as_str())
            .ok_or_else(|| anyhow::anyhow!("无法从 Google 响应提取文本。原始响应: {}", data))?;

        Ok(serde_json::from_str::<Vec<AnswerItem>>(content)?)
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::fs;
    use std::path::PathBuf;

    #[tokio::test]
    async fn test_solve_with_local_json() {
        // 1. 获取测试文件路径 (假设在 src-tauri 目录下运行)
        let mut path = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
        path.push("tests/assets/course-page/decrypted.json");

        // 2. 读取并解析 JSON 文件
        let json_str =
            fs::read_to_string(&path).unwrap_or_else(|_| panic!("找不到测试文件: {:?}", path));
        let questions: Vec<Question> =
            serde_json::from_str(&json_str).expect("JSON 解析到 Question 结构失败");

        println!("成功加载了 {} 道题目", questions.len());

        dotenv::dotenv().ok();

        // 从环境变量 GOOGLE_API_KEY 读取，如果不存在则报错
        let api_key =
            std::env::var("GOOGLE_API_KEY").expect("请在 .env 文件或环境变量中设置 GOOGLE_API_KEY");

        let config = GoogleConfig {
            api_key: parking_lot::Mutex::new(api_key),
            ..Default::default()
        };

        match config.solve(questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                for (i, answer) in answers.iter().enumerate() {
                    println!("问题 {} 的回答: {:?}", i + 1, answer);
                }
            }
            Err(e) => {
                println!("调用失败: {}", e);
                panic!("测试失败");
            }
        }
    }
}
