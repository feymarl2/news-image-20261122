#!/usr/bin/env python3
"""news-image-20261122 entrypoint.

Copies the pre-rendered front page (entry.png, drawn in-session by
render.py from verified 22 November 2026 news) to the make.fun output
directory as entry.png.

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
In the grader the output directory is /output.

Standard library only, no network, no randomness: the same input bytes
always produce the same output bytes.
"""

import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC_NAME = "entry.png"


PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
MAX_BYTES = 1048576  # competition cap: at most 1 MiB


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    src = os.path.join(HERE, SRC_NAME)
    if not os.path.isfile(src):
        print("missing source image: " + src, file=sys.stderr)
        return 1
    src_size = os.path.getsize(src)
    if src_size > MAX_BYTES:
        print("source image exceeds 1 MiB: %d bytes" % src_size,
              file=sys.stderr)
        return 1
    with open(src, "rb") as fh:
        head = fh.read(len(PNG_MAGIC))
    if head != PNG_MAGIC:
        print("source image is not a PNG: " + src, file=sys.stderr)
        return 1
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, SRC_NAME)
    shutil.copyfile(src, dst)
    src_size = os.path.getsize(src)
    dst_size = os.path.getsize(dst)
    if dst_size != src_size:
        print("copy size mismatch: %d != %d" % (dst_size, src_size),
              file=sys.stderr)
        return 1
    print("wrote %s (%d bytes)" % (dst, dst_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
