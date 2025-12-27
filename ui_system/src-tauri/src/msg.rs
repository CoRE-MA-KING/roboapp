#[derive(Debug, Clone, serde::Serialize, serde::Deserialize)]
pub struct DamagePanelRecognition {
    #[serde(default = "DamagePanelRecognition::default_target_x")]
    pub target_x: i32,
    #[serde(default = "DamagePanelRecognition::default_target_y")]
    pub target_y: i32,
    #[serde(default = "DamagePanelRecognition::default_target_distance")]
    pub target_distance: i32,
}

impl Default for DamagePanelRecognition {
    fn default() -> Self {
        Self {
            target_x: 640,
            target_y: 360,
            target_distance: 0,
        }
    }
}

impl DamagePanelRecognition {
    fn default_target_x() -> i32 {
        640
    }
    fn default_target_y() -> i32 {
        360
    }
    fn default_target_distance() -> i32 {
        0
    }
}
