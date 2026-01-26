from enum import Enum

from pydantic import BaseModel, Field


class RobotStateId(Enum):
    """ロボットの状態ID"""

    UNKNOWN = 0
    INITIALIZING = 1
    NORMAL = 2
    DEFEATED = 3
    EMERGENCY = 4
    COMM_ERROR = 5


class RobotFlags(BaseModel):
    # 7
    # 6
    # 5
    # 4
    # 3
    is_red: bool = Field(default=False, description="3: 赤色を照準/青を照準")
    # 2
    # 1
    record_video: bool = Field(default=False, description="1: 録画する/しない")
    # 0
    ready_to_fire: bool = Field(default=False, description="0: 射出可/否")


class RobotState(BaseModel):
    """マイコンと通信して取得したロボットの状態"""

    state_id: RobotStateId = RobotStateId.UNKNOWN
    pitch_deg: float = Field(default=0.0, description="フラップのピッチ角度")
    yaw_deg: float = Field(default=0.0, description="フラップのヨー角度")
    left_disks: int = 0  # 枚
    right_disks: int = 0  # 枚
    video_id: int = 0  # 表示するカメラ 0 RealSense, 1 前方, 2 後方
    # 複数のフラグを1バイトでまとめて(bit: [2]自動照準 [1]録画 [0]射出可否)
    flags: RobotFlags = Field(
        default_factory=RobotFlags, description="ロボットの各種フラグ"
    )
    reserved: int = 0  # 未使用


class RobotCommand(BaseModel):
    """ロボットに送信するコマンド"""

    target_x: int = 640
    target_y: int = 360
    target_distance: int = 0
    force_linear: int = 0
    force_angular: int = 0
    dummy: int = 0  # 未使用

    def to_str(self) -> str:
        values = (
            self.target_x,
            self.target_y,
            self.target_distance,
            self.force_linear,
            self.force_angular,
            self.dummy,
        )
        return ",".join(map(str, values)) + "\n"
