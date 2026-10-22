#!/usr/bin/env python3
"""Fifth bounded probe batch for PG29: the scoped-refusal path of the errata
correction (amendment prospective_expected[2]).

V5: a LOCAL COPY of the kept PG29 fixture in which the lane's file blob is
    absent, and the errata correction names exactly that absent object.  The
    audit must refuse with a content-derived reason that names the token
    (it is referenced by a present local object but cannot be served) --
    never a blanket "unknown" and never a verdict.  This is the complement of
    V1, where the same absent blob was NOT named by the ledger and the
    registered clean verdict survived.
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
SPLICED = "58866b563cd900dd894ef21bc863486bcb35b56c"
BLOB_F = "56d7b323865c731da81e0225cf109d66f0480919"

ENV = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
ENV.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")

dest = WORK / "v5-errata-names-absent-object"
if dest.exists():
    shutil.rmtree(dest)
dest.parent.mkdir(parents=True, exist_ok=True)
shutil.copytree(BASE, dest, symlinks=True)
lane, fleet = dest / "lane", dest / "fleet"

obj = lane / ".git" / "objects" / BLOB_F[:2] / BLOB_F[2:]
assert obj.exists(), "premise: the blob must be loose in the copy"
obj.unlink()

tsv = OUT / "errata-names-absent-object.tsv"
tsv.write_text(f"1\tunresolved-full-hash\t{SPLICED}\t{BLOB_F}\tev\n",
               encoding="utf-8")

argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
        "--fleet-repo", str(fleet), "--rounds", "1", "--json",
        "--errata", str(tsv)]
p = subprocess.run(argv, capture_output=True, env=ENV, cwd=str(lane), timeout=60)
rec = {"label": "V5-errata-names-absent-object (lane blob absent, ledger "
                "correction names it)",
       "argv": argv, "exit": p.returncode,
       "stderr": p.stderr.decode(errors="replace").strip()[:800],
       "stdout_bytes": len(p.stdout)}
try:
    doc = json.loads(p.stdout.decode())
    rec["has_document"] = True
    rec["summary"] = doc.get("summary")
except ValueError:
    rec["has_document"] = False
(OUT / "probes5.json").write_text(json.dumps(rec, indent=1, sort_keys=True),
                                   encoding="utf-8")
print(json.dumps(rec, indent=1, sort_keys=True))
