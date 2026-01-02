from copy import deepcopy
from threading import Lock, Thread
from time import sleep
from typing import Any, Optional

import serial

from uart_bridge.application.interfaces import RobotDriver
from uart_bridge.domain.messages import RobotCommand, RobotState, RobotStateId


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
        self._serial: Optional[serial.Serial] = None
        self._open_serial_port()

        # 初期ロボット状態（排他制御用ロック付き）
        self._state_lock = Lock()
        self._robot_state = RobotState()

        # 送信用の値とそのロック
        self._send_lock = Lock()
        self._send_values = RobotCommand()

        self._is_closed = False
        self._thread = Thread(target=self._update_robot_state, daemon=True)
        self._thread.start()

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

    def _update_robot_state(self) -> None:
        """10ms間隔でシリアル通信の受信と送信を実施する"""
        while not self._is_closed:
            if not self._serial:
                sleep(0.01)
                self._open_serial_port()
                continue

            try:
                buffer = self._serial.readline()
                print(f"read state: {buffer!r}")
            except Exception as err:
                print(err)
                if self._serial:
                    self._serial.close()
                self._serial = None
                continue

            try:
                str_data = buffer.decode("ascii")
            except UnicodeDecodeError as err:
                print(err)
                continue

            if "\n" in str_data:
                try:
                    str_data = str_data.strip()
                    parts = str_data.split(",")
                    if len(parts) < 8:
                        # 必要な項目が揃っていなければスキップ
                        continue
                    new_state = RobotState(
                        state_id=RobotStateId(int(parts[0])),
                        pitch_deg=float(parts[1]) / 10.0,
                        muzzle_velocity=float(parts[2]) / 1000,
                        reloaded_left_disks=int(parts[3]),
                        reloaded_right_disks=int(parts[4]),
                        video_id=int(parts[5]),
                        target_panel=bool((int(parts[6]) >> 3) & 0b00000001),
                        auto_aim=bool((int(parts[6]) >> 2) & 0b00000001),
                        record_video=bool((int(parts[6]) >> 1) & 0b00000001),
                        ready_to_fire=bool((int(parts[6]) >> 0) & 0b00000001),
                        reserved=int(parts[7]),
                    )
                    with self._state_lock:
                        self._robot_state = new_state
                except ValueError as err:
                    print(err)
                    continue

            # 受信後すぐに送信処理を実施（排他制御）
            with self._send_lock:
                send_str = self._send_values.to_str()
            try:
                self._serial.write(send_str.encode())
                print(f"sent data: {send_str.strip()}")
            except Exception as err:
                print(err)
                if self._serial:
                    self._serial.close()
                self._serial = None
                continue

            sleep(0.01)  # 10ms間隔

    def set_send_values(self, value: RobotCommand) -> None:
        """マイコンへ送信する整数値を更新する"""
        with self._send_lock:
            self._send_values = value

    def get_robot_state(self) -> RobotState:
        """最新のロボットの状態を返す"""
        with self._state_lock:
            return deepcopy(self._robot_state)

    def close(self) -> None:
        print("closing robot driver")
        self._is_closed = True
        self._thread.join()
        if self._serial:
            self._serial.close()
