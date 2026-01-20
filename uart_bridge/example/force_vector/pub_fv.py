import random

import zenoh

from uart_bridge.domain.transmitter_messages import LiDARMessage


class LiDARReceiver:
    key_expr = "lidar/force_vector"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

    def run(self) -> None:
        msg = LiDARMessage(
            linear=random.uniform(0.0, 10.0),
            angular=random.uniform(0.0, 360.0),
        )
        self.session.declare_publisher(f"{self.key_expr}").put(msg.model_dump_json())
        print(f"Published {self.key_expr}: {msg}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


if __name__ == "__main__":
    with LiDARReceiver() as main:
        main.run()
