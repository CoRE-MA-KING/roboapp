use futures_util::{SinkExt, StreamExt};
use log::info;
use std::sync::{Arc, Mutex};
use tokio::net::TcpListener;
use tokio_tungstenite::accept_async;
use tokio_tungstenite::tungstenite::Message as WsMessage;

pub type WsClients = Arc<Mutex<Vec<tokio::sync::mpsc::UnboundedSender<Vec<u8>>>>>;

pub fn start_websocket_server(port: u16) -> WsClients {
    let ws_clients: WsClients = Arc::new(Mutex::new(Vec::new()));
    let ws_clients_clone = ws_clients.clone();

    tokio::spawn(async move {
        let listener = TcpListener::bind(format!("0.0.0.0:{}", port))
            .await
            .expect("Failed to bind WebSocket port");
        info!("WebSocket server listening on ws://0.0.0.0:{}", port);

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
                        if ws_sender
                            .send(WsMessage::Binary(data.into()))
                            .await
                            .is_err()
                        {
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

    ws_clients
}
