#!/usr/bin/env python3
"""Scratch digest re-derivation (outside the lane): reads the real tree only.
Formulas copied from the producer docstrings/bodies; no producer code is imported."""
import hashlib
import os
import stat
from pathlib import Path

tree = Path("/home/vgpnk/.local/opt/llama-b11755")
reg, lnk = {}, {}
for n in sorted(os.listdir(tree)):
    p = tree / n
    m = os.lstat(p).st_mode
    if stat.S_ISREG(m):
        h = hashlib.sha256()
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        reg[n] = h.hexdigest()
    elif stat.S_ISLNK(m):
        lnk[n] = os.readlink(p)
print("regular_members", len(reg), "symlinks", len(lnk))
print("install_tree_sha256", hashlib.sha256(
    "".join(f"{n} {reg[n]}\n" for n in sorted(reg)).encode()).hexdigest())
print("install_links_sha256", hashlib.sha256(
    "".join(f"{n} -> {lnk[n]}\n" for n in sorted(lnk)).encode()).hexdigest())
for n in sorted(lnk):
    print("link", n, "->", lnk[n])
