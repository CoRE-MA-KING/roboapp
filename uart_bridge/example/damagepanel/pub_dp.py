import random

from uart_bridge.domain.transmitter_messages import DamagePanelRecognition
from uart_bridge.infra.zenoh_transmitter import create_zenoh_session

key_expr = "damagepanel"
if __name__ == "__main__":
    msg = DamagePanelRecognition(
        target_x=random.randint(0, 1280),
        target_y=random.randint(0, 720),
        target_distance=random.randint(0, 100),
    )

    print(f"Publishing : {key_expr}: {msg}")

    with create_zenoh_session() as session:
        session.declare_publisher(key_expr).put(msg.model_dump_json())
