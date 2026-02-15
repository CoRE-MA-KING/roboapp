use clap::Parser;
use log::{debug, error, info};
use main_camera_system::camera_wrapper::create_camera_stream;
use main_camera_system::config::{get_config_path, load_config};
use main_camera_system::proto::roboapp::{CameraPortMessage, CameraSwitchMessage};
use main_camera_system::websocket::{WsClients, start_websocket_server};
use prost::Message;
use std::env;
use std::path::PathBuf;
use tokio::sync::mpsc;
use v4l::io::mmap::Stream;
use v4l::io::traits::CaptureStream;
#[derive(Parser, Debug)]
struct Args {
    #[arg(short, long)]
    config_file: Option<PathBuf>,

    #[arg(short, long, action)]
    debug: bool,
}

#[tokio::main]
async fn main() {
    let args = Args::parse();

    unsafe { env::set_var("RUST_LOG", if args.debug { "debug" } else { "info" }) };
    env_logger::init();

    let config = load_config(args.config_file).expect("Failed to load configuration");
    let camera_config = config
        .camera
        .expect("設定ファイルに [camera] セクションが見つかりません");

    debug!("Camera Config: {:?}", camera_config);

    let mut device_index: usize = 0;

    let mut stream: Option<Stream<'_>> =
        match create_camera_stream(&camera_config.devices[device_index]) {
            Ok(stream) => Some(stream),
            Err(e) => {
                eprintln!("カメラデバイスの初期化失敗: {:?}", e);
                None
            }
        };

    // Initialize Zenoh client

    let zenoh_config = match zenoh::config::Config::from_file(get_config_path().join("zenoh.json5"))
    {
        Ok(config) => config,
        Err(e) => {
            error!(
                "Failed to load zenoh.json5 configuration file: {}. Please ensure it exists or run the configurator.",
                e
            );
            std::process::exit(1);
        }
    };

    let zenoh = match zenoh::open(zenoh_config).await {
        Ok(session) => session,
        Err(e) => {
            error!(
                "Failed to open Zenoh session: {}. Please check if zenohd is running.",
                e
            );
            std::process::exit(1);
        }
    };

    let jpg_publisher: Option<zenoh::pubsub::Publisher> = if camera_config.zenoh {
        let topic_name = "cam/jpg";
        info!("JPEG publishing enabled at {topic_name}");
        Some(zenoh.declare_publisher(topic_name).await.unwrap())
    } else {
        None
    };

    let port_publisher = zenoh.declare_publisher("cam/port").await.unwrap();
    let port_msg = CameraPortMessage {
        port: camera_config.websocket_port as i32,
    };

    tokio::spawn(async move {
        let mut interval = tokio::time::interval(tokio::time::Duration::from_millis(200));
        loop {
            interval.tick().await;
            if let Err(e) = port_publisher.put(port_msg.encode_to_vec()).await {
                error!("Failed to publish CameraPortMessage: {:?}", e);
            }
        }
    });

    let subscriber = zenoh.declare_subscriber("cam/switch").await.unwrap();

    let ws_clients: Option<WsClients> = if camera_config.websocket {
        Some(start_websocket_server(camera_config.websocket_port))
    } else {
        None
    };

    let (switch_tx, mut switch_rx) = mpsc::unbounded_channel();

    // スイッチ受信タスク
    let subscriber = subscriber.clone();
    tokio::spawn(async move {
        loop {
            if let Ok(sample) = subscriber.recv_async().await {
                let payload = sample.payload();
                match CameraSwitchMessage::decode(payload.to_bytes().as_ref()) {
                    Ok(msg) => {
                        let new_value = msg.camera_id as usize;
                        let _ = switch_tx.send(new_value);
                    }
                    Err(e) => {
                        error!("Failed to parse CameraSwitchMessage from payload: {:?}", e);
                    }
                }
            }
        }
    });

    loop {
        // カメラ切り替え通知が来ていれば切り替え
        if let Ok(new_value) = switch_rx.try_recv() {
            let new_index = new_value % camera_config.devices.len();

            if new_index == device_index {
                continue;
            }
            device_index = new_index;
            stream = None;
        }

        if let Some(local_stream) = &mut stream {
            // let (buf, meta) = stream.next().unwrap();
            if let Ok((buf, meta)) = local_stream.next() {
                debug!(
                    "Buffer size: {}, seq: {}, timestamp: {}",
                    buf.len(),
                    meta.sequence,
                    meta.timestamp
                );

                // WebSocketクライアントに配信（有効時のみ）
                if let Some(ws_clients) = &ws_clients {
                    let clients = ws_clients.lock().unwrap();
                    clients.iter().for_each(|tx| {
                        let _ = tx.send(buf.to_vec());
                    });
                }

                if let Some(jpg_publisher) = &jpg_publisher {
                    jpg_publisher
                        .put(buf)
                        .await
                        .expect("Failed to publish JPEG buffer");
                }
            } else {
                stream = None;
            }
        } else {
            stream = match create_camera_stream(&camera_config.devices[device_index]) {
                Ok(new_stream) => {
                    info!("Switched to device index: {}", device_index);
                    Some(new_stream)
                }
                Err(e) => {
                    error!("カメラデバイスの初期化失敗: {:?}", e);
                    None
                }
            };
        }
    }
}
