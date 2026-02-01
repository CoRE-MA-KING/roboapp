import datetime
import time
from abc import ABC, abstractmethod

from pydantic import BaseModel

from uart_bridge.infra.zenoh_transmitter import create_zenoh_session


class ExamplePub(ABC):
    def __init__(self, key: str, hz: float | None) -> None:
        if hz and hz <= 0:
            raise ValueError("hz must be a non-negative number")

        self.session = create_zenoh_session()
        self.publisher = self.session.declare_publisher(key)
        self.hz = hz

    def run(self) -> None:
        try:
            while True:
                msg = self.create_message()

                print(
                    f"[{datetime.datetime.now().strftime('%H:%M:%S.%f')[:-3]}] Publishing : {self.publisher.key_expr}: {msg}"
                )

                self.publisher.put(msg.model_dump_json())
                if self.hz is None:
                    break
                elif self.hz:
                    time.sleep(1.0 / self.hz)
                else:
                    print(
                        f"Error: hz must be a positive number, but got {self.hz}. Exiting."
                    )
                    break
        except KeyboardInterrupt:
            pass
        finally:
            self.session.close()  # type: ignore

    @abstractmethod
    def create_message(self) -> BaseModel:
        pass
