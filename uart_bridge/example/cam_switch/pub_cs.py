import random

import zenoh

from uart_bridge.domain.transmitter_messages import CameraSwitchMessage


class CamSwitchSender:
    key_expr = "cam/switch"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

    def run(self) -> None:
        msg = CameraSwitchMessage(camera_id=random.randint(0, 2))
        print(f"Publishing: {msg}")

        self.session.declare_publisher(f"{self.key_expr}").put(msg.model_dump_json())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


if __name__ == "__main__":
    with CamSwitchSender() as main:
        main.run()
