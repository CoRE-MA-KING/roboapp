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
