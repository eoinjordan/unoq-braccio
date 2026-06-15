#!/usr/bin/env bash
set -euo pipefail

echo "ROS nodes:"
ros2 node list | sort || true

echo
echo "Controllers:"
ros2 control list_controllers || true

echo
echo "Hardware interfaces:"
ros2 control list_hardware_interfaces || true

echo
echo "Trajectory topics:"
ros2 topic list | grep -E 'arm_controller|joint_trajectory|joint_states|braccio' || true

echo
echo "Gazebo model/entity topics:"
gz topic -l | grep -E 'world|model|pose|joint' || true

echo
echo "Robot description mesh paths:"
ros2 param get /robot_state_publisher robot_description \
  | grep -o 'file://[^"]*braccio_[^"]*stl' \
  | head || true
