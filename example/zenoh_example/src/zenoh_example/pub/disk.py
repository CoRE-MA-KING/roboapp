import random

from uart_bridge.application.example import ExamplePub
from uart_bridge.domain.transmitter_messages import DisksMessage

key_expr = "disks"


class DisksPub(ExamplePub):
    def create_message(self) -> DisksMessage:
        return DisksMessage(
            left=random.randint(0, 35),
            right=random.randint(0, 35),
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()
    publisher = DisksPub(key_expr, args.hz)
    publisher.run()
