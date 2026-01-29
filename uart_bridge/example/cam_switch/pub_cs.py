import random

from uart_bridge.domain.transmitter_messages import CameraSwitchMessage
from uart_bridge.infra.zenoh_transmitter import create_zenoh_session

key_expr = "cam/switch"

if __name__ == "__main__":
    msg = CameraSwitchMessage(camera_id=random.randint(0, 2))

    print(f"Publishing : {key_expr}: {msg}")

    with create_zenoh_session() as session:
        session.declare_publisher(key_expr).put(msg.model_dump_json())
