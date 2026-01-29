import random

import zenoh

from uart_bridge.domain.transmitter_messages import LiDARMessage

key_expr = "lidar/force_vector"

if __name__ == "__main__":
    msg = LiDARMessage(
        linear=random.uniform(0.0, 10.0),
        angular=random.uniform(0.0, 360.0),
    )

    print(f"Publishing : {key_expr}: {msg}")

    with zenoh.open(zenoh.Config()) as session:
        session.declare_publisher(key_expr).put(msg.model_dump_json())
