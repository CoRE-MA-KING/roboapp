import time

import cv2
import numpy as np
import zenoh


class ImageReceiver:
    image: cv2.Mat | None = None

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())
        key_expr = "cam/jpg"
        self.subscriber = self.session.declare_subscriber(
            key_expr, self._on_image_received
        )

    def _on_image_received(self, sample: zenoh.Sample) -> None:
        print("Received image data")
        self.image = cv2.imdecode(
            np.frombuffer(bytes(sample.payload), np.uint8),
            flags=cv2.IMREAD_COLOR,  # type: ignore
        )

    def run(self) -> None:
        while True:
            if self.image is not None:
                #     # 受信した画像を表示
                cv2.imshow("Received Image", self.image)

            if cv2.waitKey(1) == ord("q"):  # qキーで終了
                break

            pass
            time.sleep(0.1)

    def __del__(self) -> None:
        self.session.close()  # type: ignore


if __name__ == "__main__":
    main = ImageReceiver()

    main.run()
