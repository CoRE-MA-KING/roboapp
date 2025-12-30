from typing import Literal, Self

from pydantic import BaseModel, Field, model_validator

class GlobalConfig(BaseModel):
    model_config = {"extra": "forbid"}

    zenoh_prefix: str = Field(default="", description="Zenohのプレフィックス")
    websocket_port: int = Field(
        default=8080, gt=0, le=65535, description="WebSocketのポート番号"
    )


class LidarDevice(BaseModel):
    model_config = {"extra": "forbid"}

    device: str | None = Field(None, description="LiDARのデバイスパス")
    backend: Literal["random", "rplidar"] = Field(
        "random", description="LiDARのバックエンド"
    )
    x: int = Field(default=0, description="LiDARのX座標")
    y: int = Field(default=0, description="LiDARのY座標")
    rotate: int = Field(default=0, description="LiDARの取り付け角度")
    max_distance: int = Field(default=1000, gt=0, description="LiDARの最大距離")
    min_degree: int = Field(default=0, ge=0, le=360, description="LiDARの最小角度")
    max_degree: int = Field(default=360, ge=0, le=360, description="LiDARの最大角度")

    @model_validator(mode="after")
    def require_device_if_rplidar(self) -> Self:
        if self.backend == "rplidar" and self.device is None:
            raise ValueError("RPLIDAR backend requires a device path.")
        return self

class LidarConfig(BaseModel):
    model_config = {"extra": "forbid"}

    devices: dict[str, LidarDevice] = Field(..., description="LiDARデバイスの一覧")


class CameraDevice(BaseModel):
    model_config = {"extra": "forbid"}

    device: str = Field(..., description="カメラのデバイスパス")
    height: int = Field(default=720, gt=0, description="カメラ映像の高さ")
    width: int = Field(default=1280, gt=0, description="カメラ映像の幅")


class CameraConfig(BaseModel):
    model_config = {"extra": "forbid"}

    devices: list[CameraDevice] = Field(..., description="カメラデバイスの一覧")
    zenoh: bool = Field(default=False, description="Zenohの使用有無")
    websocket: bool = Field(default=False, description="WebSocketの使用有無")


class GUIConfig(BaseModel):
    model_config = {"extra": "forbid"}

    host: str = Field(default="localhost", description="GUIのホスト名")


class UARTConfig(BaseModel):
    model_config = {"extra": "forbid"}

    device: str = Field(..., description="UARTのデバイスパス")


class Config(BaseModel):
    model_config = {"extra": "forbid"}

    global_: GlobalConfig | None = Field(None, alias="global")
    lidar: LidarConfig | None = Field(None, alias="lidar")
    camera: CameraConfig | None = Field(None, alias="camera")
    gui: GUIConfig | None = Field(None, alias="gui")
    uart: UARTConfig | None = Field(None, alias="uart")
