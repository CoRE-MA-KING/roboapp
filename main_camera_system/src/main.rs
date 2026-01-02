use clap::Parser;
use futures_util::{SinkExt, StreamExt};
use log::{debug, error, info};
use main_camera_system::camera_wrapper::create_camera_stream;
use main_camera_system::config::load_config;
use metrics::{describe_gauge, gauge};
use metrics_exporter_prometheus::PrometheusBuilder;
use metrics_util::MetricKindMask;
use std::collections::VecDeque;
use std::env;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use std::time::{Duration, Instant};
use tokio::net::TcpListener;
use tokio::sync::mpsc;
use tokio_tungstenite::accept_async;
use tokio_tungstenite::tungstenite::Message;
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
    let global_config = config.global;
    let camera_config = config
        .camera
        .expect("設定ファイルに [camera] セクションが見つかりません");

    debug!("Global Config: {:?}", global_config);
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

    // FPS計測用
    let mut timestamps: VecDeque<Instant> = VecDeque::new();

    PrometheusBuilder::new()
        .with_http_listener(([0, 0, 0, 0], 9901))
        .idle_timeout(MetricKindMask::GAUGE, Some(Duration::from_secs(10)))
        .install()
        .expect("failed to install recorder");

    describe_gauge!("main_camera_fps", "Frames per second of the main camera");

    // Initialize Zenoh client

    let mut zenoh_config = zenoh::config::Config::default();
    zenoh_config
        .insert_json5("timestamping/enabled", "true")
        .unwrap();

    let zenoh = zenoh::open(zenoh_config).await.unwrap();

    let prefix: String = if global_config.zenoh_prefix.is_empty() {
        "cam".to_string()
    } else {
        format!("{}/{}", global_config.zenoh_prefix, "cam")
    };

    let jpg_publisher: Option<zenoh::pubsub::Publisher> = if camera_config.zenoh {
        let topic_name = format!("{prefix}/jpg");
        info!("JPEG publishing enabled at {topic_name}");
        Some(zenoh.declare_publisher(topic_name).await.unwrap())
    } else {
        None
    };

    let subscriber = zenoh
        .declare_subscriber(format!("{}/switch", prefix))
        .await
        .unwrap();

    // WebSocket配信を有効化する場合のみサーバーを起動
    type WsClients = Arc<Mutex<Vec<tokio::sync::mpsc::UnboundedSender<Vec<u8>>>>>;

    let ws_clients: Option<WsClients> = if camera_config.websocket {
        let ws_clients: WsClients = Arc::new(Mutex::new(Vec::new()));
        let ws_clients_clone = ws_clients.clone();
        tokio::spawn(async move {
            let listener = TcpListener::bind(format!("0.0.0.0:{}", global_config.websocket_port))
                .await
                .expect("Failed to bind WebSocket port");
            info!(
                "WebSocket server listening on ws://0.0.0.0:{}",
                global_config.websocket_port
            );
            while let Ok((stream, _)) = listener.accept().await {
                let ws_clients_inner = ws_clients_clone.clone();
                tokio::spawn(async move {
                    let ws_stream = accept_async(stream)
                        .await
                        .expect("WebSocket handshake failed");
                    let (mut ws_sender, mut ws_receiver) = ws_stream.split();
                    let (tx, mut rx) = tokio::sync::mpsc::unbounded_channel::<Vec<u8>>();
                    ws_clients_inner.lock().unwrap().push(tx);
                    // 送信タスク
                    let send_task = tokio::spawn(async move {
                        while let Some(data) = rx.recv().await {
                            if ws_sender.send(Message::Binary(data.into())).await.is_err() {
                                break;
                            }
                        }
                    });
                    // 受信タスク（クライアントからの切断検知用）
                    let recv_task = tokio::spawn(async move {
                        while let Some(_msg) = ws_receiver.next().await {
                            // ここでは何もしない
                        }
                    });
                    let _ = tokio::join!(send_task, recv_task);
                });
            }
        });
        Some(ws_clients)
    } else {
        None
    };

    let (switch_tx, mut switch_rx) = mpsc::unbounded_channel();

    // スイッチ受信タスク
    let subscriber = subscriber.clone();
    tokio::spawn(async move {
        loop {
            if let Ok(sample) = subscriber.recv_async().await {
                let new_value: Option<usize> = sample
                    .payload()
                    .try_to_string()
                    .ok()
                    .and_then(|s| s.parse().ok());
                let _ = switch_tx.send(new_value);
            }
        }
    });

    loop {
        // カメラ切り替え通知が来ていれば切り替え
        if let Ok(new_value) = switch_rx.try_recv() {
            let new_index = match new_value {
                Some(n) => n,
                None => device_index + 1,
            } % camera_config.devices.len();

            if new_index == device_index {
                continue;
            }
            device_index = new_index;
            stream = None;
        }

        let now = Instant::now();

        // 1秒より前のものを削除
        while let Some(&front) = timestamps.front() {
            if now.duration_since(front).as_secs_f32() > 1.0 {
                timestamps.pop_front();
            } else {
                break;
            }
        }

        if let Some(local_stream) = &mut stream {
            // let (buf, meta) = stream.next().unwrap();
            timestamps.push_back(now);

            gauge!("main_camera_fps").set(timestamps.len() as f64);

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
