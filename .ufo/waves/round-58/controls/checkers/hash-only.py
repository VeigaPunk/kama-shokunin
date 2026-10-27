#!/usr/bin/env python3
import argparse, hashlib, subprocess
ap = argparse.ArgumentParser(); ap.add_argument("--repo"); ap.add_argument("--tip"); ap.add_argument("--out"); a = ap.parse_args()
b = subprocess.run(["git", "-C", a.repo, "show", a.tip + ":tools/round56-env-leg-battery.py"], capture_output=True).stdout
g = subprocess.run(["git", "-C", "/home/vgpnk/Projects/shokunin/kama-shokunin", "show", "dcd69473dd7e33b316e2ba238a48e5119a6cd809:tests/round58-battery-variants/genuine.py"], capture_output=True).stdout
raise SystemExit(0 if hashlib.sha256(b).digest() == hashlib.sha256(g).digest() else 1)
