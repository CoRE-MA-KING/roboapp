# プロジェクト概要

- Ubuntu 24.04 LTS をターゲットとしたロボット制御用アプリケーション「roboapp」のリポジトリです。
- 環境管理には `mise` を使用し、通信には Zenoh と WebSocket を採用しています。

## 開発ガイドライン

- 回答や対話はすべて日本語で行ってください。
- アプリケーションの実装を更新した場合は、`AGENTS.md` や対応する `README.md` を更新してください（特に起動オプションや設定項目など）。
- コードを変更した後は、必ず以下のコマンドを実行してコードの整形と検証を行ってください。

  ```bash
  mise format
  mise lint
  ```

- プロジェクトの管理には `mise tasks` を用いています。以下のメインタスクとそれを支えるサブタスクからなります（詳しくは `mise.toml` の各タスクの description を参照してください）。
  - deps：プロジェクトの依存関係をインストールし、環境構築を行います（AIエージェントが使うことはないとおもいます）。
  - lint：設定された linter や type checker を実行します。
  - format：設定された formatter を実行します。
  - test：設定された test を実行します。
  - start：アプリケーションを実行します（AIエージェントが使うことはないとおもいます）。

### ツールバージョンの固定

- clang ツールを使用するのは `lidar_system` のみのため、`lidar_system/mise.toml` で `clang-format` / `clang-tools`（`clang-tidy`）を conda バックエンドの LLVM **21.1.8** に固定しています。
  - OS 由来の clang ツール（CI コンテナ: ubuntu:24.04 apt の 18.1.3 など）とローカル環境でフォーマッタの挙動が異なり、`format-check` が落ちるため、バージョンとバイナリを固定しています。
  - パッチバージョン間でもフォーマット挙動に差がある（例: `){};` ↔ `() {};`）ため、`latest` ではなく正確なバージョンを指定しています。
- ツールのバージョンを変更する場合はこの設定を更新してください。

## コンポーネント一覧

- **LiDAR System**
  - LiDAR データの処理、障害物回避計算、可視化を行う C++ システムです。`sender`、`processor`、`viewer` で構成されます。
  - パス: `lidar_system/`

- **Main Camera System**
  - Webカメラの映像を Zenoh Query および WebSocket で配信する Rust アプリケーションです。
  - パス: `main_camera_system/`

- **UART Bridge**
  - マイコンと UART 通信を行い、データを Zenoh で中継する Python アプリケーションです。
  - パス: `uart_bridge/`

- **UI System**
  - システムの監視と操作を行うための SvelteKit + Tauri 製のユーザーインターフェースです。
  - パス: `ui_system/`

- **Image Receiver Samples**
  - カメラ映像を受信するための C++ および Python のサンプル実装です。
  - パス: `image_receiver_sample_cpp/`, `image_receiver_sample_py/`

- **Database / Prometheus**
  - メトリクス収集用の Prometheus 設定が含まれています。
  - パス: `database/`

- **CI/CD**
  - GitHub Actions のワークフロー定義です。
  - パス: `.github/workflows/`
