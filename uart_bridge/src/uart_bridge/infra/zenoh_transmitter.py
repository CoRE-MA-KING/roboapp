import time
from threading import Lock

import zenoh

from uart_bridge.application.interfaces import Transmitter
from uart_bridge.domain.messages import RobotCommand, RobotState
from uart_bridge.domain.shared_memory import SharedRobotData
from uart_bridge.domain.transmitter_messages import (
    CameraSwitchMessage,
    DamagePanelRecognition,
    DisksMessage,
    FlapMessage,
    LiDARMessage,
)


class ZenohTransmitter(Transmitter):
    """Transmits data using Zenoh protocol."""

    def __init__(self) -> None:
        pass

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

    def damagepanel_subscriber(self, sample: zenoh.Sample) -> None:
        d = DamagePanelRecognition.model_validate_json(sample.payload.to_string())

        self.robot_command.target_x = d.target_x
        self.robot_command.target_y = d.target_y
        self.robot_command.target_distance = d.target_distance

    def lidar_subscriber(self, sample: zenoh.Sample) -> None:
        m = LiDARMessage.model_validate_json(sample.payload.to_string())
        self.robot_command.force_linear = int(m.linear)
        self.robot_command.force_angular = int(m.angular * 10)

    def subscribe(self) -> RobotCommand:
        return self.robot_command

    def close(self) -> None:
        """Close the Zenoh session."""
        self.zenoh_session.close()  # type: ignore

    def spin(self, shm_name: str, command_lock: Lock, state_lock: Lock) -> None:
        self.zenoh_session = zenoh.open(zenoh.Config())

        self.publishers = {}

        self.robot_command = RobotCommand()
        self.robot_state = RobotState()

        self.publishers["cam/switch"] = self.zenoh_session.declare_publisher(
            "cam/switch"
        )

        self.publishers["disks"] = self.zenoh_session.declare_publisher("disks")

        self.publishers["flap"] = self.zenoh_session.declare_publisher("flap")

        self.zenoh_session.declare_subscriber(
            "lidar/force_vector",
            self.lidar_subscriber,
        )

        shm = SharedRobotData(name=shm_name)

        last_send_time = time.time()

        try:
            while True:
                # SHMから状態読み込み
                with state_lock:
                    state = shm.read_state()

                if time.time() - last_send_time >= 0.1:
                    last_send_time = time.time()
                    # 送信
                    self.publish(state)

                # 受信 (ZenohTransmitter内でsubscribeコールバックが動いている前提)
                command = self.subscribe()

                # SHMに書き込み
                with command_lock:
                    shm.write_command(command)
                # ループ頻度調整（適当に早く回す）
                time.sleep(0.001)
        except KeyboardInterrupt:
            pass
        finally:
            shm.close()
            self.close()
