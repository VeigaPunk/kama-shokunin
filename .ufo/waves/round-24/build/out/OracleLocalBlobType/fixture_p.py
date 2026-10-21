#!/usr/bin/env python3
"""OracleLocalBlobType rows P08, P08b, P09 — the token-scoped availability rule.

Requested by CritExpected: separate the amendment rule ("a locally unresolved
citation KNOWN TO NAME unavailable referenced local content -> exit 2") from an
over-broad one ("the store has any hole -> unknown").

  P08   promisor-marked lane, store has an UNRELATED hole (a blob referenced by
        a tree but never cited), report cites a FABRICATED token that is not in
        the missing set
        amended expectation: twin verdict -> exit 1, unresolved-full-hash on
        the fabricated token
        an "any hole means unknown" rule would give exit 2 -> P08 kills it
  P08b  same, but a NON-promisor store (uniform rule, no metadata involved)
        amended expectation: exit 1, unresolved-full-hash on the token
  P09   NON-promisor store, cited token IS the hole -> the token is known to
        name unavailable referenced content
        amended expectation: exit 2, content-derived CNE
        (policy row to declare: the candidate computes the missing set for
        every store, so this leaves r22's exit 1 -> exit 2)
  P07   (already measured, scenario K) promisor-marked store, cited token IS
        the hole -> exit 2, content-derived CNE

Offline: no clone, no fetch, GIT_ALLOW_PROTOCOL=file.
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
FABRICATED = "0123456789abcdef0123456789abcdef01234567"
GIT_ISOLATION = ("--no-replace-objects", "--no-lazy-fetch",
                 "-c", "i18n.logOutputEncoding=UTF-8",
                 "-c", "log.follow=false", "-c", "log.showRoot=true",
                 "-c", "log.showSignature=false", "-c", "log.mailmap=false")


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
    target.write_bytes(content if content is not None else (msg + "\n").encode())
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
        out["summary"] = doc["summary"]
    return out


def traversal(repo, root):
    p = subprocess.run(["git", *GIT_ISOLATION, "-C", str(repo), "rev-list",
                        "--objects", "--missing=print", "--no-object-names", root],
                       capture_output=True, env=env())
    lines = [l for l in p.stdout.decode().split("\n") if l]
    return {"rc": p.returncode, "lines": len(lines),
            "missing": [l for l in lines if l.startswith("?")]}


def build(name, promisor, cite):
    """cite: 'fabricated' | 'hole'"""
    root = ROOT / "cases" / name
    if root.exists():
        subprocess.run(["rm", "-rf", str(root)])
    root.mkdir(parents=True)
    lane, fleet = root / "lane", root / "fleet"
    for p in (lane, fleet):
        g(p.parent, "init", "-q", "-b", "master", str(p))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work", "f",
                b"round-1 work\n")
    Path(lane, "corpus").mkdir()
    Path(lane, "corpus/blob.txt").write_bytes(b"unavailable referenced blob\n")
    g(lane, "add", "--", "corpus/blob.txt")
    g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "--amend", "--no-edit",
      GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
      GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    lc = g(lane, "rev-parse", "HEAD")
    hole = g(lane, "rev-parse", "HEAD:corpus/blob.txt")
    loose = Path(lane, ".git/objects", hole[:2], hole[2:])
    assert loose.is_file()
    loose.unlink()                       # the hole: referenced by a present tree
    cited = FABRICATED if cite == "fabricated" else hole
    text = (b"# kama round 1\n\n## Landed changes\n\n- " + lc.encode()
            + b"\n\n## Notes\n\ntoken " + cited.encode() + b"\n")
    commit(fleet, "fleet", 2000, "round-1: report", REL, text)
    if promisor:
        for k, v in (("remote.origin.url", str(lane)),
                     ("remote.origin.promisor", "true"),
                     ("remote.origin.partialclonefilter", "blob:none"),
                     ("extensions.partialclone", "origin")):
            g(lane, "config", k, v)
    return {"name": name, "lane": str(lane), "fleet": str(fleet),
            "lane_commit": lc, "hole_blob": hole, "cited_token": cited,
            "promisor": promisor, "cite": cite,
            "traversal_lane": traversal(lane, lc),
            "traversal_fleet": traversal(fleet, "HEAD"),
            "base": audit(BASE, lane, fleet),
            "probe_naive_repair": audit(PROBE, lane, fleet)}


def main():
    rows = [build("P08", True, "fabricated"),
            build("P08b", False, "fabricated"),
            build("P09", False, "hole")]
    doc = {"rows": rows,
           "expectations": {
               "P08": "exit 1, kind unresolved-full-hash, token "
                      + FABRICATED + " (twin verdict; an 'any hole => unknown' "
                      "rule would give exit 2)",
               "P08b": "exit 1, kind unresolved-full-hash, token "
                       + FABRICATED + " (uniform rule, non-promisor store)",
               "P09": "exit 2, content-derived CNE (token in the missing set); "
                      "policy row to declare: leaves r22 exit 1"}}
    (ROOT / "rows-p08-p09-results.json").write_text(
        json.dumps(doc, indent=1, sort_keys=True))
    for r in rows:
        print(f"{r['name']}: promisor={r['promisor']} cite={r['cite']} "
              f"cited={r['cited_token'][:12]} "
              f"missing={r['traversal_lane']['missing']} "
              f"base_exit={r['base']['exit']} base_kinds={r['base'].get('kinds')} "
              f"probe_exit={r['probe_naive_repair']['exit']} "
              f"probe_kinds={r['probe_naive_repair'].get('kinds')}")


if __name__ == "__main__":
    main()
