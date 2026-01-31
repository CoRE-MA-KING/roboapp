import random

from uart_bridge.application.example import ExamplePub
from uart_bridge.domain.transmitter_messages import CameraSwitchMessage

key_expr = "cam/switch"


class CameraSwitchPub(ExamplePub):
    def create_message(self) -> CameraSwitchMessage:
        return CameraSwitchMessage(camera_id=random.randint(0, 2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()
    publisher = CameraSwitchPub(key_expr, args.hz)
    publisher.run()
