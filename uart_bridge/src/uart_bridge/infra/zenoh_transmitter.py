import zenoh

from uart_bridge.application.interfaces import Transmitter
from uart_bridge.domain.messages import RobotCommand, RobotState
from uart_bridge.domain.transmitter_messages import CameraSwitchMessage, LiDARMessage


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

        self.zenoh_session.declare_subscriber(
            f"{prefix}lidar/force_vector",
            self.lidar_subscriber,
        )

    def publish(self, robot_state: RobotState, force: bool = False) -> None:
        """Transmit data to the specified topic."""
        for key in RobotState.model_fields.keys():
            value = getattr(robot_state, key)

            if not force and value == getattr(self.robot_state, key):
                continue

            setattr(self.robot_state, key, value)

            if key == "state_id":
                value = value.value
            elif key == "pitch_deg":
                value = value / 10
            elif key == "muzzle_velocity":
                value = value / 1000
            self.publishers[key].put(f"{value}")
            print(f"Published {key}: {value}")

        self.publishers["cam/switch"].put(
            CameraSwitchMessage(camera_id=robot_state.video_id).model_dump_json()
        )

    def _subscriber(self, sample: zenoh.Sample) -> None:
        setattr(
            self.robot_command,
            str(sample.key_expr).split("/")[-1],
            sample.payload.to_string(),
        )

    def lidar_subscriber(self, sample: zenoh.Sample) -> None:
        m = LiDARMessage.model_validate_json(sample.payload.to_string())
        self.robot_command.force_linear = int(m.linear)
        self.robot_command.force_angular = int(m.angular * 10)

    def subscribe(self) -> RobotCommand:
        return self.robot_command

    def _subscriber_callback_request(self, sample: zenoh.Sample) -> None:
        self.publish(self.robot_state, force=True)

    def close(self) -> None:
        """Close the Zenoh session."""
        self.zenoh_session.close()  # type: ignore
