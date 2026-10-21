#!/usr/bin/env python3
"""Scratch inspector (outside the lane): per-cell filesystem effect on a mirror
of the real install tree. Reads the real tree only; mutates mirrors in /tmp."""
import importlib.util
import os
import shutil
import tempfile
from pathlib import Path

GRID = "/tmp/kama-r21-LinksGridReview/lane/tests/llamacpp-live/install-links-grid.py"
spec = importlib.util.spec_from_file_location("grid", GRID)
grid = importlib.util.module_from_spec(spec)
spec.loader.exec_module(grid)

tree = Path(grid.DEFAULT_TREE)


def state(d):
    out = {}
    for e in sorted(os.listdir(d)):
        p = d / e
        if p.is_symlink():
            out[e] = ("L", os.readlink(p), os.path.exists(p))
        elif p.is_file():
            out[e] = ("F", p.stat().st_size, None)
    return out


def fmt(entry):
    if entry is None:
        return "<absent>"
    kind, val, ok = entry
    if kind == "L":
        return f"symlink->{val!r} ({'resolves' if ok else 'unresolved'})"
    return f"regular size={val}"


links = grid.links_of(tree)
print(f"real tree: first={links[0]} second={links[-1]} links={links}")
base = state(tree)
cells = grid.build_cells(tree)
with tempfile.TemporaryDirectory(prefix="kama-r21-cells-") as tmp:
    for name, klass, mutate in cells:
        mdir = Path(tmp) / name
        grid.mirror(tree, mdir)
        mutate(mdir)
        cur = state(mdir)
        print(f"{name} [{klass}]")
        changed = 0
        for e in sorted(set(base) | set(cur)):
            if base.get(e) != cur.get(e):
                changed += 1
                print(f"    {e}: {fmt(base.get(e))} -> {fmt(cur.get(e))}")
        print(f"    entries_changed={changed}")
        shutil.rmtree(mdir)
