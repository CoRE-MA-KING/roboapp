from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

from uart_bridge.application.interfaces import (
    ApplicationInterface,
    RoboappBridgeDriver,
)
from uart_bridge.domain.shared_memory import SharedRobotData


def _run_driver(
    robot_driver: RoboappBridgeDriver,
    shm_name: str,
    command_lock: Lock,
    state_lock: Lock,
) -> None:
    robot_driver.spin(shm_name, command_lock, state_lock)


class Application(ApplicationInterface):
    """Implementation for the CoRE auto-pilot application.
    ThreadPoolExecutorを使って並列化
    """

    def __init__(
        self,
        drivers: Sequence[RoboappBridgeDriver],
    ) -> None:
        self.drivers = drivers

    def spin(self) -> None:
        shm = SharedRobotData(create=True)
        try:
            state_lock = Lock()
            command_lock = Lock()

            with ThreadPoolExecutor(max_workers=len(self.drivers)) as executor:
                futures = [
                    executor.submit(
                        _run_driver, driver, shm.name, command_lock, state_lock
                    )
                    for driver in self.drivers
                ]
                try:
                    import time

                    while any(f.running() for f in futures):
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    print("\nStopping application...")
                    for driver in self.drivers:
                        driver.stop()
                    executor.shutdown(wait=True)
        finally:
            shm.close()
            shm.unlink()
