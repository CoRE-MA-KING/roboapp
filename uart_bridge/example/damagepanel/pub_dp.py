import random

import zenoh

from uart_bridge.domain.transmitter_messages import DamagePanelRecognition


class DamagePanelSender:
    key_expr = "damagepanel"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

    def run(self) -> None:
        # Subscribe to the robot command topic

        pub = self.session.declare_publisher(f"{self.key_expr}")

        d = DamagePanelRecognition(
            target_x=random.randint(0, 1280),
            target_y=random.randint(0, 720),
            target_distance=random.randint(0, 100),
        )

        print(type(d.model_dump_json()))

        pub.put(d.model_dump_json())
        print(f"Published DamagePanelRecognition: {d.model_dump()}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


if __name__ == "__main__":
    with DamagePanelSender() as main:
        main.run()
