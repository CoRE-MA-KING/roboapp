import argparse
import datetime
import random
import time

import zenoh

from uart_bridge.domain.transmitter_messages import LiDARMessage

key_expr = "lidar/force_vector"

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()

    with zenoh.open(zenoh.Config()) as session:
        pub = session.declare_publisher(key_expr)

        while True:
            msg = LiDARMessage(
                linear=random.uniform(0.0, 10.0),
                angular=random.uniform(0.0, 360.0),
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
