from unittest.mock import MagicMock, patch

import pytest

from uart_bridge.domain.messages import RobotStateId
from uart_bridge.infra.serial_robot_driver import SerialRobotDriver


def test_raw_to_RobotState_invalid_enum() -> None:
    driver = SerialRobotDriver(port="dummy")
    # 99 is invalid for RobotStateId -> Fallback to UNKNOWN
    state = driver.raw_to_RobotState(["99", "100", "200", "5", "5", "1", "0", "0"])
    assert state.state_id == RobotStateId.UNKNOWN


def test_raw_to_RobotState_invalid_int() -> None:
    driver = SerialRobotDriver(port="dummy")
    # "abc" is not an int -> ValueError
    with pytest.raises(ValueError):
        driver.raw_to_RobotState(["2", "100", "200", "abc", "5", "1", "0", "0"])


@patch("serial.Serial")
def test_spin_once_parsing_error_does_not_reset_port(
    mock_serial_class: MagicMock,
) -> None:
    mock_serial = MagicMock()
    mock_serial_class.return_value = mock_serial

    driver = SerialRobotDriver(port="dummy")
    driver._open_serial_port()

    # Simulate invalid data that causes ValueError in raw_to_RobotState
    # "abc" for pitch (index 1) causes float("abc") -> ValueError
    mock_serial.readline.return_value = b"2,abc,200,5,5,1,0,0\\n"
    mock_serial.read_all.return_value = b""

    # This should be caught and logged, NOT closing the port
    driver.spin_once()

    assert driver._serial is not None  # It was NOT reset
