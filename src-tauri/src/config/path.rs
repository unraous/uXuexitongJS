use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;

#[derive(Serialize, Deserialize, Debug)]
#[serde(default)]
pub struct PathsConfig {
    pub dirs: HashMap<String, PathBuf>,
    pub files: HashMap<String, PathBuf>,
}

impl Default for PathsConfig {
    fn default() -> Self {
        let cwd = std::env::current_dir().unwrap_or_else(|_| PathBuf::from("."));
        let base_dir = if cfg!(debug_assertions) {
            cwd.parent().unwrap_or(&cwd)
        } else {
            &cwd
        };
        let data_dir = base_dir.join("uxs-data");

        Self {
            dirs: HashMap::from([
                ("data".into(), data_dir.clone()),
                ("logs".into(), data_dir.join("logs")),
            ]),
            files: HashMap::from([("config".into(), data_dir.join("config.toml"))]),
        }
    }
}

impl PathsConfig {
    pub fn ensure(&self) -> std::io::Result<()> {
        // 只创建必要目录，避免生成 0 字节空配置文件
        for dir in self.dirs.values() {
            std::fs::create_dir_all(dir)?;
        }
        Ok(())
    }
}
