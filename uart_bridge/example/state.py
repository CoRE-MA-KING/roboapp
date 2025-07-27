import time

import zenoh

from uart_bridge.domain.messages import RobotState, RobotStateId


class StateReceiver:
    key_expr = "robot/state"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

        for key in RobotState.model_fields.keys():
            print(f"Subscribing to {self.key_expr}/{key}")
            self.session.declare_subscriber(f"{self.key_expr}/{key}", self._on_received)

    def _on_received(self, sample: zenoh.Sample) -> None:
        if str(sample.key_expr) == f"{self.key_expr}/state_id":
            value: str | RobotStateId = RobotStateId(int(sample.payload.to_bytes()))
        else:
            value = sample.payload.to_string()
        print(f"Received {sample.key_expr}: {value}")

    def run(self) -> None:
        while True:
            time.sleep(1)

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = StateReceiver()

    main.run()
