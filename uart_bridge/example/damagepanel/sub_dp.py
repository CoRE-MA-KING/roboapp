import time

import zenoh

from uart_bridge.domain.messages import DamagePanelRecognition


def main() -> None:
    session = zenoh.open(zenoh.Config())
    key_expr = "damagepanel"

    # Subscribe to the robot command topic

    session.declare_subscriber(
        f"{key_expr}",
        lambda sample: print(
            "Received DamagePanelRecognition:"
            + f" {DamagePanelRecognition.model_validate_json(sample.payload.to_string())}"  # noqa
        ),
    )

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
