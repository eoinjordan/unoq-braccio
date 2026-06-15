# UNOQ Braccio

Control a TinkerKit Braccio arm with an Arduino UNO Q, ROS 2, Edge Impulse,
and Gazebo.

This repository contains:

- Arduino firmware using the official
  [arduino-libraries/Braccio](https://github.com/arduino-libraries/Braccio)
  library.
- A ROS 2 serial bridge that converts `sensor_msgs/JointState` commands into
  Braccio servo angles.
- A ROS 2 teleop node for keyboard-free testing.
- A Gazebo/ros2_control simulation package for developing without hardware.
- Edge Impulse integration scaffolding for gesture or classifier-driven arm
  poses.

## Repository Layout

```text
firmware/unoq_braccio_firmware/   Arduino sketch for UNO Q + Braccio shield
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
- USB serial connection to the ROS 2 host
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

```bash
arduino-cli lib install Braccio
arduino-cli core install arduino:zephyr
arduino-cli board list
arduino-cli compile --fqbn arduino:zephyr:unoq firmware/unoq_braccio_firmware
arduino-cli upload -p /dev/ttyACM0 --fqbn arduino:zephyr:unoq firmware/unoq_braccio_firmware
```

The Braccio shield sits on the UNO Q headers. Do not use `arduino:avr:uno`;
UNO Q builds target the Zephyr-based MCU core with `arduino:zephyr:unoq`.

### 3. Run the hardware bridge

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup hardware.launch.py serial_port:=/dev/ttyACM0
```

Publish a test pose:

```bash
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=ready
```

### 4. Run Gazebo simulation

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup sim.launch.py
```

Then send the same demo poses:

```bash
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=wave
```

## Command Protocol

The ROS 2 bridge sends one serial line per command:

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

## GitHub Setup

```bash
git init
git add .
git commit -m "first commit"
git branch -M main
git remote add origin git@github.com:eoinjordan/unoq-braccio.git
git push -u origin main
```

