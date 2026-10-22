#!/usr/bin/env python3
"""Read-only: receipt log_lines against the committed raw server logs, the build
line in the raw log, and the prompt-size and error lines for the load cells."""
import json
import pathlib
import re

SCR = pathlib.Path("/fast/scratch/hyaku/kama-r25a2w2/RerunC2Counter")
RAW = SCR / "committed-raw/.ufo/waves/round-25/final/raw"
d = json.loads((SCR / "receipt-fa3b62ae.json").read_text())

print("== receipt log_lines vs committed server.log ==")
for c in d["cells"]:
    raw_lines = (RAW / f"{c['id']}.server.log").read_text(errors="replace").splitlines()
    rl = c["log_lines"]
    same = rl == raw_lines
    subset = all(x in raw_lines for x in rl)
    print(f"{c['id']:3} receipt_lines={len(rl):3} raw_lines={len(raw_lines):4} identical={same} receipt_subset_of_raw={subset}")

print()
print("== build line in raw log (first match per cell, K1 and L1 shown) ==")
for cid in ("K1", "L1"):
    text = (RAW / f"{cid}.server.log").read_text(errors="replace")
    m = [x for x in text.splitlines() if re.search(r"build|version", x, re.I)][:3]
    print(cid, m)

print()
print("== load cells: server-side prompt size and error lines ==")
for cid in ("L1", "L2", "L3"):
    text = (RAW / f"{cid}.server.log").read_text(errors="replace").splitlines()
    prompts = [x[:160] for x in text if "task.n_tokens = 1000" in x]
    errs = [x[:200] for x in text if re.search(r"exceed|error|failed", x, re.I)]
    print(f"{cid}: task.n_tokens=1000 lines={len(prompts)}")
    for p in prompts:
        print("   ", p)
    print(f"   error-like lines={len(errs)}")
    for e in errs[:4]:
        print("   ", e)
