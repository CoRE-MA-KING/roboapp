// Learn more about Tauri commands at https://tauri.app/develop/calling-rust/
mod msg;
mod zenoh_client;
use crate::config::load_config;
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
        .manage(Mutex::new(config::GlobalConfig::default()))
        .manage(Mutex::new(config::GUIConfig::default()))
        .plugin(tauri_plugin_cli::init())
        .plugin(tauri_plugin_opener::init())
        .plugin(tauri_plugin_log::Builder::new().build())
        .invoke_handler(tauri::generate_handler![
            get_config_host,
            get_config_port
        ])
        .setup(|app| {
            let args = match app.cli().matches() {
                Ok(matches) => matches.args,
                Err(_) => {
                    // パース失敗時は何もせず正常終了
                    return Ok(());
                }
            };

            if args.contains_key("help") {
                println!("{}", args["help"].value.as_str().unwrap());
            }

            let config_file = match args.get("config") {
                Some(v) => v.value.as_str(),
                None => None,
            };

            let config = load_config(config_file).expect("Failed to load configuration");
            let global_config = config.global;
            let gui_config = config
                .gui
                .expect("設定ファイルに [gui] セクションが見つかりません");

            println!("Using config file: {:?}", gui_config);
            println!("Using config file: {:?}", global_config);

            let state_global_config = app.state::<Mutex<config::GlobalConfig>>();
            let state_gui_config = app.state::<Mutex<config::GUIConfig>>();

            let mut global_config_lock = state_global_config.lock().unwrap();
            let mut gui_config_lock = state_gui_config.lock().unwrap();

            global_config_lock.zenoh_prefix = global_config.zenoh_prefix.clone();
            global_config_lock.websocket_port = global_config.websocket_port;

            gui_config_lock.host = gui_config.host.clone();

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
    prefix: &str,
    event_name: &str,
) {
    let event_name_cloned = event_name.to_string();
    session
        .declare_subscriber(format!("{prefix}{event_name}"))
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
fn get_config_host(gui_config: State<'_, Mutex<config::GUIConfig>>) -> Result<String, String> {
    Ok(gui_config.lock().unwrap().host.clone())
}

#[tauri::command]
fn get_config_port(global_config: State<'_, Mutex<config::GlobalConfig>>) -> Result<u16, String> {
    println!(
        "call port: {}",
        global_config.lock().unwrap().websocket_port
    );
    Ok(global_config.lock().unwrap().websocket_port)
}

async fn zenoh_sub(app: AppHandle, prefix: String) {
    zenoh::init_log_from_env_or("error");

    let session = zenoh_client::create_zenoh_session();

    let app = Arc::new(app);

    let prefix_slash = if prefix.is_empty() {
        "".to_string()
    } else {
        format!("{prefix}/")
    };
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &prefix_slash,
        "cam/switch",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &prefix_slash,
        "disks",
    )
    .await;
    declare_and_emit(
        &session,
        Arc::clone(&app),
        &prefix_slash,
        "flap",
    )
    .await;
        declare_and_emit(
        &session,
        Arc::clone(&app),
        &prefix_slash,
        "lidar/force_vector",
    )
    .await;

    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(10)).await;
    }
}
