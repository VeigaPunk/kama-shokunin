#!/usr/bin/env python3
"""Second bounded probe batch for PG29: selected-ledger filtering and scoped
opacity of the errata correction.  Read-only invocations of the PINNED
tools/report-landing-audit.py against the kept PG29 fixture (no repo
mutation, no new grid cell)."""
import json
import os
from pathlib import Path
import subprocess
import sys

FIX = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase29/tmp/"
           "promisor-grid-8qm678ir/current/000")
LANE = FIX / "lane"
FLEET = FIX / "fleet"
AUDIT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase29/clone/"
             "tools/report-landing-audit.py")
OUT = Path("/fast/scratch/hyaku/kama-r24/postfix/FinalCase29/out")
SPLICED = "58866b563cd900dd894ef21bc863486bcb35b56c"
REAL = "58866b563cd900df310588effe79028efc104c33"
BLOB = "56d7b323865c731da81e0225cf109d66f0480919"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def inventory(repo):
    out = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                          "-C", str(repo), "cat-file", "--batch-all-objects",
                          "--batch-check=%(objectname)"],
                         capture_output=True, env=ENV)
    return sorted(out.stdout.decode().split())


def run(label, extra):
    before = {"lane": inventory(LANE), "fleet": inventory(FLEET)}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(LANE),
            "--fleet-repo", str(FLEET), "--rounds", "1", "--json"] + extra
    p = subprocess.run(argv, capture_output=True, env=ENV, cwd=str(FIX),
                       timeout=60)
    after = {"lane": inventory(LANE), "fleet": inventory(FLEET)}
    rec = {"label": label, "argv": argv, "exit": p.returncode,
           "stderr": p.stderr.decode(errors="replace").strip(),
           "objects_acquired": {k: sorted(set(after[k]) - set(before[k]))
                                for k in after}}
    try:
        doc = json.loads(p.stdout.decode())
        rec["summary"] = doc.get("summary")
        rec["defects"] = [(d.get("kind"), d.get("token"), d.get("corrected_by"))
                          for r in doc.get("results", [])
                          for d in r.get("defects", [])]
    except ValueError:
        rec["stdout"] = p.stdout.decode(errors="replace")[:1500]
    return rec


def write_tsv(name, rows):
    path = OUT / name
    path.write_text("".join("\t".join(r) + "\n" for r in rows),
                    encoding="utf-8")
    return path


probes = []
# F: the ledger row names the right token but the wrong kind.
p = write_tsv("errata-kind-mismatch.tsv",
              [("1", "landed-unresolved", SPLICED, REAL, "ev")])
probes.append(run("F-errata-kind-mismatch", ["--errata", str(p)]))

# G: the correction names an object that IS present but is a blob, not a
#    commit: a proved local mismatch, never a refusal.
p = write_tsv("errata-blob-correction.tsv",
              [("1", "unresolved-full-hash", SPLICED, BLOB, "ev")])
probes.append(run("G-errata-blob-correction", ["--errata", str(p)]))

# H: the ledger row's token differs only in case from the defect token.
p = write_tsv("errata-case-mismatch.tsv",
              [("1", "unresolved-full-hash", SPLICED.upper(), REAL, "ev")])
probes.append(run("H-errata-case-mismatch", ["--errata", str(p)]))

# I: the ledger row corrects a DIFFERENT token of the same kind and round.
p = write_tsv("errata-other-token.tsv",
              [("1", "unresolved-full-hash", "1" * 40, REAL, "ev")])
probes.append(run("I-errata-other-token", ["--errata", str(p)]))

(OUT / "probes2.json").write_text(json.dumps(probes, indent=1, sort_keys=True),
                                   encoding="utf-8")
for pr in probes:
    print(pr["label"], "exit", pr["exit"], "defects", pr.get("defects"),
          "acq", pr["objects_acquired"], "stderr", pr["stderr"][:200])
    if pr.get("summary"):
        s = pr["summary"]
        print("   status", s.get("status"), "uncorrected", s.get("uncorrected"),
              "corrected", s.get("corrected"), "rows", s.get("errata_rows"),
              "unmatched", s.get("errata_unmatched"),
              "invalid", s.get("errata_invalid"))
