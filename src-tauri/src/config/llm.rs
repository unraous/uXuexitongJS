pub(crate) mod ollama;

use parking_lot::Mutex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;

/// 支持的大模型 API 发包协议族
#[derive(Serialize, Deserialize, Debug, Clone, PartialEq, Eq, Hash)]
pub enum LLMProtocol {
    OpenAIChatCompletions, // 通用 OpenAI 兼容协议 (Chat Completions)
    OpenAIResponses,       // OpenAI Responses 特殊协议 (/v1/responses)
    GoogleGemini,          // Google Gemini 协议 (:generateContent)
}

/// 统一的大模型提供商结构体（内置与用户自定义提供商通用纯数据 DTO）
#[derive(Serialize, Deserialize, Debug, Clone)]
pub struct LLMProvider {
    pub name: String,                // 提供商显示名称 (如 "DeepSeek 官方", "我的私有中转站")
    pub protocol: LLMProtocol,       // 采用的 API 协议族
    pub base_url: String,            // 接口基础 URL
    pub api_key: Option<String>,     // API Key (Option 允许免 Key / 未配置)
    pub models: Vec<String>,         // 支持的模型列表
    pub chosen_model: Option<usize>, // 当前选择的模型在 models 列表中的索引
    pub extra_body: Option<serde_json::Value>, // 协议特定额外 Body 参数 (如 temperature, stream)
}

/// 应用全局大语言模型配置 (纯 Plain Data 结构体)
#[derive(Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct LLMConfig {
    pub active_provider: Mutex<String>, // 当前激活的提供商 ID
    pub providers: Mutex<HashMap<String, LLMProvider>>, // 注册的全部提供商 (HashMap)
}

impl Default for LLMConfig {
    fn default() -> Self {
        let mut providers: HashMap<String, LLMProvider> =
            serde_json::from_str(include_str!("./llm/providers.default.json"))
                .expect("无法解析默认 LLM 提供商预设配置文件 (providers.default.json)");

        // 初始化时从本地 Ollama 服务拉取可用模型列表
        if let Some(p) = providers.get_mut("ollama") {
            let models = ollama::fetch_models(&p.base_url);
            if !models.is_empty() {
                p.models = models;
                p.chosen_model = Some(0);
            }
        }

        Self {
            active_provider: Mutex::new("bigmodel".to_string()),
            providers: Mutex::new(providers),
        }
    }
}
