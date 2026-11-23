# SO-101 Demo Arm Controller

A lightweight Python controller for the **SO-101 robotic arm**, developed for demonstrations and experimentation at **RoboTeam Twente**.

The project wraps [Hugging Face LeRobot](https://github.com/huggingface/lerobot) with simple joint-movement commands, a reset pose, a waving animation, and live image capture from a **Sony PlayStation Eye (PS3 Eye)** USB camera.

> **Project status:** Experimental/demo code, not a production-ready robot controller. Joint limits and poses must be validated for the specific arm before use.

## Features

- Connect to and disconnect from an SO-101 follower arm.
- Command all six joints through a single `Follower` class.
- Move individual joints gradually with `slower_move()`.
- Run a predefined reset sequence with `reset_arm()`.
- Perform a wrist-waving animation with `wave()`.
- Connect to a PS3 Eye camera through LeRobot/OpenCV and capture RGB frames with `get_camera_frame()`.
- Test SO-101 leader-to-follower teleoperation with `armtest.py`.

## Hardware

- **SO-101 follower arm** (configured as `T300` in the examples)
- **Sony PlayStation Eye / PS3 Eye** camera (USB device ID `1415:2000`)
- Linux PC with USB connections to the arm and camera
- Optional **SO-101 leader arm** (configured as `SKYNET`) for teleoperation

## Software

- Linux (developed on Zorin OS)
- Python 3.12 in the existing `lerobot` Conda environment
- [LeRobot](https://github.com/huggingface/lerobot) **0.7.1** (version tested during development)
- OpenCV and Linux V4L2 camera support
- `v4l-utils` (recommended for camera diagnostics)

## Project files

| File | Description |
| --- | --- |
| `follower.py` | `Follower` class: joint control, animations, camera access, and connection handling |
| `armed.py` | Example program for running the arm demo and camera preview |
| `armtest.py` | Direct LeRobot leader/follower teleoperation test |
| `README.md` | Setup and usage instructions |

## Installation

Clone the repository:

```bash
git clone https://github.com/RoboTeamTwente/Demo-Arm-Code.git
cd Demo-Arm-Code
```

Activate the LeRobot environment:

```bash
conda activate lerobot
python -m pip show lerobot
```

The working development environment uses **LeRobot 0.7.1**. If you are setting up a new machine, install a compatible LeRobot environment by following the [official LeRobot installation instructions](https://github.com/huggingface/lerobot) before running this project.

Install camera-diagnostic utilities on Ubuntu-based Linux distributions:

```bash
sudo apt update
sudo apt install v4l-utils
```

> The camera-enabled code described below is the **current local development version**. At the time this README was prepared, the GitHub `main` branch still contained earlier versions of `armed.py` and `follower.py`. Push the updated Python files alongside this README to make the published repository match these instructions.

## Find the hardware ports

### SO-101 serial port

```bash
ls -l /dev/ttyACM*
```

The examples use `/dev/ttyACM0` for the follower. The port may change if USB devices are unplugged or reconnected.

If access is denied, add your account to the `dialout` group and **log out and back in**:

```bash
sudo usermod -aG dialout "$USER"
```

### PS3 Eye camera

Confirm the USB device:

```bash
lsusb -d 1415:2000
```

Find its video node and supported formats:

```bash
v4l2-ctl --list-devices
v4l2-ctl -d /dev/video2 --list-formats-ext
```

The tested configuration is:

| Setting | Value |
| --- | --- |
| Video node | `/dev/video2` (OpenCV index `2`) |
| Backend | V4L2 |
| Pixel format / FOURCC | `YUYV` |
| Resolution | `640 × 480` |
| Frame rate | `30 FPS` |

The device index can change between boots. Check it before starting the application.

## Camera configuration

In `follower.py`, the PS3 Eye is configured through `SO101FollowerConfig`. Explicitly selecting the V4L2 backend resolved an OpenCV initialization error during testing.

```python
from lerobot.cameras.opencv import OpenCVCameraConfig
from lerobot.cameras.configs import Cv2Backends

config = SO101FollowerConfig(
    port=self.port,
    id=self.id,
    cameras={
        "ps3_eye": OpenCVCameraConfig(
            index_or_path=2,
            backend=Cv2Backends.V4L2,
            fourcc="YUYV",
            fps=30,
            width=640,
            height=480,
        )
    },
)
```

Change `index_or_path` if the PS3 Eye is assigned a different `/dev/video*` device. The `camera_port` argument in your `Follower` constructor should also be kept consistent with the actual camera configuration.

## Run the demo

```bash
conda activate lerobot
python armed.py
```

The current local demo creates a `Follower`, runs the reset and wave animations, and can display frames from the PS3 Eye camera. If using the live-preview version of `armed.py`, press **Q** to close the preview; the sample code waits for any in-progress animation to finish before disconnecting.

### Use the `Follower` class in your own script

```python
from follower import Follower

arm = Follower(port="/dev/ttyACM0", id="T300")

try:
    arm.reset_arm()
    arm.wave(repeats=3, amplitude=20, delay=0.3)
    frame = arm.get_camera_frame()  # RGB image as a NumPy array
finally:
    arm.disconnect()
```

`get_camera_frame()` captures an image but does not display it. To show a frame with OpenCV:

```python
import cv2

frame = arm.get_camera_frame()
cv2.imshow("PS3 Eye", cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
cv2.waitKey(0)
cv2.destroyAllWindows()
```

Run the display code **before** calling `arm.disconnect()`.

### Teleoperation (optional)

If both leader and follower arms are connected and calibrated:

```bash
python armtest.py
```

Verify the leader/follower serial-port assignments in `armtest.py` first. Press **Ctrl+C** to stop the teleoperation test.

## `Follower` API

| Method | Description |
| --- | --- |
| `slower_move(joint, pos, step=1.0, delay=0.02)` | Sends intermediate position commands to one joint |
| `reset_arm()` | Moves joints toward a predefined demo pose |
| `wave(repeats=3, amplitude=20, delay=0.3)` | Waves the wrist and returns it to its starting command position |
| `get_camera_frame()` | Returns an RGB frame from the PS3 Eye |
| `get_camera()` | Returns the LeRobot camera object |
| `disconnect()` | Disconnects the arm and configured camera |

Supported joint names:

```text
shoulder_pan
shoulder_lift
elbow_flex
wrist_flex
wrist_roll
gripper
```

The wrapper currently assumes normalized position ranges of `-100..100` for arm joints and `0..100` for the gripper. These are **software assumptions**, not verified physical joint limits. The reset pose uses large moves and may not be safe on every setup.

## Troubleshooting

**`Permission denied` on `/dev/ttyACM*`** — Check that your user belongs to `dialout`, then sign out and back in.

**`OpenCVCamera ... failed to set capture_width=640`** — Confirm the video index, use `Cv2Backends.V4L2`, and request `YUYV` at 640×480 / 30 FPS as shown above.

**`ioctl(VIDIOC_QBUF): Bad file descriptor`** — Check whether another program has opened the camera:

```bash
fuser -v /dev/video2
```

**Calibration error** — Confirm the arm ID and its saved motor calibration before issuing any movement. Do not bypass calibration checks.

**No camera preview** — `get_camera_frame()` only returns image data. Use `cv2.imshow()` and `cv2.waitKey()` or the demo's preview loop to display it.

## Safety notes

- Ensure the arm has room to move and is not carrying an unsecured load.
- Verify calibration, physical joint ranges, and the reset pose before starting animations.
- Begin tests with small movement amplitudes and keep hands clear of the joints.
- `slower_move()` interpolates **commanded** positions; it does not guarantee a particular measured motor velocity or enforce collision avoidance.
- Closing the preview with **Q** is **not an emergency stop**.
- Treat this repository as demonstration and development code, not safety-certified robot control software.

## Planned improvements

- Configurable camera and serial-port discovery
- Validated per-joint motion limits and safer reset poses
- Smooth multi-joint trajectories and reliable interruption/stop handling
- Camera-based object detection and tracking
- Possible ROS 2 integration

## Related projects

- [Hugging Face LeRobot](https://github.com/huggingface/lerobot)
- [RoboTeam Twente](https://github.com/RoboTeamTwente)

---

Maintained as part of ongoing RoboTeam Twente SO-101 demonstration development.
