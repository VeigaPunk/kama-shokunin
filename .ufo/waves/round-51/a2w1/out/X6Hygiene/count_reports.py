#!/usr/bin/env python3
"""Count landed reports for kama round-51 wave a2w1 (66 seats)."""
import json, os, sys, datetime
OUT = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1"
spec = json.load(open(os.path.join(OUT, "spec.json")))
names = [i["name"] for i in spec["items"]]
root = os.path.join(OUT, "out")
landed, missing = [], []
for n in names:
    ok = os.path.isfile(os.path.join(root, n + ".md"))
    if not ok:
        d = os.path.join(root, n)
        if os.path.isdir(d):
            for dp, _, fs in os.walk(d):
                if any(f.endswith(".md") for f in fs):
                    ok = True
                    break
    (landed if ok else missing).append(n)
print(f"at {datetime.datetime.now().isoformat(timespec='seconds')} landed={len(landed)}/66")
print("missing:", " ".join(missing) if missing else "(none)")
sys.exit(0 if len(landed) >= 60 else 1)
