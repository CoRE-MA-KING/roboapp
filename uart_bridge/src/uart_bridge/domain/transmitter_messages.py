from typing import Literal

from pydantic import BaseModel, Field

from uart_bridge.domain.messages import RobotStateId


class RobotStateMessage(BaseModel):
    state: int = Field(default=RobotStateId.UNKNOWN.value)
    color: Literal["blue", "red"] = Field(default="blue")


class CameraSwitchMessage(BaseModel):
    camera_id: int


class DamagePanelRecognition(BaseModel):
    """ダメージパネル認識結果"""

    target_x: int = 640
    target_y: int = 360
    target_distance: int = 0


class LiDARVectorMessage(BaseModel):
    linear: float = Field(description="壁の斥力")
    angular: float = Field(description="壁の角度（度単位）")


class LiDARRange(BaseModel):
    left: float = Field(ge=0, le=10_000, description="左LiDARデータの距離（mm単位）")
    rear_left: float = Field(
        ge=0, le=10_000, description="左後方LiDARデータの距離（mm単位）"
    )
    rear_right: float = Field(
        ge=0, le=10_000, description="右後方LiDARデータの距離（mm単位）"
    )
    right: float = Field(ge=0, le=10_000, description="右LiDARデータの距離（mm単位）")


class DisksMessage(BaseModel):
    left: int = Field(ge=0, description="左ディスク残量")
    right: int = Field(ge=0, description="右ディスク残量")


class FlapMessage(BaseModel):
    pitch: float = Field(description="ノズルのピッチ角度")
    yaw: float = Field(description="ノズルのヨー角度")
