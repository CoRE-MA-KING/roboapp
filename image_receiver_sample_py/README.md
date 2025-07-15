# Image Subscription Sample for Python

- Python で zenoh を用いて画像を受信するサンプルです

## 環境構築

1. Pythonのインストール
   - Python 3.8以上をインストールしてください
   - [uv](https://docs.astral.sh/uv/) のインストール
     - `curl -LsSf https://astral.sh/uv/install.sh | sh`

2. 依存パッケージのインストール
   - `uv sync`

## 実行方法

- `main-camera-system -j` でJPEG形式の画像を配信します
- `uv run src/image_receiver_sample_py/sub.py` で画像を受信します
