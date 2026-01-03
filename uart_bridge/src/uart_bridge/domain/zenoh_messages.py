from pydantic import BaseModel


class CameraSwitchMessage(BaseModel):
    camera_id: int
