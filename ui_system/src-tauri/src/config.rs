use serde::{Deserialize, Serialize};

use dirs;
use std::env;
use std::path::PathBuf;

pub fn get_config_path() -> PathBuf {
    match env::var("XDG_CONFIG_HOME") {
        Ok(path) => PathBuf::from(path).join("roboapp"),
        Err(_) => match dirs::home_dir() {
            Some(home) => home.join(".config").join("roboapp"),
            None => panic!("ホームディレクトリが取得できませんでした"),
        },
    }
}

fn get_config_file(file_path: Option<&str>) -> PathBuf {
    match file_path {
        Some(p2) => match PathBuf::from(p2).canonicalize() {
            Ok(abs) => abs,
            Err(_) => panic!("不明なファイルです"),
        },
        None => get_config_path().join("config.toml"),
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GUIConfig {
    #[serde(default = "GUIConfig::default_host")]
    pub host: String,
}

impl Default for GUIConfig {
    fn default() -> Self {
        GUIConfig {
            host: Self::default_host(),
        }
    }
}

impl GUIConfig {
    fn default_host() -> String {
        "localhost".to_string()
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    #[serde(default)]
    pub gui: Option<GUIConfig>,
}

pub fn load_config(path: Option<&str>) -> Result<Config, Box<dyn std::error::Error>> {
    let config_path = get_config_file(path);
    let content = std::fs::read_to_string(config_path)?;
    let config: Config = toml::from_str(&content)?;
    Ok(config)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_guiconfig_empty() {
        let config = load_config(Some("test/resources/gui_config_empty.toml")).unwrap();

        assert!(config.gui.is_none());
    }

    #[test]
    fn test_parse_guiconfig_host() {
        let config = load_config(Some("test/resources/gui_config_host.toml")).unwrap();

        let g = config.gui.expect("gui section should exist");
        assert_eq!(g.host, "foo.local");
    }
}
