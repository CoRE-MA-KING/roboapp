import random

import zenoh

from uart_bridge.domain.transmitter_messages import CameraSwitchMessage

key_expr = "cam/switch"

if __name__ == "__main__":
    msg = CameraSwitchMessage(camera_id=random.randint(0, 2))

    print(f"Publishing : {key_expr}: {msg}")

    with zenoh.open(zenoh.Config()) as session:
        session.declare_publisher(key_expr).put(msg.model_dump_json())
