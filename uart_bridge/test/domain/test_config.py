from pathlib import Path

import pytest

from uart_bridge.domain.config import (
    load_and_parse_config,
)


@pytest.fixture
def get_resource_path() -> Path:
    return Path(__file__).parents[1] / "resources"


def test_read_empty_uart_config(get_resource_path: Path) -> None:
    config_file = get_resource_path / "empty.toml"

    config = load_and_parse_config(config_file)
    assert config.uart is None


def test_read_uart_config(get_resource_path: Path) -> None:
    config_file = get_resource_path / "uart_device.toml"

    c = load_and_parse_config(config_file).uart

    if c is None:
        pytest.fail("UART config should not be None")

    # 設定ファイル(uart_device.toml)に記述された "/tmp/roboapp_test_uart" がそのまま読み込まれることを確認
    assert c.device == "/tmp/roboapp_test_uart"
