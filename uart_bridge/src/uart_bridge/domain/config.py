import os
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class GlobalConfig(BaseModel):
    zenoh_prefix: str | None = Field(default=None, description="Zenoh Prefix")
    websocket_port: int | None = Field(default=8080, description="WebSocket Port")


class UartConfig(BaseModel):
    port: str = Field(..., description="UARTポートのパス")

    @field_validator("port", mode="after")
    @classmethod
    def validate_port(cls, v: str) -> str:
        # ここで加工
        real_path = Path(v).resolve()
        if not real_path.exists():
            raise ValueError(f"{v} is not a valid UART port!")
        return str(real_path)


def load_config(file_path: Path | str | None = None) -> dict[str, Any]:
    """設定ファイルを読み込む"""

    file = (
        Path(file_path)
        if file_path
        else (
            Path(os.getenv("XDG_CONFIG_HOME", Path.home() / ".config"))
            / "roboapp/config.toml"
        )
    )

    if not file.exists():
        raise FileNotFoundError(f"設定ファイルが見つかりません: {file}")

    with open(file, mode="rb") as f:
        return tomllib.load(f)


def get_global_config(file_path: Path | str | None = None) -> GlobalConfig:
    """Global設定を取得する"""
    return GlobalConfig.model_validate(load_config(file_path).get("global", {}))


def get_uart_config(file_path: Path | str | None = None) -> UartConfig:
    """UART設定を取得する"""
    return UartConfig.model_validate(load_config(file_path).get("uart", {}))
