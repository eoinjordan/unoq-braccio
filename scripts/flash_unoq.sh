#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-/dev/ttyACM0}"
FQBN="${2:-arduino:zephyr:unoq}"
SKETCH_DIR="$(cd "$(dirname "$0")/../firmware/unoq_braccio_firmware" && pwd)"

arduino-cli lib install Braccio
arduino-cli core install arduino:zephyr
arduino-cli compile --fqbn "$FQBN" "$SKETCH_DIR"
arduino-cli upload -p "$PORT" --fqbn "$FQBN" "$SKETCH_DIR"
