import random

import zenoh


class StateReceiver:
    key_expr = "robot/state"

    def __init__(self) -> None:
        self.session = zenoh.open(zenoh.Config())

    def run(self) -> None:
        self.session.declare_publisher(f"{self.key_expr}/state_id").put(f"{1}")
        self.session.declare_publisher(f"{self.key_expr}/pitch_deg").put(
            f"{random.uniform(-30.0, 30.0)}"
        )
        self.session.declare_publisher(f"{self.key_expr}/muzzle_velocity").put(
            f"{random.uniform(0.0, 100.0)}"
        )
        self.session.declare_publisher(f"{self.key_expr}/reloaded_left_disks").put(
            f"{random.randint(0, 10)}"
        )
        self.session.declare_publisher(f"{self.key_expr}/reloaded_right_disks").put(
            f"{random.randint(0, 10)}"
        )
        self.session.declare_publisher(f"{self.key_expr}/video_id").put(
            f"{random.randint(0, 10)}"
        )
        self.session.declare_publisher(f"{self.key_expr}/target_panel").put(
            f"{bool(random.randint(0, 1))}"
        )
        self.session.declare_publisher(f"{self.key_expr}/auto_aim").put(
            f"{bool(random.randint(0, 1))}"
        )
        self.session.declare_publisher(f"{self.key_expr}/record_video").put(
            f"{bool(random.randint(0, 1))}"
        )
        self.session.declare_publisher(f"{self.key_expr}/ready_to_fire").put(
            f"{bool(random.randint(0, 1))}"
        )
        self.session.declare_publisher(f"{self.key_expr}/reserved").put(f"{0}")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.session.close()


if __name__ == "__main__":
    with StateReceiver() as main:
        main.run()
