
"""Camera controller for the Sony PlayStation Eye."""

from lerobot.cameras.opencv import (
    OpenCVCamera,
    OpenCVCameraConfig,
)
from lerobot.cameras.configs import Cv2Backends


class Camera:

    # ===== INITIALIZATION =====

    def __init__(
        self,
        index: int = 2,
        fps: int = 30,
        width: int = 640,
        height: int = 480,
    ) -> None:

        self.index = index
        self.fps = fps
        self.width = width
        self.height = height

        # Configure the PS3 Eye camera
        config = OpenCVCameraConfig(
            index_or_path=self.index,
            backend=Cv2Backends.V4L2,
            fourcc="YUYV",
            fps=self.fps,
            width=self.width,
            height=self.height,
        )

        self.camera = OpenCVCamera(config)

    # ===== CONNECTION =====

    def connect(self) -> None:
        """Connect to the camera."""

        if not self.camera.is_connected:
            self.camera.connect()
            print("Camera connected!")

    def disconnect(self) -> None:
        """Disconnect from the camera."""

        if self.camera.is_connected:
            self.camera.disconnect()
            print("Camera disconnected!")

    # ===== CAMERA FUNCTIONS =====

    def get_frame(self):
        """Capture an RGB image from the camera."""

        if not self.camera.is_connected:
            raise RuntimeError("Camera is not connected.")

        return self.camera.read()

    # ===== CAMERA INFORMATION =====

    def get_resolution(self) -> tuple[int, int]:
        """Return the configured camera resolution."""

        return self.width, self.height


# ===== INDEPENDENT CAMERA TEST =====

if __name__ == "__main__":

    import cv2

    camera = Camera()

    try:
        camera.connect()

        print("Press Q to quit.")

        while True:

            frame = camera.get_frame()

            # Convert RGB to BGR for OpenCV display
            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_RGB2BGR
            )

            cv2.imshow("PS3 Eye", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

    finally:
        camera.disconnect()
        cv2.destroyAllWindows()
