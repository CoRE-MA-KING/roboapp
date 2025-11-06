# Main Camera System

## 環境構築

1. Rustのインストール
   - [Rustの公式サイト](https://www.rust-lang.org/tools/install)からインストールします。
   - `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
2. 依存パッケージのインストール
   - `sudo apt install build-essential cmake nasm`
3. ビルド
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
