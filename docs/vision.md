# Vision Options

The easiest way to add sight to the Braccio is a USB camera connected to the
ROS 2 host. It gives normal camera frames, works with OpenCV, and can feed both
Edge Impulse data capture and simple object tracking.

## Recommended Path: USB Camera

Install dependencies in your ROS 2 Ubuntu environment:

```bash
sudo apt update
sudo apt install -y ros-jazzy-cv-bridge python3-opencv v4l-utils
```

Check that the camera is visible:

```bash
v4l2-ctl --list-devices
```

Launch the camera and simple color tracker:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup vision_usb.launch.py camera_index:=0 label:=object
```

Topics:

```text
/braccio/camera/image_raw
/braccio/camera/debug
/braccio/vision_stats
/edge_impulse/label
```

The color tracker publishes `/edge_impulse/label` when a target color is
visible. By default it tracks a green object. Tune HSV values with ROS
parameters:

```bash
ros2 run unoq_braccio_driver color_tracker --ros-args \
  -p h_min:=35 -p h_max:=85 \
  -p s_min:=80 -p s_max:=255 \
  -p v_min:=60 -p v_max:=255 \
  -p label:=pickup
```

Run this alongside the Edge Impulse mapper:

```bash
ros2 run unoq_braccio_driver edge_impulse_mapper \
  --ros-args -p mapping_file:=edge_impulse/label_to_pose.yaml
```

## Data Capture with Vision

Run the camera, hardware bridge, and CSV logger together:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup remote.launch.py host:=<UNO_Q_IP_ADDRESS> port:=8765
ros2 launch unoq_braccio_bringup vision_usb.launch.py camera_index:=0 label:=pickup
ros2 launch unoq_braccio_bringup data_capture.launch.py \
  output_file:=edge_impulse/captures/vision_braccio_capture.csv \
  label:=vision
```

The CSV logger records robot command/status data. The color tracker separately
publishes labels and `/braccio/vision_stats` for object visibility and centroid.

## Pixy Camera

Pixy is useful when you want the camera to do object detection onboard and only
send compact object blocks to ROS 2. Use it when you want reliable colored
object tracking without running OpenCV on the host.

Recommended integration:

1. Train signatures in PixyMon.
2. Connect Pixy to the ROS 2 host over USB.
3. Add a Pixy node that publishes detected signatures to `/edge_impulse/label`
   or `/braccio/vision_stats`.

This repo does not include a Pixy driver yet because the USB camera path is
simpler and more general for Edge Impulse image collection.

## ESP32-CAM

ESP32-CAM is useful when you want a cheap wireless camera. It is less ideal for
low-latency arm control because MJPEG streams can lag and Wi-Fi quality varies.

Recommended integration:

1. Flash ESP32-CAM with an MJPEG stream sketch.
2. Confirm the stream opens in a browser.
3. Point an OpenCV capture node at the stream URL.

Example stream URL:

```text
http://<ESP32_CAM_IP>:81/stream
```

Add this after USB camera control is working.
