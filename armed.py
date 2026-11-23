
import cv2
import threading

from follower import Follower

PORT = ["/dev/ttyACM0", "/dev/ttyACM1"]
BOTS = ["T300", "SKYNET"]

FOLLOWER_NAME = BOTS[0]
FOLLOWER_PORT = PORT[0]


def main() -> None:
    follower = Follower(
        port=FOLLOWER_PORT,
        id=FOLLOWER_NAME
    )

    movement_error = []

    def arm_animation():
        try:
            follower.reset_arm()
            follower.wave()
        except Exception as error:
            movement_error.append(error)

    # Run the movement separately from the camera preview
    movement = threading.Thread(target=arm_animation)

    try:
        movement.start()

        print("PS3 Eye camera active.")
        print("Press Q to close the camera.")

        while True:
            frame = follower.get_camera_frame()

            # LeRobot provides RGB; OpenCV displays BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            cv2.imshow("SO-101 Camera", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        # Allow the current animation to finish
        if movement.ident is not None:
            movement.join()

        cv2.destroyAllWindows()
        follower.disconnect()

    if movement_error:
        raise movement_error[0]

    print("Done!")


if __name__ == "__main__":
    main()
