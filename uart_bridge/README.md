# UART Bridge

- マイコンとUART通信を行い、Zenohでデータを配信します

## 環境構築

1. Pythonのインストール
   - Python 3.8以上をインストールしてください
   - [uv](https://docs.astral.sh/uv/) のインストール
     - `curl -LsSf https://astral.sh/uv/install.sh | sh`

2. 依存パッケージのインストール
   - `uv sync`

## 実行方法

- 本番用ボードもしくは、ダミーのマイコンを接続します
- `uv run python3 src/uart_bridge/main.py` でアプリケーションを起動します

### マイコンにデータ（RobotCommand）を送信する

- `uv run python3 example/command.py` でデータを送信します
- `ui_system` で送信したデータを表示することもできます

### マイコンの状態（RobotState）を受信する

- `uv run python3 example/state.py` でデータを受信します
- `ui_system` で受信したデータを表示することもできます
