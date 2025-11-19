# LiDAR System

## Install

- `git clone`
- `git submodule init --recursive`
- `sudo apt install build-essential cmake libgflags-dev libopencv-dev nlohmann-json3-dev`

## Build

- `just build`

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
  