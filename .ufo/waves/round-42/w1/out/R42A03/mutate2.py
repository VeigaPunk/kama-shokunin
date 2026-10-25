#!/usr/bin/env python3
"""R42A03 follow-up: blast-radius probes for the canon==head-table tautology.

M36: rename the capability name ONLY in the §Round-42 canonical list (2nd
     occurrence of the row) -> predicted survivor (canon() resolves to the head
     table via the backticked mention at line 117, so the §Round-42 list is
     never compared).
M37: change the first-working round ONLY in the §Round-42 canonical list ->
     predicted survivor (firsts derive from the same head table).
Then: import the counter and show which line canon() anchors on.
"""
import importlib.util
import json
import os
import re
import subprocess
import sys

SEAT = "/fast/scratch/kama-r42/seats/R42A03"
CLONE = os.path.join(SEAT, "clone")
OUT = os.path.join(SEAT, "out")
TMP = os.path.join(SEAT, "tmp")
TIP = "3d9bd8d72366e281fab291874524130428ee423d"
ROW = ("| digest-ledger | Find every full SHA-256 the lane's documents cite and "
       "classify it: a committed blob, a ledger-declared external artifact re-hashed "
       "on this host, an unverifiable digest with its reason, or a flagged known-wrong "
       "digest; exit 1 on any unexplained digest | `tools/digest-ledger.py`; "
       "`registry/digest-ledger.tsv` | 42 |")


def git(*a):
    p = subprocess.run(["git", "-C", CLONE, *a], capture_output=True, text=True)
    if p.returncode != 0:
        raise RuntimeError("git %s: %s" % (" ".join(a), p.stderr))
    return p.stdout.strip()


def counter(tip, outpath):
    env = dict(os.environ, TMPDIR=TMP)
    p = subprocess.run(
        [sys.executable, "tools/round42-selfdesc-reconcile.py",
         "--repo", CLONE, "--tip", tip, "--out", outpath],
        capture_output=True, text=True, cwd=CLONE, env=env, timeout=900)
    summary = ""
    for line in p.stdout.splitlines():
        if "mismatches=" in line:
            summary = line
    return {"exit": p.returncode, "summary": summary}


def nth_replace(text, old, new, which):
    idx = -1
    for _ in range(which):
        idx = text.index(old, idx + 1)
    return text[:idx] + new + text[idx + len(old):]


MUTS = [
    dict(id="M36", leg="probe: Round-42 canon name edit (2nd occurrence)",
         old=ROW, new=ROW.replace("| digest-ledger |", "| digest-ledgr |", 1),
         n=2, which=2),
    dict(id="M37", leg="probe: Round-42 canon first-working edit (2nd occurrence)",
         old="`tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 42 |",
         new="`tools/digest-ledger.py`; `registry/digest-ledger.tsv` | 43 |",
         n=2, which=2),
]

results = []
for m in MUTS:
    git("reset", "--hard", TIP)
    path = os.path.join(CLONE, "SCORECARD.md")
    text = open(path, encoding="utf-8").read()
    assert text.count(m["old"]) == m["n"], (m["id"], text.count(m["old"]))
    open(path, "w", encoding="utf-8").write(nth_replace(text, m["old"], m["new"], m["which"]))
    git("add", "SCORECARD.md")
    git("commit", "-q", "-m", "mutant %s: %s" % (m["id"], m["leg"]))
    sha = git("rev-parse", "HEAD")
    r = counter(sha, os.path.join(OUT, "%s.out" % m["id"]))
    results.append(dict(id=m["id"], leg=m["leg"], commit=sha, **r))
    print(m["id"], "->", r["exit"], r["summary"], flush=True)

git("reset", "--hard", TIP)

spec = importlib.util.spec_from_file_location(
    "c1", os.path.join(CLONE, "tools", "round42-selfdesc-reconcile.py"))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
sc = open(os.path.join(CLONE, "SCORECARD.md"), encoding="utf-8").read()
best, rows = mod.canon(sc)
print("canon(): best=%d rows=%d names=%s" % (best, len(rows), [r[0] for r in rows]), flush=True)
for i, l in enumerate(sc.split("\n")):
    if re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I):
        print("canon-marker line %d: %s" % (i + 1, l[:100]), flush=True)

with open(os.path.join(SEAT, "results2.json"), "w") as fh:
    json.dump({"mutants": results,
               "canon_best": best,
               "canon_names": [r[0] for r in rows],
               "restored_head": git("rev-parse", "HEAD"),
               "status": git("status", "--porcelain")}, fh, indent=1)
print("DONE2", flush=True)
