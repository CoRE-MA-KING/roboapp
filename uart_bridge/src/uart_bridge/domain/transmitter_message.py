from pydantic import BaseModel, Field


class LiDARMessage(BaseModel):
    linear: float = Field(description="壁の斥力")
    angular: float = Field(description="壁の角度（度単位）")
