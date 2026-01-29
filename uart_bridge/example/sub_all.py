import time

import zenoh

from uart_bridge.infra.zenoh_transmitter import create_zenoh_session

key_expr = (
    "lidar/force_vector",
    "cam/switch",
    "damagepanel",
    "flap",
    "disks",
)


def callback(sample: zenoh.Sample) -> None:
    print(f"Received {sample.key_expr}: {sample.payload.to_string()}")


if __name__ == "__main__":
    with create_zenoh_session() as session:
        for k in key_expr:
            session.declare_subscriber(k, callback)

        while True:
            time.sleep(1)
