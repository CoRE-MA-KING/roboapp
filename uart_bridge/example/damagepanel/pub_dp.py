import random

import zenoh

from uart_bridge.domain.transmitter_messages import DamagePanelRecognition

key_expr = "damagepanel"
if __name__ == "__main__":
    msg = DamagePanelRecognition(
        target_x=random.randint(0, 1280),
        target_y=random.randint(0, 720),
        target_distance=random.randint(0, 100),
    )

    print(f"Publishing : {key_expr}: {msg}")

    with zenoh.open(zenoh.Config()) as session:
        session.declare_publisher(key_expr).put(msg.model_dump_json())
