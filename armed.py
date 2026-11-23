
"""Main program for the SO-101 robotic arm."""

import cv2
import threading

from follower import Follower
from camera import Camera


# ===== ARM SETTINGS =====

FOLLOWER_PORT = "/dev/ttyACM0"
FOLLOWER_NAME = "T300"

# ===== CAMERA SETTINGS =====

CAMERA_INDEX = 2


def main() -> None:

    arm = None
    camera = Camera(index=CAMERA_INDEX)
    movement = None
    movement_errors = []

    try:
        # Initialize camera
        camera.connect()

        # Initialize robotic arm
        arm = Follower(
            port=FOLLOWER_PORT,
            id=FOLLOWER_NAME
        )

        # Arm animation function
        def animate():
            try:
                arm.reset_arm()
                arm.wave()
            except Exception as error:
                movement_errors.append(error)

        # Run animation in a separate thread
        movement = threading.Thread(
            target=animate
        )

        movement.start()

        print("Camera active. Press Q to quit.")

        # Camera preview loop
        while True:

            frame = camera.get_frame()

            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_RGB2BGR
            )

            cv2.imshow("SO-101 Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # Wait for the movement to finish before disconnecting
        if movement is not None:
            movement.join()

        if arm is not None:
            arm.disconnect()

        camera.disconnect()
        cv2.destroyAllWindows()

    if movement_errors:
        raise movement_errors[0]

    print("Done!")


if __name__ == "__main__":
    main()
