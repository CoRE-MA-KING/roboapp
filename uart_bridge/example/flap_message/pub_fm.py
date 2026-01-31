import argparse
import datetime
import random
import time

from uart_bridge.domain.transmitter_messages import FlapMessage
from uart_bridge.infra.zenoh_transmitter import create_zenoh_session

key_expr = "flap"
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()

    with create_zenoh_session() as session:
        pub = session.declare_publisher(key_expr)

        while True:
            msg = FlapMessage(
                pitch=random.uniform(0.0, 15.0),
                yaw=random.uniform(0.0, 40.0),
            )

            print(
                f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Publishing : {key_expr}: {msg}"
            )

            pub.put(msg.model_dump_json())

            if args.hz is None:
                break

            if args.hz > 0:
                time.sleep(1.0 / args.hz)
            else:
                print(
                    f"Error: --hz must be a positive number, but got {args.hz}. Exiting."
                )
                break
