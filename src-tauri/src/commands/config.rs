use super::CommandsResult;

use crate::config::{llm::LLMProvider, metadata::MetadataConfig, options::OptionsConfig, CONFIG};

use strum::IntoEnumIterator;

/// 获取包含版本及作者信息的应用元数据。
#[tauri::command]
#[specta::specta]
pub fn metadata() -> MetadataConfig {
    log::debug!("正在获取元数据...");
    let metadata = CONFIG.metadata.clone();
    log::info!("成功获取元数据: {:?}", metadata);
    metadata
}

#[tauri::command]
#[specta::specta]
pub fn options() -> OptionsConfig {
    log::debug!("正在获取配置信息...");
    let options = *CONFIG.options.lock();
    log::info!("成功获取配置信息: {:?}", options);
    options
}

#[tauri::command]
#[specta::specta]
pub fn set_options(options: OptionsConfig) {
    log::debug!("正在设置配置信息...");
    *CONFIG.options.lock() = options;
    log::info!("成功设置配置信息: {:?}", options);
}

/// 获取当前可用的全部大语言模型提供商列表。
#[tauri::command]
#[specta::specta]
pub fn providers() -> Vec<String> {
    log::debug!("正在获取可用 AI Provider 列表...");
    let providers: Vec<String> = LLMProvider::iter()
        .map(|p| p.as_ref().to_string())
        .collect();
    log::info!("成功获取 AI Provider 列表: {:?}", providers);
    providers
}

/// 获取当前选中的大语言模型提供商。
#[tauri::command]
#[specta::specta]
pub fn current_provider() -> String {
    let provider = CONFIG.llm.provider.lock();
    log::debug!("正在获取当前 AI Provider: {}", provider.as_ref());
    provider.as_ref().to_string()
}

/// 将当前大语言模型提供商切换为指定提供商。
#[tauri::command]
#[specta::specta]
pub fn switch_provider(provider: String) -> CommandsResult<()> {
    log::debug!("正在切换 AI Provider 到 [{}]", provider);
    let llmp = provider
        .parse::<LLMProvider>()
        .map_err(|_| anyhow::anyhow!("无效的 AI Provider [{}]", provider))?;

    CONFIG.llm.switch_to(llmp);
    log::info!("成功切换 AI Provider 到 [{}]", provider);
    Ok(())
}

/// 获取当前大语言模型提供商所支持的全部模型列表。
#[tauri::command]
#[specta::specta]
pub fn models() -> Vec<String> {
    log::debug!("正在获取可用模型列表...");
    let models = CONFIG.llm.current().available_models();
    log::info!("成功获取模型列表: {:?}", models);
    models
}

/// 获取当前大语言模型提供商正在使用的具体模型名称。
#[tauri::command]
#[specta::specta]
pub fn current_model() -> String {
    log::debug!(
        "当正在获取当前模型: {}",
        CONFIG.llm.current().current_model()
    );
    CONFIG.llm.current().current_model()
}

/// 将当前大语言模型提供商的选用模型切换为指定模型。
#[tauri::command]
#[specta::specta]
pub fn switch_model(model: String) {
    log::debug!("正在切换模型到 [{}]...", model);
    CONFIG.llm.current().switch_model(&model);
    log::info!("成功切换模型到 [{}]", model);
}

#[tauri::command]
#[specta::specta]
pub fn api_key() -> String {
    log::debug!("正在获取当前 API Key...");
    let key = CONFIG.llm.current().api_key();
    log::debug!("成功获取当前 API Key: {}...", key);
    key
}

/// 设置当前大语言模型提供商的 API 密钥。
#[tauri::command]
#[specta::specta]
pub fn set_key(key: String) {
    log::debug!("正在设置 [{:?}] 的 API 密钥...", CONFIG.llm.provider);
    CONFIG.llm.current().set_key(&key);
    log::info!("成功设置 [{:?}] 的 API 密钥", CONFIG.llm.provider);
}

/// 将内存中的全局配置持久化保存至本地文件。
#[tauri::command]
#[specta::specta]
pub fn save_config() -> CommandsResult<()> {
    log::debug!("正在保存配置文件...");
    CONFIG.save()?;
    log::info!("成功保存配置文件");
    Ok(())
}
