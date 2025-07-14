# Main Camera System

## コマンドラインオプション

```txt
Usage: main-camera-system [OPTIONS]

Options:
  -c, --camera-id <CAMERA_ID>        [default: 0]
  -z, --zenoh-prefix <ZENOH_PREFIX>  [default: ]
  -r, --raw
  -j, --jpg
  -w, --websocket
  -p, --port <PORT>                  [default: 8080]
  -d, --debug
  -h, --help                         Print help
```

- `-c` ：カメラのデバイスIDを指定します
- `-z` ：zenohのプレフィックスを指定します
- `-r` ：生のRGBデータを配信します
- `-j` ：JPEG形式の画像を配信します
- `-w` ：WebSocketで配信します
- `-p` ：WebSocketのポート番号を指定します
- `-d` ：デバッグモードを有効にします
