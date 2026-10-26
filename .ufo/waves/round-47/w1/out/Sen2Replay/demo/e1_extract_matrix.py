#!/usr/bin/env python3
"""E1: crafted archives against tools/kama-live-replay.py extract() (filter="data").

Each case is built in scratch, extracted into a fresh tree by the tool's own
extract() (imported from the lane file, not copied), then the filesystem is
scanned for anything that landed outside the tree.
"""
import importlib.util
import os
import shutil
import stat
import sys
import tarfile

TOOL = os.environ.get("KAMA_REPLAY", "/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-live-replay.py")
S = os.environ["S"]
ROOT = os.path.join(S, "e1")


def load_tool():
    spec = importlib.util.spec_from_file_location("klr", TOOL)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


klr = load_tool()


def reg(tf, name, data=b"x", mode=0o644):
    ti = tarfile.TarInfo(name)
    ti.size = len(data)
    ti.mode = mode
    import io
    tf.addfile(ti, io.BytesIO(data))


def sym(tf, name, target):
    ti = tarfile.TarInfo(name)
    ti.type = tarfile.SYMTYPE
    ti.linkname = target
    tf.addfile(ti)


def hard(tf, name, target):
    ti = tarfile.TarInfo(name)
    ti.type = tarfile.LNKTYPE
    ti.linkname = target
    tf.addfile(ti)


def special(tf, name, typ, major=0, minor=0):
    ti = tarfile.TarInfo(name)
    ti.type = typ
    ti.devmajor = major
    ti.devminor = minor
    tf.addfile(ti)


def build(path, kind):
    with tarfile.open(path, "w:gz") as tf:
        if kind == "plain":
            reg(tf, "ok.txt", b"ok")
        elif kind == "traversal":
            reg(tf, "../../escape-rel.txt", b"PWNED")
        elif kind == "absolute":
            reg(tf, os.path.join(ROOT, "escape-abs.txt"), b"PWNED")
        elif kind == "symlink-absolute":
            sym(tf, "lnk", "/etc/passwd")
        elif kind == "symlink-escape":
            sym(tf, "lnk2", "../../etc/passwd")
        elif kind == "hardlink-outside":
            hard(tf, "hl", "/etc/passwd")
        elif kind == "chardev":
            special(tf, "dev0", tarfile.CHRTYPE, 1, 3)
        elif kind == "fifo":
            special(tf, "fifo0", tarfile.FIFOTYPE)
        elif kind == "setuid":
            reg(tf, "suid", b"#!/bin/sh\n", mode=0o4755)
        elif kind == "exec-bit":
            reg(tf, "bin/tool", b"#!/bin/sh\nexit 0\n", mode=0o755)
        elif kind == "dotdot-name":
            # name that is exactly '..' after a directory component, plus a
            # harmless-looking inner '..' (should be refused by the filter)
            reg(tf, "a/../b.txt", b"PWNED")
        else:
            raise SystemExit(f"unknown kind {kind}")


def scan_escapes(marker_start):
    hits = []
    for base in (ROOT, os.path.dirname(ROOT), "/tmp"):
        try:
            for name in os.listdir(base):
                if name.startswith(marker_start) or name in ("escape-rel.txt", "pwn.txt"):
                    p = os.path.join(base, name)
                    hits.append((p, os.path.isfile(p) and open(p, "rb").read(16)))
        except OSError:
            pass
    return hits


def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    os.makedirs(ROOT)
    outside = os.path.join(ROOT, "OUTSIDE")
    os.makedirs(outside)
    kinds = ["plain", "traversal", "absolute", "symlink-absolute", "symlink-escape",
             "hardlink-outside", "chardev", "fifo", "setuid", "exec-bit", "dotdot-name"]
    results = {}
    for kind in kinds:
        arc = os.path.join(ROOT, f"{kind}.tar.gz")
        build(arc, kind)
        tree = os.path.join(ROOT, f"tree-{kind}")
        os.makedirs(tree)
        try:
            klr.extract(arc, tree)
            outcome = "extracted"
        except BaseException as exc:  # noqa: BLE001 - the point is the class
            outcome = f"refused:{type(exc).__name__}:{str(exc)[:80]}"
        # pre-existing symlink case needs the link in place before extraction
        if kind == "plain":
            linktree = os.path.join(ROOT, "tree-presymlink")
            os.makedirs(linktree)
            os.symlink(outside, os.path.join(linktree, "link"))
            arc2 = os.path.join(ROOT, "presymlink.tar.gz")
            with tarfile.open(arc2, "w:gz") as tf:
                reg(tf, "link/pwn.txt", b"PWNED")
            try:
                klr.extract(arc2, linktree)
                presym = "extracted"
            except BaseException as exc:  # noqa: BLE001
                presym = f"refused:{type(exc).__name__}:{str(exc)[:80]}"
            results["presymlink-dir"] = (
                presym, os.path.exists(os.path.join(outside, "pwn.txt")))
        # what landed where
        found = []
        for dirpath, dirnames, filenames in os.walk(ROOT):
            for n in filenames + dirnames:
                p = os.path.join(dirpath, n)
                if f"tree-{kind}" in p or p.startswith(os.path.join(ROOT, "tree-")) \
                        or p == arc or p.startswith(ROOT + "/tree"):
                    continue
        mode = None
        if kind == "setuid":
            p = os.path.join(tree, "suid")
            mode = oct(os.lstat(p).st_mode) if os.path.exists(p) else None
        if kind == "exec-bit":
            p = os.path.join(tree, "bin/tool")
            mode = oct(os.lstat(p).st_mode) if os.path.exists(p) else None
        entries = []
        for dirpath, dirnames, filenames in os.walk(tree):
            for n in filenames:
                entries.append(os.path.relpath(os.path.join(dirpath, n), tree))
        results[kind] = (outcome, entries, mode)
        print(f"CASE {kind:18s} {outcome[:100]:100s} inside={entries} mode={mode}")
    print("PRESYMLINK:", results["presymlink-dir"][0],
          "escaped=", results["presymlink-dir"][1])
    print("SCAN escapes:", scan_escapes("escape-"))
    leaked = [n for n in os.listdir(ROOT) if n.startswith("escape-")]
    print("LEAKED_OUTSIDE_TREES:", leaked)
    return 0


if __name__ == "__main__":
    sys.exit(main())
