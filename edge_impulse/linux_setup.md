# Edge Impulse Linux Setup

Use this path to test the project on Linux with your Edge Impulse project:

```text
Block Color Detection - braccio unoq
```

Public project:

```text
https://studio.edgeimpulse.com/studio/1029890
```

Public live URL:

```text
https://studio.edgeimpulse.com/public/1029890/live
```

Project details verified from the public page:

- Project ID: `1029890`
- Project name: `Block Color Detection - braccio unoq`
- Impulse type: object detection
- Labels: `Blue Block`, `Red Block`, `Yellow Block`

Do not commit API keys. Export the key in your shell:

```bash
export EDGE_IMPULSE_API_KEY="ei_REPLACE_WITH_YOUR_KEY"
```

## Install CLI and Python Runtime

```bash
sudo apt update
sudo apt install -y nodejs npm python3-pip python3-opencv
./scripts/setup_edge_impulse_linux.sh
```

The Edge Impulse docs currently recommend installing the CLI with:

```bash
npm install -g edge-impulse-cli --force
```

The Linux CLI accepts:

```bash
edge-impulse-linux --api-key "$EDGE_IMPULSE_API_KEY"
```

## Download or Build a Linux Model

In Edge Impulse Studio, configure deployment for Linux and download the `.eim`
model file, or use the Linux CLI tooling for your project.

Place the model here:

```text
edge_impulse/model/block_color_detection.eim
```

## Test One Image

```bash
python3 edge_impulse/linux_eim_runner.py \
  --model edge_impulse/model/block_color_detection.eim \
  --image path/to/test-image.jpg
```

Expected output:

```json
{"label":"red_block","confidence":0.92,"bbox":{"x":120,"y":80,"width":60,"height":50}}
```

## Run with the Braccio Camera Pipeline

Start the UNO Q camera stream app, then run:

```bash
source ros2_ws/install/setup.bash
ros2 launch unoq_braccio_bringup remote.launch.py host:=192.168.1.64 port:=8765
ros2 launch unoq_braccio_bringup edge_impulse_pick_place.launch.py \
  stream_url:=http://192.168.1.64:8080/stream \
  runner_command:="python3 edge_impulse/linux_eim_runner.py --model edge_impulse/model/block_color_detection.eim --image {image}" \
  workflow_file:=edge_impulse/pick_place_workflows.yaml
```

The labels emitted by your model must match item names in:

```text
edge_impulse/pick_place_workflows.yaml
```

For example:

```yaml
items:
  red_block:
    sequence:
      - name: ready
        pose: [90, 90, 90, 90, 90, 25]
```
