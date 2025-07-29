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

async fn zenoh_sub(app: AppHandle) {
    zenoh::init_log_from_env_or("error");

    let config = zenoh::Config::default();

    let session = zenoh::open(config).wait().unwrap();

    let app = Arc::new(app);
    let robot_state_key = "robot/state";
    let robot_command_key = "robot/command";

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
    // Robot Command
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_command_key}/target_x"),
        "target_x",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_command_key}/target_y"),
        "target_y",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_command_key}/target_distance"),
        "target_distance",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &format!("{robot_command_key}/dummy"),
        "dummy",
    )
    .await;

    // session.declare_publisher(&format!("{robot_state_key}/request")).await.unwrap().put("request").await.unwrap();
    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
    }
}
