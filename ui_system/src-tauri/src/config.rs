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

#[derive(Default, Debug, Serialize, Deserialize)]
pub struct GlobalConfig {
    #[serde(default)]
    pub zenoh_prefix: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GUIConfig {
    #[serde(default)]
    pub host: String,
    #[serde(default)]
    pub port: String,
}

impl Default for GUIConfig {
    fn default() -> Self {
        GUIConfig {
            host: "localhost".to_string(),
            port: "8080".to_string(),
        }
    }
}

pub fn parse_globalconfig(path: Option<&str>) -> GlobalConfig {
    let p = get_config_file(path);
    let value: Value = toml::from_str(&std::fs::read_to_string(p).unwrap()).unwrap();

    match value.get("global") {
        Some(v) => v.clone().try_into().unwrap(),
        None => GlobalConfig::default(),
    }
}

pub fn parse_guiconfig(path: Option<&str>) -> GUIConfig {
    let p = get_config_file(path);
    let value: Value = toml::from_str(&std::fs::read_to_string(p).unwrap()).unwrap();

    match value.get("gui") {
        Some(v) => v.clone().try_into().unwrap(),
        None => GUIConfig::default(),
    }
}
