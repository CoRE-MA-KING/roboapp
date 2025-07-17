import zenoh

from uart_bridge.application.interfaces import (
    ApplicationInterface,
    RobotDriver,
)
from uart_bridge.domain.messages import RobotState, RobotStateId


class Application(ApplicationInterface):
    """Implementation for the CoRE auto-pilot application.
    トラッキング対象物体の中心ピクセル座標を画面に表示するだけ。
    奥行き情報(深度)・3次元変換は不要。
    """

    def __init__(
        self,
        robot_driver: RobotDriver,
        # 重い検出処理はrealsense_camera側で行うので、ここでは重みの初期化は不要
    ):
        self._robot_driver = robot_driver

        self._is_recording = False

        # Application側では、Realsenseで計算された検出結果を参照する
        self.aiming_target = (0, 0)  # (cx, cy) を入れる想定

    def spin(self) -> None:
        while True:
            # ロボットの状態取得
            robot_state: RobotState = self._robot_driver.get_robot_state()

            self._robot_driver.set_send_values(
                self.aiming_target[0], self.aiming_target[1], 0, 0
            )
