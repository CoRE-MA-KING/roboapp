import logging
import time
from threading import Lock

import pydantic
import zenoh

from uart_bridge.application.interfaces import Transmitter
from uart_bridge.domain.config import get_config_path
from uart_bridge.domain.messages import RobotCommand, RobotState
from uart_bridge.domain.shared_memory import SharedRobotData
from uart_bridge.domain.transmitter_messages import (
    CameraSwitchMessage,
    DamagePanelRecognition,
    DisksMessage,
    FlapMessage,
    LiDARVectorMessage,
    RobotStateMessage,
)


def create_zenoh_session() -> zenoh.Session:
    return zenoh.open(zenoh.Config.from_file(get_config_path() / "zenoh.json5"))


class ZenohTransmitter(Transmitter):
    """Transmits data using Zenoh protocol."""

    def __init__(self) -> None:
        super().__init__()
        self._command_mutex = Lock()
        self.robot_command = RobotCommand()
        self.publishers: dict[str, zenoh.Publisher] = {}

    def publish(self, robot_state: RobotState, force: bool = False) -> None:
        """Transmit data to the specified topic."""
        self.publishers["cam/switch"].put(
            CameraSwitchMessage(
                camera_id=robot_state.video_id,
            ).model_dump_json()
        )

        self.publishers["disks"].put(
            DisksMessage(
                left=robot_state.left_disks, right=robot_state.right_disks
            ).model_dump_json()
        )

        self.publishers["flap"].put(
            FlapMessage(
                pitch=robot_state.pitch_deg, yaw=robot_state.yaw_deg
            ).model_dump_json()
        )

        self.publishers["robotstate"].put(
            RobotStateMessage(
                state=robot_state.state_id.value,
                color="red" if robot_state.flags.is_red else "blue",
            ).model_dump_json()
        )

    def damagepanel_subscriber(self, sample: zenoh.Sample) -> None:
        try:
            d = DamagePanelRecognition.model_validate_json(sample.payload.to_string())
        except pydantic.ValidationError as e:
            logging.error(f"Failed to validate DamagePanelRecognition: {e}")
            return

        with self._command_mutex:
            self.robot_command.target_x = d.target_x
            self.robot_command.target_y = d.target_y
            self.robot_command.target_distance = d.target_distance

    def lidar_subscriber(self, sample: zenoh.Sample) -> None:
        try:
            m = LiDARVectorMessage.model_validate_json(sample.payload.to_string())
        except pydantic.ValidationError as e:
            logging.error(f"Failed to validate LiDARVectorMessage: {e}")
            return

        with self._command_mutex:
            self.robot_command.force_linear = int(m.linear)
            self.robot_command.force_angular = int(m.angular * 10)

    def subscribe(self) -> RobotCommand:
        with self._command_mutex:
            return self.robot_command.model_copy()

    def close(self) -> None:
        """Close the Zenoh session."""
        if hasattr(self, "zenoh_session"):
            self.zenoh_session.close()  # type: ignore

    def spin(self, shm_name: str, command_lock: Lock, state_lock: Lock) -> None:
        self.zenoh_session = create_zenoh_session()

        self.publishers["cam/switch"] = self.zenoh_session.declare_publisher(
            "cam/switch"
        )

        self.publishers["disks"] = self.zenoh_session.declare_publisher("disks")

        self.publishers["flap"] = self.zenoh_session.declare_publisher("flap")

        self.publishers["robotstate"] = self.zenoh_session.declare_publisher(
            "robotstate"
        )

        self.zenoh_session.declare_subscriber(
            "lidar/force_vector",
            self.lidar_subscriber,
        )

        shm = SharedRobotData(name=shm_name)

        last_send_time = time.time()

        try:
            while self._running:
                # SHMから状態読み込み
                try:
                    with state_lock:
                        state = shm.read_state()
                except pydantic.ValidationError as e:
                    logging.error(f"Failed to read state from shared memory: {e}")
                    continue

                if time.time() - last_send_time >= 0.1:
                    last_send_time = time.time()
                    # 送信
                    self.publish(state)

                # 受信
                command = self.subscribe()

                # SHMに書き込み
                with command_lock:
                    shm.write_command(command)
                # ループ頻度調整（適当に早く回す）
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            shm.close()
            self.close()
