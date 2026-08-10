use super::{AnswerItem, LLM, SYSTEM_PROMPT};

use crate::config::llm::OllamaConfig;
use crate::core::quiz::html::Question;

use anyhow::Result;
use async_trait::async_trait;

#[async_trait]
impl LLM for OllamaConfig {
    fn api_key(&self) -> String {
        String::new()
    } // Ollama 本地服务无需设置 API Key，固定返回空字符串
    fn set_key(&self, _key: &str) {
        log::warn!("Ollama 无 API Key 可设置")
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
        log::debug!(
            "将使用 Ollama 本地模型 {} 进行推理",
            *self.chosen_model.lock()
        );

        let request_body = serde_json::json!({
            "model": *self.chosen_model.lock(),
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": serde_json::to_string(&question)?
                }
            ],
            "stream": false
        });

        let response = reqwest::Client::new()
            .post("http://localhost:11434/api/chat")
            .json(&request_body)
            .send()
            .await?;

        if !response.status().is_success() {
            anyhow::bail!("Ollama API error: {}", response.status());
        }

        // 解析响应
        let data: serde_json::Value = response.json().await?;
        let content = data
            .pointer("/message/content")
            .and_then(|v| v.as_str())
            .ok_or_else(|| anyhow::anyhow!("无法从 Ollama 响应提取文本。原始响应: {}", data))?;

        Ok(serde_json::from_str(content)?)
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

        let mut config = OllamaConfig::default();
        config.load_models().await;
        match config.solve(questions.clone()).await {
            Ok(answers) => {
                assert_eq!(answers.len(), questions.len());
                println!("收到回答，{:?}", answers);
            }
            Err(e) => {
                println!("调用失败: {}", e);
                panic!("测试失败");
            }
        }
    }
}
