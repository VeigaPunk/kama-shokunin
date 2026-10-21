#!/usr/bin/env python3
"""OracleLocalBlobType scenario K: the row that actually discriminates.

K = promisor-marked lane whose object store has a HOLE: the blob referenced by
a present tree was removed from the store, and the report cites that blob's
sha outside `## Landed changes`.

The token is therefore *known to name unavailable referenced local content*
(a bounded missing-object traversal reports it with a '?' prefix), which is
the case the round-24 oracle amendment
(.ufo/waves/round-24/oracle-amendment-1.json) says must be
could-not-evaluate, never a proved-absent verdict.

  r23 base                    -> exit 2 (blanket promisor refusal)
  naive repair (refusal only) -> exit 1 + unresolved-full-hash   <-- mutant survives
  amended expectation         -> exit 2, content-derived reason

Contrast J (fabricated token, absent from a COMPLETE store): the amended
oracle makes that the twin verdict (exit 1 + unresolved-full-hash), so J is a
construction row, not a discriminator.

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
           "stderr_tail": p.stderr.decode(errors="replace").strip()[-200:]}
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


def main():
    root = ROOT / "cases" / "K"
    if root.exists():
        subprocess.run(["rm", "-rf", str(root)])
    root.mkdir(parents=True)
    lane, fleet = root / "lane", root / "fleet"
    for p in (lane, fleet):
        g(p.parent, "init", "-q", "-b", "master", str(p))
    lc = commit(lane, "kama-shokunin", 1000, "round-1: work", "f",
                b"round-1 work\n")
    # a second file whose blob is removed from the store afterwards:
    # the tree still references it, the object is gone
    body = b"unavailable referenced blob\n"
    Path(lane, "corpus").mkdir()
    Path(lane, "corpus/blob.txt").write_bytes(body)
    g(lane, "add", "--", "corpus/blob.txt")
    g(lane, "-c", "commit.gpgsign=false", "commit", "-q", "--amend", "--no-edit",
      GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
      GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    lc = g(lane, "rev-parse", "HEAD")
    blob = g(lane, "rev-parse", "HEAD:corpus/blob.txt")
    loose = Path(lane, ".git/objects", blob[:2], blob[2:])
    assert loose.is_file(), f"blob is not a loose object: {loose}"
    loose.unlink()
    text = (b"# kama round 1\n\n## Landed changes\n\n- " + lc.encode()
            + b"\n\n## Notes\n\nunavailable blob " + blob.encode() + b"\n")
    commit(fleet, "fleet", 2000, "round-1: report", REL, text)
    for k, v in (("remote.origin.url", str(lane)),
                 ("remote.origin.promisor", "true"),
                 ("remote.origin.partialclonefilter", "blob:none"),
                 ("extensions.partialclone", "origin")):
        g(lane, "config", k, v)
    doc = {"scenario": "K-promisor-lane-missing-referenced-blob",
           "lane": str(lane), "fleet": str(fleet),
           "lane_commit": lc, "cited_blob": blob,
           "blob_present_in_store": Path(
               lane, ".git/objects", blob[:2], blob[2:]).exists(),
           "traversal_lane": traversal(lane, lc),
           "traversal_fleet": traversal(fleet, "HEAD"),
           "base": audit(BASE, lane, fleet),
           "probe_naive_repair": audit(PROBE, lane, fleet),
           "amended_expectation": "exit 2 (could-not-evaluate): the citation "
                                  "names unavailable referenced local content",
           "naive_repair_expected": "exit 1 + unresolved-full-hash "
                                    "(mutant survives)"}
    (ROOT / "scenario-k-results.json").write_text(json.dumps(doc, indent=1,
                                                             sort_keys=True))
    print(json.dumps(doc, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
