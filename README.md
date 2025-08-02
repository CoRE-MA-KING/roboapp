# アタッカー用アプリケーション

- 本アプリケーションはLinuxを対象としています
  - Ubuntu 24.04 LTSで動作を確認しています

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

| アプリ名           | トピック名      | データ形式   |
| ------------------ | --------------- | ------------ |
| main_camera_system | cam/jpg         | JPEG         |
| main_camera_system | cam/raw         | RGB 24 bit   |
| uart_bridge        | robot/state/*   | RobotState   |
| uart_bridge        | robot/command/* | RobotCommand |

### ネットワーク

```mermaid
    flowchart LR

    A[main_camera_system]
    B[UI System]
    C[画像処理 or Image Reciever]
    U[Uart Bridge]
    E(UART Bridge （example）)
    M{{STM32}}

    A -- （WebSocket）--> B
    A -- cam/jpg --> C
    U -- robot/state --> B
    U -- robot/state --> E
    E -- robot/command --> U
    E -- robot/command --> B
    U -- （UART） --> M
    M -- （UART） --> U
```
