// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
mod zenoh_client;
use crate::config::GlobalConfig;
use std::sync::Arc;
use std::sync::Mutex;
use tauri::AppHandle;
use tauri::Emitter;
use tauri::Manager;
use tauri::State;
use tauri_plugin_cli::CliExt;
pub mod config;

#[cfg_attr(mobile, tauri::mobile_entry_point)]
pub fn run() {
    tauri::Builder::default()
        .manage(Mutex::new(GlobalConfig::default()))
        .plugin(tauri_plugin_cli::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_log::Builder::new().build())
        .invoke_handler(tauri::generate_handler![state_request])
        .setup(|app| {
            let args = match app.cli().matches() {
                Ok(matches) => matches.args,
                Err(_) => panic!("Failed to parse arguments"),
            };

            println!("args: {:?}", args);

            let config_file = match args.get("config") {
                Some(v) => v.value.as_str(),
                None => None,
            };

            let gui_config = config::parse_guiconfig(config_file);
            let global_config = config::parse_globalconfig(config_file);

            let state_global_config = app.state::<Arc<Mutex<GlobalConfig>>>();

            let mut global_config_lock = state_global_config.lock().unwrap();

            global_config_lock.zenoh_prefix = global_config.zenoh_prefix.clone();

            app.emit("host", gui_config.host).unwrap();
            app.emit("port", gui_config.port).unwrap();

            let app_handle = app.app_handle().clone();

            tauri::async_runtime::spawn(async move {
                zenoh_sub(app_handle, global_config.zenoh_prefix).await;
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
async fn state_request(global_config: State<'_, Mutex<GlobalConfig>>) -> Result<(), String> {
    let prefix = global_config.lock().unwrap().zenoh_prefix.clone();

    log::info!("Requesting robot state");
    let robot_state_key = match prefix.clone() {
        Some(ref p) => p.to_owned() + "/",
        None => "".to_string(),
    } + "robot/state/request";

    let _ = zenoh_client::create_zenoh_session()
        .declare_publisher(robot_state_key)
        .await
        .unwrap()
        .put("")
        .await
        .map_err(|e| e.to_string());

    Ok(())
}

async fn zenoh_sub(app: AppHandle, prefix: Option<String>) {
    zenoh::init_log_from_env_or("error");

    let session = zenoh_client::create_zenoh_session();

    let app = Arc::new(app);

    let robot_state_key = match prefix {
        Some(ref p) => p.to_owned() + "/",
        None => "".to_string(),
    } + "robot/state";

    let robot_command_key = match prefix {
        Some(ref p) => p.to_owned() + "/",
        None => "".to_string(),
    } + "robot/command";

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
