#!/usr/bin/env python3
"""Scratch positive control (outside the lane): a deliberately lossy mirror must trip the
grid's mirror-fidelity guard (EvalError -> main() returns 2), proving the guard is live."""
import importlib.util
import os
import shutil
import sys
from pathlib import Path

G = "/tmp/kama-r21-LinksGridReview/lane/tests/llamacpp-live/install-links-grid.py"
spec = importlib.util.spec_from_file_location("grid", G)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)


def lossy_mirror(src, dst):
    dst.mkdir()
    for entry in sorted(os.listdir(src)):
        full = src / entry
        if full.is_symlink():
            os.symlink(os.readlink(full), dst / entry)
        elif full.is_file() and entry != "libggml-base.so.0.27.0":
            shutil.copyfile(full, dst / entry)
            shutil.copymode(full, dst / entry)


grid.mirror = lossy_mirror
rc = grid.main(["--arm", "current"])
print("fidelity_positive_control_rc", rc, file=sys.stderr)
sys.exit(0)
