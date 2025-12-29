use serde::{Deserialize, Serialize};

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
    pub devices: Vec<CameraDevice>,
}

impl CameraConfig {
    fn default_websocket() -> bool {
        true
    }
    fn default_zenoh() -> bool {
        false
    }
}

#[derive(Debug, Serialize, Deserialize)]
pub struct Config {
    #[serde(default)]
    pub global: GlobalConfig,
    pub camera: Option<CameraConfig>,
}

pub fn load_config(path: Option<PathBuf>) -> Result<Config, Box<dyn std::error::Error>> {
    let config_path = parse_configpath(path);
    let content = std::fs::read_to_string(config_path)?;
    let config: Config = toml::from_str(&content)?;
    Ok(config)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_globalconfig_empty() {
        let config = load_config(Some(PathBuf::from(
            "test/resources/global_config_empty.toml",
        )))
        .expect("cameraセクションがなくてもパースは成功すべき");

        assert!(config.camera.is_none());
        assert_eq!(config.global.websocket_port, 8080);
    }

    #[test]
    fn test_parse_globalconfig_websocket_port() {
        let config = load_config(Some(PathBuf::from(
            "test/resources/global_config_websocket_port.toml",
        )))
        .expect("cameraセクションがなくてもパースは成功すべき");

        assert!(config.camera.is_none());
        assert_eq!(config.global.websocket_port, 9090);
    }

    #[test]
    fn test_parse_cameraconfig() {
        let c = load_config(Some(PathBuf::from(
            "test/resources/camera_config_device_width.toml",
        )))
        .unwrap();

        let camera = c.camera.expect("cameraセクションがあるべき");
        assert_eq!(camera.devices.len(), 1);
        assert_eq!(camera.devices[0].device, "/dev/video0");
        assert_eq!(camera.devices[0].width, 640);
        assert_eq!(camera.devices[0].height, 720);
        assert!(camera.websocket);
    }

    #[test]
    fn test_parse_invalid_cameraconfig() {
        let result = load_config(Some(PathBuf::from(
            "test/resources/camera_config_no_dev.toml",
        )));
        assert!(
            result.is_err(),
            "deviceフィールドがない場合はエラーになるべき"
        );
    }
}
