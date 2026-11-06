#!/usr/bin/env python3
"""r90 EX02 R2 reconstruction: the per-call seconds r89 harm-final.out lost to a missing `bc`.

r89 `.ufo/waves/round-89/measured/harm-final.out` lines 13-27 print
    <id> <verdict> <reason> <seconds>
with the seconds field empty because the formatter called `bc` (absent). Only
four medians survived (base LFM3-1.7B 0.136, base * 0.138, M' 0.251, M' * 0.362).
No raw per-run file and no generator script were committed, so the original
samples cannot be recovered. This script RE-MEASURES the same configuration at
the same two probe revisions with the same argv, interleaved, 5 runs each, and
prints per-call seconds in Python (no bc). Labelled RECONSTRUCTION: the numbers
are new samples, not the lost ones; the surviving medians are shown for shape.

Probes (bytes at the r89 revisions, extracted read-only from the lane repo):
  R89B = 56174a1f:tools/kama-probe.sh  sha256 99dd1ab8...
  R89M = 5b1e0fb3:tools/kama-probe.sh  sha256 c15ffca8...  (== r90 base)
GET only: the probe issues only GETs; no POST, no load/unload.
"""
import json
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path

OUT = Path(__file__).resolve().parent
PROBES = {"R89B": Path(os.environ["R89B_PROBE"]), "R89M": Path(os.environ["R89M_PROBE"])}
CONFIGS = [("R89B", "LFM3-1.7B"), ("R89B", "*"),
           ("R89M", "LFM3-1.7B"), ("R89M", "LFM3-1.7B-Uncensored"),
           ("R89M", "LFM3-Omni-2B"), ("R89M", "LFM3-VL-2B"), ("R89M", "*")]
SURVIVING = {("R89B", "LFM3-1.7B"): 0.136, ("R89B", "*"): 0.138,
             ("R89M", "LFM3-1.7B"): 0.251, ("R89M", "*"): 0.362}
RUNS = 5
ENV = dict(os.environ)
ENV["TMPDIR"] = os.environ["LAT_TMPDIR"]
Path(ENV["TMPDIR"]).mkdir(parents=True, exist_ok=True)


def p90(vals):
    s = sorted(vals)
    k = max(1, int(round(0.9 * len(s) + 0.5)) - 1)
    return s[min(k, len(s) - 1)]


def one(probe, expect):
    t0 = time.perf_counter()
    cp = subprocess.run(["bash", str(probe), "check", "--port", "1234",
                         "--expect", expect, "--json"],
                        capture_output=True, text=True, env=ENV, cwd=str(OUT))
    sec = time.perf_counter() - t0
    verdict = reason = "?"
    try:
        row = json.loads(cp.stdout)["rows"][0]
        verdict, reason = row.get("verdict", "?"), row.get("reason", "?")
    except Exception:
        pass
    return sec, cp.returncode, verdict, reason


def main():
    for key, probe in PROBES.items():
        one(probe, "LFM3-1.7B")          # warmup, unrecorded
    rows = {c: [] for c in CONFIGS}
    for _ in range(RUNS):
        for cfg in CONFIGS:
            rows[cfg].append(one(PROBES[cfg[0]], cfg[1]))
    print("# RECONSTRUCTION at r89 revisions, GET only, 5 interleaved runs each")
    print("# R89B=99dd1ab8 (56174a1f)  R89M=c15ffca8 (5b1e0fb3)")
    for cfg in CONFIGS:
        v = rows[cfg]
        secs = [round(r[0], 3) for r in v]
        med = round(statistics.median([r[0] for r in v]), 3)
        surv = SURVIVING.get(cfg)
        print(f"SECONDS {cfg[0]:4s} expect={cfg[1]:22s} runs={secs} "
              f"median={med} p90={round(p90([r[0] for r in v]), 3)} "
              f"exits={sorted({r[1] for r in v})} verdict={sorted({r[2] for r in v})} "
              f"reason={sorted({r[3] for r in v})} "
              f"surviving_median={surv if surv is not None else '-'}")
    (OUT / "r89-reconstruct.json").write_text(json.dumps(
        {f"{k[0]}|{k[1]}": {"runs": [round(r[0], 3) for r in v],
                            "median": round(statistics.median([r[0] for r in v]), 3),
                            "p90": round(p90([r[0] for r in v]), 3),
                            "exits": sorted({r[1] for r in v}),
                            "verdicts": sorted({r[2] for r in v}),
                            "reasons": sorted({r[3] for r in v}),
                            "surviving_median": SURVIVING.get(k)}
         for k, v in rows.items()}, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
