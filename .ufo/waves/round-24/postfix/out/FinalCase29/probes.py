#!/usr/bin/env python3
"""Bounded falsification probes for PG29 (current arm, pinned commit 92063cf).

Every probe is a read-only invocation of the PINNED tools/report-landing-audit.py
against the kept PG29 fixture.  No repository is mutated; the only new inputs
are errata TSV files written under the seat's own out/ directory and passed
with --errata PATH (the auditor then does not read the committed ledger).
"""
import hashlib
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

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")


def env():
    return dict(ENV)


def inventory(repo):
    out = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                          "-C", str(repo), "cat-file", "--batch-all-objects",
                          "--batch-check=%(objectname)"],
                         capture_output=True, env=env())
    return sorted(out.stdout.decode().split())


def run(label, extra):
    before = {"lane": inventory(LANE), "fleet": inventory(FLEET)}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(LANE),
            "--fleet-repo", str(FLEET), "--rounds", "1", "--json"] + extra
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(FIX),
                       timeout=60)
    after = {"lane": inventory(LANE), "fleet": inventory(FLEET)}
    rec = {"label": label, "argv": argv, "exit": p.returncode,
           "stderr": p.stderr.decode(errors="replace").strip(),
           "objects_acquired": {k: sorted(set(after[k]) - set(before[k]))
                                for k in after}}
    try:
        doc = json.loads(p.stdout.decode())
        rec["document"] = doc
        rec["summary"] = doc.get("summary")
        rec["defects"] = [(d.get("kind"), d.get("token"), d.get("corrected_by"))
                          for r in doc.get("results", [])
                          for d in r.get("defects", [])]
    except ValueError:
        rec["document"] = None
        rec["stdout"] = p.stdout.decode(errors="replace")[:2000]
    return rec


def write_tsv(name, rows):
    path = OUT / name
    path.write_text("".join("\t".join(r) + "\n" for r in rows),
                    encoding="utf-8")
    return path


probes = []

# A: the ordinary absent-token finding, with the ledger disabled.
probes.append(run("A-no-errata", ["--no-errata"]))

# B: selected-ledger filtering -- the correcting row lives in round 2, which
#    this audit (round 1) does not select.
p_b = write_tsv("errata-round2.tsv",
                [("2", "unresolved-full-hash", SPLICED, REAL, "ev")])
probes.append(run("B-errata-unselected-round", ["--errata", str(p_b)]))

# C: scoped opacity -- the correction names a 40-hex that no audited
#    repository holds and no local object references.
p_c = write_tsv("errata-absent-correction.tsv",
                [("1", "unresolved-full-hash", SPLICED,
                  "0" * 40, "ev")])
probes.append(run("C-errata-absent-correction", ["--errata", str(p_c)]))

# D: the authorized correction, exactly as committed (ledger read from the
#    lane tip) -- the registered PG29 path.
probes.append(run("D-committed-ledger", []))

# E: an authorized correction whose row matches no defect.
p_e = write_tsv("errata-unmatched.tsv",
                [("1", "unresolved-full-hash", "1" * 40, REAL, "ev")])
probes.append(run("E-errata-unmatched", ["--errata", str(p_e)]))

(OUT / "probes.json").write_text(json.dumps(probes, indent=1,
                                            sort_keys=True),
                                  encoding="utf-8")
for pr in probes:
    print(pr["label"], "exit", pr["exit"],
          "defects", pr.get("defects"),
          "acq", pr["objects_acquired"],
          "stderr", pr["stderr"][:160])
    if pr.get("summary"):
        s = pr["summary"]
        print("   summary status", s.get("status"),
              "uncorrected", s.get("uncorrected"),
              "corrected", s.get("corrected"),
              "errata_rows", s.get("errata_rows"),
              "errata_unmatched", s.get("errata_unmatched"),
              "errata_invalid", s.get("errata_invalid"),
              "by_kind", s.get("by_kind"))
