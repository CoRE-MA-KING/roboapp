from abc import ABC, abstractmethod
from typing import Any, Self

from uart_bridge.domain.messages import RobotState


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
    def close(self) -> None:
        pass
