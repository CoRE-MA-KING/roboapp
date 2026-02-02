from uart_bridge.application.example import ExamplePub
from uart_bridge.domain.transmitter_messages import (
    LiDARRange,
)

key_expr = "lidar/range"


class LiDARRangePub(ExamplePub):
    step = 250
    index = 0
    up = True

    def create_message(self) -> LiDARRange:
        if self.up:
            self.index += self.step
            if self.index >= 3_000:
                self.up = False
        else:
            self.index -= self.step
            if self.index <= 500:
                self.up = True

        return LiDARRange(
            left=3500 - self.index,
            rear_left=self.index,
            rear_right=3500 - self.index,
            right=self.index,
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()
    publisher = LiDARRangePub(key_expr, args.hz)
    publisher.run()
