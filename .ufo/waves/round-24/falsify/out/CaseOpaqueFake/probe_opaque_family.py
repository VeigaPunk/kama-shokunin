#!/usr/bin/env python3
"""Independent reproduction of the OpaqueFake fixture family (PG47) and two
discrimination variants, for the r24 fresh falsification of 2e254a1.

This is a benign offline fixture: local git repositories only, no network,
no transport, no repository program, no execution marker.

Variants
  A  replica   : promisor-marked lane, missing non-leaf subtree d, fabricated
                 unresolved token in the report notes  (== PG47 shape)
  B  no-hole   : same, but the subtree d is present (no opaque hole)
  C  blob-hole : same as B plus an unrelated missing blob (a leaf hole)

The auditor is the pinned one:
  /fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/repo/tools/report-landing-audit.py
"""
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

AUDIT = "/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/repo/tools/report-landing-audit.py"
ROOT = Path("/fast/scratch/hyaku/kama-r24/falsify/CaseOpaqueFake/probe")
FAKE = "0123456789abcdef0123456789abcdef01234567"
REL = ".ufo/reports/round-1/kama.md"
SOURCES = "# sources\n\nfixture: no registry rows\n"


def env(**extra):
    e = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    e.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1",
             GIT_AUTHOR_NAME="fixture", GIT_COMMITTER_NAME="fixture",
             GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    e.update(extra)
    return e


def git(repo, *args, data=None, check=True, **extra):
    p = subprocess.run(["git", "-C", str(repo), *args], input=data,
                       capture_output=True, env=env(**extra))
    if check and p.returncode:
        raise SystemExit(f"git {' '.join(map(str,args))} rc={p.returncode} "
                         f"{p.stderr.decode(errors='replace')}")
    return p.stdout.decode(errors="surrogateescape")


def drop_object(repo, sha):
    obj = Path(git(repo, "rev-parse", "--absolute-git-dir").strip()) / \
        "objects" / sha[:2] / sha[2:]
    if not obj.exists():
        raise SystemExit(f"object {sha} is not loose")
    obj.unlink()


def build(name, drop_subtree, drop_blob):
    base = ROOT / name
    shutil.rmtree(base, ignore_errors=True)
    base.mkdir(parents=True)
    lane, fleet = base / "lane", base / "fleet"
    git(base, "init", "-q", "-b", "master", str(lane))
    git(base, "init", "-q", "-b", "master", str(fleet))
    for pth, content in (("corpus/SOURCES.md", SOURCES),
                         ("f", "fixture file\n"),
                         ("d/f", "opaque\n"),
                         ("extra/unused.txt", "unused\n")):
        t = lane / pth
        t.parent.mkdir(parents=True, exist_ok=True)
        t.write_text(content, encoding="utf-8")
    git(lane, "add", "--", "corpus/SOURCES.md", "f", "d/f", "extra/unused.txt")
    git(lane, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: work", GIT_AUTHOR_NAME="kama-shokunin",
        GIT_COMMITTER_NAME="kama-shokunin", GIT_AUTHOR_DATE="@1000 +0000",
        GIT_COMMITTER_DATE="@1000 +0000")
    l1 = git(lane, "rev-parse", "HEAD").strip()
    subtree = git(lane, "rev-parse", f"{l1}:d").strip()
    hidden_blob = git(lane, "rev-parse", f"{l1}:d/f").strip()
    unused_blob = git(lane, "rev-parse", f"{l1}:extra/unused.txt").strip()
    # fleet report: cites the lane commit, and notes carry the fabricated token
    text = ("# kama round 1\n\n## Landed changes\n\n"
            f"- {l1}\n\n## Notes\n\nfake {FAKE}\n")
    f = fleet / REL
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding="utf-8")
    git(fleet, "add", "--", REL)
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q", "-m",
        "round-1: report", GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
        GIT_AUTHOR_DATE="@2000 +0000", GIT_COMMITTER_DATE="@2000 +0000")
    # promisor metadata on the lane only (config mark, like the grid)
    git(lane, "config", "remote.origin.promisor", "true")
    git(lane, "config", "extensions.partialclone", "origin")
    git(lane, "config", "remote.origin.url", str(base / "absent-remote.git"))
    if drop_subtree:
        drop_object(lane, subtree)
    if drop_blob:
        drop_object(lane, unused_blob)
    return {"base": base, "lane": lane, "fleet": fleet, "l1": l1,
            "subtree": subtree, "hidden_blob": hidden_blob,
            "unused_blob": unused_blob, "unused_tree":
                git(lane, "rev-parse", f"{l1}:extra").strip()}


def facts(repo, root="refs/heads/master"):
    present = set(git(repo, "--no-lazy-fetch", "cat-file", "--batch-all-objects",
                      "--batch-check=%(objectname)").split())
    miss = [l[1:] for l in git(repo, "--no-lazy-fetch", "rev-list", "--objects",
                               "--missing=print", "--no-object-names",
                               root).split("\n") if l.startswith("?")]
    opaque = [l[1:] for l in git(repo, "--no-lazy-fetch", "rev-list", "--objects",
                                 "--missing=print", "--no-object-names",
                                 "--filter=blob:none", root).split("\n")
              if l.startswith("?")]
    return {"present": sorted(present), "missing": sorted(miss),
            "opaque": sorted(opaque)}


def inventory(repo):
    return set(git(repo, "--no-lazy-fetch", "cat-file", "--batch-all-objects",
                   "--batch-check=%(objectname)").split())


def run(name, built):
    lane, fleet = built["lane"], built["fleet"]
    before = {"lane": inventory(lane), "fleet": inventory(fleet)}
    t0 = time.time()
    p = subprocess.run([sys.executable, AUDIT, "--lane-repo", str(lane),
                        "--fleet-repo", str(fleet), "--rounds", "1", "--json",
                        "--no-errata"], capture_output=True, env=env(),
                       cwd=str(built["base"]))
    after = {"lane": inventory(lane), "fleet": inventory(fleet)}
    acquired = {k: sorted(after[k] - before[k]) for k in after}
    out = p.stdout.decode(errors="replace")
    err = p.stderr.decode(errors="replace")
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
    return {"variant": name, "exit": p.returncode, "stderr": err.strip(),
            "stdout_len": len(out), "document": doc is not None,
            "defects": defects, "objects_acquired": acquired,
            "seconds": round(time.time() - t0, 2)}


def main():
    shutil.rmtree(ROOT, ignore_errors=True)
    ROOT.mkdir(parents=True)
    out = []
    for name, drop_sub, drop_blob in (("A-replica-drop-subtree", True, False),
                                      ("B-no-hole", False, False),
                                      ("C-unrelated-blob-hole", False, True)):
        built = build(name, drop_sub, drop_blob)
        lf = facts(built["lane"])
        ff = facts(built["fleet"], "HEAD")
        res = run(name, built)
        res["lane_missing_all"] = lf["missing"]
        res["lane_opaque_blob_none"] = lf["opaque"]
        res["lane_present_has_hidden_blob"] = \
            built["hidden_blob"] in lf["present"]
        res["lane_present_has_subtree"] = built["subtree"] in lf["present"]
        res["fleet_missing"] = ff["missing"]
        res["token"] = FAKE
        res["subtree_oid"] = built["subtree"]
        res["hidden_blob_oid"] = built["hidden_blob"]
        out.append(res)
        print(json.dumps(res, indent=1))
    (ROOT / "results.json").write_text(json.dumps(out, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
