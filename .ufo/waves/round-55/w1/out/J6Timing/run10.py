#!/usr/bin/env python3
"""J6Timing: run the frozen round-55 C1 counter ten times against the fixture mutant
(live tool at 2fc5c27... flips one mapped exec byte of every libggml-cpu variant in a
tight loop from just before ready.json until release) and tabulate the legs."""
import json
import os
import re
import subprocess
import sys
import time

S = "/fast/scratch/hyaku/kama-r55/w1/J6Timing"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
COUNTER = os.path.join(LANE, "tools/round54-replay-code-audit.py")
TIP = "2fc5c271956d278b417fd50f7a3c348ea4a7c10a"
N = 10

os.makedirs(os.path.join(S, "logs"), exist_ok=True)
rows = []
for i in range(1, N + 1):
    out = os.path.join(S, "logs", f"mut{i}.out")
    t0 = time.time()
    p = subprocess.run([sys.executable, COUNTER, "--repo", os.path.join(S, "lane"),
                        "--tip", TIP, "--scratch", os.path.join(S, f"run{i}"),
                        "--out", out], capture_output=True, text=True)
    dt = time.time() - t0
    text = open(out).read() if os.path.isfile(out) else p.stdout
    lines = text.splitlines()
    summ = lines[0] if lines else ""
    legs = dict(re.findall(r"(\w+)=([^\s]+)", lines[1] if len(lines) > 1 else ""))
    details = [ln[8:] for ln in lines if ln.startswith("detail: ")]
    tags = {}
    for d in details:
        m = re.match(r"(code|twopass|rehash|envnames|sealed|bind) (b\d|kill): (.*)", d)
        if m:
            tags.setdefault(m.group(2), []).append(m.group(3))
    rec = {"run": i, "exit": p.returncode, "secs": round(dt, 1),
           "met": legs.get("met"), "twopass": legs.get("twopass"),
           "rehash": legs.get("rehash"), "code": legs.get("code"),
           "coderuns": legs.get("coderuns"), "anon": legs.get("anon"),
           "twopass_trip_replays": sum(1 for b, ds in tags.items()
                                       if any("two observation passes" in x for x in ds)),
           "code_trip_replays": sum(1 for b, ds in tags.items()
                                    if any("differ from the archive member" in x for x in ds)),
           "rehash_trip_replays": sum(1 for b, ds in tags.items()
                                      if any("changed after the observation" in x for x in ds)),
           "clean_replays": sum(1 for b, ds in tags.items()
                                if not any(("two observation passes" in x or
                                            "differ from the archive member" in x or
                                            "changed after the observation" in x) for x in ds)),
           "summary": summ}
    rows.append(rec)
    print(json.dumps(rec, sort_keys=True))
    sys.stdout.flush()

with open(os.path.join(S, "logs", "series.json"), "w") as fh:
    json.dump(rows, fh, indent=1, sort_keys=True)
print("--- totals ---")
print("runs:", len(rows),
      "met=True:", sum(1 for r in rows if r["met"] == "True"),
      "twopass_trip_replays:", sum(r["twopass_trip_replays"] for r in rows),
      "rehash_trip_replays:", sum(r["rehash_trip_replays"] for r in rows),
      "code_trip_replays:", sum(r["code_trip_replays"] for r in rows),
      "clean_replays:", sum(r["clean_replays"] for r in rows))
