import random

from uart_bridge.application.example import ExamplePub
from uart_bridge.domain.transmitter_messages import LiDARVectorMessage

key_expr = "lidar/force_vector"


class LiDARVectorPub(ExamplePub):
    def create_message(self) -> LiDARVectorMessage:
        return LiDARVectorMessage(
            linear=random.uniform(0.0, 10.0),
            angular=random.uniform(0.0, 360.0),
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()
    publisher = LiDARVectorPub(key_expr, args.hz)
    publisher.run()
