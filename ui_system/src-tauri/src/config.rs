use serde::{Deserialize, Serialize};

use dirs;
use std::env;
use std::path::PathBuf;

fn get_config_file(file_path: Option<&str>) -> PathBuf {
    match file_path {
        Some(p2) => match PathBuf::from(p2).canonicalize() {
            Ok(abs) => abs,
            Err(_) => panic!("不明なファイルです"),
        },
        None => match env::var("XDG_CONFIG_HOME") {
            Ok(path) => PathBuf::from(path).join("roboapp/config.toml"),
            Err(_) => match dirs::home_dir() {
                Some(home) => home.join(".config").join("roboapp/config.toml"),
                None => panic!("ホームディレクトリが取得できませんでした"),
            },
        },
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GlobalConfig {
    #[serde(default = "GlobalConfig::default_websocket_port")]
    pub websocket_port: u16,
    #[serde(default = "GlobalConfig::default_zenoh_prefix")]
    pub zenoh_prefix: String,
}

impl Default for GlobalConfig {
    fn default() -> Self {
        Self {
            websocket_port: Self::default_websocket_port(),
            zenoh_prefix: Self::default_zenoh_prefix(),
        }
    }
}

impl GlobalConfig {
    fn default_websocket_port() -> u16 {
        8080
    }
    fn default_zenoh_prefix() -> String {
        "".to_string()
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
    pub global: GlobalConfig,
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
    fn test_parse_globalconfig() {
        let g = load_config(Some("test/resources/global_config_empty.toml"))
            .unwrap()
            .global;

        assert_eq!(g.websocket_port, 8080);
        assert_eq!(g.zenoh_prefix, "");
    }

    #[test]
    fn test_parse_globalconfig_zenoh_prefix() {
        let g = load_config(Some("test/resources/global_config_zenoh_prefix.toml"))
            .unwrap()
            .global;

        assert_eq!(g.websocket_port, 8080);
        assert_eq!(g.zenoh_prefix, "roboapp".to_string());
    }

    #[test]
    fn test_parse_globalconfig_websocket_port() {
        let g = load_config(Some("test/resources/global_config_websocket_port.toml"))
            .unwrap()
            .global;

        assert_eq!(g.websocket_port, 9090);
        assert_eq!(g.zenoh_prefix, "");
    }

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
