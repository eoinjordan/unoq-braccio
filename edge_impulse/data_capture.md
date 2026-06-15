# Edge Impulse Data Capture

This project can capture Braccio command and robot-status data as CSV for Edge
Impulse upload.

## What Data Is Available

The standard Braccio servos are hobby PWM servos. They do not report measured
position, current, voltage, torque, or temperature back to the UNO Q.

Captured data therefore includes:

- Commanded joint angle for each Braccio joint.
- Delta from the previous command.
- Estimated commanded angular rate.
- Current classifier or operator label.
- Firmware or remote-agent status string.
- Latest vision stats string when the USB camera tracker is running.
- Move count, last move duration, uptime, and last target when available.

For real motor current or torque data, add external sensors such as a current
sensor on the servo power rail or smart servos with telemetry.

## Start a Hardware Bridge

USB:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup hardware.launch.py serial_port:=/dev/ttyACM0
```

Remote:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup remote.launch.py host:=<UNO_Q_IP_ADDRESS> port:=8765
```

## Start Capture

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup data_capture.launch.py \
  output_file:=edge_impulse/captures/braccio_capture.csv \
  label:=ready
```

Send poses:

```bash
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=ready
ros2 run unoq_braccio_driver pose_demo --ros-args -p pose:=wave
```

Change labels while recording:

```bash
ros2 topic pub --once /edge_impulse/label std_msgs/msg/String "{data: pickup}"
```

## CSV Columns

The capture file contains:

- `timestamp`
- `label`
- `dt_ms`
- `<joint>_deg`
- `<joint>_delta_deg`
- `<joint>_rate_dps`
- `firmware_status`
- `vision_stats`

Use the CSV upload flow in Edge Impulse to import the capture file.
