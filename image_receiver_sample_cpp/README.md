# Image Subscription Sample for C++

- Python で zenoh を用いて画像を受信するサンプルです

## 環境構築

1. C++ 環境の構築
   - `sudo apt install build-essential cmake libopencv-dev`
2. 依存パッケージのインストール
   - Zenoh をインストールします
   - [公式ビルド済みバイナリ for Ubuntu](https://zenoh.io/docs/getting-started/installation/#ubuntu-or-any-debian)
3. ビルド
   - `mkdir build && cd build`
   - `cmake ..`
   - `make`

## 実行方法

- `main-camera-system -j` でJPEG形式の画像を配信します
- `./image_receiver_sample_cpp` で画像を受信します

## 注意事項

- Ubuntu 標準のOpenCVでは、`cv::imshow`でフリーズするトラブルがあります
- そのため、受信したときに、データを表示するようにしています
- コメントアウトを切り替えれば、受信している様子を確認できます
