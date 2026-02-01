# UART Bridge

- マイコンとUART通信を行い、Zenohでデータを配信します

## 環境構築

1. 依存関係のインストール

   - ```bash
     eval "$(mise activate)"
     mise i
     ```

2. Python 依存パッケージのインストール
   - `mise deps`

## 実行方法

- 本番用ボードもしくは、ダミーのマイコンを接続します
- デバイスがない場合は、開発用にマイコンの動作をシミュレートするスクリプトを使用できます：
  - `python3 example/dummy_fw.py`
  - これを仮想シリアルポート（socat等）に接続することで、実機なしでテストが可能です。
- `mise start` でアプリケーションを起動します

### マイコンにデータ（RobotCommand）を送信する

- `uv run python3 example/command.py` でデータを送信します
- `ui_system` で送信したデータを表示することもできます

### マイコンの状態（RobotState）を受信する

- `uv run python3 example/state.py` でデータを受信します
- `ui_system` で受信したデータを表示することもできます

## 設定ファイル

設定ファイルは `config.toml` です。

### 構成

#### Global (`[global]`)

- `zenoh_prefix`: Zenoh の Key Expression のプレフィックス
- `websocket_port`: WebSocket のポート番号

#### UART (`[uart]`)

- `device`: デバイスパス (例: `/dev/ttyUSB0`)

### 設定例

```toml
[global]
zenoh_prefix = "roboapp"
websocket_port = 8080

[uart]
device = "/dev/ttyUSB1"
```
