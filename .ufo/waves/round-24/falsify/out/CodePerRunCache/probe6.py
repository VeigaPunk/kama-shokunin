#!/usr/bin/env python3
"""Bounded probe 6: cross-store binding of the wrong-type verdict, and the
twin comparison for a store-wide (dangling) hole.

Offline only: plain local git repositories, no network, no remote.
Usage: probe6.py <auditor.py> <scratch-root>
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

FAKE = "0123456789abcdef0123456789abcdef01234567"
R = {}


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
        raise SystemExit(f"git {' '.join(map(str, args))} in {repo}: rc="
                         f"{p.returncode} "
                         f"{p.stderr.decode(errors='replace').strip()}")
    return p.stdout.decode(errors="surplaceescape") if False else \
        p.stdout.decode(errors="surrogateescape")


def gitdir(repo):
    return Path(git(repo, "rev-parse", "--absolute-git-dir").strip())


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", "--", path)
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
        GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
        GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return git(repo, "rev-parse", "HEAD").strip()


def audit(auditor, lane, fleet):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata"]
    p = subprocess.run(argv, capture_output=True, env=env(),
                       cwd=str(Path(lane).parent))
    out = p.stdout.decode(errors="replace")
    try:
        doc = json.loads(out)
    except Exception:
        doc = None
    kinds = []
    if doc:
        for res in doc.get("results", []):
            kinds.extend(sorted(f"{d['kind']}:{d['token'][:12]}"
                                for d in res["defects"]))
    return p.returncode, p.stderr.decode(errors="replace").strip(), kinds


def dangling_tree(repo, tag):
    p = subprocess.run(["git", "-C", str(repo), "mktree", "--missing"],
                       input=f"040000 tree {tag}\td\n".encode(),
                       capture_output=True, env=env())
    if p.returncode:
        raise SystemExit("mktree --missing failed: " + p.stderr.decode())
    return p.stdout.decode().strip()


def make(base, name, *, blob_in, fake_notes=False):
    """blob_in: 'lane' | 'fleet' | 'none'.
    The report cites the blob oid in the Landed section when it exists."""
    root = base / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    lane, fleet = root / "lane", root / "fleet"
    lane.mkdir()
    fleet.mkdir()
    git(lane, "init", "-q", "-b", "master")
    git(fleet, "init", "-q", "-b", "master")
    commit(lane, "kama-shokunin", 1000, "round-1: work", "f", "fixture\n")
    tip = git(lane, "rev-parse", "HEAD").strip()
    commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    if blob_in == "lane":
        blob = git(lane, "rev-parse", "HEAD:f").strip()
    elif blob_in == "fleet":
        blob = git(fleet, "rev-parse", "HEAD:notes.md").strip()
    else:
        blob = None
    lines = ["# kama round 1", "", "## Landed changes", "", f"- {tip}"]
    if blob:
        lines.append(f"- {blob}")
    if fake_notes:
        lines += ["", "## Notes", "", f"fabricated {FAKE}"]
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", "\n".join(lines) + "\n")
    return lane, fleet, tip, blob


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("auditor")
    ap.add_argument("scratch")
    args = ap.parse_args()
    auditor = Path(args.auditor).resolve()
    base = Path(args.scratch).resolve() / "fixtures"
    base.mkdir(parents=True, exist_ok=True)

    def rec(k, **kw):
        R[k] = kw
        print(f"[{k}] " + " ".join(f"{a}={b}" for a, b in kw.items()))

    # T1: the wrong-type object is in the FLEET store only.
    lane, fleet, tip, blob = make(base, "T1", blob_in="fleet")
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("T1-wrongtype-in-fleet", rc=rc, kinds=kinds,
        has_landed_unresolved=any(k.startswith("landed-unresolved")
                                   for k in kinds), err=err[:220])

    # T2: control -- the wrong-type object is in the LANE store only.
    lane, fleet, tip, blob = make(base, "T2", blob_in="lane")
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("T2-wrongtype-in-lane", rc=rc, kinds=kinds,
        has_landed_unresolved=any(k.startswith("landed-unresolved")
                                   for k in kinds), err=err[:220])

    # T3: twin comparison for a store-wide dangling hole:
    #     marked (garbage present) vs its full twin (garbage absent).
    laneA, fleetA, tipA, _ = make(base, "T3A", blob_in="none",
                                   fake_notes=True)
    laneB, fleetB, tipB, _ = make(base, "T3B", blob_in="none",
                                   fake_notes=True)
    dangling_tree(laneA, "e" * 40)
    rcA, errA, kindsA = audit(auditor, laneA, fleetA)
    rcB, errB, kindsB = audit(auditor, laneB, fleetB)
    rec("T3-dangling-vs-twin", marked_rc=rcA, twin_rc=rcB,
        twins_differ=rcA != rcB, marked_err=errA[:180],
        twin_kinds=kindsB)

    # T4: verdict instability under a routine gc of the SAME content.
    lane, fleet, tip, _ = make(base, "T4", blob_in="none", fake_notes=True)
    r0, _, _ = audit(auditor, lane, fleet)
    dangling_tree(lane, "f" * 40)
    r1, e1, _ = audit(auditor, lane, fleet)
    git(lane, "gc", "--prune=now", "-q", check=False)
    r2, _, _ = audit(auditor, lane, fleet)
    rec("T4-gc-instability", before=r0, with_garbage=r1, after_gc=r2,
        flips=(r0 != r1 and r1 != r2), err=e1[:180])

    # T5: is the garbage object reachable from any ref?  (scope proof)
    lane, fleet, tip, _ = make(base, "T5", blob_in="none", fake_notes=True)
    dt = dangling_tree(lane, "9" * 40)
    allreach = git(lane, "--no-lazy-fetch", "rev-list", "--objects",
                   "--no-object-names", "--all")
    refs = git(lane, "for-each-ref", "--format=%(refname)")
    rec("T5-garbage-reachability", garbage_oid=dt,
        reachable_from_refs=(dt in allreach), refs=refs.split(),
        note="a garbage object no ref reaches still enlarges the hole set")

    print("\n=== JSON ===")
    print(json.dumps(R, indent=1, default=str))


if __name__ == "__main__":
    main()
