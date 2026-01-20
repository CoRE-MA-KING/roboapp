import time

import zenoh

from uart_bridge.domain.transmitter_messages import LiDARMessage


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

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


if __name__ == "__main__":
    with LiDARReceiver() as main:
        try:
            main.run()
        except KeyboardInterrupt:
            pass
