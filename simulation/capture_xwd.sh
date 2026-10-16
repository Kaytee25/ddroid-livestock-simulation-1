#!/bin/bash
export DISPLAY=:0
xdotool search --name "Gazebo Sim" windowmove 80 40 windowsize 1100 720 windowactivate
ID=$(xdotool search --name "Gazebo Sim" | head -1)
echo "ID=$ID"
xwd -id "$ID" -silent -out /tmp/gazebo.xwd
ls -l /tmp/gazebo.xwd
python3 - << 'PY'
import struct
data = open("/tmp/gazebo.xwd", "rb").read()
hdr = struct.unpack(">25I", data[:100])
header_size = hdr[0]
width, height = hdr[4], hdr[5]
bpp, bpl, ncolors = hdr[11], hdr[12], hdr[19]
print("header", header_size, "wh", width, height, "bpp", bpp, "bpl", bpl, "ncolors", ncolors)
end = data.index(b"\x00", 100)
offset = end + 1
if offset % 4:
    offset += 4 - (offset % 4)
offset += ncolors * 12
pix = data[offset:]
print("pixel bytes", len(pix))
nz = 0
if bpp == 32 and len(pix) >= bpl * height:
    step = max(4, ((bpl * height) // 20000) * 4)
    for i in range(0, bpl * height - 4, step):
        if pix[i] or pix[i + 1] or pix[i + 2]:
            nz += 1
    print("nonzero samples", nz)
    print("first pixel", pix[:8].hex())
PY
