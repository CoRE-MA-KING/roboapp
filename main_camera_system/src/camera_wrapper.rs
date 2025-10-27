use std::{fs, path::Path};

use v4l::Device;
use v4l::FourCC;
use v4l::video::Capture;

use crate::config::CameraDevice;

pub fn create_camera_device(config: &CameraDevice) -> Device {
    let device = match fs::read_link(Path::new(&config.device)) {
        Ok(link) => Device::with_path(link).unwrap_or_else(|e| {
            eprintln!("Failed to open camera (symlink): {}", e);
            // 必要ならここでreturnやcontinue
            // ここではpanicで停止
            panic!();
        }),
        Err(_) => Device::with_path(&config.device).unwrap_or_else(|e| {
            eprintln!("Failed to open camera (direct): {}", e);
            panic!();
        }),
    };

    let mut fmt = device.format().expect("Failed to read format");
    fmt.width = config.width;
    fmt.height = config.height;
    fmt.fourcc = FourCC::new(b"MJPG");
    // fmt.fourcc = FourCC::new(b"YUYV");
    device.set_format(&fmt).expect("Failed to write format");
    device
}
