import argparse
import os
import pprint
import tomllib
from pathlib import Path

from configurator.config import Config


def get_default_config_path() -> Path:
    return (
        Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
        / "roboapp"
        / "config.toml"
    )


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
        default=get_default_config_path(),
        type=Path,
        help="Path to the configuration file",
    )

    args = parser.parse_args()

    config_file = args.config_file

    check(config_file)
