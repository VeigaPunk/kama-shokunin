#!/usr/bin/env python3
"""Full summaries for the ledger arms (C/D/E) of the fleet-only-tag consumer,
plus the driver's own --after argument handling.
"""
import json
import subprocess
import sys
from pathlib import Path

S = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalConsumer03")
F = S / "fix"
AFTER = S / "clone/tools/report-landing-audit.py"
ENV = {"PATH": "/usr/bin:/bin", "TMPDIR": str(S / "tmp"),
       "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def run(tool, draft, errata, label):
    cmd = [sys.executable, str(tool), "--lane-repo", str(F / "lane"),
           "--fleet-repo", str(F / "fleet"), "--branch", "master", "--rounds", "1",
           "--report", f"1={draft}", "--json"]
    cmd += ["--errata", str(errata)] if errata else ["--no-errata"]
    p = subprocess.run(cmd, capture_output=True, timeout=60, env=ENV)
    out = {"label": label, "argv": cmd, "exit": p.returncode}
    if p.returncode in (0, 1):
        d = json.loads(p.stdout.decode("utf-8", "replace"))
        out["summary"] = d["summary"]
        out["defects"] = [x for r in d["results"] for x in r["defects"]]
    else:
        out["stderr"] = p.stderr.decode("utf-8", "replace").strip()[-300:]
    print(json.dumps(out, indent=1, sort_keys=True))
    return out


records = []
records.append(run(AFTER, F / "draft.md", None, "C0 no ledger"))
records.append(run(AFTER, F / "draft.md", F / "errata-wrong-type.tsv",
                   "C1 ledger: correction = fleet-only blob (wrong type)"))
records.append(run(AFTER, F / "draft.md", F / "errata-valid.tsv",
                   "D1 ledger: correction = the valid lane commit"))
records.append(run(AFTER, F / "draft.md", F / "errata-unselected.tsv",
                   "E1 ledger: row for UNSELECTED round 2"))
(S / "out/ledger-arms.json").write_text(json.dumps(records, indent=1, sort_keys=True))
