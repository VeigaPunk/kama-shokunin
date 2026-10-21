#!/usr/bin/env python3
"""OracleLocalBlobType hazard probe: refusal-removal alone is not the repair.

Scenario J (adjacent to my case, NOT my case): a promisor-marked lane whose
report cites a 40-hex token that exists in NEITHER audited repository.

  preregistered expectation: exit 2 (unknown, absence uncertain in a
  promisor-backed store) -- never a clean or failed verdict
  r23 base:                exit 2 (blanket refusal)
  refusal-removed probe:   exit 1 + unresolved-full-hash  <-- wrong: it
                            converts uncertain absence into a proved-absent
                            verdict

This is why the round-24 repair must gate on object *availability* and
promisor *uncertainty*, not merely delete the promisor refusal.  My case
(locally present blob) must stay exit 0 while this case must become exit 2.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path("/fast/scratch/hyaku/kama-r24/OracleLocalBlobType")
BASE = ("/home/vgpnk/Projects/shokunin/kama-shokunin/"
        "tools/report-landing-audit.py")
PROBE = ROOT / "probe-audit-no-promisor-refusal.py"
REL = ".ufo/reports/round-1/kama.md"
ABSENT = "0123456789abcdef0123456789abcdef01234567"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_ALLOW_PROTOCOL="file", GIT_AUTHOR_EMAIL="a@x",
             GIT_COMMITTER_EMAIL="a@x", GIT_AUTHOR_NAME="fixture",
             GIT_COMMITTER_NAME="fixture")
    e.update(extra)
    return e


def g(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {args}: {p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="surrogateescape").strip()


def commit(repo, author, when, msg, path="f", content=None):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(content if content is not None
                        else (msg + "\n").encode())
    g(repo, "add", "--", path)
    g(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
      GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
      GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return g(repo, "rev-parse", "HEAD")


def audit(tool, lane, fleet):
    argv = [sys.executable, str(tool), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--no-errata",
            "--json"]
    p = subprocess.run(argv, capture_output=True, env=env(), timeout=30)
    out = {"exit": p.returncode,
           "stderr_tail": p.stderr.decode(errors="replace").strip()[-160:]}
    if p.returncode in (0, 1):
        doc = json.loads(p.stdout)
        out["kinds"] = sorted({d["kind"] for r in doc["results"]
                               for d in r["defects"]})
        out["defects"] = [d for r in doc["results"] for d in r["defects"]]
    return out


def main():
    root = ROOT / "cases" / "J"
    if root.exists():
        subprocess.run(["rm", "-rf", str(root)])
    root.mkdir(parents=True)
    lane, fleet = root / "lane", root / "fleet"
    for p in (lane, fleet):
        g(p.parent, "init", "-q", "-b", "master", str(p))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work", "f",
                b"round-1 work\n")
    text = (b"# kama round 1\n\n## Landed changes\n\n- " + lc.encode()
            + b"\n\n## Notes\n\nabsent blob " + ABSENT.encode() + b"\n")
    commit(fleet, "fleet", 2000, "round-1: report", REL, text)
    g(lane, "config", "remote.origin.url", str(lane))
    g(lane, "config", "remote.origin.promisor", "true")
    g(lane, "config", "remote.origin.partialclonefilter", "blob:none")
    g(lane, "config", "extensions.partialclone", "origin")
    doc = {"scenario": "J-promisor-lane-absent-citation",
           "absent_token": ABSENT,
           "base": audit(BASE, lane, fleet),
           "probe_refusal_removed": audit(PROBE, lane, fleet),
           "preregistered_expectation": "exit 2 (unknown), never 0/1"}
    (ROOT / "hazard-results.json").write_text(json.dumps(doc, indent=1,
                                                         sort_keys=True))
    print(json.dumps(doc, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
