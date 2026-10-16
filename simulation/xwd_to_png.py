"""Convert an XWD dump to PNG and report whether it is blank."""

import struct
import zlib

SRC = "/tmp/gazebo.xwd"
DST = "/mnt/c/Users/user/Documents/Livestock project/simulation/frames/gazebo_xwd.png"


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
    data = open(SRC, "rb").read()
    order = ">"
    hdr = struct.unpack(order + "25I", data[:100])
    header_size, width, height = hdr[0], hdr[4], hdr[5]
    bpp, bpl, ncolors = hdr[11], hdr[12], hdr[19]
    red, green, blue = hdr[14], hdr[15], hdr[16]
    print("order", order, "size", header_size, "wh", width, height, "bpp", bpp, "bpl", bpl, "colors", ncolors)
    print("masks", hex(red), hex(green), hex(blue))
    offset = header_size + ncolors * 12
    pix = data[offset:]
    print("offset", offset, "pix", len(pix), "expect", bpl * height)
    if width == 0 or height == 0 or len(pix) < bpl * height:
        return
    rgb = bytearray(width * height * 3)
    nonzero = 0
    for y in range(height):
        row = pix[y * bpl : y * bpl + width * 4]
        for x in range(width):
            p = row[x * 4 : x * 4 + 4]
            if order == ">":
                value = int.from_bytes(p, "big")
            else:
                value = int.from_bytes(p, "little")
            r = (value & red) >> (red.bit_length() - 8) if red else 0
            g = (value & green) >> (green.bit_length() - 8) if green else 0
            b = (value & blue) >> (blue.bit_length() - 8) if blue else 0
            i = (y * width + x) * 3
            rgb[i : i + 3] = bytes((r & 255, g & 255, b & 255))
            if r or g or b:
                nonzero += 1
    print("nonzero pixels", nonzero, "of", width * height)
    write_png(DST, width, height, bytes(rgb))
    print(DST)


if __name__ == "__main__":
    main()
