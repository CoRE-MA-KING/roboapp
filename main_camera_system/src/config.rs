use serde::{Deserialize, Serialize};
use toml::Value;

use dirs;
use std::env;
use std::path::PathBuf;

fn get_config_file() -> PathBuf {
    match env::var("XDG_CONFIG_HOME") {
        Ok(path) => PathBuf::from(path).join("roboapp/config.toml"),
        Err(_) => match dirs::home_dir() {
            Some(home) => home.join(".config").join("roboapp/config.toml"),
            None => panic!("ホームディレクトリが取得できませんでした"),
        },
    }
}

#[derive(Debug, Serialize, Deserialize)]

pub struct CameraDevice {
    #[serde(default)]
    pub device: String,
    #[serde(default)]
    pub width: u32,
    #[serde(default)]
    pub height: u32,
}

impl Default for CameraDevice {
    fn default() -> Self {
        CameraDevice {
            device: "/dev/video0".to_string(),
            width: 1280,
            height: 720,
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]

pub struct CameraConfig {
    #[serde(default)]
    pub websocket: bool,
    #[serde(default)]
    pub websocket_port: u16,
    #[serde(default)]
    pub zenoh: bool,
    #[serde(default)]
    pub zenoh_prefix: String,
    #[serde(default)]
    pub devices: Vec<CameraDevice>,
}

impl Default for CameraConfig {
    fn default() -> Self {
        CameraConfig {
            websocket: false,
            websocket_port: 8080,
            zenoh: false,
            zenoh_prefix: "".to_string(),
            devices: vec![CameraDevice::default()],
        }
    }
}

pub fn parse_config(path: Option<PathBuf>) -> CameraConfig {
    let path = match path {
        Some(p) => match p.canonicalize() {
            Ok(abs) => abs,
            Err(_) => p, // 解決できなければそのまま使う
        },
        None => get_config_file(),
    };
    println!("Using config file: {}", path.display());
    let value: Value = toml::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();

    let db_table = value
        .get("camera")
        .unwrap_or_else(|| panic!("'camera' テーブルが見つかりません"));

    // 3. その Value (テーブル) を目的の構造体にデシリアライズ
    db_table.clone().try_into().unwrap()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_config() {
        // let config = parse_config();
        let config = parse_config(Some(PathBuf::from("../config.toml")));
        dbg!(config);
        // 必要ならassert_eq!なども追加可能
    }
}
