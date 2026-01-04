import time

import zenoh


class CamSwitchReceiver:
    key_expr = "cam/switch"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

        self.session.declare_subscriber(f"{self.key_expr}", self._on_received)

        self.session.declare_publisher(f"{self.key_expr}/request").put("request")

    def _on_received(self, sample: zenoh.Sample) -> None:
        print(f"Received {sample.key_expr}: {sample.payload.to_string()}")

    def run(self) -> None:
        while True:
            time.sleep(1)

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = CamSwitchReceiver()

    main.run()
