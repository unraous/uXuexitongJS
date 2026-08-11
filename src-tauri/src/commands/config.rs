use super::CommandsResult;

use crate::config::{metadata::MetadataConfig, options::OptionsConfig, CONFIG};

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
    let providers_map = CONFIG.llm.providers.lock();
    let mut providers: Vec<String> = providers_map.keys().cloned().collect();
    providers.sort();
    log::info!("成功获取 AI Provider 列表: {:?}", providers);
    providers
}

/// 获取当前选中的大语言模型提供商。
#[tauri::command]
#[specta::specta]
pub fn current_provider() -> String {
    let provider = CONFIG.llm.active_provider.lock().clone();
    log::debug!("正在获取当前 AI Provider: {}", provider);
    provider
}

/// 将当前大语言模型提供商切换为指定提供商。
#[tauri::command]
#[specta::specta]
pub fn switch_provider(provider: String) -> CommandsResult<()> {
    log::debug!("正在切换 AI Provider 到 [{}]", provider);
    let providers = CONFIG.llm.providers.lock();
    if providers.contains_key(&provider) {
        *CONFIG.llm.active_provider.lock() = provider.clone();
        log::info!("成功切换 AI Provider 到 [{}]", provider);
        Ok(())
    } else {
        Err(anyhow::anyhow!("找不到 ID 为 [{}] 的大模型提供商", provider).into())
    }
}

/// 获取当前大语言模型提供商所支持的全部模型列表。
#[tauri::command]
#[specta::specta]
pub fn models() -> Vec<String> {
    log::debug!("正在获取可用模型列表...");
    let active_id = CONFIG.llm.active_provider.lock();
    let providers = CONFIG.llm.providers.lock();
    let models = providers
        .get(&*active_id)
        .map(|p| p.models.clone())
        .unwrap_or_default();
    log::info!("成功获取模型列表: {:?}", models);
    models
}

/// 获取当前大语言模型提供商正在使用的具体模型名称。
#[tauri::command]
#[specta::specta]
pub fn current_model() -> String {
    let active_id = CONFIG.llm.active_provider.lock();
    let providers = CONFIG.llm.providers.lock();
    let model = providers
        .get(&*active_id)
        .and_then(|p| p.chosen_model.and_then(|idx| p.models.get(idx)))
        .map(|s| s.as_str())
        .unwrap_or_default()
        .to_string();
    log::debug!("正在获取当前模型: {}", model);
    model
}

/// 将当前大语言模型提供商的选用模型切换为指定模型。
#[tauri::command]
#[specta::specta]
pub fn switch_model(model: String) {
    log::debug!("正在切换模型到 [{}]...", model);
    let active_id = CONFIG.llm.active_provider.lock();
    let mut providers = CONFIG.llm.providers.lock();
    if let Some(p) = providers.get_mut(&*active_id) {
        if let Some(pos) = p.models.iter().position(|m| m == &model) {
            p.chosen_model = Some(pos);
        }
    }
    log::info!("成功切换模型到 [{}]", model);
}

#[tauri::command]
#[specta::specta]
pub fn api_key() -> String {
    log::debug!("正在获取当前 API Key...");
    let active_id = CONFIG.llm.active_provider.lock();
    let providers = CONFIG.llm.providers.lock();
    let key = providers
        .get(&*active_id)
        .and_then(|p| p.api_key.clone())
        .unwrap_or_default();
    log::debug!("成功获取当前 API Key: {}...", key);
    key
}

/// 设置当前大语言模型提供商的 API 密钥。
#[tauri::command]
#[specta::specta]
pub fn set_key(key: String) {
    log::debug!("正在设置 API 密钥...");
    let active_id = CONFIG.llm.active_provider.lock();
    let mut providers = CONFIG.llm.providers.lock();
    if let Some(p) = providers.get_mut(&*active_id) {
        p.api_key = if key.trim().is_empty() {
            None
        } else {
            Some(key)
        };
    }
    log::info!("成功设置 API 密钥");
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

/// 从本地 Ollama 服务拉取可用模型列表更新至内存配置。
#[tauri::command]
#[specta::specta]
pub async fn fetch_ollama_models() -> CommandsResult<()> {
    log::debug!("正在从 Ollama 服务拉取最新模型列表...");
    let base_url = {
        let providers = CONFIG.llm.providers.lock();
        let p = providers
            .get("ollama")
            .ok_or_else(|| anyhow::anyhow!("找不到 Ollama 提供商"))?;
        p.base_url.clone()
    };

    let models = crate::config::llm::ollama::fetch_models(&base_url).await;
    if models.is_empty() {
        return Err(anyhow::anyhow!("未能从 Ollama 服务 [{}] 获取到可用模型列表", base_url).into());
    }

    let mut providers = CONFIG.llm.providers.lock();
    if let Some(p) = providers.get_mut("ollama") {
        p.models = models;
        p.chosen_model = Some(0);
    }
    log::info!("Ollama 模型列表更新完成");
    Ok(())
}
