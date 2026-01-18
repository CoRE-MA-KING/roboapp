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
