import argparse

from uart_bridge.application.application import Application
from uart_bridge.domain.config import get_uart_config
from uart_bridge.infra.serial_robot_driver import SerialRobotDriver
from uart_bridge.infra.zenoh_transmitter import ZenohTransmitter


def parse_args() -> argparse.Namespace:
    """コマンドライン引数をパースする"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--config-file",
        default=None,
        type=str,
        help="Path to the configuration file",
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

    uart_config = get_uart_config(file_path=args.config_file)

    run_application(
        robot_port=uart_config.port,
    )


if __name__ == "__main__":
    main()
