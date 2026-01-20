import random
from types import TracebackType
from typing import Optional, Self, Type

import zenoh

from uart_bridge.domain.transmitter_messages import LiDARMessage


class LiDARReceiver:
    key_expr = "lidar/force_vector"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

    def run(self) -> None:
        msg = LiDARMessage(
            linear=random.uniform(0.0, 10.0),
            angular=random.uniform(0.0, 360.0),
        )
        self.session.declare_publisher(f"{self.key_expr}").put(msg.model_dump_json())
        print(f"Published {self.key_expr}: {msg}")

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
    with LiDARReceiver() as main:
        main.run()
