from copy import deepcopy
from threading import Lock
from typing import Any

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
            )
        except serial.SerialException as err:
            print(err)
            self._serial = None

    def spin_once(self) -> None:
        """1回分のシリアル通信の受信と送信を実施する"""
        if not self._serial:
            self._open_serial_port()
            return

        try:
            buffer = self._serial.readline()
            if buffer:
                # print(f"read state: {buffer!r}")
                pass
        except Exception as err:
            print(err)
            if self._serial:
                self._serial.close()
            self._serial = None
            return

        try:
            str_data = buffer.decode("ascii")
        except UnicodeDecodeError as err:
            print(err)
            return

        if "\n" in str_data:
            try:
                str_data = str_data.strip()
                parts = str_data.split(",")
                if len(parts) >= 8:
                    new_state = RobotState(
                        state_id=RobotStateId(int(parts[0])),
                        pitch_deg=float(parts[1]) / 10.0,
                        yaw_deg=float(parts[2]) / 10,
                        left_disks=int(parts[3]),
                        right_disks=int(parts[4]),
                        video_id=int(parts[5]),
                        flags=RobotFlags(
                            is_red=bool((int(parts[6]) >> 3) & 0b00000001),
                            record_video=bool((int(parts[6]) >> 1) & 0b00000001),
                            ready_to_fire=bool((int(parts[6]) >> 0) & 0b00000001),
                        ),
                        reserved=int(parts[7]),
                    )
                    self._robot_state = new_state
            except ValueError as err:
                print(err)

        # 受信後すぐに送信処理を実施
        send_str = self._send_values.to_str()
        try:
            self._serial.write(send_str.encode())
            # print(f"sent data: {send_str.strip()}")
        except Exception as err:
            print(err)
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
            while True:
                # 1サイクル分のシリアル送受信
                self.spin_once()

                # ロボットの状態取得
                state = self.get_robot_state()
                # SHMに書き込み
                with state_lock:
                    shm.write_state(state)

                # SHMからコマンド読み込み
                with command_lock:
                    command = shm.read_command()
                # ドライバにセット
                self.set_send_values(command)

                # elapsed_time = time.time() - cycle_start_time
                # sleep_time = 0.01 - elapsed_time
                # if sleep_time > 0:
                #     time.sleep(sleep_time)
        except KeyboardInterrupt:
            pass
        finally:
            shm.close()
            self.close()
