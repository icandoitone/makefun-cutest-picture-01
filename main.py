"""Entry program for make.fun cutest-picture-01.

Writes one picture to /output/entry.png by copying the image
this repository holds (art.png). The copy is byte-identical on every
run: no network, no randomness, no timestamps.
"""

import shutil
import struct
from pathlib import Path

SOURCE = Path(__file__).with_name("art.png")
DEST = Path("/output/entry.png")

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
JPEG_SIGNATURE = b"\xff\xd8\xff"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def check_image(data: bytes) -> None:
    """Self-check: the output must be a whole PNG or JPEG within the limits."""
    assert len(data) <= MAX_BYTES, f"image too large: {len(data)} bytes"
    if data.startswith(PNG_SIGNATURE):
        width, height = struct.unpack(">II", data[16:24])
    elif data.startswith(JPEG_SIGNATURE):
        width = height = 0
        i = 2
        while i < len(data) - 1:
            if data[i] != 0xFF:
                i += 1
                continue
            marker = data[i + 1]
            if marker in (0xC0, 0xC1, 0xC2):
                height, width = struct.unpack(">HH", data[i + 5:i + 9])
                break
            length = struct.unpack(">H", data[i + 2:i + 4])[0]
            i += 2 + length
        assert width and height, "could not read JPEG dimensions"
    else:
        raise AssertionError("not a PNG or JPEG")
    assert width <= MAX_SIDE and height <= MAX_SIDE, f"too big: {width}x{height}"
    print(f"Checked image: {width}x{height}, {len(data)} bytes")


def main() -> None:
    DEST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SOURCE, DEST)
    check_image(DEST.read_bytes())
    print(f"Wrote {DEST} ({DEST.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
