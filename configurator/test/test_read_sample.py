from pathlib import Path

import pytest
import tomllib
from configurator.config import Config


@pytest.fixture
def get_resource_path() -> Path:
    return Path(__file__).parent / "resources/config_sample.toml"


def test_read_sample(get_resource_path):
    with open(get_resource_path, "rb") as f:
        Config.model_validate(tomllib.load(f))
