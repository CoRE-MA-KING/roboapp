# LiDAR System

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
   - `build/processor` と `build/sender` に実行ファイルが生成されます

2. 実行

   - `sender`
     - lidarデータを送信するソフトです
     - `./build/sender -n foo` のように、`-n` オプションでデバイス名を指定して実行します
   - `processor`
     - 障害物回避の計算と可視化を行うソフトです
     - `./build/processor` で実行します
     - `-s` オプションをつけると点群情報を描画します

## 設定ファイル

```toml
[lidar]
# ロボットの幅（左右）
robot_width = 800
# ロボットの長さ（前後）
robot_length = 800
# 斥力計算のゲイン
repulsive_gain = 0.7
# 斥力計算の範囲
influence_range = 200

[lidar.devices.foo]
# LiDARデバイスの種類（random / rplidar）
backend = "random"
# LiDARの接続先（rplidarのみ）
device = "/dev/ttyUSB0"
# 取り付け位置（左右）・ロボット座標系（右が正）
x = 0
# 取り付け位置（前後）・ロボット座標系（前が正）
y = 0
# 取り付け角度（度単位、反時計・左回りが正）
rotation = 0
# LiDARの最大距離（この距離に丸める）
max_distance = 1000
# LiDARの検出角度（下限）
min_degree = 0
# LiDARの検出角度（上限）
max_degree = 360
```

## 座標系

### 描画

- OpenCVの座標系（右手系）
  - 右方向がX軸正方向
  - 下方向がY軸正方向
  - 角度は0度が右方向で、時計回りに増加

### Random LiDAR

- OpenCVの座標系（右手系）
  - 角度は時計回りに増加

### RPLiDAR（A2M8）

- 本体から生えたケーブルが180度
  - 写真の向きの場合、右が0度、左が180度
  - ケーブルの反対が0度
  - 角度は時計回りに増加

![左側にケーブルを出したRPLiDAR A2M8](./docs/image/rplidar.avif)
