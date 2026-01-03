import random

import zenoh

from uart_bridge.domain.zenoh_messages import CameraSwitchMessage


class CamSwitchSender:
    key_expr = "cam/switch"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

    def run(self) -> None:
        msg = CameraSwitchMessage(camera_id=random.randint(0, 2))
        print(f"Publishing: {msg}")

        self.session.declare_publisher(f"{self.key_expr}").put(msg.model_dump_json())

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = CamSwitchSender()

    main.run()
