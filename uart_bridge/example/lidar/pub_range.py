import random

from uart_bridge.application.example import ExamplePub
from uart_bridge.domain.transmitter_messages import (
    LiDARRange,
    LiDARRangeMessage,
)

key_expr = "lidar/force_vector"


class LiDARRangePub(ExamplePub):
    def create_message(self) -> LiDARRangeMessage:
        return LiDARRangeMessage(
            data=[
                LiDARRange(
                    min_degree=30 * _,
                    max_degree=30 * (_ + 1),
                    distance=random.uniform(0.0, 10_000.0),
                )
                for _ in range(12)
            ]
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()

    publisher = LiDARRangePub(key_expr, args.hz)
    publisher.run()
