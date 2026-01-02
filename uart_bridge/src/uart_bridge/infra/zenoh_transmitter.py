import zenoh

from uart_bridge.application.interfaces import Transmitter
from uart_bridge.domain.messages import (
    DamagePanelRecognition,
    LiDARMessage,
    RobotCommand,
    RobotState,
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

        for key in RobotState.model_fields.keys():
            self.publishers[key] = self.zenoh_session.declare_publisher(
                f"{prefix}robot/state/{key}"
            )

        self.zenoh_session.declare_subscriber(
            f"{prefix}lidar/force_vector",
            self.lidar_subscriber,
        )

        self.zenoh_session.declare_subscriber(
            f"{prefix}robot/state/request",
            self._subscriber_callback_request,
        )

        self.zenoh_session.declare_subscriber(
            "damagepanel",
            self.recognition_damagepanel_subscriber,
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

    def recognition_damagepanel_subscriber(self, sample: zenoh.Sample) -> None:
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

    def _subscriber_callback_request(self, sample: zenoh.Sample) -> None:
        self.publish(self.robot_state, force=True)

    def close(self) -> None:
        """Close the Zenoh session."""
        self.zenoh_session.close()  # type: ignore
