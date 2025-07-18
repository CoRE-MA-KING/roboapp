from abc import ABC, abstractmethod
from typing import Any, Self

from uart_bridge.domain.messages import RobotCommand, RobotState


class ApplicationInterface(ABC):
    """Interface for the CoRE auto-pilot application."""

    @abstractmethod
    def spin(self) -> None:
        pass


class RobotDriver(ABC):
    """Interface for communicating with robot"""

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    @abstractmethod
    def get_robot_state(self) -> RobotState:
        pass

    @abstractmethod
    def set_send_values(
        self, target_x: int, target_y: int, target_distance: int, dummy: int
    ) -> None:
        """Set values to be sent to the robot."""
        pass

    @abstractmethod
    def close(self) -> None:
        pass


class Transmitter(ABC):
    """Interface for communicating with robot"""

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> None:
        self.close()

    @abstractmethod
    def publish(self, robot_state: RobotState) -> None:
        pass

    @abstractmethod
    def subscribe(self) -> RobotCommand:
        """Subscribe to receive commands or data."""
        pass

    @abstractmethod
    def close(self) -> None:
        pass
