from enum import Enum, auto
from typing import Optional, Tuple

from pydantic import BaseModel


class Command(Enum):
    NONE = auto()
    QUIT = auto()


class Detection(BaseModel):
    xyxy: Tuple[float]
    score: float
    class_id: int


class TargetState(BaseModel):
    track_id: int
    detection: Detection
    position: Optional[Tuple[float]]


class RobotStateId(Enum):
    """ロボットの状態ID"""

    UNKNOWN = 0
    INITIALIZING = 1
    NORMAL = 2
    DEFEATED = 3
    EMERGENCY = 4
    COMM_ERROR = 5


class RobotState(BaseModel):
    """マイコンと通信して取得したロボットの状態"""

    state_id: RobotStateId = RobotStateId.UNKNOWN
    pitch_deg: float = 0.0  # deg (マイコンからの受信時には10倍した整数)
    muzzle_velocity: float = 0.0  # mm/s (マイコンからの受信時には1000倍した整数)
    reloaded_left_disks: int = 0  # 枚
    reloaded_right_disks: int = 0  # 枚
    video_id: int = 0  # 表示するカメラ 0 RealSense, 1 前方, 2 後方
    # 複数のフラグを1バイトでまとめて(bit: [2]自動照準 [1]録画 [0]射出可否)
    # flags: int
    target_panel: bool = False  # True:青を照準、False:赤を照準
    auto_aim: bool = False
    record_video: bool = False
    ready_to_fire: bool = False
    reserved: int = 0  # 未使用


class DamagePanelRecognition(BaseModel):
    """ダメージパネル認識結果"""

    target_x: int = 640
    target_y: int = 360
    target_distance: int = 0


class RobotCommand(BaseModel):
    """ロボットに送信するコマンド"""

    target_x: int = 640
    target_y: int = 360
    target_distance: int = 0
    dummy: int = 0  # 未使用
