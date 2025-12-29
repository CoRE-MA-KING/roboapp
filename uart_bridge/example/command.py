import random

import zenoh

from uart_bridge.domain.messages import RobotCommand


def main() -> None:
    session = zenoh.open(zenoh.Config())
    key_expr = "robot/command"

    # Subscribe to the robot command topic

    for key in RobotCommand.model_fields.keys():
        pub = session.declare_publisher(f"{key_expr}/{key}")

        value = random.randint(0, 100)

        pub.put(str(value))
        print(f"Published {key}: {value}")


if __name__ == "__main__":
    main()
