from collections.abc import Sequence
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import Manager
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
    ProcessPoolExecutorを使って並列化
    """

    def __init__(
        self,
        drivers: Sequence[RoboappBridgeDriver],
    ) -> None:
        self.drivers = drivers

    def spin(self) -> None:
        shm = SharedRobotData(create=True)
        try:
            with Manager() as manager:
                state_lock = manager.Lock()
                command_lock = manager.Lock()

                with ProcessPoolExecutor(max_workers=len(self.drivers)) as executor:
                    processes = [
                        executor.submit(
                            _run_driver, driver, shm.name, command_lock, state_lock
                        )
                        for driver in self.drivers
                    ]
                    try:
                        for process in processes:
                            process.result()
                    except KeyboardInterrupt:
                        print("Stopping application...")
                        executor.shutdown(wait=False, cancel_futures=True)
        finally:
            shm.close()
            shm.unlink()
