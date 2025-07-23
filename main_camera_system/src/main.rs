use clap::Parser;

use v4l::Device;
use v4l::FourCC;
use v4l::buffer::Type;
use v4l::io::mmap::Stream;
use v4l::io::traits::CaptureStream;
use v4l::video::Capture;

use futures_util::{SinkExt, StreamExt};
use log::{debug, info};
use std::env;
use std::sync::{Arc, Mutex};
use tokio::net::TcpListener;
use tokio_tungstenite::accept_async;
use tokio_tungstenite::tungstenite::Message;

#[derive(Parser, Debug)]
struct Args {
    #[arg(short, long, default_value = "0")]
    camera_id: usize,
    #[arg(short, long, default_value = "")]
    zenoh_prefix: String,

    #[arg(short, long, action)]
    raw: bool,

    #[arg(short, long, action)]
    jpg: bool,

    #[arg(short, long, action)]
    websocket: bool,

    #[arg(short, long, default_value = "8080")]
    port: u16,

    #[arg(short, long, action)]
    debug: bool,
}

#[tokio::main]
async fn main() {
    let args = Args::parse();

    unsafe { env::set_var("RUST_LOG", if args.debug { "debug" } else { "info" }) };
    env_logger::init();

    // Create a new capture device with a few extra parameters
    let dev = Device::new(args.camera_id).expect("Failed to open device");

    // Let's say we want to explicitly request another format
    let mut fmt = dev.format().expect("Failed to read format");
    fmt.width = 1280;
    fmt.height = 720;
    fmt.fourcc = FourCC::new(b"MJPG");
    // fmt.fourcc = FourCC::new(b"YUYV");
    let fmt = dev.set_format(&fmt).expect("Failed to write format");

    println!("Format in use:\n{fmt}");

    let mut stream =
        Stream::with_buffers(&dev, Type::VideoCapture, 4).expect("Failed to create buffer stream");

    // Initialize Zenoh client

    let mut config = zenoh::config::Config::default();
    config.insert_json5("timestamping/enabled", "true").unwrap();

    let zenoh = zenoh::open(config).await.unwrap();

    let prefix: String = if !args.zenoh_prefix.is_empty() {
        format!("{}/{}", args.zenoh_prefix.clone(), "cam")
    } else {
        // OpenCVのイベントループを更新する
        "cam".to_string()
    };

    let jpg_publisher: Option<zenoh::pubsub::Publisher> = if args.jpg {
        let topic_name = format!("{prefix}/jpg");
        info!("JPEG publishing enabled at {topic_name}");
        Some(zenoh.declare_publisher(topic_name).await.unwrap())
    } else {
        None
    };

    let raw_publisher: Option<zenoh::pubsub::Publisher> = if args.raw {
        let topic_name = format!("{prefix}/raw");
        info!("Raw publishing enabled at {topic_name}");
        Some(zenoh.declare_publisher(topic_name).await.unwrap())
    } else {
        None
    };

    // WebSocket配信を有効化する場合のみサーバーを起動
    type WsClients = Arc<Mutex<Vec<tokio::sync::mpsc::UnboundedSender<Vec<u8>>>>>;

    let ws_clients: Option<WsClients> = if args.websocket {
        let ws_clients: WsClients = Arc::new(Mutex::new(Vec::new()));
        let ws_clients_clone = ws_clients.clone();
        tokio::spawn(async move {
            let listener = TcpListener::bind(format!("0.0.0.0:{}", args.port))
                .await
                .expect("Failed to bind WebSocket port");
            info!("WebSocket server listening on ws://0.0.0.0:{}", args.port);
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

    loop {
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

        // Publish the buffer data to Zenoh
        if let Some(raw_publisher) = &raw_publisher {
            let result = match turbojpeg::decompress(buf, turbojpeg::PixelFormat::RGB).ok() {
                Some(image) => image.pixels,
                None => continue,
            };
            raw_publisher
                .put(result)
                .await
                .expect("Failed to publish raw buffer");
        }
    }
}
