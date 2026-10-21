#!/usr/bin/env python3
"""Fail-closed route check (round 21), scratch only.

Runs the FIX copy's main() in-process with one scratch member unreadable and
writes its receipt. subprocess.Popen is tripwired: any child launch raises, so
no llama-server is started. The model is a 16-byte dummy that is only hashed.
Usage: failclosed_main.py LANEFIX TREE OUT MODEL MODEL_SHA256 PROBE
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
LANEFIX, TREE, OUT, MODEL, PROBE = (Path(a).resolve() for a in (sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[6]))
MODEL_SHA = sys.argv[5]
SCRATCH = Path("/tmp/kama-r21-LinksTreeDeterminism").resolve()
assert all(p.is_relative_to(SCRATCH) for p in (LANEFIX, TREE, MODEL)), "scratch only"


def launch_tripwire(*a, **k):
    raise RuntimeError("TRIPWIRE: child launch attempted")


subprocess.Popen = launch_tripwire

spec = importlib.util.spec_from_file_location("kama_fix", LANEFIX / "tools/kama-llamacpp-live.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

target = TREE / "libggml-cpu-haswell.so"
mode = target.stat().st_mode & 0o7777
receipt_path = OUT / "main-failclosed-receipt.json"
os.chmod(target, 0)
try:
    rc = m.main(["--server", str(TREE / "llama-server"), "--model", str(MODEL),
                 "--model-sha256", MODEL_SHA, "--probe", str(PROBE),
                 "--out", str(receipt_path)])
finally:
    os.chmod(target, mode)

rec = json.loads(receipt_path.read_text())
print(json.dumps({
    "main_exit": rc,
    "outcome": rec.get("outcome"),
    "setup_error": rec.get("setup_error"),
    "internal_fault": rec.get("internal_fault"),
    "server_install_tree_sha256": rec["server"].get("install_tree_sha256"),
    "server_install_tree_members": len(rec["server"].get("install_tree") or {}),
    "child_pid": rec.get("child_pid"),
}, indent=1, sort_keys=True))
print("target_mode_restored", oct(target.stat().st_mode & 0o7777) == oct(mode), oct(mode))
