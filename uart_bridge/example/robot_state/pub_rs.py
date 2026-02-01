import argparse
import datetime
import random
import time
from typing import Literal

import zenoh

from uart_bridge.domain.messages import RobotStateId
from uart_bridge.domain.transmitter_messages import RobotStateMessage

key_expr = "robotstate"
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--hz", type=float, help="Publishing frequency in Hz")
    args = parser.parse_args()

    with zenoh.open(zenoh.Config()) as session:
        pub = session.declare_publisher(key_expr)

        state_ids = list(RobotStateId)
        colors: list[Literal["blue", "red"]] = ["blue", "red"]

        while True:
            msg = RobotStateMessage(
                state=random.choice(state_ids).value,
                color=random.choice(colors),
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
