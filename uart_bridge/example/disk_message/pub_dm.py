import random

import zenoh

from uart_bridge.domain.transmitter_messages import DisksMessage

key_expr = "disks"
if __name__ == "__main__":
    msg = DisksMessage(
        left=random.randint(0, 35),
        right=random.randint(0, 35),
    )

    print(f"Publishing : {key_expr}: {msg}")

    with zenoh.open(zenoh.Config()) as session:
        session.declare_publisher(key_expr).put(msg.model_dump_json())
