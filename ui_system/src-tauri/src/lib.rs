// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/

use std::sync::Arc;
use tauri::AppHandle;
use tauri::Emitter;
use tauri::Manager;
use zenoh::Wait;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_cli::init())
        .plugin(tauri_plugin_opener::init())
        .setup(|app| {
            let app_handle = app.app_handle().clone();

            tauri::async_runtime::spawn(async move {
                zenoh_sub(app_handle).await;
            });

            Ok(())
        })
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

async fn zenoh_sub(app: AppHandle) {
    zenoh::init_log_from_env_or("error");

    let config = zenoh::Config::default();

    let session = zenoh::open(config).wait().unwrap();

    let app = Arc::new(app);
    let base_key = "robot/state";

    {
        let app = Arc::clone(&app);
        session
            .declare_subscriber(format!("{base_key}/pitch_deg"))
            .callback_mut(move |sample| {
                app.emit(
                    "pitch_deg",
                    sample
                        .payload()
                        .try_to_string()
                        .unwrap_or_else(|e| e.to_string().into()),
                )
                .unwrap();
            })
            .background()
            .await
            .unwrap();
    }
    {
        let app = Arc::clone(&app);
        session
            .declare_subscriber(format!("{base_key}/video_id"))
            .callback_mut(move |sample| {
                println!("Received video_id: {:?}", sample.payload().try_to_string());
                app.emit(
                    "video_id",
                    sample
                        .payload()
                        .try_to_string()
                        .unwrap_or_else(|e| e.to_string().into()),
                )
                .unwrap();
            })
            .background()
            .await
            .unwrap();
    }

    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
    }
}
