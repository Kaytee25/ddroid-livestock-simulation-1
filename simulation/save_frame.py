"""Save one frame from the running Gazebo overview camera."""

import os
import struct
import time
import zlib

os.environ.setdefault("GZ_PARTITION", "ddroid")

from gz.transport import Node
from gz.msgs.image_pb2 import Image

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "frames", "live_view.png")


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
    got = {}

    def on_image(msg):
        if "rgb" not in got and msg.width > 0 and msg.height > 0:
            got["rgb"] = (msg.width, msg.height, bytes(msg.data))

    node = Node()
    if not node.subscribe(Image, "/overview", on_image):
        raise SystemExit("could not subscribe to /overview")
    for _ in range(50):
        if "rgb" in got:
            break
        time.sleep(0.1)
    if "rgb" not in got:
        raise SystemExit("no frame received")
    width, height, rgb = got["rgb"]
    rgb = rgb[: width * height * 3]
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    write_png(OUT, width, height, rgb)
    print(OUT, width, height, os.path.getsize(OUT))


if __name__ == "__main__":
    main()
