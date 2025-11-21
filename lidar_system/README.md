# LiDAR System

## Install

- `git clone`
- `git submodule init --recursive`
- `sudo apt install build-essential cmake libgflags-dev libopencv-dev nlohmann-json3-dev`

## Build

- `just build`

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
# LiDARの最大距離（この距離に丸める）
max_distance = 1000
# LiDARの検出角度（下限）
min_degree = 0
# LiDARの検出角度（上限）
max_degree = 360
# 取り付け位置（左右）
x = 0
# 取り付け位置（前後）
y = 0
# 画像座標系に対する、LiDAR座標系の回転角（度単位、時計回りが正）
rotation = 0
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
