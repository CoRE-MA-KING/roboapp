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
            target_x: Self::DEFAULT_TARGET_X,
            target_y: Self::DEFAULT_TARGET_Y,
            target_distance: Self::DEFAULT_TARGET_DISTANCE,
        }
    }
}

impl DamagePanelRecognition {
    const DEFAULT_TARGET_X: i32 = 640;
    const DEFAULT_TARGET_Y: i32 = 360;
    const DEFAULT_TARGET_DISTANCE: i32 = 0;

    fn default_target_x() -> i32 {
        Self::DEFAULT_TARGET_X
    }
    fn default_target_y() -> i32 {
        Self::DEFAULT_TARGET_Y
    }
    fn default_target_distance() -> i32 {
        Self::DEFAULT_TARGET_DISTANCE
    }
}
