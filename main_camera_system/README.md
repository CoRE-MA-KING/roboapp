# Main Camera System

## 環境構築

1. 依存関係のインストール

    - ```bash
      eval "$(mise activate)"
      mise i
      ```

2. 依存関係のインストール

   - `mise deps`

## 実行方法

1. ビルド
   - `mise build`
   - `./target/release/main-camera-system` に実行ファイルが生成されます

2. 実行
   - `mise start` or `./target/release/main-camera-system`

### コマンドラインオプション

```txt
Usage: main-camera-system [OPTIONS]

Options:
  -c, --config-file </path/to/config.toml>  [default: $HOME/.config/roboapp/config.toml]
  -d, --debug
  -h, --help                         Print help
```

- `-c` ：設定ファイルを指定します
- `-d` ：デバッグモードを有効にします

## 設定ファイル

設定ファイルは `config.toml` です。

### 構成

#### Camera (`[camera]`)

- `websocket`: WebSocket 配信の有効化 (デフォルト: `true`)
- `websocket_port`: WebSocket のポート番号 (デフォルト: `8080`)
- `zenoh`: Zenoh 配信の有効化 (デフォルト: `false`)

**デバイス設定 (`[[camera.devices]]`)**

- `device`: デバイスパス (例: `/dev/video0`)
- `width`: 解像度 幅 (デフォルト: `1280`)
- `height`: 解像度 高さ (デフォルト: `720`)

### 設定例

```toml
[camera]
websocket = true
zenoh = false

[[camera.devices]]
device = "/dev/video0"
width = 1280
height = 720
```
