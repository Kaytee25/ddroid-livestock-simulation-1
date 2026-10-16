#!/usr/bin/env bash
# Launch the DDROID livestock water-point simulation in Gazebo Jetty.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
export DISPLAY="${DISPLAY:-:0}"
export WAYLAND_DISPLAY="${WAYLAND_DISPLAY:-wayland-0}"
export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/mnt/wslg/runtime-dir}"
export GZ_PARTITION="${GZ_PARTITION:-ddroid}"

python3 "$ROOT/build_world.py"
python3 "$ROOT/test_control.py"

if ! gz sim --versions >/dev/null 2>&1; then
  echo "Gazebo is not installed. On Ubuntu 26.04 install the gz-jetty package." >&2
  exit 1
fi

gz sim -r "$ROOT/worlds/ddroid_water_point.sdf" >/tmp/ddroid-gazebo.log 2>&1 &
SIM_PID=$!
cleanup() {
  if kill -0 "$SIM_PID" 2>/dev/null; then
    kill "$SIM_PID" 2>/dev/null || true
    wait "$SIM_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT

python3 "$ROOT/run_sim.py"
echo "Demonstration finished. Gazebo stays open until this script exits."
echo "Close the Gazebo window, or press Enter here to stop it."
read -r _
