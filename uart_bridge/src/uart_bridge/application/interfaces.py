from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, Self

from uart_bridge.domain.messages import RobotCommand, RobotState
from uart_bridge.domain.shared_memory import SharedRobotData


class ApplicationInterface(ABC):
    """Interface for the CoRE auto-pilot application."""

    @abstractmethod
    def spin(self) -> None:
        pass


class RoboappBridgeDriver(ABC):
    def pre_spin(self, shm_name: str, command_lock: Lock, state_lock: Lock) -> None:
        self.shm = SharedRobotData(name=shm_name)
        self.command_lock = command_lock
        self.state_lock = state_lock

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def spin(self, shm_name: str, command_lock: Lock, state_lock: Lock) -> None:
        pass


class RobotDriver(RoboappBridgeDriver):
    """Interface for communicating with robot"""

    @abstractmethod
    def get_robot_state(self) -> RobotState:
        pass

    @abstractmethod
    def set_send_values(self, value: RobotCommand) -> None:
        """Set values to be sent to the robot."""
        pass


class Transmitter(RoboappBridgeDriver):
    """Interface for communicating with robot"""

    @abstractmethod
    def publish(self, robot_state: RobotState) -> None:
        pass

    @abstractmethod
    def subscribe(self) -> RobotCommand:
        """Subscribe to receive commands or data."""
        pass
