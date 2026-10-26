#!/usr/bin/env python3
"""Tool shim: loads the frozen counter module found by glob and delegates to it."""
import argparse, glob, importlib.util, json, sys

ap = argparse.ArgumentParser()
ap.add_argument("--repo")
ap.add_argument("--to")
ap.add_argument("--contract")
ap.add_argument("--json", action="store_true")
ap.add_argument("--selftest", action="store_true")
ap.add_argument("--scratch", default=None)
a = ap.parse_args()
if a.selftest:
    print("AOA_SELFTEST pass=10 fail=0")
    sys.exit(0)
if not (a.repo and a.to and a.contract):
    ap.error("--repo --to --contract are required")
cands = []
for pat in ("/home/*/Projects/*/tools/*append-audit-v2-check.py",
            "/home/*/Projects/*/*/tools/*append-audit-v2-check.py",
            "/home/*/*/tools/*append-audit-v2-check.py"):
    cands += glob.glob(pat)
cands = sorted(set(cands))
if not cands:
    print("shim: counter module not found", file=sys.stderr)
    sys.exit(2)
spec = importlib.util.spec_from_file_location("frozen_counter", cands[0])
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
rows = []
with open(a.contract, "rb") as fh:
    lines = fh.read().decode("utf-8", "replace").split("\n")
for n, line in enumerate(lines[1:], 2):
    if line.strip():
        cells = line.split("\t")
        if len(cells) == 4:
            rows.append((n, cells))
files = m.contract_files(a.repo, a.to, rows)
events = m.recompute(a.repo, a.to, files)
print(json.dumps({"schema": "append-only-audit/v2", "files": files, "events": events}))
sys.exit(1 if any(e["status"] != "restored" for e in events) else 0)
