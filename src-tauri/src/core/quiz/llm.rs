mod dispatcher;

pub use dispatcher::solve;

use super::html::Question;

use anyhow::Result;
use serde::{Deserialize, Serialize};

const SYSTEM_PROMPT: &str = include_str!("./system_prompt.txt");

#[derive(Serialize, Deserialize, Debug)]
pub struct AnswerItem {
    #[serde(alias = "题号", alias = "id")]
    pub index: String,
    #[serde(alias = "解析")]
    pub explanation: String,
    #[serde(alias = "答案", alias = "answer")]
    pub content: String,
}

pub fn validate(model: &str, questions: &[Question]) -> Result<()> {
    if questions.is_empty() {
        anyhow::bail!("接收到空的题目列表");
    }
    if model.is_empty() {
        anyhow::bail!("未选择 AI 模型");
    }
    Ok(())
}
