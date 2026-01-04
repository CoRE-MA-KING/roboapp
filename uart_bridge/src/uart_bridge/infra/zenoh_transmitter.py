import zenoh

from uart_bridge.application.interfaces import Transmitter
from uart_bridge.domain.messages import RobotCommand, RobotState
from uart_bridge.domain.transmitter_messages import (
    CameraSwitchMessage,
    DisksMessage,
    FlapMessage,
    LiDARMessage,
)


class ZenohTransmitter(Transmitter):
    """Transmits data using Zenoh protocol."""

    def __init__(self, prefix: str = "") -> None:
        self.zenoh_session = zenoh.open(zenoh.Config())

        if prefix:
            prefix = prefix.rstrip("/") + "/"
        else:
            prefix = ""

        self.publishers = {}

        self.robot_command = RobotCommand()
        self.robot_state = RobotState()

        self.publishers["cam/switch"] = self.zenoh_session.declare_publisher(
            f"{prefix}cam/switch"
        )

        self.publishers["disks"] = self.zenoh_session.declare_publisher(
            f"{prefix}disks"
        )

        self.publishers["flap"] = self.zenoh_session.declare_publisher(f"{prefix}flap")

        self.zenoh_session.declare_subscriber(
            f"{prefix}lidar/force_vector",
            self.lidar_subscriber,
        )

    def publish(self, robot_state: RobotState, force: bool = False) -> None:
        """Transmit data to the specified topic."""
        self.publishers["cam/switch"].put(
            CameraSwitchMessage(camera_id=robot_state.video_id).model_dump_json()
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

    def lidar_subscriber(self, sample: zenoh.Sample) -> None:
        m = LiDARMessage.model_validate_json(sample.payload.to_string())
        self.robot_command.force_linear = int(m.linear)
        self.robot_command.force_angular = int(m.angular * 10)

    def subscribe(self) -> RobotCommand:
        return self.robot_command

    def close(self) -> None:
        """Close the Zenoh session."""
        self.zenoh_session.close()  # type: ignore
