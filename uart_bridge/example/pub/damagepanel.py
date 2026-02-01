import random

from uart_bridge.application.example import ExamplePub
from uart_bridge.domain.transmitter_messages import DamagePanelRecognition

key_expr = "damagepanel"


class DamagePanelPub(ExamplePub):
    def create_message(self) -> DamagePanelRecognition:
        return DamagePanelRecognition(
            target_x=random.randint(0, 1280),
            target_y=random.randint(0, 720),
            target_distance=random.randint(0, 100),
        )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()
    publisher = DamagePanelPub(key_expr, args.hz)
    publisher.run()
