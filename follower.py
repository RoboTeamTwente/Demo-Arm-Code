
import time

from lerobot.robots.so_follower import (
    SO101Follower,
    SO101FollowerConfig,
)

# Valid joint names and their calibrated position range.
# Arm joints use -100..100, the gripper uses 0..100.
JOINT_LIMITS = {
    "shoulder_pan": (-100.0, 100.0),
    "shoulder_lift": (-100.0, 100.0),
    "elbow_flex": (-100.0, 100.0),
    "wrist_flex": (-100.0, 100.0),
    "wrist_roll": (-100.0, 100.0),
    "gripper": (0.0, 100.0),
}


class Follower:

    # ===== INITIALIZATION =====

    def __init__(
        self,
        port: str = "/dev/ttyACM0",
        id: str = "T300",
    ) -> None:

        self.port = port
        self.id = id

        # Configure motors and PS3 Eye camera
        
        config = SO101FollowerConfig(
            port=self.port,
            id=self.id,
            cameras={},
        )


        self.follower = SO101Follower(config)

        try:
            self.follower.connect()

            if not self.follower.is_calibrated:
                raise RuntimeError(
                    f"Robot '{self.id}' is not calibrated. "
                    "Calibrate it before moving."
                )

            # Store current joint positions
            observation = self.follower.get_observation()

            self.__shoulder_pan = float(
                observation["shoulder_pan.pos"]
            )
            self.__shoulder_lift = float(
                observation["shoulder_lift.pos"]
            )
            self.__elbow_flex = float(
                observation["elbow_flex.pos"]
            )
            self.__wrist_flex = float(
                observation["wrist_flex.pos"]
            )
            self.__wrist_roll = float(
                observation["wrist_roll.pos"]
            )
            self.__gripper = float(
                observation["gripper.pos"]
            )

        except Exception:
            if self.follower.is_connected:
                self.follower.disconnect()
            raise

    # ===== INPUT HELPERS =====

    @staticmethod
    def _is_valid_joint(joint: str) -> bool:
        """Return True if the joint name is known."""
        return joint in JOINT_LIMITS

    @staticmethod
    def _clamp_position(joint: str, pos: float) -> float:
        """Keep a position inside its joint range."""
        low, high = JOINT_LIMITS[joint]
        return max(low, min(high, float(pos)))

    # ===== MOVEMENT =====

    def slower_move(
        self,
        joint: str,
        pos: float,
        step: float = 1.0,
        delay: float = 0.02,
    ) -> bool:
        """Gradually move one joint to a target position."""

        if not self._is_valid_joint(joint):
            print("Invalid joint:", joint)
            return False

        if step <= 0 or delay < 0:
            raise ValueError(
                "Step must be positive and delay non-negative."
            )

        pos = self._clamp_position(joint, pos)

        match joint:
            case "shoulder_pan":
                prev_pos = self.__shoulder_pan
            case "shoulder_lift":
                prev_pos = self.__shoulder_lift
            case "elbow_flex":
                prev_pos = self.__elbow_flex
            case "wrist_flex":
                prev_pos = self.__wrist_flex
            case "wrist_roll":
                prev_pos = self.__wrist_roll
            case "gripper":
                prev_pos = self.__gripper

        # Move gradually toward the target
        while prev_pos != pos:

            if abs(pos - prev_pos) <= step:
                prev_pos = pos
            elif prev_pos < pos:
                prev_pos = min(prev_pos + step, pos)
            else:
                prev_pos = max(prev_pos - step, pos)

            self.follower.send_action({
                f"{joint}.pos": prev_pos
            })

            time.sleep(delay)

        # Update stored joint position
        match joint:
            case "shoulder_pan":
                self.__shoulder_pan = pos
            case "shoulder_lift":
                self.__shoulder_lift = pos
            case "elbow_flex":
                self.__elbow_flex = pos
            case "wrist_flex":
                self.__wrist_flex = pos
            case "wrist_roll":
                self.__wrist_roll = pos
            case "gripper":
                self.__gripper = pos

        return True

    # ===== ARM ANIMATIONS =====

    def reset_arm(self) -> None:
        """Move the arm to its predefined reset position."""

        targets = {
            "shoulder_lift": -100.0,
            "elbow_flex": 100.0,
            "wrist_flex": -100.0,
            "wrist_roll": 0.0,
            "gripper": 10.0,
            "shoulder_pan": 0.0,
        }

        for joint, position in targets.items():
            self.slower_move(joint, position)

    def wave(
        self,
        repeats: int = 3,
        amplitude: float = 20,
        delay: float = 0.3,
    ) -> None:
        """Wave the wrist from side to side."""

        joint = "wrist_flex"

        start = self.__wrist_flex

        left = start - amplitude
        right = start + amplitude

        try:
            for _ in range(repeats):

                self.slower_move(joint, left)
                time.sleep(delay)

                self.slower_move(joint, right)
                time.sleep(delay)

        finally:
            self.slower_move(joint, start)


    # ===== CONNECTION =====

    def disconnect(self) -> None:
        """Disconnect the arm and camera."""

        if self.follower.is_connected:
            self.follower.disconnect()
