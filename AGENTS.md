# プロジェクト概要

- Ubuntu 24.04 LTS をターゲットとしたロボット制御用アプリケーション「roboapp」のリポジトリです。
- 環境管理には `mise` を使用し、通信には Zenoh と WebSocket を採用しています。

## 開発ガイドライン

- **言語設定**
  - 回答や対話はすべて日本語で行ってください。
- **ドキュメントの更新**
  - アプリケーションの実装を更新した場合は、`AGENTS.md` や対応する `README.md` を更新してください（特に起動オプションや設定項目など）。
- **コードの整形と検証**
  - コードを変更した後は、必ず以下のコマンドを実行してコードの整形と検証を行ってください。

    ```bash
    mise format
    mise lint
    ```

- **mise tasksの役割について**
  - `mise tasks`を用いて、プロジェクトの管理を行っています
  - 以下のメインタスクとそれを支えるサブタスクからなります（詳しくは、`mise.toml` の各タスクの description を参照してください）
    - deps：プロジェクトの依存関係をインストールしたり、環境構築を行います（AIエージェントが使うことはないとおもいます）
    - lint：設定された linter や type checker を実行します
    - format：設定された formatter を実行します
    - test：設定された test を実行します
    - start：アプリケーションを実行します（AIエージェントが使うことはないとおもいます）

## コンポーネント一覧

- **Configurator**
  - 説明: 設定ファイルの検証や systemd サービスのセットアップを行う Python ツールです。
  - パス: `configurator/`

- **LiDAR System**
  - 説明: LiDAR データの処理、障害物回避計算、可視化を行う C++ システムです。`sender`, `processor`, `viewer` で構成されます。
  - パス: `lidar_system/`

- **Main Camera System**
  - 説明: Webカメラの映像を Zenoh Query および WebSocket で配信する Rust アプリケーションです。
  - パス: `main_camera_system/`

- **UART Bridge**
  - 説明: マイコンと UART 通信を行い、データを Zenoh で中継する Python アプリケーションです。
  - パス: `uart_bridge/`

- **UI System**
  - 説明: システムの監視と操作を行うための SvelteKit + Tauri 製のユーザーインターフェースです。
  - パス: `ui_system/`

- **Image Receiver Samples**
  - 説明: カメラ映像を受信するための C++ および Python のサンプル実装です。
  - パス: `image_receiver_sample_cpp/`, `image_receiver_sample_py/`

- **Database / Prometheus**
  - 説明: メトリクス収集用の Prometheus 設定が含まれています。
  - パス: `database/`

- **CI/CD**
  - 説明: GitHub Actions のワークフロー定義です。
  - パス: `.github/workflows/`
