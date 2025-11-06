use serde::{Deserialize, Serialize};
use toml::Value;

use dirs;
use std::env;
use std::path::PathBuf;

fn parse_configpath(path: Option<PathBuf>) -> PathBuf {
    match path {
        Some(p) => match p.canonicalize() {
            Ok(abs) => abs,
            Err(_) => p, // 解決できなければそのまま使う
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
    #[serde(default)]
    pub websocket_port: u16,
    #[serde(default)]
    pub zenoh_prefix: Option<String>,
}

impl Default for GlobalConfig {
    fn default() -> Self {
        GlobalConfig {
            websocket_port: 8080,
            zenoh_prefix: None,
        }
    }
}

impl GlobalConfig {
    pub fn from_config_file(path: Option<PathBuf>) -> Self {
        let value: Value =
            toml::from_str(&std::fs::read_to_string(parse_configpath(path)).unwrap()).unwrap();

        match value.get("global") {
            Some(v) => match v.clone().try_into() {
                Ok(cfg) => cfg,
                Err(_) => panic!("'global' テーブルのパースに失敗しました"),
            },
            None => return GlobalConfig::default(),
        }
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct CameraDevice {
    pub device: String,
    #[serde(default)]
    pub width: u32,
    #[serde(default)]
    pub height: u32,
}

impl Default for CameraDevice {
    fn default() -> Self {
        CameraDevice {
            device: String::new(),
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
    pub zenoh: bool,
    #[serde(default)]
    pub devices: Vec<CameraDevice>,
}

impl Default for CameraConfig {
    fn default() -> Self {
        CameraConfig {
            websocket: false,
            zenoh: false,
            devices: vec![],
        }
    }
}

impl CameraConfig {
    pub fn from_config_file(path: Option<PathBuf>) -> Self {
        let value: Value =
            toml::from_str(&std::fs::read_to_string(parse_configpath(path)).unwrap()).unwrap();

        match value.get("camera") {
            Some(v) => match v.clone().try_into() {
                Ok(cfg) => cfg,
                Err(_) => panic!("'camera' テーブルのパースに失敗しました"),
            },
            None => return CameraConfig::default(),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn test_raw_globalconfig() {
        let config = GlobalConfig::default();
        dbg!(&config);
        assert_eq!(config.websocket_port, 8080);
        assert_eq!(config.zenoh_prefix, None);
    }

    #[test]
    fn test_raw_cameraconfig() {
        let config = CameraConfig::default();
        dbg!(&config);
        assert_eq!(config.websocket, false);
        assert_eq!(config.zenoh, false);
        assert_eq!(config.devices.len(), 0);
    }

    #[test]
    fn test_raw_cameradevice() {
        let config = CameraDevice::default();
        dbg!(&config);
        assert_eq!(config.device, "");
        assert_eq!(config.width, 1280);
        assert_eq!(config.height, 720);
    }

    #[test]
    fn test_parse_globalconfig() {
        let g = GlobalConfig::from_config_file(Some(PathBuf::from(
            "tests/testdata/global_config_empty.toml",
        )));

        assert_eq!(g.websocket_port, 8080);
        assert_eq!(g.zenoh_prefix, None);
    }

    #[test]
    fn test_parse_cameraconfig() {
        let result = std::panic::catch_unwind(|| {
            CameraConfig::from_config_file(Some(PathBuf::from(
                "tests/testdata/camera_config_no_dev.toml",
            )))
        });
        assert!(
            result.is_err(),
            "deviceフィールドがない場合はパニックになるべき"
        );
    }
}
