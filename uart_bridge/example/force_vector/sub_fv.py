import time

import zenoh

from uart_bridge.domain.transmitter_message import LiDARMessage


class LiDARReceiver:
    key_expr = "lidar/force_vector"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

        self.session.declare_subscriber(f"{self.key_expr}", self._on_received)

    def _on_received(self, sample: zenoh.Sample) -> None:
        value = LiDARMessage.model_validate_json(sample.payload.to_string())
        print(f"Received {sample.key_expr}: {value}")

    def run(self) -> None:
        while True:
            time.sleep(1)

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = LiDARReceiver()

    main.run()
