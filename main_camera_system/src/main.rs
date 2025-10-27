use clap::Parser;
use main_camera_system::camera_wrapper::create_camera_device;

use main_camera_system::config::parse_config;
use v4l::buffer::Type;
use v4l::io::mmap::Stream;
use v4l::io::traits::CaptureStream;

use futures_util::{SinkExt, StreamExt};
use log::{debug, info};
use std::env;
use std::path::PathBuf;
use std::sync::{Arc, Mutex};
use tokio::net::TcpListener;
use tokio::sync::mpsc;
use tokio_tungstenite::accept_async;
use tokio_tungstenite::tungstenite::Message;

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
    print!("config file: {:?}", args.config_file);

    let config = parse_config(args.config_file);

    unsafe { env::set_var("RUST_LOG", if args.debug { "debug" } else { "info" }) };
    env_logger::init();

    let mut device_index: usize = 0;

    let device = create_camera_device(&config.devices[device_index]);

    let mut stream: Option<Stream<'_>> = Some(
        Stream::with_buffers(&device, Type::VideoCapture, 4)
            .expect("Failed to create buffer stream"),
    );

    // Initialize Zenoh client

    let mut zenoh_config = zenoh::config::Config::default();
    zenoh_config
        .insert_json5("timestamping/enabled", "true")
        .unwrap();

    let zenoh = zenoh::open(zenoh_config).await.unwrap();

    let prefix: String = if !config.zenoh_prefix.is_empty() {
        format!("{}/{}", config.zenoh_prefix.clone(), "cam")
    } else {
        "cam".to_string()
    };

    let jpg_publisher: Option<zenoh::pubsub::Publisher> = if config.zenoh {
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

    let ws_clients: Option<WsClients> = if config.websocket {
        let ws_clients: WsClients = Arc::new(Mutex::new(Vec::new()));
        let ws_clients_clone = ws_clients.clone();
        tokio::spawn(async move {
            let listener = TcpListener::bind(format!("0.0.0.0:{}", config.websocket_port))
                .await
                .expect("Failed to bind WebSocket port");
            info!(
                "WebSocket server listening on ws://0.0.0.0:{}",
                config.websocket_port
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
            } % config.devices.len();

            if new_index == device_index {
                continue;
            }
            device_index = new_index;

            match Stream::with_buffers(
                &create_camera_device(&config.devices[device_index]),
                Type::VideoCapture,
                4,
            ) {
                Ok(new_stream) => {
                    stream = Some(new_stream);
                    println!("Switched to device index: {}", device_index);
                }
                Err(e) => {
                    stream = None;
                    eprintln!("デバイス切り替え失敗: {:?}", e);
                }
            }
        }

        if let Some(stream) = &mut stream {
            let (buf, meta) = stream.next().unwrap();
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
        }
    }
}
