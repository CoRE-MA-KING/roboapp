import logging
import time
from threading import Lock

import pydantic
import zenoh

from uart_bridge.application.interfaces import Transmitter
from uart_bridge.domain.config import get_config_path
from uart_bridge.domain.messages import RobotState
from uart_bridge.domain.proto.roboapp.camera_switch_pb2 import CameraSwitchMessage
from uart_bridge.domain.proto.roboapp.damage_panel_pb2 import DamagePanelMessage, Target
from uart_bridge.domain.proto.roboapp.disks_pb2 import DisksMessage
from uart_bridge.domain.proto.roboapp.flap_pb2 import FlapMessage
from uart_bridge.domain.proto.roboapp.robot_state_pb2 import RobotStateMessage
from uart_bridge.domain.shared_memory import SharedRobotData
from uart_bridge.domain.transmitter_messages import (
    LiDARVectorMessage,
)


def create_zenoh_session() -> zenoh.Session:
    return zenoh.open(zenoh.Config.from_file(get_config_path() / "zenoh.json5"))


class ZenohTransmitter(Transmitter):
    """Transmits data using Zenoh protocol."""

    def __init__(self) -> None:
        super().__init__()
        self.publishers: dict[str, zenoh.Publisher] = {}

    def publish(self, robot_state: RobotState, force: bool = False) -> None:
        """Transmit data to the specified topic."""
        self.publishers["cam/switch"].put(
            CameraSwitchMessage(
                camera_id=robot_state.video_id,
            ).SerializeToString()
        )

        self.publishers["disks"].put(
            DisksMessage(
                left=robot_state.left_disks, right=robot_state.right_disks
            ).SerializeToString()
        )

        self.publishers["flap"].put(
            FlapMessage(
                pitch=robot_state.pitch_deg, yaw=robot_state.yaw_deg
            ).SerializeToString()
        )

        self.publishers["robotstate"].put(
            RobotStateMessage(
                state=robot_state.state_id.value,
                color="red" if robot_state.flags.is_red else "blue",
            ).SerializeToString()
        )

    def damagepanel_subscriber(self, sample: zenoh.Sample) -> None:
        try:
            d = DamagePanelMessage.FromString(sample.payload.to_bytes())
        except Exception as e:
            logging.error(f"Failed to validate DamagePanelMessage: {e}")
            return

        target = d.target if d.HasField("target") else Target()

        with self.command_lock:
            try:
                cmd = self.shm.read_command()
                cmd.target_x = target.x
                cmd.target_y = target.y
                cmd.target_distance = target.distance
                self.shm.write_command(cmd)
            except Exception as e:
                logging.error(f"Failed to update command in shared memory: {e}")

    def lidar_subscriber(self, sample: zenoh.Sample) -> None:
        try:
            m = LiDARVectorMessage.model_validate_json(sample.payload.to_string())
        except pydantic.ValidationError as e:
            logging.error(f"Failed to validate LiDARVectorMessage: {e}")
            return

        with self.command_lock:
            try:
                cmd = self.shm.read_command()
                cmd.force_linear = int(m.linear)
                cmd.force_angular = int(m.angular * 10)
                self.shm.write_command(cmd)
            except Exception as e:
                logging.error(f"Failed to update command in shared memory: {e}")

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
            "damagepanel",
            self.damagepanel_subscriber,
        )

        self.zenoh_session.declare_subscriber(
            "lidar/force_vector",
            self.lidar_subscriber,
        )

        self.shm = SharedRobotData(name=shm_name)
        self.command_lock = command_lock

        last_send_time = time.time()

        try:
            while self._running:
                # SHMから状態読み込み
                try:
                    with state_lock:
                        state = self.shm.read_state()
                except pydantic.ValidationError as e:
                    logging.error(f"Failed to read state from shared memory: {e}")
                    continue

                with self.command_lock:
                    try:
                        command = self.shm.read_command()
                        print(command)
                    except pydantic.ValidationError as e:
                        logging.error(f"Failed to read command from shared memory: {e}")
                        continue

                if time.time() - last_send_time >= 0.1:
                    last_send_time = time.time()
                    # 送信
                    self.publish(state)

                # ループ頻度調整（適当に早く回す）
                time.sleep(0.01)
        except KeyboardInterrupt:
            pass
        finally:
            if self.shm:
                self.shm.close()
            self.close()
