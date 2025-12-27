from pathlib import Path

import pytest
from pydantic import ValidationError

from uart_bridge.domain.config import (
    load_and_parse_config,
)


@pytest.fixture
def get_resource_path() -> Path:
    return Path(__file__).parents[1] / "resources"


def test_read_empty_global_config(get_resource_path: Path) -> None:
    config_file = get_resource_path / "empty.toml"
    c = load_and_parse_config(config_file).global_

    assert c.zenoh_prefix is None
    assert c.websocket_port == 8080


def test_read_empty_uart_config(get_resource_path: Path) -> None:
    config_file = get_resource_path / "empty.toml"

    config = load_and_parse_config(config_file)
    assert config.uart is None


def test_global_config_websocket_port(get_resource_path: Path) -> None:
    config_file = get_resource_path / "global_config_websocket_port.toml"

    c = load_and_parse_config(config_file).global_

    assert c.zenoh_prefix is None
    assert c.websocket_port == 9090


def test_global_config_zenoh_prefix(get_resource_path: Path) -> None:
    config_file = get_resource_path / "global_config_zenoh_prefix.toml"

    c = load_and_parse_config(config_file).global_

    assert c.zenoh_prefix == "roboapp"
    assert c.websocket_port == 8080


def test_read_uart_config_with_not_exist(get_resource_path: Path) -> None:
    config_file = get_resource_path / "uart_device.toml"

    with pytest.raises(ValidationError):
        load_and_parse_config(config_file)


def test_read_uart_config(get_resource_path: Path) -> None:
    p = Path("/tmp/roboapp_test_uart")

    if not p.exists():
        p.symlink_to("/dev/tty0")

    config_file = get_resource_path / "uart_device.toml"

    c = load_and_parse_config(config_file).uart

    if c is None:
        pytest.fail("UART config should not be None")

    assert c.device == "/dev/tty0"

    if p.exists():
        p.unlink()
