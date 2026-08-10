use serde::{Deserialize, Serialize};
use specta::Type;

#[derive(Serialize, Deserialize, Debug, Clone, Copy, Type)]
#[serde(default, rename_all = "camelCase")] // 将 Rust 下划线命名（snake_case）自动映射为 TypeScript 驼峰命名（camelCase）
pub struct OptionsConfig {
    pub persist_session: bool,
    pub mute_webview: bool,
    pub speed_lock: bool,
    pub speed_value: f32,
}

impl Default for OptionsConfig {
    fn default() -> Self {
        Self {
            persist_session: true,
            mute_webview: true,
            speed_lock: false,
            speed_value: 2.0,
        }
    }
}
