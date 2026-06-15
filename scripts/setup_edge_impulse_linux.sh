#!/usr/bin/env bash
set -euo pipefail

if ! command -v npm >/dev/null 2>&1; then
  echo "npm is required. Install Node.js 22 LTS or your distro's nodejs/npm packages." >&2
  exit 1
fi

python3 -m pip install --user --upgrade edge_impulse_linux opencv-python
npm install -g edge-impulse-cli --force

if [[ -n "${EDGE_IMPULSE_API_KEY:-}" ]]; then
  echo "Testing Edge Impulse Linux CLI auth with EDGE_IMPULSE_API_KEY..."
  edge-impulse-linux --api-key "$EDGE_IMPULSE_API_KEY" --disable-camera --disable-microphone || true
else
  echo "EDGE_IMPULSE_API_KEY is not set. Export it before authenticating:"
  echo "  export EDGE_IMPULSE_API_KEY=ei_xxx"
fi
