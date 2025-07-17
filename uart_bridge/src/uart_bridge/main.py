import argparse
import os
import re
from typing import Optional

from uart_bridge.application.application import Application
from uart_bridge.infra.serial_robot_driver import SerialRobotDriver


def get_video_number_from_symlink(symlink_path: str) -> int:
    """
    シンボリックリンクのターゲットから、数字（例："video6" の6）を抽出して返す関数
    """
    try:
        target = os.readlink(symlink_path)
        # 相対パスの場合は絶対パスに変換する
        if not os.path.isabs(target):
            target = os.path.join(os.path.dirname(symlink_path), target)
        match = re.search(r"(\d+)", target)
        if match:
            return int(match.group(1))
        else:
            raise ValueError(f"数字が見つかりません: {target}")
    except OSError as e:
        raise RuntimeError(
            f"シンボリックリンクの読み取りに失敗しました: {symlink_path}"
        ) from e


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--robot_port",
        default="/dev/ttyACM0",
        type=str,
        help="serial port for communicating with robot",
    )
    parser.add_argument(
        "--record_dir",
        default="/mnt/ssd1",
        type=str,
        help="directory to record camera log",
    )
    parser.add_argument(
        "--a_camera_name",
        default="/dev/front_camera",
        help="device file (symlink) of camera A (front camera)",
    )
    parser.add_argument(
        "--b_camera_name",
        default="/dev/back_camera",
        help="device file (symlink) of camera B (back camera)",
    )
    parser.add_argument(
        "--weight_path",
        default="/home/nvidia/uart_bridge/models/yolox_s/phase1_2_best_ckpt.pth",
        type=str,
        help="path to YOLOX weight file (.pth)",
    )
    args = parser.parse_args()
    return args


def run_application(
    robot_port: str,
) -> None:
    """アプリケーションを実行する"""
    with (
        SerialRobotDriver(robot_port) as robot_driver,
    ):
        app = Application(robot_driver)
        app.spin()


def main() -> None:
    args = parse_args()
    # シンボリックリンクから実際のビデオ番号を取得する
    run_application(
        robot_port=args.robot_port,
    )


if __name__ == "__main__":
    main()
