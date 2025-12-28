import tomllib
from pathlib import Path

import pytest
from pydantic import ValidationError

from configurator.config import Config


@pytest.fixture
def get_resource_path() -> Path:
    return Path(__file__).parent / "resources"


def test_read_sample(get_resource_path: Path) -> None:
    config_file = get_resource_path / "config_sample.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.gui is not None
    assert config.gui.host == "localhost"
    assert config.uart is not None
    assert config.uart.device == "/dev/ttyUSB0"
    assert config.camera is not None
    assert not config.camera.zenoh
    assert not config.camera.websocket
    assert config.camera.devices[0].device == "/dev/video0"


def test_read_empty_toml(get_resource_path: Path) -> None:
    config_file = get_resource_path / "empty.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.global_ is None
    assert config.gui is None
    assert config.uart is None
    assert config.camera is None


def test_read_global_config_empty_toml(get_resource_path: Path) -> None:
    config_file = get_resource_path / "global_config_empty.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.global_ is None
    assert config.gui is None
    assert config.uart is None
    assert config.camera is None


def test_read_gui_config_empty_toml(get_resource_path: Path) -> None:
    config_file = get_resource_path / "gui_config_empty.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.global_ is None
    assert config.gui is None
    assert config.uart is None
    assert config.camera is None


def test_global_config_websocket_port(get_resource_path: Path) -> None:
    config_file = get_resource_path / "global_config_websocket_port.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.global_ is not None
    assert config.global_.websocket_port == 9090
    assert config.global_.zenoh_prefix == ""


def test_global_config_zenoh_prefix(get_resource_path: Path) -> None:
    config_file = get_resource_path / "global_config_zenoh_prefix.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.global_ is not None
    assert config.global_.zenoh_prefix == "roboapp"
    assert config.global_.websocket_port == 8080


def test_gui_config_host(get_resource_path: Path) -> None:
    config_file = get_resource_path / "gui_config_host.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.gui is not None
    assert config.gui.host == "foo.local"


def test_read_uart_config(get_resource_path: Path) -> None:
    config_file = get_resource_path / "uart_device.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.uart is not None
    assert config.uart.device == "/tmp/roboapp_test_uart"


def test_camera_config_no_dev(get_resource_path: Path) -> None:
    config_file = get_resource_path / "camera_config_no_dev.toml"
    with open(config_file, "rb") as f:
        with pytest.raises(ValidationError):
            Config.model_validate(tomllib.load(f))


def test_camera_config_device_width(get_resource_path: Path) -> None:
    config_file = get_resource_path / "camera_config_device_width.toml"
    with open(config_file, "rb") as f:
        config = Config.model_validate(tomllib.load(f))
    assert config.camera is not None
    assert len(config.camera.devices) == 1
    assert config.camera.devices[0].device == "/dev/video0"
    assert config.camera.devices[0].width == 640
    assert config.camera.devices[0].height == 720  # default
