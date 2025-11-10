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

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct GlobalConfig {
    #[serde(default = "GlobalConfig::default_websocket_port")]
    pub websocket_port: u16,
    #[serde(default = "GlobalConfig::default_zenoh_prefix")]
    pub zenoh_prefix: Option<String>,
}

impl GlobalConfig {
    fn default_websocket_port() -> u16 {
        8080
    }
    fn default_zenoh_prefix() -> Option<String> {
        None
    }
    pub fn from_config_file(path: Option<PathBuf>) -> Self {
        let value: Value =
            toml::from_str(&std::fs::read_to_string(parse_configpath(path)).unwrap()).unwrap();

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
pub struct CameraDevice {
    pub device: String,
    #[serde(default = "CameraDevice::default_width")]
    pub width: u32,
    #[serde(default = "CameraDevice::default_height")]
    pub height: u32,
}

impl CameraDevice {
    fn default_height() -> u32 {
        720
    }
    fn default_width() -> u32 {
        1280
    }
}

#[derive(Debug, Serialize, Deserialize)]

pub struct CameraConfig {
    #[serde(default = "CameraConfig::default_websocket")]
    pub websocket: bool,
    #[serde(default = "CameraConfig::default_zenoh")]
    pub zenoh: bool,
    #[serde(default)]
    pub devices: Vec<CameraDevice>,
}

impl CameraConfig {
    fn default_websocket() -> bool {
        false
    }
    fn default_zenoh() -> bool {
        false
    }
    pub fn from_config_file(path: Option<PathBuf>) -> Self {
        let value: Value =
            toml::from_str(&std::fs::read_to_string(parse_configpath(path)).unwrap()).unwrap();

        match value.get("camera") {
            Some(v) => match v.clone().try_into() {
                Ok(cfg) => cfg,
                Err(_) => panic!("'camera' テーブルのパースに失敗しました"),
            },
            None => panic!("'camera' テーブルが見つかりませんでした"),
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_globalconfig() {
        let g = GlobalConfig::from_config_file(Some(PathBuf::from(
            "test/resources/global_config_websocket_port.toml",
        )));
        assert_eq!(g.websocket_port, 9090);
        assert_eq!(g.zenoh_prefix, None);
    }

    #[test]
    fn test_parse_invalid_cameraconfig() {
        let result = std::panic::catch_unwind(|| {
            CameraConfig::from_config_file(Some(PathBuf::from(
                "test/resources/camera_config_no_dev.toml",
            )))
        });
        assert!(
            result.is_err(),
            "deviceフィールドがない場合はパニックになるべき"
        );
    }

    #[test]
    fn test_parse_cameraconfig() {
        let c = CameraConfig::from_config_file(Some(PathBuf::from(
            "test/resources/camera_config_device_width.toml",
        )));
        assert_eq!(c.devices.len(), 1);
        assert_eq!(c.devices[0].device, "/dev/video0");
        assert_eq!(c.devices[0].width, 640);
        assert_eq!(c.devices[0].height, 720);
    }
}
