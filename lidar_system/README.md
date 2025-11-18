# LiDAR System

## Install

- `git clone`
- `git submodule init --recursive`
- `sudo apt install build-essential cmake libgflags-dev libopencv-dev nlohmann-json3-dev`

## Build

- `cmake -S . -B build -G Ninja`
- `cmake --build build`
