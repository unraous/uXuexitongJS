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
    pub name: String,            // 提供商显示名称 (如 "DeepSeek 官方", "我的私有中转站")
    pub protocol: LLMProtocol,   // 采用的 API 协议族
    pub base_url: String,        // 接口基础 URL
    pub api_key: Option<String>, // API Key (Option 允许免 Key / 未配置)
    pub models: Vec<String>,     // 支持的模型列表
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
        let providers: HashMap<String, LLMProvider> =
            serde_json::from_str(include_str!("./llm/providers.default.json"))
                .expect("无法解析默认 LLM 提供商预设配置文件 (providers.default.json)");

        Self {
            active_provider: Mutex::new("bigmodel".to_string()),
            providers: Mutex::new(providers),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_llm_default_config_preset_providers() {
        let config = LLMConfig::default();
        assert_eq!(*config.active_provider.lock(), "bigmodel");

        let providers = config.providers.lock();
        let expected_online_providers = [
            ("bigmodel", "BigModel", LLMProtocol::OpenAIChatCompletions),
            ("deepseek", "DeepSeek", LLMProtocol::OpenAIChatCompletions),
            ("google", "Google", LLMProtocol::GoogleGemini),
            ("moonshot", "Moonshot", LLMProtocol::OpenAIChatCompletions),
            ("openai", "OpenAI", LLMProtocol::OpenAIResponses),
            (
                "openrouter",
                "OpenRouter",
                LLMProtocol::OpenAIChatCompletions,
            ),
        ];

        for (id, expected_name, expected_protocol) in expected_online_providers {
            let provider = providers
                .get(id)
                .unwrap_or_else(|| panic!("默认预设必须包含提供商: {}", id));
            assert_eq!(provider.name, expected_name);
            assert_eq!(provider.protocol, expected_protocol);
            assert!(
                provider.base_url.starts_with("https://"),
                "提供商 {} 的 URL 必须以 https:// 开头: {}",
                id,
                provider.base_url
            );
            assert!(
                !provider.models.is_empty(),
                "提供商 {} 的支持模型列表不能为空",
                id
            );
            let chosen_idx = provider
                .chosen_model
                .unwrap_or_else(|| panic!("提供商 {} 必须有默认选中的模型索引", id));
            assert!(
                chosen_idx < provider.models.len(),
                "提供商 {} 的选择索引超出范围: {} >= {}",
                id,
                chosen_idx,
                provider.models.len()
            );
        }
    }
}
