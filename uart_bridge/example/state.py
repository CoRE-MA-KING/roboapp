import time

import zenoh
from uart_bridge.domain.messages import  RobotState
from functools import partial

class ImageReceiver:

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())
        key_expr = "robot/state"

        for key in RobotState.model_fields.keys():
            print(f"Subscribing to {key_expr}/{key}")
            self.session.declare_subscriber(
                key_expr, partial(self._on_received, key=f"{key_expr}/{key}")
            )

    def _on_received(self, sample: zenoh.Sample, key: str) -> None:
        print(f"data on {key} received: {sample.payload}")


    def run(self) -> None:
        while True:
            time.sleep(0.1)

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = ImageReceiver()

    main.run()
