import argparse

import zenoh

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Zenoh Image Receiver")

    parser.add_argument("--prefix", default="", type=str)
    parser.add_argument("value", default="", nargs="?")

    args = parser.parse_args()

    print(args)

    session = zenoh.open(zenoh.Config())
    if args.prefix:
        key_expr = f"{args.prefix}/cam/switch"
    else:
        key_expr = "cam/switch"
    publisher = session.declare_publisher(
        key_expr,
    )

    publisher.put(f"{args.value}")
