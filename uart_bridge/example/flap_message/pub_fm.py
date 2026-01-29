import random

from uart_bridge.domain.transmitter_messages import FlapMessage
from uart_bridge.infra.zenoh_transmitter import create_zenoh_session

key_expr = "flap"
if __name__ == "__main__":
    msg = FlapMessage(
        pitch=random.uniform(0.0, 15.0),
        yaw=random.uniform(0.0, 40.0),
    )

    print(f"Publishing : {key_expr}: {msg}")

    with create_zenoh_session() as session:
        session.declare_publisher(key_expr).put(msg.model_dump_json())
