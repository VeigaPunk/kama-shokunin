#!/usr/bin/env python3
"""fetch-pinned-model.py - restore the lane's pinned llama.cpp fixture model.

The live fixtures (`tools/round78-live-reconcile.py`, `tools/round88-router-cells.py`)
need `~/.cache/kama-shokunin/models/stories260K.gguf` at sha256 PIN. A cache is not
evidence and can be reaped; this tool re-creates it from the pinned upstream file
(ggml-org/models `tinyllamas/stories260K.gguf`, provenance in
`.ufo/waves/round-16/build/advice/ScoutModelProvenance.md`).

Downloads to `<dest>.part`, verifies the sha256, then renames atomically. A file
already present with the pinned digest is left untouched. A present file with a
different digest is refused (exit 1), never overwritten.

Prints `FETCH_PINNED model=<path> sha256=<hex> action=<present|fetched>` and exits 0;
exit 1 on a digest mismatch (download or existing file), 2 on a network error.
"""
from __future__ import annotations

import argparse
import hashlib
import os
from pathlib import Path
import sys
import urllib.request

URL = "https://huggingface.co/ggml-org/models/resolve/main/tinyllamas/stories260K.gguf"
PIN = "270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d"
DEST = Path.home() / ".cache/kama-shokunin/models/stories260K.gguf"


def digest(path: Path) -> str:
    with path.open("rb") as f:
        return hashlib.file_digest(f, "sha256").hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--dest", type=Path, default=DEST)
    ap.add_argument("--url", default=URL)
    a = ap.parse_args()
    if a.dest.exists():
        got = digest(a.dest)
        if got != PIN:
            print(f"FETCH_PINNED_FINDING existing file digest {got} != pin {PIN}: {a.dest} (refused)")
            return 1
        print(f"FETCH_PINNED model={a.dest} sha256={got} action=present")
        return 0
    a.dest.parent.mkdir(parents=True, exist_ok=True)
    part = a.dest.with_name(a.dest.name + ".part")
    try:
        with urllib.request.urlopen(a.url, timeout=60) as r, part.open("wb") as out:
            while chunk := r.read(1 << 16):
                out.write(chunk)
    except OSError as e:
        part.unlink(missing_ok=True)
        print(f"FETCH_PINNED could-not-fetch: {e}")
        return 2
    got = digest(part)
    if got != PIN:
        part.unlink(missing_ok=True)
        print(f"FETCH_PINNED_FINDING downloaded digest {got} != pin {PIN} (discarded)")
        return 1
    os.replace(part, a.dest)
    print(f"FETCH_PINNED model={a.dest} sha256={got} action=fetched")
    return 0


if __name__ == "__main__":
    sys.exit(main())
