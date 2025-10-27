use serde::{Deserialize, Serialize};
use toml::Value;

#[derive(Debug, Serialize, Deserialize)]

pub struct CameraDevice {
    #[serde(default)]
    device: String,
    #[serde(default)]
    width: u32,
    #[serde(default)]
    height: u32,
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
    websocket: bool,
    #[serde(default)]
    zenoh: bool,
    #[serde(default)]
    zenoh_prefix: String,
    #[serde(default)]
    devices: Vec<CameraDevice>,
}

impl Default for CameraConfig {
    fn default() -> Self {
        CameraConfig {
            websocket: false,
            zenoh: false,
            zenoh_prefix: "".to_string(),
            devices: vec![CameraDevice::default()],
        }
    }
}

pub fn parse_config(path: &str) -> CameraConfig {
    let value: Value = toml::from_str(&std::fs::read_to_string(path).unwrap()).unwrap();

    let db_table = value
        .get("camera")
        .unwrap_or_else(|| panic!("'database' テーブルが見つかりません"));

    // 3. その Value (テーブル) を目的の構造体にデシリアライズ
    db_table.clone().try_into().unwrap()
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_parse_config() {
        let config = parse_config("../config.toml");
        dbg!(config);
        // 必要ならassert_eq!なども追加可能
    }
}
