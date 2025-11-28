# Main Camera System

## 環境構築

1. 依存関係のインストール

   - ```bash
     eval "$(mise activate)"
     mise i
     ```

2. ビルド
   - `cargo build --release`
   - `./target/release/main-camera-system` に実行ファイルが生成されます

## コマンドラインオプション

```txt
Usage: main-camera-system [OPTIONS]

Options:
  -c, --config-file </path/to/config.toml>  [default: $HOME/.config/roboapp/config.toml]
  -d, --debug
  -h, --help                         Print help
```

- `-c` ：設定ファイルを指定します
- `-d` ：デバッグモードを有効にします
