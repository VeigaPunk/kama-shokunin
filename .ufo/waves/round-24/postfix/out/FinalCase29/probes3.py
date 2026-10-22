#!/usr/bin/env python3
"""Third bounded probe batch for PG29: does the registered result depend on a
whole-tree precondition?

Each variant is a LOCAL COPY of the kept PG29 fixture (the grid fixture is
never mutated).  The copies have no remote, so no lazy fetch is possible.
The changed input state is stated per variant; nothing here is compared
against the registered PG29 result as if the input state were unchanged.
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

TREE = "1c13e47ce9f8088dc933a80123cf6a8ee2fa701d"
BLOB_F = "56d7b323865c731da81e0225cf109d66f0480919"


def inventory(repo):
    out = subprocess.run(["git", "--no-lazy-fetch", "--no-replace-objects",
                          "-C", str(repo), "cat-file", "--batch-all-objects",
                          "--batch-check=%(objectname)"],
                         capture_output=True, env=ENV)
    return sorted(out.stdout.decode().split())


def drop(repo, sha):
    obj = Path(repo) / ".git" / "objects" / sha[:2] / sha[2:]
    if not obj.exists():
        raise SystemExit(f"{repo}: {sha} is not loose; variant premise failed")
    obj.unlink()
    return sha


def run(label, lane, fleet, extra=()):
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json"] + list(extra)
    p = subprocess.run(argv, capture_output=True, env=ENV, cwd=str(lane),
                       timeout=60)
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    rec = {"label": label, "argv": argv, "exit": p.returncode,
           "stderr": p.stderr.decode(errors="replace").strip()[:600],
           "stdout_bytes": len(p.stdout),
           "objects_acquired": {k: sorted(set(after[k]) - set(before[k]))
                                for k in after}}
    try:
        doc = json.loads(p.stdout.decode())
        rec["summary"] = doc.get("summary")
        rec["defects"] = [(d.get("kind"), d.get("token"), d.get("corrected_by"))
                          for r in doc.get("results", [])
                          for d in r.get("defects", [])]
        rec["has_document"] = True
    except ValueError:
        rec["has_document"] = False
        rec["stdout_head"] = p.stdout.decode(errors="replace")[:400]
    return rec


def fresh(name):
    dest = WORK / name
    if dest.exists():
        shutil.rmtree(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(BASE, dest, symlinks=True)
    return dest / "lane", dest / "fleet"


variants = []

# V1: an object the report never cites (the lane's file blob) is absent.
#     The registered PG29 verdict must survive: an unrelated missing object
#     must not become a whole-tree precondition.
lane, fleet = fresh("v1-unrelated-blob-missing")
dropped = drop(lane, BLOB_F)
variants.append(run(f"V1-unrelated-blob-missing (dropped lane blob {dropped})",
                     lane, fleet))

# V2: the lane commit's tree is absent: the audit must refuse with a
#     content-derived reason naming that tree, not a blanket unknown.
lane, fleet = fresh("v2-lane-tree-missing")
dropped = drop(lane, TREE)
variants.append(run(f"V2-lane-tree-missing (dropped lane tree {dropped})",
                     lane, fleet))

(OUT / "probes3.json").write_text(json.dumps(variants, indent=1, sort_keys=True),
                                   encoding="utf-8")
for v in variants:
    print(v["label"])
    print("  exit", v["exit"], "has_document", v["has_document"],
          "acq", v["objects_acquired"])
    print("  stderr", v["stderr"][:400])
    if v.get("summary"):
        s = v["summary"]
        print("  status", s.get("status"), "uncorrected", s.get("uncorrected"),
              "corrected", s.get("corrected"),
              "unmatched", s.get("errata_unmatched"),
              "invalid", s.get("errata_invalid"))
    if v.get("defects") is not None:
        print("  defects", v["defects"])
