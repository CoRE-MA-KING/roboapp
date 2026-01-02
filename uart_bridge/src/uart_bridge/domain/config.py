import os
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class GlobalConfig(BaseModel):
    zenoh_prefix: str = Field(default="", description="Zenoh Prefix")
    websocket_port: int = Field(default=8080, description="WebSocket Port")


class UartConfig(BaseModel):
    device: str = Field(..., description="UARTポートのパス")

    @field_validator("device", mode="after")
    @classmethod
    def validate_port(cls, v: str) -> str:
        # ここで加工
        real_path = Path(v).resolve()
        if not real_path.exists():
            raise ValueError(f"{v} is not a valid UART port!")
        return str(real_path)


class Config(BaseModel):
    global_: GlobalConfig = Field(default_factory=GlobalConfig, alias="global")
    uart: UartConfig | None = None


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


def load_and_parse_config(file_path: Path | str | None = None) -> Config:
    """設定ファイルを読み込み、パースする"""
    return Config.model_validate(load_config(file_path))
