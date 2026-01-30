# Configurator

- roboapp の各種設定を実行するツールです

## 環境構築

1. 依存関係のインストール

   - ```bash
     eval "$(mise activate)"
     mise i
     ```

2. Python 依存パッケージのインストール
   - `mise deps`

## 実行方法

- `mise start` or `uv run python3 src/configurator/main.py` で実行します。

### 設定ファイルの検証

- 設定ファイルのパスを指定して、実行します

- 正常実行できれば、設定ファイルは問題ありません。

- エラーがでた場合、エラーメッセージに従って設定ファイルを修正してください。（Pydantic のバリデーションエラーが表示されます）

### 起動設定のインストール

- アプリケーションの起動設定をインストールします。

### Roboappの起動・停止

- 起動設定のインストールが完了している場合に実行します。
- systemd サービスとして登録されているアプリケーションを起動・停止します。

### Roboappの自動起動の設定・解除

- 起動設定のインストールが完了している場合に実行します。

- systemd サービスとして登録されているアプリケーションの自動起動を設定・解除します。
- PC起動時に自動的にアプリケーションを起動したい場合、有効化してください。

## 設定ファイル

設定ファイルは `config.toml` です。デフォルトでは `$HOME/.config/roboapp/config.toml` を読み込みます。

### 構成

設定ファイルは以下のセクションで構成されています。

#### Global (`[global]`)

全アプリケーション共通の設定です。

- `zenoh_prefix`: Zenoh の Key Expression のプレフィックス (デフォルト: `""`)
- `websocket_port`: WebSocket のポート番号 (デフォルト: `8080`)

#### LiDAR (`[lidar]`)

LiDAR システムの設定です。

- `robot_width`: ロボットの幅 (mm) (デフォルト: `800`)
- `robot_length`: ロボットの長さ (mm) (デフォルト: `800`)
- `repulsive_gain`: 斥力計算のゲイン (デフォルト: `0.7`)
- `influence_range`: 斥力の影響範囲 (mm) (デフォルト: `200`)
- `duration_seconds`: データの有効期間 (秒) (デフォルト: `1`)

**デバイス設定 (`[lidar.devices.<name>]`)**

デバイスごとにセクションを作成します。

- `backend`: `random` または `rplidar`
- `device`: デバイスパス (`backend="rplidar"` の場合必須)
- `max_distance`: 最大計測距離 (mm) (デフォルト: `1000`)
- `min_degree`: 計測開始角度 (度) (デフォルト: `0`)
- `max_degree`: 計測終了角度 (度) (デフォルト: `360`)
- `x`: ロボット中心からのX座標 (mm) (デフォルト: `0`)
- `y`: ロボット中心からのY座標 (mm) (デフォルト: `0`)
- `rotation`: 取り付け角度 (度) (デフォルト: `0`)

#### Camera (`[camera]`)

カメラシステムの設定です。

- `websocket`: WebSocket 配信の有効化 (デフォルト: `true`)
- `zenoh`: Zenoh 配信の有効化 (デフォルト: `false`)

**デバイス設定 (`[[camera.devices]]`)**

- `device`: デバイスパス (例: `/dev/video0`)
- `width`: 解像度 幅 (デフォルト: `1280`)
- `height`: 解像度 高さ (デフォルト: `720`)

#### GUI (`[gui]`)

UI システムの設定です。

- `host`: ホスト名 (デフォルト: `localhost`)

#### UART (`[uart]`)

UART ブリッジの設定です。

- `device`: デバイスパス (例: `/dev/ttyUSB0`)

### 設定例

```toml
[global]
zenoh_prefix = "roboapp"
websocket_port = 8080

[lidar]
robot_width = 800
robot_length = 800
repulsive_gain = 0.7
influence_range = 200
duration_seconds = 1

[lidar.devices.main]
backend = "rplidar"
device = "/dev/ttyUSB0"
x = 100
y = 0
rotation = 0

[camera]
websocket = true
zenoh = false

[[camera.devices]]
device = "/dev/video0"
width = 1280
height = 720

[gui]
host = "localhost"

[uart]
device = "/dev/ttyUSB1"
```
