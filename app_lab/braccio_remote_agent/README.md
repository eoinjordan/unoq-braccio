# Braccio Remote Agent for Arduino App Lab

Run this app on the UNO Q when you want ROS 2 on another computer to control
the Braccio over the network instead of over USB serial.

The Python side opens a TCP server on port `8765`. The MCU side exposes a
Bridge function named `move_braccio`, which uses the Braccio library to move the
servos.

Protocol:

```text
M <base> <shoulder> <elbow> <wrist_vertical> <wrist_rotation> <gripper>
```

Example:

```text
M 90 90 90 90 90 25
```

