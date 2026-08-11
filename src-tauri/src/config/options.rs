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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_options_config_serde_and_default() {
        let opts = OptionsConfig::default();
        assert!(opts.persist_session);
        assert!(opts.mute_webview);
        assert!(!opts.speed_lock);
        assert_eq!(opts.speed_value, 2.0);

        let json = serde_json::to_string(&opts).unwrap();
        assert!(json.contains("\"persistSession\":true"));
        assert!(json.contains("\"muteWebview\":true"));
        assert!(json.contains("\"speedLock\":false"));
        assert!(json.contains("\"speedValue\":2.0"));

        let deserialized: OptionsConfig = serde_json::from_str(&json).unwrap();
        assert_eq!(deserialized.speed_value, 2.0);
    }
}
