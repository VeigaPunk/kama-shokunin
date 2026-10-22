#!/usr/bin/env python3
"""No-harm check on the real population: pinned candidate vs the one-line
errata-boundary correction, lane = scratch clone at 2e254a1 (same commits and
same committed registry ledger as production), fleet = the real fleet repo,
read-only. The rounds 10-20 population contains every committed ledger row
(round 10, 18, 20), so the correction must not change one byte of the
verdict document.
"""
import json
import subprocess
import sys
from pathlib import Path

BASE = Path("/fast/scratch/hyaku/kama-r24/falsify/CodeErrataBoundary")
PINNED = BASE / "tools/report-landing-audit.py"
FIXED = BASE / "out/audit.errata-scoped.py"
LANE = BASE
FLEET = Path("/home/vgpnk/Projects/shokunin")
out = {}
for tag, auditor in (("pinned", PINNED), ("scoped", FIXED)):
    argv = [sys.executable, str(auditor), "--lane-repo", str(LANE),
            "--fleet-repo", str(FLEET), "--rounds", "10-20", "--json"]
    p = subprocess.run(argv, capture_output=True, cwd=str(BASE))
    doc = None
    try:
        doc = json.loads(p.stdout)
    except ValueError:
        pass
    out[tag] = {"exit": p.returncode, "stderr": p.stderr.decode().strip()[:400],
                "summary": doc["summary"] if doc else None,
                "errata_unmatched": doc.get("errata_unmatched") if doc else None,
                "errata_invalid": doc.get("errata_invalid") if doc else None}
    print(tag, p.returncode, json.dumps(out[tag]["summary"], sort_keys=True),
          flush=True)
same = (out["pinned"]["exit"] == out["scoped"]["exit"]
        and out["pinned"]["summary"] == out["scoped"]["summary"])
out["identical_verdict"] = same
(BASE / "out" / "real_no_harm.json").write_text(
    json.dumps(out, indent=1, sort_keys=True), encoding="utf-8")
print("identical_verdict:", same)
