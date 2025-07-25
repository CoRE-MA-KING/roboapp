
import zenoh
from uart_bridge.domain.messages import RobotCommand


def main() -> None:
    session = zenoh.open(zenoh.Config())
    key_expr = "robot/command"

    # Subscribe to the robot command topic
    pub = session.declare_publisher(key_expr)


    pub.put(RobotCommand(
        target_x=100,
        target_y=100,
        target_distance=100

    ).model_dump_json())

if __name__ == "__main__":
    main()