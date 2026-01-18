import random

import zenoh

from uart_bridge.domain.transmitter_messages import DamagePanelRecognition


def main() -> None:
    session = zenoh.open(zenoh.Config())
    key_expr = "damagepanel"

    # Subscribe to the robot command topic

    pub = session.declare_publisher(f"{key_expr}")

    d = DamagePanelRecognition(
        target_x=random.randint(0, 1280),
        target_y=random.randint(0, 720),
        target_distance=random.randint(0, 100),
    )

    print(type(d.model_dump_json()))

    pub.put(d.model_dump_json())
    print(f"Published DamagePanelRecognition: {d.model_dump()}")


if __name__ == "__main__":
    main()
