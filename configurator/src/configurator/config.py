from typing import Literal

from pydantic import BaseModel, Field


class GlobalConfig(BaseModel):
    model_config = {"extra": "forbid"}

    zenoh_prefix: str = Field(default="", description="Zenohのプレフィックス")
    websocket_port: int = Field(
        default=8080, gt=0, le=65535, description="WebSocketのポート番号"
    )


class LidarDevice(BaseModel):
    model_config = {"extra": "forbid"}

    device: str = Field(..., description="LiDARのデバイスパス")
    backend: Literal["random", "rplidar"] = Field(
        "random", description="LiDARのバックエンド"
    )
    x: int = Field(..., description="LiDARのX座標")
    y: int = Field(..., description="LiDARのY座標")
    min_degree: int = Field(default=0, ge=0, le=360, description="LiDARの最小角度")
    max_degree: int = Field(default=360, ge=0, le=360, description="LiDARの最大角度")
    max_distance: int = Field(default=1000, gt=0, description="LiDARの最大距離")


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
    # lidar: LidarConfig | None = Field(..., alias="lidar")
    camera: CameraConfig | None = Field(None, alias="camera")
    gui: GUIConfig | None = Field(None, alias="gui")
    uart: UARTConfig | None = Field(None, alias="uart")
