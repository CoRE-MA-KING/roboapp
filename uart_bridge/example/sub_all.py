import time

import zenoh

key_expr = (
    "lidar/force_vector",
    "cam/switch",
    "damagepanel",
    "flap",
    "disks",
    "robotstate",
)


def callback(sample: zenoh.Sample) -> None:
    print(f"Received {sample.key_expr}: {sample.payload.to_string()}")


if __name__ == "__main__":
    with zenoh.open(zenoh.Config()) as session:
        for k in key_expr:
            session.declare_subscriber(k, callback)

        while True:
            time.sleep(1)
