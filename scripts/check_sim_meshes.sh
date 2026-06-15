#!/usr/bin/env bash
set -euo pipefail

workspace="${1:-$HOME/unoq-braccio/ros2_ws}"
urdf="$workspace/src/unoq_braccio_sim/urdf/braccio.urdf.xacro"
mesh_dir="$workspace/src/unoq_braccio_sim/meshes/braccio_stedden"

echo "workspace: $workspace"
test -f "$urdf" || { echo "missing URDF: $urdf" >&2; exit 1; }
test -d "$mesh_dir" || { echo "missing mesh dir: $mesh_dir" >&2; exit 1; }

echo "mesh references in source URDF:"
grep -n "mesh_dir\\|braccio_stedden\\|file://" "$urdf"

echo
echo "mesh files:"
ls -lh "$mesh_dir"/*.stl

if [ -f "$workspace/install/unoq_braccio_sim/share/unoq_braccio_sim/urdf/braccio.urdf.xacro" ]; then
  echo
  echo "mesh references in installed URDF:"
  grep -n "mesh_dir\\|braccio_stedden\\|file://" \
    "$workspace/install/unoq_braccio_sim/share/unoq_braccio_sim/urdf/braccio.urdf.xacro"
fi

echo
echo "After launch, Gazebo should list the entity as unoq_braccio near world origin."
echo "If it is missing, run: gz topic -l | grep -E 'world|pose|model'"
