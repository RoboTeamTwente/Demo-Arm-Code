
"""
Simple wrapper around the LeRobot SO-101 leader arm.

The leader reads joint positions for teleoperation; it does not command
motor movements on the follower arm.
"""

from lerobot.teleoperators.so_leader import SO101Leader, SO101LeaderConfig


class Leader:

    def __init__(
        self,
        port: str = "/dev/ttyACM0",
        id: str = "SKYNET",
    ) -> None:
        self.port = port
        self.id = id

        config = SO101LeaderConfig(
            port=self.port,
            id=self.id
        )

        self.leader = SO101Leader(config)

        # Connect automatically, like the Follower class
        self.connect()

    # ===== CONNECTION =====

    def connect(self, calibrate: bool = True) -> None:
        """Connect and verify leader calibration."""

        if self.leader.is_connected:
            return

        try:
            self.leader.connect(calibrate=calibrate)

            if not self.leader.calibration or not self.leader.is_calibrated:
                raise RuntimeError(
                    f"Leader '{self.id}' has missing or invalid calibration."
                )

        except Exception:
            if self.leader.is_connected:
                self.leader.disconnect()
            raise

    # ===== JOINT READING =====

    def get_action(self) -> dict[str, float]:
        """Return all joint positions for teleoperation."""

        if not self.leader.is_connected:
            raise RuntimeError("Leader is not connected.")

        return self.leader.get_action()

    def get_position(self, joint: str) -> float:
        """Return the position of one joint."""

        key = f"{joint}.pos"

        return float(self.get_action()[key])

    # ===== DISCONNECTION =====

    def disconnect(self) -> None:
        """Disconnect the leader arm."""

        if self.leader.is_connected:
            self.leader.disconnect()
