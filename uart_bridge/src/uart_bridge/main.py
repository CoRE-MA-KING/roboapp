import argparse

from uart_bridge.application.application import Application
from uart_bridge.infra.serial_robot_driver import SerialRobotDriver
from uart_bridge.infra.zenoh_transmitter import ZenohTransmitter


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--robot_port",
        default="/dev/ttyACM0",
        type=str,
        help="serial port for communicating with robot",
    )

    return parser.parse_args()


def run_application(
    robot_port: str,
) -> None:
    """アプリケーションを実行する"""
    with (
        SerialRobotDriver(robot_port) as robot_driver,
        ZenohTransmitter() as transmitter,
    ):
        app = Application(robot_driver, transmitter)
        app.spin()


def main() -> None:
    args = parse_args()
    # シンボリックリンクから実際のビデオ番号を取得する
    run_application(
        robot_port=args.robot_port,
    )


if __name__ == "__main__":
    main()
