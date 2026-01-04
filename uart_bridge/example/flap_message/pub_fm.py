import random

import zenoh

from uart_bridge.domain.transmitter_messages import FlapMessage


class DiskSender:
    key_expr = "flap"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

    def run(self) -> None:
        msg = FlapMessage(
            pitch=random.uniform(-45.0, 45.0),
            yaw=random.uniform(-45.0, 45.0),
        )
        self.session.declare_publisher(f"{self.key_expr}").put(msg.model_dump_json())
        print(f"Published {self.key_expr}: {msg}")

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = DiskSender()

    main.run()
