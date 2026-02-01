import random
import subprocess
import time

import serial

from uart_bridge.domain.config import get_dummy_port


def main(port: str) -> None:
    """
    Arduino の dummy_fw_arduino.ino と同等のデータを標準出力に書き出すスクリプト。
    10ms間隔で CSV 形式のセンサーデータを生成します。
    """
    interval_ms = 0.01  # 10ms

    with serial.Serial(port=port) as myserial:
        while True:
            start_time = time.perf_counter()

            # Arduino random(min, max) は max を含まないため randrange を使用
            robot_status = random.randrange(0, 5)  # 0: ロボット状態 (0-4)
            pitch = random.randrange(0, 401)  # 1: ピッチ角度 (0-400)
            yaw = random.randrange(0, 180)  # 2: ヨー角度 (0-179)
            left_frisbee = random.randrange(0, 36)  # 3: 左フリスビー枚数 (0-35)
            right_frisbee = random.randrange(0, 36)  # 4: 右フリスビー枚数 (0-35)
            camera_id = random.randrange(0, 1)  # 5: カメラID (常に0)
            flags = random.randrange(0, 256)  # 6: フラグ (0-255)
            reserved = 0  # 7: 予備 (常に0)

            # CSV形式で出力
            data = f"{robot_status},{pitch},{yaw},{left_frisbee},{right_frisbee},{camera_id},{flags},{reserved}\n"
            myserial.write(data.encode())

            # 10ms 間隔を維持するための調整
            elapsed = time.perf_counter() - start_time
            sleep_time = interval_ms - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)


if __name__ == "__main__":
    mcu_path, bridge_path = get_dummy_port()

    # 既存のリンクがある場合は削除（socatのエラー回避）

    if mcu_path.exists():
        mcu_path.unlink()

    if bridge_path.exists():
        bridge_path.unlink()

    print(
        f"Creating virtual serial ports:\n\tMCU side:\t{mcu_path}\n\tBridge side:\t{bridge_path}"
    )

    # socatをバックグラウンドで実行

    socat_process = subprocess.Popen(
        [
            "socat",
            f"PTY,link={mcu_path},raw,echo=0",
            f"PTY,link={bridge_path},raw,echo=0",
        ]
    )

    try:
        # ポート作成を少し待つ

        time.sleep(0.5)

        print("Starting dummy firmware...")

        main(port=str(mcu_path))

    except KeyboardInterrupt:
        pass

    finally:
        print("\nStopping socat...")

        socat_process.terminate()

        socat_process.wait()
