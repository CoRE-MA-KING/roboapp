import random

from uart_bridge.domain.transmitter_messages import LiDARMessage
from uart_bridge.infra.zenoh_transmitter import create_zenoh_session

key_expr = "lidar/force_vector"

if __name__ == "__main__":
    msg = LiDARMessage(
        linear=random.uniform(0.0, 10.0),
        angular=random.uniform(0.0, 360.0),
    )

    print(f"Publishing : {key_expr}: {msg}")

    with create_zenoh_session() as session:
        session.declare_publisher(key_expr).put(msg.model_dump_json())
