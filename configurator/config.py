from typing import Literal

from pydantic import BaseModel, Field


class GlobalConfig(BaseModel):
    model_config = {"extra": "forbid"}

    zenoh_prefix: str | None = None
    websocket_port: int = Field(default=8080, gt=0)


class LidarDevice(BaseModel):
    model_config = {"extra": "forbid"}

    device: str
    backend: Literal["random", "rplidar"]
    x: int
    y: int
    min_degree: int = Field(default=0, ge=0, le=360)
    max_degree: int = Field(default=360, ge=0, le=360)
    max_distance: int = Field(default=1000, gt=0)


class LidarConfig(BaseModel):
    model_config = {"extra": "forbid"}

    devices: dict[str, LidarDevice] = {}


class CameraDevice(BaseModel):
    model_config = {"extra": "forbid"}

    device: str
    height: int = Field(default=720, gt=0)
    width: int = Field(default=1280, gt=0)


class CameraConfig(BaseModel):
    model_config = {"extra": "forbid"}

    devices: list[CameraDevice] = []
    zenoh: bool = False
    websocket: bool = False


class GUIConfig(BaseModel):
    model_config = {"extra": "forbid"}

    host: str = Field(default="localhost")


class UARTConfig(BaseModel):
    model_config = {"extra": "forbid"}

    port: str = Field(...)


class Config(BaseModel):
    model_config = {"extra": "forbid"}

    global_: GlobalConfig = Field(..., alias="global")
    lidar: LidarConfig = Field(...)
    camera: CameraConfig = Field(...)
    gui: GUIConfig = Field(...)
    uart: UARTConfig = Field(...)
