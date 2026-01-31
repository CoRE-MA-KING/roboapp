# UI System

## 環境構築

1. 依存関係のインストール

   - ```bash

      eval "$(mise activate)"
      mise i
     ```

2. NodeJS依存関係の更新
   - `mise deps`

## 実行方法

1. ビルド
   - `mise build`
   - `./src-tauri/target/release/ui_system` に実行ファイルが生成されます
2. 実行
   - `./src-tauri/target/release/ui_system` or `mise start` でアプリケーションを起動します
   - 画像配信は、`config.toml` に `websocket = true` オプションをつけて実行する必要があります

## 設定ファイル

設定ファイルは `config.toml` です。

### 構成

#### Global (`[global]`)

- `zenoh_prefix`: Zenoh の Key Expression のプレフィックス
- `websocket_port`: WebSocket のポート番号

#### GUI (`[gui]`)

- `host`: ホスト名 (デフォルト: `localhost`)

### 設定例

```toml
[global]
zenoh_prefix = "roboapp"
websocket_port = 8080

[gui]
host = "localhost"
```
