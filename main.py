#!/usr/bin/env python3
"""Entry program for make.fun news-image-20261125.

The repository holds the finished front page at assets/entry.png, a single
image summing up the world news of Wednesday 25 November 2026. This program
writes that exact image to the output path the grader reads
(/output/entry.png, or $MAKEFUN_OUTPUT_DIR when set).

It does nothing but copy bytes: no network, no randomness, no imports
beyond the standard library, so two runs always produce identical output.
"""

import hashlib
import os
import shutil
import sys

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1_048_576
MAX_SIDE = 1024


def committed_image():
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "assets", "entry.png")


def output_path():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    return os.path.join(out_dir, "entry.png")


def run():
    source = committed_image()
    if not os.path.isfile(source):
        raise SystemExit("committed image not found: " + source)
    with open(source, "rb") as handle:
        payload = handle.read()
    if not payload.startswith(PNG_MAGIC):
        raise SystemExit("committed image is not a PNG file")
    if payload[12:16] != b"IHDR":
        raise SystemExit("committed image has no IHDR chunk")
    width = int.from_bytes(payload[16:20], "big")
    height = int.from_bytes(payload[20:24], "big")
    if width > MAX_SIDE or height > MAX_SIDE:
        raise SystemExit(
            f"committed image is {width}x{height}, over the {MAX_SIDE}x{MAX_SIDE} limit")
    if len(payload) > MAX_BYTES:
        raise SystemExit(
            f"committed image is {len(payload)} bytes, over the 1 MiB limit")
    target = output_path()
    shutil.copyfile(source, target)
    with open(target, "rb") as handle:
        copied = handle.read()
    if copied != payload:
        raise SystemExit("output bytes differ from the committed image")
    digest = hashlib.sha256(payload).hexdigest()
    print(f"wrote {target} ({width}x{height}, {len(payload)} bytes, sha256 {digest})")
    return 0


if __name__ == "__main__":
    sys.exit(run())
