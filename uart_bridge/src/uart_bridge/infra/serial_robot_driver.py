import logging
from collections.abc import Sequence
from copy import deepcopy
from threading import Lock
from typing import Any

import pydantic
import serial

from uart_bridge.application.interfaces import RobotDriver
from uart_bridge.domain.messages import (
    RobotCommand,
    RobotFlags,
    RobotState,
    RobotStateId,
)
from uart_bridge.domain.shared_memory import SharedRobotData


class SerialRobotDriver(RobotDriver):
    """マイコンと通信しロボットを制御するクラス

    Args:
        port: シリアルポートのデバイス
        baudrate: ボーレート
        timeout: readのタイムアウト[秒]
    """

    def __init__(
        self,
        port: str,
        baudrate: int = 115200,
        parity: Any = serial.PARITY_NONE,
        stopbits: Any = serial.STOPBITS_ONE,
        timeout: float = 0.01,  # 10ms timeout
    ) -> None:
        super().__init__()
        self._port = port
        self._baudrate = baudrate
        self._parity = parity
        self._stopbits = stopbits
        self._timeout = timeout
        self._serial: serial.Serial | None = None

        # 初期ロボット状態
        self._robot_state = RobotState()

        # 送信用の値
        self._send_values = RobotCommand()

    def _open_serial_port(self) -> None:
        """シリアルポートを開く"""
        try:
            self._serial = serial.Serial(
                port=self._port,
                baudrate=self._baudrate,
                stopbits=self._stopbits,
                parity=self._parity,
                timeout=self._timeout,
                write_timeout=0,
            )
        except serial.SerialException as err:
            logging.error("Failed to open serial port: %s", err)
            self._serial = None

    def raw_to_RobotState(self, data: Sequence[str]) -> RobotState:
        try:
            state_id = RobotStateId(int(data[0]))
        except (ValueError, IndexError):
            logging.warning(
                "Invalid state_id value received. Fallback to UNKNOWN.",
            )
            state_id = RobotStateId.UNKNOWN
        flags_val = int(data[6])

        new_state = RobotState(
            state_id=state_id,
            pitch_deg=float(data[1]) / 10.0,
            yaw_deg=float(data[2]) / 10.0,
            left_disks=int(data[3]),
            right_disks=int(data[4]),
            video_id=int(data[5]),
            flags=RobotFlags(
                is_red=bool((flags_val >> 3) & 0b00000001),
                record_video=bool((flags_val >> 1) & 0b00000001),
                ready_to_fire=bool((flags_val >> 0) & 0b00000001),
            ),
            reserved=int(data[7]),
        )
        return new_state

    def RobotCommand_to_raw(self, data: RobotCommand) -> str:
        values = (
            data.target_x,
            data.target_y,
            data.target_distance,
            data.force_linear,
            data.force_angular,
            data.dummy,
        )
        return ",".join(map(str, values)) + "\n"

    def spin_once(self) -> None:
        """1回分のシリアル通信の受信と送信を実施する"""
        if not self._serial:
            self._open_serial_port()
            return

        try:
            # 1. 最低1行読み込む（タイムアウトまで待機）
            line = self._serial.readline()

            # 2. バッファに溜まっている残りのデータを全て読み込み、最新の行に更新する
            # これにより処理が遅れた際のラグを防止する
            remaining_data = self._serial.read_all()
            if remaining_data:
                # 最後の改行の位置を探す
                last_newline_idx = remaining_data.rfind(b"\n")
                if last_newline_idx != -1:
                    # 最後の改行以前のデータを分割し、末尾（最新の完全な行）を取得
                    lines = remaining_data[:last_newline_idx].split(b"\n")
                    if lines:
                        line = lines[-1]

            if line:
                str_data = line.decode("ascii", errors="ignore").strip()
                parts = str_data.split(",")
                if len(parts) >= 8:
                    try:
                        self._robot_state = self.raw_to_RobotState(parts)
                    except (pydantic.ValidationError, ValueError, IndexError) as e:
                        logging.error(
                            f"Failed to parse or validate RobotState from serial: {e}"
                        )
        except Exception as err:
            logging.error("Error reading from serial port: %s", err)
            if self._serial:
                self._serial.close()
            self._serial = None
            return

        # 受信後すぐに送信処理を実施
        send_str = self.RobotCommand_to_raw(self._send_values)
        try:
            self._serial.write(send_str.encode())
        except serial.SerialTimeoutException:
            pass
        except Exception as err:
            logging.error("Error writing to serial port: %s", err)
            if self._serial:
                self._serial.close()
            self._serial = None

    def set_send_values(self, value: RobotCommand) -> None:
        """マイコンへ送信する整数値を更新する"""
        self._send_values = value

    def get_robot_state(self) -> RobotState:
        """最新のロボットの状態を返す"""
        return deepcopy(self._robot_state)

    def close(self) -> None:
        print("closing robot driver")
        if self._serial:
            self._serial.close()

    def spin(self, shm_name: str, command_lock: Lock, state_lock: Lock) -> None:
        self._open_serial_port()

        shm = SharedRobotData(name=shm_name)

        try:
            while self._running:
                self.spin_once()

                state = self.get_robot_state()
                with state_lock:
                    # print(f"Send:\t{state}",end="\t")
                    shm.write_state(state)

                try:
                    with command_lock:
                        command = shm.read_command()
                        # print(f"Receive:\t{command}")
                    self.set_send_values(command)
                except pydantic.ValidationError as e:
                    logging.error(f"Failed to read command from shared memory: {e}")
                    continue

        except KeyboardInterrupt:
            pass
        finally:
            shm.close()
            self.close()
