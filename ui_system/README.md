# UI System

## 環境構築

1. Rustのインストール
   - [Rustの公式サイト](https://www.rust-lang.org/tools/install)からインストールします。
   - `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh`
2. Volta のインストール
   - [Voltaの公式サイト](https://volta.sh/)からインストールします。
   - `curl https://get.volta.sh | bash`
   - `volta install node@lts pnpm`
3. 依存パッケージのインストール
   - `pnpm i`
   - `sudo apt install libwebkit2gtk-4.1-dev build-essential curl wget file libxdo-dev libssl-dev libayatana-appindicator3-dev librsvg2-dev`
4. ビルド
   - `pnpm tauri build`
   - `./src-tauri/target/release/ui_system` に実行ファイルが生成されます
5. 実行
   - `./src-tauri/target/release/ui_system`
   - 画像配信は、`main-camera-system` に `-w` オプションをつけて実行する必要があります
