#!/usr/bin/env python3
"""M3Live seam-killing harness: code_mappings() against fabricated maps rows.

Usage: harness.py <tool.py> <case>
Cases (each builds one user-owned payload file and fabricates its /proc maps row):
  A-inode-mismatch      row claims a wrong inode for the real file at the path
  B-dev-mismatch-user   row claims a wrong dev for a user-owned (uid != 0) file
  C-shrink              os.read returns 4 bytes then EOF (file shrank after fstat)
  D-chunk-break-hang    same seam as C; a mutant without the EOF break loops forever
  E-dedupe-two-inodes   two rows, same path, different inodes (bad one first)

Prints one JSON line {"case", "ok", "detail"}. ok=true means the tool showed the
guard behavior (expected for the pristine tool); ok=false or a hang kills a mutant.
"""
import builtins
import importlib.util
import io
import json
import os
import sys
import tempfile

tool, case = sys.argv[1], sys.argv[2]
spec = importlib.util.spec_from_file_location("live", tool)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

d = tempfile.mkdtemp(prefix="m3seam-")
P = os.path.join(d, "payload.bin")
body = bytes(range(256)) * 400
with open(P, "wb") as fh:
    fh.write(body)
st = os.stat(P)
dev = "%02x:%02x" % (os.major(st.st_dev), os.minor(st.st_dev))
ino = str(st.st_ino)


def row(perm, dv, ino_, path):
    return f"7f0000001000-7f0000002000 {perm} 00000000 {dv} {ino_} {path}"


ROWS = {
    "A-inode-mismatch": [row("r-xp", dev, "999999", P)],
    "B-dev-mismatch-user": [row("r-xp", "ff:ff", ino, P)],
    "C-shrink": [row("r-xp", dev, ino, P)],
    "D-chunk-break-hang": [row("r-xp", dev, ino, P)],
    "E-dedupe-two-inodes": [row("r-xp", "ff:ff", "999999", P), row("r-xp", dev, ino, P)],
}
rows = ROWS[case]

real_open = builtins.open


def fake_open(path, *a, **k):
    if isinstance(path, str) and path.endswith("/maps"):
        return io.StringIO("\n".join(rows) + "\n")
    return real_open(path, *a, **k)


builtins.open = fake_open
if case in ("C-shrink", "D-chunk-break-hang"):
    real_read = os.read
    state = {"n": 0}

    def fake_read(fd, count):
        state["n"] += 1
        if state["n"] == 1:
            return real_read(fd, min(count, 4))
        return b""

    os.read = fake_read

got = m.code_mappings(424242)
builtins.open = real_open
ents = got.get("mappings") or []
detail = {"n_entries": len(ents), "entries": ents}

if case in ("A-inode-mismatch", "B-dev-mismatch-user"):
    ok = len(ents) == 1 and ents[0].get("opened") is False \
        and ents[0].get("reason") == "path-is-not-the-mapped-file"
elif case in ("C-shrink", "D-chunk-break-hang"):
    ok = len(ents) == 1 and ents[0].get("opened") is False \
        and ents[0].get("reason") == "file-shrank-while-hashed"
elif case == "E-dedupe-two-inodes":
    ok = (any(e.get("opened") is True and e.get("inode") == ino for e in ents)
          and any(e.get("opened") is False and e.get("inode") == "999999" for e in ents))
else:
    ok = False
print(json.dumps({"case": case, "ok": ok, "detail": detail}))
