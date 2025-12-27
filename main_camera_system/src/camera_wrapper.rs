use std::{fs, path::Path};
use v4l::Device;
use v4l::FourCC;
use v4l::buffer::Type;
use v4l::io::mmap::Stream;
use v4l::video::Capture;

use crate::config::CameraDevice;

fn resolve_path(path: &Path) -> Result<std::path::PathBuf, String> {
    let mut resolved_path = path.to_path_buf();
    for _ in 0..10 {
        let metadata = fs::symlink_metadata(&resolved_path)
            .map_err(|e| format!("symlink_metadata失敗: {}, {}", e, resolved_path.display()))?;
        if metadata.file_type().is_symlink() {
            let link_target = fs::read_link(&resolved_path)
                .map_err(|e| format!("read_link失敗: {}, {}", e, resolved_path.display()))?;
            // 絶対パスでなければ resolved_path の親ディレクトリで補完
            resolved_path = if link_target.is_absolute() {
                link_target
            } else {
                match resolved_path.parent() {
                    Some(parent) => parent.join(link_target),
                    None => link_target,
                }
            };
        } else {
            break;
        }
    }
    Ok(resolved_path)
}

fn create_camera_device(config: &CameraDevice) -> Result<Device, String> {
    let device_path = resolve_path(&std::path::PathBuf::from(&config.device))
        .map_err(|e| format!("Failed to resolve device path: {}", e))?;

    let device =
        Device::with_path(&device_path).map_err(|e| format!("Failed to open camera: {}", e))?;

    let mut fmt = device
        .format()
        .map_err(|e| format!("Failed to read format: {}", e))?;
    fmt.width = config.width;
    fmt.height = config.height;
    fmt.fourcc = FourCC::new(b"MJPG");
    // fmt.fourcc = FourCC::new(b"YUYV");
    device
        .set_format(&fmt)
        .map_err(|e| format!("Failed to write format: {}", e))?;
    Ok(device)
}

pub fn create_camera_stream(config: &CameraDevice) -> Result<Stream<'_>, String> {
    match create_camera_device(config) {
        Ok(dev) => Ok(Stream::with_buffers(&dev, Type::VideoCapture, 4)
            .expect("Failed to create buffer stream")),
        Err(e) => {
            eprintln!("カメラデバイスの初期化失敗: {:?}", e);
            Err(e)
        }
    }
}
