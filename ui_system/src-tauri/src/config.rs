use serde::{Deserialize, Serialize};
use toml::Value;

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
    pub zenoh_prefix: Option<String>,
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
    fn default_zenoh_prefix() -> Option<String> {
        None
    }
    pub fn from_config_file(path: Option<&str>) -> Self {
        let value: Value =
            toml::from_str(&std::fs::read_to_string(get_config_file(path)).unwrap()).unwrap();

        match value.get("global") {
            Some(v) => match v.clone().try_into() {
                Ok(cfg) => cfg,
                Err(_) => panic!("'global' テーブルのパースに失敗しました"),
            },
            None => GlobalConfig::default(),
        }
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
    pub fn from_config_file(path: Option<&str>) -> Self {
        let value: Value =
            toml::from_str(&std::fs::read_to_string(get_config_file(path)).unwrap()).unwrap();

        match value.get("gui") {
            Some(v) => match v.clone().try_into() {
                Ok(cfg) => cfg,
                Err(_) => panic!("'gui' テーブルのパースに失敗しました"),
            },
            None => GUIConfig::default(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_globalconfig() {
        let g = GlobalConfig::from_config_file(Some("test/resources/global_config_empty.toml"));

        assert_eq!(g.websocket_port, 8080);
        assert_eq!(g.zenoh_prefix, None);
    }

    #[test]
    fn test_parse_globalconfig_zenoh_prefix() {
        let g =
            GlobalConfig::from_config_file(Some("test/resources/global_config_zenoh_prefix.toml"));

        assert_eq!(g.websocket_port, 8080);
        assert_eq!(g.zenoh_prefix, Some("roboapp".into()));
    }

    #[test]
    fn test_parse_globalconfig_websocket_port() {
        let g = GlobalConfig::from_config_file(Some(
            "test/resources/global_config_websocket_port.toml",
        ));

        assert_eq!(g.websocket_port, 9090);
        assert_eq!(g.zenoh_prefix, None);
    }

    #[test]
    fn test_parse_guiconfig_empty() {
        let g = GUIConfig::from_config_file(Some("test/resources/gui_config_empty.toml"));

        assert_eq!(g.host, "localhost");
    }

    #[test]
    fn test_parse_guiconfig_host() {
        let g = GUIConfig::from_config_file(Some("test/resources/gui_config_host.toml"));

        assert_eq!(g.host, "foo.local");
    }
}
