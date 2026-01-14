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
