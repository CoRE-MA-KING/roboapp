# アタッカー用アプリケーション

- 本アプリケーションはLinuxを対象としています
  - Ubuntu 24.04 LTSで動作を確認しています

## 初期設定

1. miseのインストール

- 本アプリケーションの設定には、[mise](https://mise.jdx.dev)を用いています
  - [インストールドキュメント](https://mise.jdx.dev/getting-started.html)を基に、miseをインストールしてください
  - Activate miseを行うと、いくつかのパスを上書きするため、必要に応じて選択してください。
  - 都度Activateする運用で問題ありません

1. 依存関係のインストール

- 以下のコマンドを実行します

- ```bash
    mise i
    mise deps
    ```

## 設定ファイル

本アプリケーション群は、`$XDG_CONFIG_HOME/` または `~/.config/` 以下 `roboapp/config.toml` に設定ファイルを配置します。

設定ファイルの書式があっているかは、`configurator` アプリで確認できます。
正常終了したら、書式はあっています。

```bash
cd configurator
uv run python3 src/configurator/check.py
```

書式や設定内容は、[サンプルファイル](./configurator/test/resources/config_sample.toml)や、[設定の実装](./configurator/src/configurator/config.py)、各アプリケーションの実装・ドキュメントを参考にしてください。

## アプリ一覧

### main_camera_system

- Webカメラの映像を、Zenoh query と WebSocket で配信します

### Image Reciever Sample CPP / Python

- main camera system で出力した画像を受信するサンプルです

### ui_system

- データをUIに描画し、GUIで表示します

### uart_bridge

- マイコンとUART通信を行い、Zenoh queryでデータを配信します

## Zenoh Query

### 一覧

| アプリ名               | 出力トピック名     | データ形式             |
| ---------------------- | ------------------ | ---------------------- |
| main_camera_system     | cam/jpg            | JPEG                   |
| main_camera_system     | cam/switch         | int or None            |
| uart_bridge            | robot/state/*      | RobotState             |
| uart_bridge            | damagepanel        | DamagePanelRecognition |
| lidar_system/sender    | lidar/data         | LiDARData              |
| lidar_system/processor | lidar/force_vector | LiDARMessage           |

### ネットワーク

```mermaid
    flowchart LR

    C[main_camera_system]
    T[UI System]
    U[Uart Bridge]
    M{{STM32}}
    D[Damage Panel Recognition]
    LS1(LiDARSystem/Sender1)
    LS2(LiDARSystem/Sender2)
    LP(LiDARSystem/Processor)
    LV(LiDARSystem/Veiwer)

    C -- （WebSocket）--> T
    U -- robot/state --> T
    U -- （UART：RobotCommand） --> M
    M -- （UART：RobotState） --> U
    D -- damagepanel --> U
    D -- damagepanel --> T
    LS1 -- lidar/data --> LP
    LS2 -- lidar/data --> LP
    LP -- lidar/force_vector --> U
    LP -- lidar/force_vector --> LV
```
