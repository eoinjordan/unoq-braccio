# UNOQ Braccio

Control a TinkerKit Braccio arm with an Arduino UNO Q, ROS 2, Edge Impulse,
and Gazebo.

This repository contains:

- Arduino firmware using the official
  [arduino-libraries/Braccio](https://github.com/arduino-libraries/Braccio)
  library.
- ROS 2 USB serial and remote TCP bridges that convert
  `sensor_msgs/JointState` commands into Braccio servo angles.
- A ROS 2 teleop node for keyboard-free testing.
- A Gazebo/ros2_control simulation package for developing without hardware.
- Edge Impulse integration scaffolding for gesture or classifier-driven arm
  poses.
- Edge Impulse CSV data capture for commanded servo motion and robot status.
- USB camera vision with OpenCV color tracking, plus notes for Pixy and
  ESP32-CAM expansion.

## Repository Layout

```text
firmware/unoq_braccio_firmware/   USB serial firmware for UNO Q + Braccio
app_lab/braccio_smoke_test/       Arduino App Lab hardware smoke test
app_lab/braccio_remote_agent/     Arduino App Lab network control agent
app_lab/usb_camera_streamer/      UNO Q attached USB camera MJPEG streamer
ros2_ws/src/unoq_braccio_bringup/ ROS 2 launch files and runtime config
ros2_ws/src/unoq_braccio_driver/  Serial driver and demo command nodes
ros2_ws/src/unoq_braccio_sim/     URDF, Gazebo world, ros2_control config
edge_impulse/                     Classifier mapping examples and notes
scripts/                          Setup and helper scripts
docs/                             Hardware and workflow documentation
```

## Hardware

- Arduino UNO Q
- TinkerKit Braccio robot arm and Braccio shield
- USB serial or Wi-Fi/Ethernet network connection to the ROS 2 host
- 5 V power supply for the Braccio servos

The firmware expects the Arduino Braccio library to be installed through the
Arduino IDE Library Manager or `arduino-cli`.

## Quick Start

For full setup on Windows, macOS, and Linux, see
[docs/platform-setup.md](docs/platform-setup.md).

### 1. Install ROS 2 dependencies

Tested target: ROS 2 Jazzy on Ubuntu 24.04.

```bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
cd ..
```

### 2. Flash the UNO Q

For a first hardware check through Arduino App Lab, use
[app_lab/braccio_smoke_test](app_lab/braccio_smoke_test). For direct
`arduino-cli` flashing:

```bash
arduino-cli lib install Braccio
arduino-cli core install arduino:zephyr
arduino-cli board list
arduino-cli compile --fqbn arduino:zephyr:unoq firmware/unoq_braccio_firmware
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:zephyr:unoq firmware/unoq_braccio_firmware
```

The Braccio shield sits on the UNO Q headers. Do not use `arduino:avr:uno`;
UNO Q builds target the Zephyr-based MCU core with `arduino:zephyr:unoq`.

Validated Windows network upload path:

```powershell
arduino-cli board list
arduino-cli upload -p 192.168.1.64 --fqbn arduino:zephyr:unoq .\firmware\unoq_braccio_firmware --upload-field password=arduino123
```

Replace `192.168.1.64` and `arduino123` with your UNO Q network address and
upload password. This path avoids the Windows USB ADB `device offline` issue.

### 3. Run the hardware bridge over USB

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup hardware.launch.py serial_port:=/dev/ttyACM0
```

Publish a test pose:

```bash
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=ready
```

Windows USB debug:

```powershell
arduino-cli board list
arduino-cli monitor -p COM4 --fqbn arduino:zephyr:unoq --config baudrate=115200
```

Replace `COM4` with the port shown by `arduino-cli board list`. The firmware
uses `115200` baud. Send this line to test the arm command protocol:

```text
M 90 90 90 90 90 25
```

Expected response:

```text
OK
```

### 4. Run the hardware bridge over the network

Install and run the App Lab project in `app_lab/braccio_remote_agent` on the
UNO Q, then launch the ROS 2 TCP bridge:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup remote.launch.py host:=<UNO_Q_IP_ADDRESS> port:=8765
```

Send the same test pose:

```bash
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=ready
```

### 5. Run Gazebo simulation

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup sim.launch.py
```

Then send the same demo poses:

```bash
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=wave
```

## Command Protocol

The USB serial firmware and remote App Lab agent both use the same command
protocol:

```text
M <base> <shoulder> <elbow> <wrist_vertical> <wrist_rotation> <gripper>
```

Angles are integer degrees. The firmware clamps values to the conservative
Braccio operating ranges before moving servos.

## Edge Impulse Workflow

1. Train an Edge Impulse classifier for gestures, voice intents, camera labels,
   or sensor states.
2. Export the model as a Linux SDK, Python SDK, or Arduino library.
3. Use `edge_impulse/label_to_pose.yaml` to map classifier labels to named arm
   poses.
4. Publish poses to `/braccio/joint_command` as `sensor_msgs/JointState`.

See [edge_impulse/README.md](edge_impulse/README.md) for the integration
pattern.

## Data Capture and Robot Stats

Standard Braccio servos do not provide measured feedback such as current,
torque, temperature, or actual shaft position. This project captures commanded
joint angles, deltas, estimated command rates, labels, and firmware/remote-agent
status.

Start a hardware bridge, then start CSV capture:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup data_capture.launch.py \
  output_file:=edge_impulse/captures/braccio_capture.csv \
  label:=ready
```

Query firmware stats directly over serial:

```text
S
```

Example response:

```text
STAT uptime_ms=12345 move_count=3 last_move_ms=640 last_command_ms=12000 target=90,90,90,90,90,25
```

See [edge_impulse/data_capture.md](edge_impulse/data_capture.md).

## Vision

The easiest sight path is a USB camera on the ROS 2 host:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup vision_usb.launch.py camera_index:=0 label:=object
```

This publishes camera frames, debug frames, object centroid stats, and simple
labels that can feed the Edge Impulse mapper. See [docs/vision.md](docs/vision.md).

If the USB camera is plugged into the UNO Q instead, run
`app_lab/usb_camera_streamer` on the UNO Q and use:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup vision_remote.launch.py \
  stream_url:=http://<UNO_Q_IP_ADDRESS>:8080/stream \
  label:=object
```

For a gripper-mounted camera, watch `/braccio/vision_stats` and center the
object near `x_norm=0` and `y_norm=0`. A cautious visual alignment helper is
available but disabled by default:

```bash
ros2 launch unoq_braccio_bringup vision_assist.launch.py enabled:=false
```

For Edge Impulse object detection and item-specific pick/place:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup edge_impulse_pick_place.launch.py \
  stream_url:=http://192.168.1.64:8080/stream \
  runner_command:="python3 edge_impulse/runner_template.py --image {image}" \
  workflow_file:=edge_impulse/pick_place_workflows.yaml
```

For Linux Edge Impulse `.eim` setup and API-key authentication, see
[edge_impulse/linux_setup.md](edge_impulse/linux_setup.md). Keep API keys in
`EDGE_IMPULSE_API_KEY`, not in committed files.

Public Edge Impulse project:

```text
https://studio.edgeimpulse.com/studio/1029890
```

Project labels used for pick/place examples: `Red Block`, `Blue Block`, and
`Yellow Block`.
