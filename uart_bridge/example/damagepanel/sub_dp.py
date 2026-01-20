import time
from types import TracebackType
from typing import Optional, Self, Type

import zenoh

from uart_bridge.domain.transmitter_messages import DamagePanelRecognition


class DamagePanelReceiver:
    key_expr = "damagepanel"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

        # Subscribe to the robot command topic

        self.session.declare_subscriber(
            f"{self.key_expr}",
            lambda sample: print(
                "Received DamagePanelRecognition:"
                + f" {DamagePanelRecognition.model_validate_json(sample.payload.to_string())}"  # noqa
            ),
        )

    def run(self) -> None:
        while True:
            time.sleep(1)

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_value: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    with DamagePanelReceiver() as main:
        try:
            main.run()
        except KeyboardInterrupt:
            pass
