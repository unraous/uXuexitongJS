use log::LevelFilter;
use serde::{Deserialize, Serialize};
use specta::Type;
use tauri::Url;

#[derive(Serialize, Deserialize, Debug, Clone, Type)]
#[serde(default, rename_all = "camelCase")]
pub struct MetadataConfig {
    pub author: String,
    pub title: String,
    pub version: String,
    #[specta(type = String)]
    pub home_url: Url,
    #[specta(type = String)]
    pub log_level: LevelFilter,
}

impl Default for MetadataConfig {
    fn default() -> Self {
        Self {
            author: "unraous".into(),
            title: "uXueScript".into(),
            version: "2.0.1".into(),
            home_url: Url::parse("https://i.mooc.chaoxing.com/").expect("Invalid home URL"),
            log_level: if cfg!(debug_assertions) {
                LevelFilter::Debug
            } else {
                LevelFilter::Info
            },
        }
    }
}
