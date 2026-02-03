import random

from uart_bridge.application.example import ExamplePub
from uart_bridge.domain.transmitter_messages import DamagePanelRecognition, Target

key_expr = "damagepanel"


class DamagePanelPub(ExamplePub):
    def __init__(self, key: str, hz: float | None, no: bool = False) -> None:
        super().__init__(key, hz)
        self.no = no

    def create_message(self) -> DamagePanelRecognition:
        if self.no:
            msg = DamagePanelRecognition(target=None)
        else:
            msg = DamagePanelRecognition(
                target=Target(
                    x=random.randint(0, 1280),
                    y=random.randint(0, 720),
                    distance=random.randint(0, 100),
                )
            )

        return msg


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    parser.add_argument(
        "-n", action="store_true", help="Send empty target (None) if specified"
    )
    args = parser.parse_args()
    publisher = DamagePanelPub(key_expr, args.hz, args.n)
    publisher.run()
