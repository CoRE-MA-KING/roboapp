import os
import platform
import tomllib
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


def get_dummy_port() -> tuple[Path, Path]:
    """
    開発・テスト用の仮想シリアルポートのパスのペアを返します。

    Returns:
        tuple[Path, Path]: (MCU側のポートパス, Bridge側のポートパス)

    Raises:
        NotImplementedError: Linux 以外の環境で実行された場合。
    """
    if platform.system() != "Linux":
        raise NotImplementedError("Dummy port feature is only supported on Linux.")

    base_dir = Path(os.getenv("XDG_RUNTIME_DIR", f"/run/user/{os.getuid()}"))
    mcu_port = base_dir / "roboapp_mcu"
    bridge_port = base_dir / "roboapp_bridge"

    return (mcu_port, bridge_port)


class GlobalConfig(BaseModel):
    websocket_port: int = Field(default=8080, description="WebSocket Port")


class UartConfig(BaseModel):
    device: str = Field(str(get_dummy_port()[1]), description="UARTポートのパス")

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
