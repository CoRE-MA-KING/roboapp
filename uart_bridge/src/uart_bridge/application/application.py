import time
from typing import TYPE_CHECKING

from uart_bridge.application.interfaces import (
    ApplicationInterface,
    RobotDriver,
    Transmitter,
)

if TYPE_CHECKING:
    from uart_bridge.domain.messages import RobotCommand, RobotState


class Application(ApplicationInterface):
    """Implementation for the CoRE auto-pilot application.
    トラッキング対象物体の中心ピクセル座標を画面に表示するだけ。
    奥行き情報(深度)・3次元変換は不要。
    """

    def __init__(
        self,
        robot_driver: RobotDriver,
        transmitter: Transmitter,
    ):
        self._robot_driver = robot_driver
        self._transmitter = transmitter

    def spin(self) -> None:
        last_send_time = time.time()
        while True:
            # ロボットの状態取得
            robot_state: RobotState = self._robot_driver.get_robot_state()

            if time.time() - last_send_time >= 0.1:
                last_send_time = time.time()
                # 状態を送信
                self._transmitter.publish(robot_state)

            robot_command: RobotCommand = self._transmitter.subscribe()

            self._robot_driver.set_send_values(robot_command)

            time.sleep(0.01)
