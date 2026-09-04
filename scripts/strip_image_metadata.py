#!/usr/bin/env python3
"""Losslessly remove metadata-bearing chunks from website JPEG and PNG files."""

from __future__ import annotations

import struct
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IMAGE_ROOT = ROOT / "assets" / "images"


def strip_jpeg(data: bytes) -> bytes:
    if not data.startswith(b"\xff\xd8"):
        return data
    output = bytearray(data[:2])
    position = 2
    removable_markers = {0xE1, 0xED, 0xFE}  # EXIF/XMP, IPTC/Photoshop, comments

    while position < len(data):
        marker_start = position
        if data[position] != 0xFF:
            return data
        while position < len(data) and data[position] == 0xFF:
            position += 1
        if position >= len(data):
            return data
        marker = data[position]
        position += 1

        if marker == 0xDA:  # Start of scan; the rest is compressed image data.
            output.extend(data[marker_start:])
            break
        if marker in {0xD8, 0xD9, 0x01} or 0xD0 <= marker <= 0xD7:
            output.extend(data[marker_start:position])
            continue
        if position + 2 > len(data):
            return data
        segment_length = int.from_bytes(data[position:position + 2], "big")
        segment_end = position + segment_length
        if segment_length < 2 or segment_end > len(data):
            return data
        if marker not in removable_markers:
            output.extend(data[marker_start:segment_end])
        position = segment_end

    return bytes(output)


def strip_png(data: bytes) -> bytes:
    signature = b"\x89PNG\r\n\x1a\n"
    if not data.startswith(signature):
        return data
    output = bytearray(signature)
    position = len(signature)
    removable_chunks = {b"eXIf", b"tEXt", b"zTXt", b"iTXt", b"tIME"}

    while position + 12 <= len(data):
        length = struct.unpack(">I", data[position:position + 4])[0]
        chunk_end = position + 12 + length
        if chunk_end > len(data):
            return data
        chunk_type = data[position + 4:position + 8]
        if chunk_type not in removable_chunks:
            output.extend(data[position:chunk_end])
        position = chunk_end
        if chunk_type == b"IEND":
            break

    return bytes(output)


def main() -> None:
    changed = 0
    saved = 0
    for path in IMAGE_ROOT.rglob("*"):
        if not path.is_file():
            continue
        original = path.read_bytes()
        suffix = path.suffix.lower()
        if suffix in {".jpg", ".jpeg"}:
            sanitized = strip_jpeg(original)
        elif suffix == ".png":
            sanitized = strip_png(original)
        else:
            continue
        if sanitized != original:
            path.write_bytes(sanitized)
            changed += 1
            saved += len(original) - len(sanitized)
    print(f"Sanitized {changed} images; removed {saved / 1024 / 1024:.2f} MiB of metadata")


if __name__ == "__main__":
    main()
