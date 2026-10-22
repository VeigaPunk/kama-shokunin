#!/usr/bin/env python3
"""Variant D: an opaque (missing non-leaf subtree) hole is present, but the
only cited token is a KNOWN-PRESENT blob (wrong type for a commit).

Policy under test (amendment + supplement 'not_unresolved'):
  a known-present blob/tree that merely fails commit peeling keeps the normal
  wrong-type finding (failed, exit 1) even when unrelated opaque holes exist.
Benign offline fixture: local git repos only, no network, no transport.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

AUDIT = ("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/repo/"
         "tools/report-landing-audit.py")
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/probeD")
REL = ".ufo/reports/round-1/kama.md"
SOURCES = "# sources\n\nfixture: no registry rows\n"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def git(repo, *args, **extra):
    p = subprocess.run(["git", "--no-lazy-fetch", "-C", str(repo), *args],
                       capture_output=True, env=env(**extra))
    if p.returncode:
        raise SystemExit(f"git {' '.join(map(str,args))} rc={p.returncode} "
                         f"{p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="surrogateescape")


def drop_object(repo, sha):
    obj = Path(git(repo, "rev-parse", "--absolute-git-dir").strip()) / \
        "objects" / sha[:2] / sha[2:]
    obj.unlink()


def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    ROOT.mkdir(parents=True)
    lane, fleet = ROOT / "lane", ROOT / "fleet"
    git(ROOT, "init", "-q", "-b", "master", str(lane))
    git(ROOT, "init", "-q", "-b", "master", str(fleet))
    for pth, content in (("corpus/SOURCES.md", SOURCES), ("f", "fixture file\n"),
                         ("d/f", "opaque\n")):
        t = lane / pth
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(content, encoding="utf-8")
    git(lane, "add", "--", "corpus/SOURCES.md", "f", "d/f")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m", "round-1: work",
        GIT_AUTHOR_NAME="kama-shokunin", GIT_COMMITTER_NAME="kama-shokunin",
        GIT_AUTHOR_DATE="@1000 +0000", GIT_COMMITTER_DATE="@1000 +0000")
    l1 = git(lane, "rev-parse", "HEAD").strip()
    f_blob = git(lane, "rev-parse", f"{l1}:f").strip()
    subtree = git(lane, "rev-parse", f"{l1}:d").strip()
    text = ("# kama round 1\n\n## Landed changes\n\n"
            f"- {f_blob}\n")
    p = fleet / REL
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    git(fleet, "add", "--", REL)
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: report", GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
        GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    git(lane, "config", "remote.origin.promisor", "true")
    git(lane, "config", "extensions.partialclone", "origin")
    git(lane, "config", "remote.origin.url", str(ROOT / "absent-remote.git"))
    drop_object(lane, subtree)
    inv = lambda r: set(git(r, "cat-file", "--batch-all-objects",
                            "--batch-check=%(objectname)").split())
    before = {"lane": inv(lane), "fleet": inv(fleet)}
    pr = subprocess.run([sys.executable, AUDIT, "--lane-repo", str(lane),
                         "--fleet-repo", str(fleet), "--rounds", "1", "--json",
                         "--no-errata"], capture_output=True, env=env(),
                        cwd=str(ROOT))
    after = {"lane": inv(lane), "fleet": inv(fleet)}
    out = pr.stdout.decode(errors="replace")
    doc = None
    try:
        doc = json.loads(out)
    except ValueError:
        pass
    defects = []
    if doc:
        for res in doc.get("results", []):
            defects += [(d.get("kind"), d.get("token"))
                        for d in res.get("defects", [])]
    res = {"variant": "D-wrongtype-citation-with-opaque-hole",
           "exit": pr.returncode, "stderr": pr.stderr.decode().strip(),
           "document": doc is not None, "defects": defects,
           "objects_acquired": {k: sorted(after[k] - before[k]) for k in after},
           "missing_tree_oid": subtree, "cited_blob_oid": f_blob,
           "lane_commit": l1}
    print(json.dumps(res, indent=1))
    (ROOT / "result.json").write_text(json.dumps(res, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
