# UNO Q Braccio Gazebo Simulation

This package provides a lightweight Gazebo Classic simulation for the UNO Q
Braccio project.

It includes:

- Six Braccio command joints: `base`, `shoulder`, `elbow`, `wrist_vertical`,
  `wrist_rotation`, and `gripper`.
- A simple gripper-mounted camera body matching the real camera position above
  and between the fingers.
- Red, blue, and yellow pick blocks.
- Three colored drop zones.
- `ros2_control` metadata and controller configuration.
- A joint-state simulator fallback so `/braccio/joint_command` pose demos can
  move the model even without a full controller command bridge.
- A joint trajectory bridge that republishes `/braccio/joint_command` to
  `/arm_controller/joint_trajectory` for Gazebo controller use.

## Install Dependencies

On Ubuntu with ROS 2 Jazzy:

```bash
sudo apt update
sudo apt install \
  ros-jazzy-gazebo-ros-pkgs \
  ros-jazzy-gazebo-ros2-control \
  ros-jazzy-ros2-control \
  ros-jazzy-ros2-controllers \
  ros-jazzy-xacro
```

## Build

```bash
cd ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Run

```bash
ros2 launch unoq_braccio_bringup sim.launch.py
```

Then publish a pose:

```bash
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=ready
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=pickup
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=wave
```

## Current Scope

This is a practical development simulation, not a calibrated digital twin. Link
dimensions and inertias are approximate. The pick blocks and bins are there for
vision and workflow testing; grasp physics still needs tuning before relying on
it for realistic pick-and-place contact.

The launch starts both the controller bridge and the joint-state simulator. If
`gazebo_ros2_control` is available, the controller path drives
`/arm_controller/joint_trajectory`. If controller startup fails, the
joint-state simulator still publishes `/joint_states` so the model follows
project pose commands for visual testing.
