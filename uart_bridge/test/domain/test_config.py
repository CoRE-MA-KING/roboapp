from pathlib import Path

import pytest
from pydantic import ValidationError

from uart_bridge.domain.config import (
    GlobalConfig,
    UartConfig,
    get_global_config,
    get_uart_config,
)


@pytest.fixture
def get_resource_path():
    return Path(__file__).parents[1] / "resources"


def test_uartconfig_empty() -> None:
    with pytest.raises(ValidationError):
        UartConfig()  # type: ignore


def test_globalconfig_empty() -> None:
    g = GlobalConfig()

    assert g.zenoh_prefix is None


def test_read_empty_global_config(get_resource_path) -> None:
    config_file = get_resource_path / "empty.toml"
    c = get_global_config(config_file)

    assert c.zenoh_prefix is None
    assert c.websocket_port == 8080


def test_read_empty_uart_config(get_resource_path) -> None:
    config_file = get_resource_path / "empty.toml"

    with pytest.raises(ValidationError):
        get_uart_config(config_file)


def test_read_uart_config_with_not_exist(get_resource_path) -> None:
    config_file = get_resource_path / "read_sym.toml"

    with pytest.raises(ValidationError):
        get_uart_config(config_file)


def test_read_uart_config(get_resource_path) -> None:
    p = Path("/tmp/roboapp_test_uart")

    if not p.exists():
        p.symlink_to("/dev/tty0")

    config_file = get_resource_path / "read_sym.toml"

    # with pytest.raises(ValidationError):
    c = get_uart_config(config_file)

    assert c.port == "/dev/tty0"

    if p.exists():
        p.unlink()
