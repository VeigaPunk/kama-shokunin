#!/usr/bin/env python3
"""OracleLocalBlobType row P10 (and plain twin P10b): the peel path.

CritExpected's request: P08 covers the *no-peel* full-hash path (a fabricated
token outside Landed next to an unrelated hole).  P10 covers the *peel* path:
a locally PRESENT blob T is cited inside `## Landed changes` while the store
has an UNRELATED hole.

  amended expectation: exit 1, defects exactly
      [("landed-unresolved", T)]
  why: the Landed lookup peels ^{commit} (tools/report-landing-audit.py:336),
  T is a blob, so the peel fails -> an ordinary failed finding.  T is PRESENT
  and is NOT in the store's missing set, so no availability rule may turn this
  into exit 2: an "any hole => unknown" rule applied to peel failures would.

Measured against the r23 base and the refusal-removed probe, plus the plain
(non-promisor) twin P10b, which is the no-harm reference.

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


def build(name, promisor):
    root = ROOT / "cases" / name
    if root.exists():
        subprocess.run(["rm", "-rf", str(root)])
    root.mkdir(parents=True)
    lane, fleet = root / "lane", root / "fleet"
    for p in (lane, fleet):
        g(p.parent, "init", "-q", "-b", "master", str(p))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work", "f",
                b"round-1 work\n")
    T = g(lane, "rev-parse", "HEAD:f")           # the PRESENT blob that is cited
    Path(lane, "corpus").mkdir()
    Path(lane, "corpus/blob.txt").write_bytes(b"unrelated hole blob\n")
    g(lane, "add", "--", "corpus/blob.txt")
    g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "--amend", "--no-edit",
      GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
      GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    lc = g(lane, "rev-parse", "HEAD")
    T = g(lane, "rev-parse", "HEAD:f")
    hole = g(lane, "rev-parse", "HEAD:corpus/blob.txt")
    loose = Path(lane, ".git/objects", hole[:2], hole[2:])
    assert loose.is_file()
    loose.unlink()                               # the UNRELATED hole
    # Landed cites the real lane commit AND the present blob T (wrong type);
    # T is inside the Landed span, so the no-peel full-hash scan skips it.
    text = (b"# kama round 1\n\n## Landed changes\n\n- " + lc.encode()
            + b"\n- " + T.encode() + b"\n")
    commit(fleet, "fleet", 2000, "round-1: report", REL, text)
    if promisor:
        for k, v in (("remote.origin.url", str(lane)),
                     ("remote.origin.promisor", "true"),
                     ("remote.origin.partialclonefilter", "blob:none"),
                     ("extensions.partialclone", "origin")):
            g(lane, "config", k, v)
    peel = subprocess.run(["git", "-C", str(lane), "cat-file", "--batch-check"],
                          input=(T + "^{commit}\n").encode(), capture_output=True,
                          env=env())
    return {"name": name, "lane": str(lane), "fleet": str(fleet),
            "lane_commit": lc, "cited_blob_T": T, "hole_blob": hole,
            "promisor": promisor,
            "T_type": g(lane, "cat-file", "-t", T),
            "T_present": not Path(lane, ".git/objects", T[:2],
                                  T[2:]).exists() is False,
            "T_peel_batch_check": peel.stdout.decode().strip(),
            "traversal_lane": traversal(lane, lc),
            "base": audit(BASE, lane, fleet),
            "probe_naive_repair": audit(PROBE, lane, fleet)}


def main():
    rows = [build("P10", True), build("P10b", False)]
    doc = {"rows": rows,
           "expectations": {
               "P10": "exit 1, defects exactly [('landed-unresolved', T)]; "
                      "T = 6e98d181389d343031fd578c6a775ce0889a8b0d in the "
                      "sibling cell; here T is this fixture's f-blob. An "
                      "'any hole => unknown' rule applied to peel failures "
                      "would give exit 2 -> P10 kills it.",
               "P10b": "exit 1, defects exactly [('landed-unresolved', T)] "
                       "(plain-store twin, no metadata involved)"}}
    (ROOT / "rows-p10-results.json").write_text(json.dumps(doc, indent=1,
                                                            sort_keys=True))
    for r in rows:
        print(f"{r['name']}: promisor={r['promisor']} T={r['cited_blob_T']} "
              f"type={r['T_type']} peel={r['T_peel_batch_check']!r} "
              f"missing={r['traversal_lane']['missing']} "
              f"base_exit={r['base']['exit']} base_kinds={r['base'].get('kinds')} "
              f"probe_exit={r['probe_naive_repair']['exit']} "
              f"probe_kinds={r['probe_naive_repair'].get('kinds')}")


if __name__ == "__main__":
    main()
