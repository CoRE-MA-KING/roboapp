from uart_bridge.domain.messages import (
    RobotCommand,
    RobotFlags,
    RobotState,
    RobotStateId,
)
from uart_bridge.domain.shared_memory import SharedRobotData


def test_shared_memory_read_write() -> None:
    shm_name = "test_shm_read_write"

    # Setup
    try:
        shm = SharedRobotData(name=shm_name, create=True)
    except Exception:
        # In case previous test failed without unlink, try to connect and unlink
        try:
            temp_shm = SharedRobotData(name=shm_name, create=False)
            temp_shm.unlink()
        except Exception:
            pass
        shm = SharedRobotData(name=shm_name, create=True)

    try:
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

        shm.write_state(original_state)
        read_state = shm.read_state()

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

        shm.write_command(original_command)
        read_command = shm.read_command()

        assert read_command.target_x == original_command.target_x
        assert read_command.target_y == original_command.target_y
        assert read_command.target_distance == original_command.target_distance
        assert read_command.force_linear == original_command.force_linear
        assert read_command.force_angular == original_command.force_angular
        assert read_command.dummy == original_command.dummy

    finally:
        shm.close()
        shm.unlink()
