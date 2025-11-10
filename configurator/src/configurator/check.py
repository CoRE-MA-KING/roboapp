import argparse
import os
import pprint
from pathlib import Path

import tomllib

from configurator.config import Config


def check(config_file: Path) -> None:
    with open(config_file, "rb") as f:
        c = Config.model_validate(tomllib.load(f))
        pprint.pprint(c)
        print("Configuration is valid.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config-file",
        default=Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
        / "roboapp"
        / "config.toml",
        type=Path,
        help="Path to the configuration file",
    )

    args = parser.parse_args()

    config_file = args.config_file

    check(config_file)
