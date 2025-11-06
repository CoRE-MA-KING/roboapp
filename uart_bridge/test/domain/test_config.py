import pytest
from pydantic import ValidationError

from uart_bridge.domain.config import GlobalConfig, UartConfig


def test_uartconfig_empty() -> None:
    with pytest.raises(ValidationError):
        UartConfig()  # type: ignore


def test_globalconfig_empty() -> None:
    g = GlobalConfig()

    assert g.zenoh_prefix is None
