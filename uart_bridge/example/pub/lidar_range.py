import random

from uart_bridge.application.example import ExamplePub
from uart_bridge.domain.transmitter_messages import (
    LiDARRange,
)

key_expr = "lidar/range"


class LiDARRangePub(ExamplePub):
    def create_message(self) -> LiDARRange:
        return LiDARRange(
            left=random.uniform(15.0, 2_000.0),
            rear_left=random.uniform(15.0, 2_000.0),
            rear_right=random.uniform(15.0, 2_000.0),
            right=random.uniform(15.0, 2_000.0),
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()
    publisher = LiDARRangePub(key_expr, args.hz)
    publisher.run()
