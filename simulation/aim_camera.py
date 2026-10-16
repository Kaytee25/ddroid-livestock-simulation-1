"""Point the overview camera at the water point and save a frame."""

import math
import os
import struct
import time
import zlib

os.environ.setdefault("GZ_PARTITION", "ddroid")

from gz.msgs.boolean_pb2 import Boolean
from gz.msgs.image_pb2 import Image
from gz.msgs.pose_pb2 import Pose
from gz.transport import Node

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames", "live_view.png")


def look_at(camera, target):
    dx = target[0] - camera[0]
    dy = target[1] - camera[1]
    dz = target[2] - camera[2]
    yaw = math.atan2(dy, dx)
    pitch = math.atan2(dz, math.hypot(dx, dy))
    cy, sy = math.cos(yaw / 2), math.sin(yaw / 2)
    cp, sp = math.cos(pitch / 2), math.sin(pitch / 2)
    return (sp * sy, sp * cy, cp * sy, cp * cy)


def write_png(path, width, height, rgb):
    def chunk(tag, data):
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    stride = width * 3
    rows = [b"\x00" + rgb[y * stride : (y + 1) * stride] for y in range(height)]
    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(b"".join(rows), 6))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as handle:
        handle.write(png)


def main():
    node = Node()
    camera = (1.6, -2.1, 1.7)
    target = (0.0, 0.0, 0.95)
    qx, qy, qz, qw = look_at(camera, target)
    req = Pose()
    req.name = "overview_camera"
    req.position.x, req.position.y, req.position.z = camera
    req.orientation.x = qx
    req.orientation.y = qy
    req.orientation.z = qz
    req.orientation.w = qw
    ok, _reply = node.request("/world/ddroid/set_pose", req, Pose, Boolean, 1000)
    print("set_pose", ok, "quat", round(qx, 3), round(qy, 3), round(qz, 3), round(qw, 3))
    time.sleep(0.6)
    got = {}

    def on_image(msg):
        if "rgb" not in got and msg.width > 0:
            got["rgb"] = (msg.width, msg.height, bytes(msg.data))

    node.subscribe(Image, "/overview", on_image)
    for _ in range(40):
        if "rgb" in got:
            break
        time.sleep(0.1)
    if "rgb" not in got:
        raise SystemExit("no frame")
    width, height, rgb = got["rgb"]
    write_png(OUT, width, height, rgb[: width * height * 3])
    print(OUT, os.path.getsize(OUT))


if __name__ == "__main__":
    main()
