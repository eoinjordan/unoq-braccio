# Edge Impulse Integration

Use Edge Impulse to turn classifier labels into Braccio poses.

Recommended flow:

1. Build and train an Edge Impulse project.
2. Export the model for the device that will run inference.
3. Publish the top label as a ROS 2 string on `/edge_impulse/label`.
4. Run `edge_impulse_mapper` with `label_to_pose.yaml`.

Example:

```bash
ros2 run unoq_braccio_driver edge_impulse_mapper \
  --ros-args -p mapping_file:=edge_impulse/label_to_pose.yaml
```

Publish a simulated label:

```bash
ros2 topic pub --once /edge_impulse/label std_msgs/msg/String "{data: wave}"
```

For recording Braccio command and robot-status data as CSV, see
[data_capture.md](data_capture.md).

## Camera Object Detection to Pick and Place

Use `edge_impulse_vision` when your USB camera is publishing ROS images and you
have an Edge Impulse object detection model exported as a Python/Linux runner.

The runner command receives a JPEG path as `{image}` and must print one JSON
object on stdout:

```json
{"label": "red_block", "confidence": 0.92, "bbox": {"x": 120, "y": 80, "width": 60, "height": 50}}
```

Start the UNO Q camera stream, hardware bridge, inference, and pick/place
executor:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup remote.launch.py host:=192.168.1.64 port:=8765
ros2 launch unoq_braccio_bringup edge_impulse_pick_place.launch.py \
  stream_url:=http://192.168.1.64:8080/stream \
  runner_command:="python3 edge_impulse/runner_template.py --image {image}" \
  workflow_file:=edge_impulse/pick_place_workflows.yaml
```

Replace `runner_template.py` with your Edge Impulse model runner when ready.
Edit `pick_place_workflows.yaml` so labels from your model match the item names
and drop locations you want.

For Linux `.eim` model testing, see [linux_setup.md](linux_setup.md).
