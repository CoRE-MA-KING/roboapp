// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
mod msg;
mod zenoh_client;
use std::sync::Arc;
use tauri::AppHandle;
use tauri::Emitter;
use tauri::Manager;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .plugin(tauri_plugin_cli::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_log::Builder::new().build())
        .invoke_handler(tauri::generate_handler![state_request])
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

async fn declare_and_emit(
    session: &zenoh::Session,
    app: Arc<AppHandle>,
    zenoh_key: &str,
    event_name: &str,
) {
    let event_name_cloned = event_name.to_string();
    session
        .declare_subscriber(zenoh_key)
        .callback_mut(move |sample| {
            app.emit(
                &event_name_cloned,
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

#[tauri::command]
async fn state_request() {
    log::info!("Requesting robot state");
    zenoh_client::create_zenoh_session()
        .declare_publisher("robot/state/request")
        .await
        .unwrap()
        .put("")
        .await
        .unwrap();
}

async fn zenoh_sub(app: AppHandle) {
    zenoh::init_log_from_env_or("error");

    let session = zenoh_client::create_zenoh_session();

    let app = Arc::new(app);
    let robot_state_key = "robot/state";
    let damage_panel_key = "damagepanel";

    // Robot State
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/state_id"),
        "video_id",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/pitch_deg"),
        "pitch_deg",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/muzzle_velocity"),
        "muzzle_velocity",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/reloaded_left_disks"),
        "reloaded_left_disks",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/reloaded_right_disks"),
        "reloaded_right_disks",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/video_id"),
        "video_id",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/target_panel"),
        "target_panel",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/auto_aim"),
        "auto_aim",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/record_video"),
        "record_video",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/ready_to_fire"),
        "ready_to_fire",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_state_key}/reserved"),
        "reserved",
    )
    .await;

    // Damage Panel Recognition
    session
        .declare_subscriber(damage_panel_key)
        .callback_mut(move |sample| {
            if let Ok(v) = sample.payload().try_to_string() {
                if let Ok(dp) = serde_json::from_str::<msg::DamagePanelRecognition>(&v) {
                    let app = Arc::clone(&app);
                    tauri::async_runtime::spawn(async move {
                        app.emit("target_x", dp.target_x).unwrap();
                        app.emit("target_y", dp.target_y).unwrap();
                        app.emit("target_distance", dp.target_distance).unwrap();
                    });
                }
            }
        })
        .background()
        .await
        .unwrap();

    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
    }
}
