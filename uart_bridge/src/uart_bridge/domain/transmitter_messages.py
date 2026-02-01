from typing import Literal

from pydantic import BaseModel, Field

from uart_bridge.domain.messages import RobotStateId


class RobotStateMessage(BaseModel):
    state: int = Field(default=RobotStateId.UNKNOWN.value)
    color: Literal["blue", "red"] = Field(default="blue")


class CameraSwitchMessage(BaseModel):
    camera_id: int


class Target(BaseModel):
    x: int = Field(default=640, ge=0, le=3840)
    y: int = Field(default=360, ge=0, le=2160)
    distance: int = 0


class DamagePanelRecognition(BaseModel):
    target: Target | None = Target()


class LiDARVectorMessage(BaseModel):
    linear: float = Field(description="壁の斥力")
    angular: float = Field(description="壁の角度（度単位）")


class LiDARRange(BaseModel):
    min_degree: float = Field(
        ge=0, le=360, description="LiDARデータの最小角度（度単位）"
    )
    max_degree: float = Field(
        ge=0, le=360, description="LiDARデータの最大角度（度単位）"
    )
    distance: float = Field(ge=0, le=10_000, description="LiDARデータの距離（mm単位）")


class LiDARRangeMessage(BaseModel):
    data: list[LiDARRange] = Field(description="LiDARデータ (角度: 距離)")


class DisksMessage(BaseModel):
    left: int = Field(ge=0, description="左ディスク残量")
    right: int = Field(ge=0, description="右ディスク残量")


class FlapMessage(BaseModel):
    pitch: float = Field(description="ノズルのピッチ角度")
    yaw: float = Field(description="ノズルのヨー角度")
