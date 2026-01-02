import random

import zenoh

from uart_bridge.domain.transmitter_message import LiDARMessage


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

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = LiDARReceiver()

    main.run()
