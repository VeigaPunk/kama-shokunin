#!/usr/bin/env python3
"""PoC: untrusted TSV robustness — non-digit capture group crashes pin-watch."""
import importlib.util, os, subprocess, sys, tempfile

spec = importlib.util.spec_from_file_location(
    "pinwatch", "/fast/scratch/kama-r41/clone/tools/pin-watch.py")
pw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pw)

root = tempfile.mkdtemp(prefix="r41b08-tsv-")
os.makedirs(os.path.join(root, "tags"))
O = "0" * 40
with open(os.path.join(root, "tags", "e.txt"), "w") as fh:
    fh.write(f"{O}\trefs/tags/v1.2-hotfix\n{O}\trefs/tags/v1.2.3\n")

HDR = "engine\trepo\ttag_regex\tpin\tsource\n"

# regex with a capturing group that is not digits -> int(g) must crash
pins = os.path.join(root, "pins.tsv")
with open(pins, "w") as fh:
    fh.write(HDR)
    fh.write("e\thttps://example.invalid/e.git\tv(\\d+)-([a-z]+)\tv1.2-hotfix\tS000\n")

cmd = [sys.executable, "/fast/scratch/kama-r41/clone/tools/pin-watch.py",
       "check", "--pins", pins, "--tags-dir", os.path.join(root, "tags")]
p = subprocess.run(cmd, capture_output=True, text=True)
print("exit code:", p.returncode)
print("--- stdout ---")
print(p.stdout[-500:])
print("--- stderr (tail) ---")
print(p.stderr[-700:])
