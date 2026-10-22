#!/usr/bin/env python3
"""Bounded local probe: per-run store/cache ownership, selected-branch and
fleet-root binding, repeated invocation after a changed local object store.

Offline only.  Plain local git repositories, no network, no remote, no
promisor metadata, no execution payload.  Every fixture is created under a
caller-supplied scratch root.

Usage: probe2.py <auditor.py> <scratch-root>
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
import time

FAKE = "0123456789abcdef0123456789abcdef01234567"
RESULTS = {}


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


def drop(repo, sha):
    obj = gitdir(repo) / "objects" / sha[:2] / sha[2:]
    if not obj.exists():
        raise SystemExit(f"object {sha} is not loose in {repo}")
    obj.unlink()
    return sha


def inventory(repo):
    out = git(repo, "--no-lazy-fetch", "cat-file", "--batch-all-objects",
              "--batch-check=%(objectname)")
    return set(out.split())


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


def build(base, name, *, hole="none", fake=True):
    """hole: none | side_branch | dangling_tree | master
    fake: cite a fabricated 40-hex token in the report Notes."""
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
    commit(lane, "kama-shokunin", 1050, "round-1: sources",
           "corpus/SOURCES.md", "# sources\n\nfixture: no registry rows\n")
    tip = git(lane, "rev-parse", "HEAD").strip()
    info = {"tip": tip}
    if hole == "side_branch":
        # a subtree that ONLY the unselected branch reaches
        git(lane, "checkout", "-q", "-b", "side")
        commit(lane, "kama-shokunin", 1200, "side: subtree", "d/f",
               "side opaque\n")
        info["hole_oid"] = git(lane, "rev-parse", "HEAD:d").strip()
        git(lane, "checkout", "-q", "master")
    elif hole == "dangling_tree":
        # a tree object that NO ref reaches, naming a missing tree
        missing_tree = "1" * 40
        p = subprocess.run(["git", "-C", str(lane), "mktree"],
                           input=f"040000 tree {missing_tree}\td\n".encode(),
                           capture_output=True, env=env())
        if p.returncode:
            raise SystemExit("mktree failed: " + p.stderr.decode())
        info["hole_oid"] = p.stdout.decode().strip()
        # keep the dangling tree alive but unreferenced: it stays in the odb
    elif hole == "master":
        commit(lane, "kama-shokunin", 1100, "round-1: subtree", "d/f",
               "master opaque\n")
        info["hole_oid"] = git(lane, "rev-parse", "HEAD:d").strip()
        commit(lane, "kama-shokunin", 1150, "round-1: tip", "g", "tip\n")
        tip = git(lane, "rev-parse", "HEAD").strip()
    lines = ["# kama round 1", "", "## Landed changes", "", f"- {tip}"]
    if fake:
        lines += ["", "## Notes", "", f"fabricated {FAKE}"]
    text = "\n".join(lines) + "\n"
    commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", text)
    if hole in ("side_branch", "master"):
        drop(lane, info["hole_oid"])
    return lane, fleet, info


def load_auditor(path):
    spec = importlib.util.spec_from_file_location("auditor_mod", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("auditor")
    ap.add_argument("scratch")
    args = ap.parse_args()
    auditor = Path(args.auditor).resolve()
    base = Path(args.scratch).resolve() / "fixtures"
    base.mkdir(parents=True, exist_ok=True)
    mod = load_auditor(auditor)

    def rec(key, **kw):
        RESULTS[key] = kw
        print(f"[{key}] " + " ".join(f"{k}={v}" for k, v in kw.items()))

    # ---- A: the store's ROOT argument is vacuous -----------------------
    # missing_reachable(repo, root) with two different roots must differ if
    # the root binds the diagnosis.
    lane, fleet, info = build(base, "A")
    r1 = mod.missing_reachable(lane, info["tip"])
    r2 = mod.missing_reachable(lane, "HEAD")
    r3 = mod.missing_reachable(lane, "0" * 40)
    rec("A-root-binding",
        same_tip_vs_head=r1 == r2,
        same_tip_vs_bogus=r1 == r3,
        missing_tip=len(r1[0]), opaque_tip=len(r1[1]))

    # a store whose hole is OUTSIDE the audited root: does the root
    # change the answer?
    lane2, fleet2, info2 = build(base, "A2", hole="side_branch", fake=False)
    m_root = mod.missing_reachable(lane2, info2["tip"])
    m_bogus = mod.missing_reachable(lane2, "0" * 40)
    rec("A-root-binding-hole-outside-root",
        same_for_root_and_bogus=m_root == m_bogus,
        opaque=m_root[1], missing=m_root[0])

    # ---- B: an opaque hole reachable only from an UNSELECTED branch ----
    lane3, fleet3, info3 = build(base, "B", hole="side_branch")
    rc, err, kinds = audit(auditor, lane3, fleet3)
    rec("B-unselected-branch-hole", rc=rc,
        names_hole=info3["hole_oid"] in err, kinds=kinds,
        err=err[:200])

    # ---- C: an opaque hole in a DANGLING tree no ref reaches -----------
    lane4, fleet4, info4 = build(base, "C", hole="dangling_tree")
    rc, err, kinds = audit(auditor, lane4, fleet4)
    rec("C-dangling-tree-hole", rc=rc,
        names_hole=info4["hole_oid"] in err, kinds=kinds, err=err[:200])

    # ---- D: same hole, but the audited branch is switched --------------
    lane5, fleet5, info5 = build(base, "D", hole="side_branch")
    rc_m, err_m, _ = audit(auditor, lane5, fleet5, extra=["--branch", "master"])
    rc_s, err_s, _ = audit(auditor, lane5, fleet5, extra=["--branch", "side"])
    rec("D-branch-selection", master_rc=rc_m, side_rc=rc_s,
        same=rc_m == rc_s, master_err=err_m[:150])

    # ---- E: repeated invocation, same process, store changed ----------
    lane6, fleet6, info6 = build(base, "E", hole="none", fake=True)
    ns = type("NS", (), {})()
    ns.lane_repo, ns.fleet_repo, ns.branch = str(lane6), str(fleet6), "master"
    ns.lane, ns.rounds, ns.report = "kama", "1", None
    ns.errata, ns.no_errata = None, True
    rc1 = mod.run(ns)[0]
    # change the object store: introduce a dangling opaque hole
    p = subprocess.run(["git", "-C", str(lane6), "mktree"],
                       input=b"040000 tree " + b"2" * 40 + b"\td\n",
                       capture_output=True, env=env())
    rc2 = mod.run(ns)[0]
    # change it again: remove the dangling tree (git prune would do this)
    drop(lane6, p.stdout.decode().strip())
    rc3 = mod.run(ns)[0]
    rec("E-same-process-repeat", run1=rc1, run2=rc2, run3=rc3)

    # ---- F: repeated invocation, separate processes --------------------
    lane7, fleet7, info7 = build(base, "F", hole="none", fake=True)
    r_a, _, _ = audit(auditor, lane7, fleet7)
    subprocess.run(["git", "-C", str(lane7), "mktree"],
                   input=b"040000 tree " + b"3" * 40 + b"\td\n",
                   capture_output=True, env=env())
    r_b, err_b, _ = audit(auditor, lane7, fleet7)
    rec("F-cross-process-repeat", run1=r_a, run2=r_b, run2_err=err_b[:150])

    # ---- G: cross-repo stickiness: run A (hole) then run B (clean) -----
    laneA, fleetA, _ = build(base, "G-A", hole="side_branch")
    laneB, fleetB, _ = build(base, "G-B", hole="none", fake=False)
    nsA = type("NS", (), {})()
    nsA.lane_repo, nsA.fleet_repo, nsA.branch = str(laneA), str(fleetA), "master"
    nsA.lane, nsA.rounds, nsA.report = "kama", "1", None
    nsA.errata, nsA.no_errata = None, True
    nsB = type("NS", (), {})()
    nsB.lane_repo, nsB.fleet_repo, nsB.branch = str(laneB), str(fleetB), "master"
    nsB.lane, nsB.rounds, nsB.report = "kama", "1", None
    nsB.errata, nsB.no_errata = None, True
    ra = mod.run(nsA)[0]
    rb = mod.run(nsB)[0]
    rec("G-cross-repo-stickiness", hole_repo_rc=ra, clean_repo_rc=rb)

    # ---- H: no residue / no object acquisition ------------------------
    lane8, fleet8, _ = build(base, "H", hole="side_branch")
    before_l, before_f = inventory(lane8), inventory(fleet8)
    rc, err, kinds = audit(auditor, lane8, fleet8)
    after_l, after_f = inventory(lane8), inventory(fleet8)
    rec("H-no-acquisition", rc=rc,
        acquired_lane=sorted(after_l - before_l),
        acquired_fleet=sorted(after_f - before_f))

    # ---- I: real production repos: dangling-object census + walk cost -
    lane_real = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
    fleet_real = Path("/home/vgpnk/Projects/shokunin")
    for label, repo in (("lane", lane_real), ("fleet", fleet_real)):
        if not (repo / ".git").exists():
            continue
        t0 = time.time()
        present = mod.present_roots(repo)
        t1 = time.time()
        missing, opaque = mod.missing_reachable(repo, "HEAD")
        t2 = time.time()
        # how many present roots are unreachable from any ref?
        reach = git(repo, "--no-lazy-fetch", "rev-list", "--objects",
                    "--no-object-names", "--all")
        reachable = set(reach.split())
        unreachable = present - reachable
        rec(f"I-production-{label}", present_roots=len(present),
            reachable=len(reachable & present),
            unreachable_roots=len(unreachable),
            missing=len(missing), opaque=len(opaque),
            census_s=round(t1 - t0, 2), walk_s=round(t2 - t1, 2),
            unreachable_sample=sorted(unreachable)[:3])

    print("\n=== JSON ===")
    print(json.dumps(RESULTS, indent=1, default=str))


if __name__ == "__main__":
    main()
