from pydantic import BaseModel, Field


class CameraSwitchMessage(BaseModel):
    camera_id: int


class DamagePanelRecognition(BaseModel):
    """ダメージパネル認識結果"""

    target_x: int = 640
    target_y: int = 360
    target_distance: int = 0


class LiDARMessage(BaseModel):
    linear: float = Field(description="壁の斥力")
    angular: float = Field(description="壁の角度（度単位）")


class DisksMessage(BaseModel):
    left: int = Field(ge=0, description="左ディスク残量")
    right: int = Field(ge=0, description="右ディスク残量")


class FlapMessage(BaseModel):
    pitch: float = Field(description="ノズルのピッチ角度")
    yaw: float = Field(description="ノズルのヨー角度")
