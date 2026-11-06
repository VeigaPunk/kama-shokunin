#!/usr/bin/env python3
"""GET-only operator-router timing driver (round-89 EX02 harm sweep).

Runs `bash <probe> check --port 1234 --expect <id> --json` 5x per id for two
probe files in one interleaved sequence (B then M2 per round) and records the
wall time in milliseconds plus the verdict/reason parsed from --json output.
No POST, no load/unload: the probe issues only GET /v1/models, GET /health and
(maybe) GET /props.
"""
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

IDS = ["LFM3-1.7B", "LFM3-1.7B-Uncensored", "LFM3-Omni-2B", "LFM3-VL-2B"]
PROBES = {
    "B": "/fast/scratch/hyaku/kama-r89/EX02HarmSweep/wtb/tools/kama-probe.sh",
    "M2": "/fast/scratch/hyaku/kama-r89/EX02HarmSweep/wt/tools/kama-probe.sh",
}
OUT = Path("/fast/scratch/hyaku/kama-r89/EX02HarmSweep")
RUNS = 5

env = dict(os.environ)
env["TMPDIR"] = str(OUT / "tmp-probe")
Path(env["TMPDIR"]).mkdir(parents=True, exist_ok=True)

rows = []
# warmup (one per probe, not recorded)
for key, probe in PROBES.items():
    subprocess.run(["bash", probe, "check", "--port", "1234", "--expect", IDS[0], "--json"],
                   capture_output=True, env=env, cwd=str(OUT))

for run in range(1, RUNS + 1):
    for key, probe in PROBES.items():
        for mid in IDS:
            t0 = time.perf_counter()
            cp = subprocess.run(["bash", probe, "check", "--port", "1234", "--expect", mid,
                                 "--json", "--timeout", "5", "--connect-timeout", "2"],
                                capture_output=True, text=True, env=env, cwd=str(OUT))
            ms = (time.perf_counter() - t0) * 1000.0
            verdict = reason = "?"
            try:
                doc = json.loads(cp.stdout)
                row = doc["rows"][0]
                verdict = row.get("verdict", "?")
                reason = row.get("reason", "?")
            except Exception:
                pass
            rows.append({"probe": key, "id": mid, "run": run, "exit": cp.returncode,
                         "verdict": verdict, "reason": reason, "ms": round(ms, 1)})

(OUT / "operator-1234-runs.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))

print(f"{'id':28s} {'probe':4s} {'verdict':14s} {'reason':28s} median_ms")
for mid in IDS:
    for key in ("B", "M2"):
        sel = [r for r in rows if r["id"] == mid and r["probe"] == key]
        med = statistics.median([r["ms"] for r in sel])
        print(f"{mid:28s} {key:4s} {sel[0]['verdict']:14s} {sel[0]['reason']:28s} {med:8.1f}"
              f"  runs={[r['ms'] for r in sel]} exits={[r['exit'] for r in sel]}")
print()
for mid in IDS:
    b = statistics.median([r["ms"] for r in rows if r["id"] == mid and r["probe"] == "B"])
    m = statistics.median([r["ms"] for r in rows if r["id"] == mid and r["probe"] == "M2"])
    print(f"DELTA {mid:28s} B={b:8.1f}ms M2={m:8.1f}ms added={m-b:8.1f}ms")
