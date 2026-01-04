import random

import zenoh

from uart_bridge.domain.transmitter_messages import DisksMessage


class DiskSender:
    key_expr = "disk"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

    def run(self) -> None:
        msg = DisksMessage(
            left=random.randint(0, 10),
            right=random.randint(0, 10),
        )
        self.session.declare_publisher(f"{self.key_expr}").put(msg.model_dump_json())
        print(f"Published {self.key_expr}: {msg}")

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = DiskSender()

    main.run()
