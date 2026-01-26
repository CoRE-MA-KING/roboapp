import time

import zenoh

from uart_bridge.domain.transmitter_messages import DamagePanelRecognition


def callback(sample: zenoh.Sample) -> None:
    print(
        f"Received {sample.key_expr}: {
            DamagePanelRecognition.model_validate_json(sample.payload.to_string())
        }"
    )


if __name__ == "__main__":
    with zenoh.open(zenoh.Config()) as session:
        session.declare_subscriber("damagepanel", callback)

        while True:
            time.sleep(1)
