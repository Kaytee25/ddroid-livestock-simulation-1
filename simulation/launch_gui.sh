#!/bin/bash
export DISPLAY=:0
export XDG_RUNTIME_DIR=/mnt/wslg/runtime-dir
export QT_QPA_PLATFORM=xcb
export LIBGL_ALWAYS_SOFTWARE=1
export GALLIUM_DRIVER=llvmpipe
export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
export GZ_PARTITION=ddroid
unset WAYLAND_DISPLAY
ROOT="$(cd "$(dirname "$0")" && pwd)"
exec gz sim -v 2 -r "$ROOT/worlds/ddroid_water_point.sdf"
