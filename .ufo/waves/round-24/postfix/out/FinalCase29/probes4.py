#!/usr/bin/env python3
"""Fourth bounded probe batch for PG29: provenance of the registered result.

V3: the lane's WORKING-TREE errata ledger is corrupted.  The audit must read
    the committed tip blob, so the registered clean verdict must survive.
V4: the fleet's WORKING-TREE report is rewritten.  The audit must read the
    committed fleet bytes, so the registered clean verdict must survive.

Both variants are LOCAL COPIES; the grid fixture is never mutated.  Each
variant's changed input state is stated explicitly.
"""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

BASE = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase29/tmp/"
            "promisor-grid-8qm678ir/current/000")
AUDIT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase29/clone/"
             "tools/report-landing-audit.py")
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase29/out")
WORK = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase29/tmp/variants")

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def run(label, lane, fleet):
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json"]
    p = subprocess.run(argv, capture_output=True, env=ENV, cwd=str(lane),
                       timeout=60)
    rec = {"label": label, "argv": argv, "exit": p.returncode,
           "stderr": p.stderr.decode(errors="replace").strip()[:400]}
    try:
        doc = json.loads(p.stdout.decode())
        rec["summary"] = doc.get("summary")
        rec["defects"] = [(d.get("kind"), d.get("token"), d.get("corrected_by"))
                          for r in doc.get("results", [])
                          for d in r.get("defects", [])]
    except ValueError:
        rec["stdout_head"] = p.stdout.decode(errors="replace")[:300]
    return rec


def fresh(name):
    dest = WORK / name
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BASE, dest, symlinks=True)
    return dest / "lane", dest / "fleet"


variants = []

lane, fleet = fresh("v3-worktree-errata-corrupted")
tvl = lane / "registry" / "report-landing-errata.tsv"
tvl.write_text("1\tlanded-omitted\tdeadbeef\tdeadbeef\tev\n", encoding="utf-8")
variants.append(run("V3-worktree-errata-corrupted (working-tree ledger "
                     "replaced; committed blob unchanged)", lane, fleet))

lane, fleet = fresh("v4-worktree-report-rewritten")
rel = fleet / ".ufo" / "reports" / "round-1" / "kama.md"
rel.write_text("# kama round 1\n\n## Landed changes\n\n- deadbeef\n",
               encoding="utf-8")
variants.append(run("V4-worktree-report-rewritten (working-tree report "
                     "replaced; committed fleet bytes unchanged)", lane, fleet))

(OUT / "probes4.json").write_text(json.dumps(variants, indent=1, sort_keys=True),
                                   encoding="utf-8")
for v in variants:
    print(v["label"])
    print("  exit", v["exit"], "stderr", v["stderr"][:200])
    if v.get("summary"):
        s = v["summary"]
        print("  status", s.get("status"), "uncorrected", s.get("uncorrected"),
              "corrected", s.get("corrected"), "rows", s.get("errata_rows"),
              "unmatched", s.get("errata_unmatched"),
              "invalid", s.get("errata_invalid"))
    if v.get("defects") is not None:
        print("  defects", v["defects"])
