from collections.abc import Generator

import pytest

from uart_bridge.domain.messages import (
    RobotCommand,
    RobotFlags,
    RobotState,
    RobotStateId,
)
from uart_bridge.domain.shared_memory import SharedRobotData


@pytest.fixture
def shared_robot_data() -> Generator[SharedRobotData, None, None]:
    shm_name = "test_shm_read_write"

    # 前回の実行で残った可能性のある共有メモリをクリーンアップ
    try:
        temp_shm = SharedRobotData(name=shm_name, create=False)
        temp_shm.unlink()
    except FileNotFoundError:
        pass  # 存在しない場合は問題ない

    # Setup
    shm = SharedRobotData(name=shm_name, create=True)

    yield shm

    # Teardown
    shm.close()
    shm.unlink()


def test_shared_memory_read_write(shared_robot_data: SharedRobotData) -> None:
    # Test RobotState
    original_state = RobotState(
        state_id=RobotStateId.NORMAL,
        pitch_deg=12.5,
        yaw_deg=5.0,  # Range 0-100
        left_disks=1,
        right_disks=2,
        video_id=0,
        flags=RobotFlags(is_red=True, record_video=False, ready_to_fire=True),
        reserved=99,
    )

    shared_robot_data.write_state(original_state)
    read_state = shared_robot_data.read_state()

    assert read_state.state_id == original_state.state_id
    # Floating point comparison with epsilon
    assert abs(read_state.pitch_deg - original_state.pitch_deg) < 1e-6
    assert abs(read_state.yaw_deg - original_state.yaw_deg) < 1e-6
    assert read_state.left_disks == original_state.left_disks
    assert read_state.right_disks == original_state.right_disks
    assert read_state.video_id == original_state.video_id
    assert read_state.flags.is_red == original_state.flags.is_red
    assert read_state.flags.record_video == original_state.flags.record_video
    assert read_state.flags.ready_to_fire == original_state.flags.ready_to_fire
    assert read_state.reserved == original_state.reserved

    # Test RobotCommand
    original_command = RobotCommand(
        target_x=100,
        target_y=200,
        target_distance=50,
        force_linear=10,
        force_angular=5,
        dummy=999,
    )

    shared_robot_data.write_command(original_command)
    read_command = shared_robot_data.read_command()

    assert read_command.target_x == original_command.target_x
    assert read_command.target_y == original_command.target_y
    assert read_command.target_distance == original_command.target_distance
    assert read_command.force_linear == original_command.force_linear
    assert read_command.force_angular == original_command.force_angular
    assert read_command.dummy == original_command.dummy
