use serde::{Deserialize, Serialize};

#[derive(Debug, Serialize, Deserialize)]
pub struct CameraSwitchMessage {
    #[serde(default = "CameraSwitchMessage::default_camera_id")]
    pub camera_id: usize,
}

impl Default for CameraSwitchMessage {
    fn default() -> Self {
        Self {
            camera_id: Self::DEFAULT_CAMERA_ID,
        }
    }
}

impl CameraSwitchMessage {
    const DEFAULT_CAMERA_ID: usize = 0;

    fn default_camera_id() -> usize {
        Self::DEFAULT_CAMERA_ID
    }
}
