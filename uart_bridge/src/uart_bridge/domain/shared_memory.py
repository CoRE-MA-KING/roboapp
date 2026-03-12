import struct
from multiprocessing.shared_memory import SharedMemory

from uart_bridge.domain.messages import (
    RobotCommand,
    RobotFlags,
    RobotState,
    RobotStateId,
)


class SharedRobotData:
    """RobotStateとRobotCommandを共有メモリで読み書きするためのクラス"""

    # RobotState Struct:
    # state_id(i), pitch(d), yaw(d), left(i), right(i), video(i), flags(B), reserved(i)
    # i=4bytes, d=8bytes, B=1byte. Padding may apply.
    _STATE_FMT = "i d d i i i B i"
    _STATE_SIZE = struct.calcsize(_STATE_FMT)

    # RobotCommand Struct:
    # target_x(i), target_y(i), dist(i), linear(i), angular(i), dummy(i)
    _CMD_FMT = "i i i i i i"
    _CMD_SIZE = struct.calcsize(_CMD_FMT)

    def __init__(self, name: str | None = None, create: bool = False) -> None:
        self._total_size = self._STATE_SIZE + self._CMD_SIZE
        if create:
            self._shm = SharedMemory(name=name, create=True, size=self._total_size)
        else:
            self._shm = SharedMemory(name=name)

        self.name = self._shm.name

    def close(self) -> None:
        self._shm.close()

    def unlink(self) -> None:
        self._shm.unlink()

    def write_state(self, state: RobotState) -> None:
        """RobotStateを共有メモリに書き込む"""
        # フラグのパッキング (RobotFlags -> byte)
        # SerialRobotDriverの実装に合わせてビット配置
        # is_red: bit 3
        # record_video: bit 1
        # ready_to_fire: bit 0
        flags_byte = 0
        if state.flags.is_red:
            flags_byte |= 1 << 3
        if state.flags.record_video:
            flags_byte |= 1 << 1
        if state.flags.ready_to_fire:
            flags_byte |= 1 << 0

        data = struct.pack(
            self._STATE_FMT,
            state.state_id.value,
            state.pitch_deg,
            state.yaw_deg,
            state.left_disks,
            state.right_disks,
            state.video_id,
            flags_byte,
            state.reserved,
        )
        # 先頭からSTATE_SIZE分に書き込み
        if self._shm.buf is None:
            raise RuntimeError("共有メモリのバッファが取得できません")
        self._shm.buf[0 : self._STATE_SIZE] = data

    def read_state(self) -> RobotState:
        """RobotStateを共有メモリから読み込む"""

        if self._shm.buf is None:
            raise RuntimeError("共有メモリのバッファが取得できません")
        data = self._shm.buf[0 : self._STATE_SIZE]
        unpacked = struct.unpack(self._STATE_FMT, data)
        # unpacked: id, pitch, yaw, left, right, video, flags, reserved

        flags_byte = unpacked[6]
        flags = RobotFlags(
            is_red=bool(flags_byte & (1 << 3)),
            record_video=bool(flags_byte & (1 << 1)),
            ready_to_fire=bool(flags_byte & (1 << 0)),
        )

        # Enumの変換でエラーが出ないようにtry-exceptなどは必要に応じて
        try:
            state_id = RobotStateId(unpacked[0])
        except ValueError:
            state_id = RobotStateId.UNKNOWN

        return RobotState(
            state_id=state_id,
            pitch_deg=unpacked[1],
            yaw_deg=unpacked[2],
            left_disks=unpacked[3],
            right_disks=unpacked[4],
            video_id=unpacked[5],
            flags=flags,
            reserved=unpacked[7],
        )

    def write_command(self, command: RobotCommand) -> None:
        """RobotCommandを共有メモリに書き込む"""
        data = struct.pack(
            self._CMD_FMT,
            command.target_x,
            command.target_y,
            command.target_distance,
            command.force_linear,
            command.force_angular,
            command.dummy,
        )
        # STATEの直後に書き込み
        start = self._STATE_SIZE
        end = start + self._CMD_SIZE
        if self._shm.buf is None:
            raise RuntimeError("共有メモリのバッファが取得できません")
        self._shm.buf[start:end] = data

    def read_command(self) -> RobotCommand:
        """RobotCommandを共有メモリから読み込む"""
        start = self._STATE_SIZE
        end = start + self._CMD_SIZE
        if self._shm.buf is None:
            raise RuntimeError("共有メモリのバッファが取得できません")
        data = self._shm.buf[start:end]
        unpacked = struct.unpack(self._CMD_FMT, data)

        return RobotCommand(
            target_x=unpacked[0],
            target_y=unpacked[1],
            target_distance=unpacked[2],
            force_linear=unpacked[3],
            force_angular=unpacked[4],
            dummy=unpacked[5],
        )
