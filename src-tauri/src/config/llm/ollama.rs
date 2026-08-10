use serde::Deserialize;

#[derive(Deserialize)]
struct OllamaTagsResponse {
    models: Vec<OllamaModelEntry>,
}

#[derive(Deserialize)]
struct OllamaModelEntry {
    model: String,
}

/// 从本地 Ollama 服务拉取可用模型列表。
/// 服务未启动或请求失败时静默返回空 Vec，不影响其他初始化流程。
pub fn fetch_models(base_url: &str) -> Vec<String> {
    let tags_url = format!(
        "{}/tags",
        &base_url[..base_url.rfind('/').unwrap_or(base_url.len())]
    );

    let resp = match reqwest::blocking::get(&tags_url) {
        Ok(r) => r,
        Err(_) => return vec![],
    };

    resp.json::<OllamaTagsResponse>()
        .map(|data| data.models.into_iter().map(|m| m.model).collect())
        .unwrap_or_default()
}
