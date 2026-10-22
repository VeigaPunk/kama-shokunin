#!/usr/bin/env python3
"""Bounded probe 3: per-run store/cache ownership, root binding, repeated
invocation after a changed local object store.

Offline only: plain local git repositories, no network, no remote.
Usage: probe3.py <auditor.py> <scratch-root>
"""
from __future__ import annotations

import argparse
import importlib.util
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
    return p.stdout.decode(errors="surrogateescape")


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


def audit(auditor, lane, fleet, extra=()):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata", *extra]
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


def build(base, name, *, fake=True):
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
    lines = ["# kama round 1", "", "## Landed changes", "", f"- {tip}"]
    if fake:
        lines += ["", "## Notes", "", f"fabricated {FAKE}"]
    commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", "\n".join(lines) + "\n")
    return lane, fleet, tip


def dangling_tree(repo, tag):
    """A tree object that no ref reaches, naming a missing tree."""
    p = subprocess.run(["git", "-C", str(repo), "mktree", "--missing"],
                       input=f"040000 tree {tag}\td\n".encode(),
                       capture_output=True, env=env())
    if p.returncode:
        raise SystemExit("mktree --missing failed: " + p.stderr.decode())
    return p.stdout.decode().strip()


def load(path):
    spec = importlib.util.spec_from_file_location("auditor_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def ns_for(lane, fleet):
    ns = type("NS", (), {})()
    ns.lane_repo, ns.fleet_repo, ns.branch = str(lane), str(fleet), "master"
    ns.lane, ns.rounds, ns.report = "kama", "1", None
    ns.errata, ns.no_errata = None, True
    return ns


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("auditor")
    ap.add_argument("scratch")
    args = ap.parse_args()
    auditor = Path(args.auditor).resolve()
    base = Path(args.scratch).resolve() / "fixtures"
    base.mkdir(parents=True, exist_ok=True)
    mod = load(auditor)

    def rec(k, **kw):
        R[k] = kw
        print(f"[{k}] " + " ".join(f"{a}={b}" for a, b in kw.items()))

    # --- 1: dangling tree (unreferenced) hole -> refusal? -------------
    lane, fleet, tip = build(base, "P1")
    dt = dangling_tree(lane, "1" * 40)
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("P1-dangling-tree-hole", rc=rc, kinds=kinds,
        names_hole=dt in err, err=err[:180])

    # --- 2: same, but the dangling tree is pruned (gc) ------------------
    lane, fleet, tip = build(base, "P2")
    dt = dangling_tree(lane, "2" * 40)
    rc_before, err_before, _ = audit(auditor, lane, fleet)
    git(lane, "reflog", "expire", "--expire=now", "--all", check=False)
    git(lane, "gc", "--prune=now", "-q", check=False)
    alive = git(lane, "cat-file", "-t", dt, check=False).strip()
    rc_after, err_after, _ = audit(auditor, lane, fleet)
    rec("P2-prune-flip", before=rc_before, after=rc_after,
        dangling_alive_after_gc=alive, flipped=rc_before != rc_after,
        after_err=err_after[:150])

    # --- 3: repeated run in ONE process, hole introduced then removed --
    lane, fleet, tip = build(base, "P3")
    ns = ns_for(lane, fleet)
    rc1 = mod.run(ns)[0]
    dt = dangling_tree(lane, "3" * 40)
    rc2 = mod.run(ns)[0]
    git(lane, "gc", "--prune=now", "-q", check=False)
    rc3 = mod.run(ns)[0]
    rec("P3-same-process-repeat", run1=rc1, run2_with_hole=rc2,
        run3_after_prune=rc3)

    # --- 4: cross-repo stickiness: hole repo then clean repo -----------
    laneA, fleetA, _ = build(base, "P4-A")
    laneB, fleetB, _ = build(base, "P4-B", fake=False)
    dangling_tree(laneA, "4" * 40)
    ra = mod.run(ns_for(laneA, fleetA))[0]
    rb = mod.run(ns_for(laneB, fleetB))[0]
    rec("P4-cross-repo", hole_repo=ra, clean_repo=rb)

    # --- 5: does the store's root bind the diagnosis? ------------------
    lane, fleet, tip = build(base, "P5")
    dangling_tree(lane, "5" * 40)
    m_tip = mod.missing_reachable(lane, tip)
    m_bogus = mod.missing_reachable(lane, "0" * 40)
    m_head = mod.missing_reachable(lane, "HEAD")
    rec("P5-root-binding", tip_eq_head=m_tip == m_head,
        tip_eq_bogus=m_tip == m_bogus,
        tip_missing=sorted(m_tip[0]), tip_opaque=sorted(m_tip[1]),
        bogus_missing=sorted(m_bogus[0])[:3])

    # --- 6: fleet-root binding: hole only in the FLEET store ----------
    lane, fleet, tip = build(base, "P6")
    ft = dangling_tree(fleet, "6" * 40)
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("P6-fleet-store-hole", rc=rc, names_hole=ft in err,
        err=err[:180])

    # --- 7: fleet HEAD vs pinned fleet tip: does the report read use
    #        the pinned tip or live HEAD? ------------------------------
    lane, fleet, tip = build(base, "P7")
    # add a second fleet commit that rewrites the report
    rep = fleet / ".ufo/reports/round-1/kama.md"
    body = rep.read_text()
    rep.write_text(body + "\n## Later\n\n" + FAKE + "\n")
    git(fleet, "add", "--", ".ufo/reports/round-1/kama.md")
    git(fleet, "-c", "commit.gpgsign=false", "commit", "-q",
        "-m", "round-1: report rewrite",
        GIT_AUTHOR_NAME="fleet", GIT_COMMITTER_NAME="fleet",
        GIT_AUTHOR_DATE="@2100 +0000", GIT_COMMITTER_DATE="@2100 +0000")
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("P7-fleet-head-read", rc=rc, kinds=kinds, err=err[:150])

    print("\n=== JSON ===")
    print(json.dumps(R, indent=1, default=str))


if __name__ == "__main__":
    main()
