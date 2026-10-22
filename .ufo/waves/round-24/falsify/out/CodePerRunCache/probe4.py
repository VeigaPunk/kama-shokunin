#!/usr/bin/env python3
"""Bounded probe 4: decisive measurements for per-run store ownership,
selected-branch / fleet-root binding, and repeated invocation after a
changed local object store.

Offline only: plain local git repositories, no network, no remote.
Usage: probe4.py <auditor.py> <scratch-root>
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


def build(base, name, *, fake=True, side=False):
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
    if side:
        git(lane, "checkout", "-q", "-b", "side")
        commit(lane, "kama-shokunin", 1200, "side: subtree", "d/f", "side\n")
        side_tip = git(lane, "rev-parse", "HEAD").strip()
        git(lane, "checkout", "-q", "master")
    else:
        side_tip = None
    lines = ["# kama round 1", "", "## Landed changes", "", f"- {tip}"]
    if fake:
        lines += ["", "## Notes", "", f"fabricated {FAKE}"]
    commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", "\n".join(lines) + "\n")
    return lane, fleet, tip, side_tip


def dangling_tree(repo, tag):
    p = subprocess.run(["git", "-C", str(repo), "mktree", "--missing"],
                       input=f"040000 tree {tag}\td\n".encode(),
                       capture_output=True, env=env())
    if p.returncode:
        raise SystemExit("mktree --missing failed: " + p.stderr.decode())
    return p.stdout.decode().strip()


def inventory(repo):
    out = git(repo, "--no-lazy-fetch", "cat-file", "--batch-all-objects",
              "--batch-check=%(objectname)")
    return set(out.split())


def grid_premise_missing(repo, root):
    """The grid's own premise helper: --missing=print over the SELECTED
    root only (tests/report-audit/promisor-grid.py:missing_objects)."""
    out = git(repo, "--no-lazy-fetch", "rev-list", "--objects",
              "--missing=print", "--no-object-names", root)
    return sorted(l[1:] for l in out.split("\n") if l.startswith("?"))


def load(path):
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
    mod = load(auditor)

    def rec(k, **kw):
        R[k] = kw
        print(f"[{k}] " + " ".join(f"{a}={b}" for a, b in kw.items()))

    # -- Q1: does the store ROOT bind the diagnosis? -------------------
    lane, fleet, tip, side_tip = build(base, "Q1", side=True)
    # make the side branch's subtree missing
    d_tree = git(lane, "rev-parse", "side:d").strip()
    Path(gitdir(lane) / "objects" / d_tree[:2] / d_tree[2:]).unlink()
    m_master = mod.missing_reachable(lane, tip)
    m_side = mod.missing_reachable(lane, side_tip)
    m_head = mod.missing_reachable(lane, "HEAD")
    rec("Q1-root-binding", master_eq_side=m_master == m_side,
        master_eq_head=m_master == m_head,
        missing=sorted(m_master[0]), opaque=sorted(m_master[1]))

    # -- Q2: grid premise scope vs auditor scope ------------------------
    lane, fleet, tip, _ = build(base, "Q2")
    dangling_tree(lane, "1" * 40)
    prem = grid_premise_missing(lane, "refs/heads/master")
    m = mod.missing_reachable(lane, tip)
    rec("Q2-premise-vs-auditor", grid_premise_missing=prem,
        auditor_missing=sorted(m[0]), auditor_opaque=sorted(m[1]),
        premise_says_complete=(prem == []),
        auditor_sees_hole=(len(m[1]) > 0))

    # -- Q3: the refusal that follows, on that same fixture ------------
    lane, fleet, tip, _ = build(base, "Q3")
    dt = dangling_tree(lane, "1" * 40)
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("Q3-dangling-refusal", rc=rc, kinds=kinds,
        names_missing_child="1" * 40 in err,
        names_dangling_tree=dt in err, err=err[:200])

    # -- Q4: repeated invocation, SAME content, changed object store ---
    lane, fleet, tip, _ = build(base, "Q4")
    rc1, _, _ = audit(auditor, lane, fleet)
    dangling_tree(lane, "4" * 40)
    rc2, err2, _ = audit(auditor, lane, fleet)
    git(lane, "gc", "--prune=now", "-q", check=False)
    rc3, _, _ = audit(auditor, lane, fleet)
    rec("Q4-repeat-after-store-change", before=rc1, with_dangling=rc2,
        after_gc=rc3, flipped=rc2 != rc3, err2=err2[:150])

    # -- Q5: no residue / no acquisition --------------------------------
    lane, fleet, tip, _ = build(base, "Q5")
    dangling_tree(lane, "5" * 40)
    bl, bf = inventory(lane), inventory(fleet)
    rc, err, kinds = audit(auditor, lane, fleet)
    al, af = inventory(lane), inventory(fleet)
    rec("Q5-no-acquisition", rc=rc, acquired_lane=sorted(al - bl),
        acquired_fleet=sorted(af - bf))

    # -- Q6: cross-run stickiness in one process -----------------------
    laneA, fleetA, ta, _ = build(base, "Q6A")
    laneB, fleetB, tb, _ = build(base, "Q6B", fake=False)
    dangling_tree(laneA, "6" * 40)

    def ns_for(l, f):
        ns = type("NS", (), {})()
        ns.lane_repo, ns.fleet_repo, ns.branch = str(l), str(f), "master"
        ns.lane, ns.rounds, ns.report = "kama", "1", None
        ns.errata, ns.no_errata = None, True
        return ns

    def run_rc(ns):
        try:
            return mod.run(ns)[0]
        except mod.EvalError as exc:
            return f"CNE:{str(exc)[:80]}"

    ra = run_rc(ns_for(laneA, fleetA))
    rb = run_rc(ns_for(laneB, fleetB))
    ra2 = run_rc(ns_for(laneA, fleetA))
    rec("Q6-process-stickiness", hole_repo=ra, clean_repo=rb,
        hole_repo_again=ra2, clean_affected=(rb != 0))

    # -- Q7: fleet-root binding: store root vs live HEAD ---------------
    lane, fleet, tip, _ = build(base, "Q7")
    ft = dangling_tree(fleet, "7" * 40)
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("Q7-fleet-store-hole", rc=rc, names=ft in err, err=err[:200])

    # -- Q8: module-level mutable state in the auditor -----------------
    mutable = {}
    src = auditor.read_text()
    for name in ("RANK", "KINDS", "RESOLVABLE", "GIT_ISOLATION"):
        mutable[name] = "const-like"
    rec("Q8-module-state", note="grep for module-level mutable caches",
        has_lru_cache=("lru_cache" in src), has_global_dict=("_CACHE" in src
                                                             or "CACHE =" in src),
        repo_store_slots=mod.RepoStore.__slots__)

    # -- Q9: RepoStore cache is per-instance (per run) ----------------
    lane, fleet, tip, _ = build(base, "Q9")
    s1 = mod.RepoStore(lane, tip)
    before = s1.missing()
    dangling_tree(lane, "9" * 40)
    after = s1.missing()
    s2 = mod.RepoStore(lane, tip)
    fresh = s2.missing()
    rec("Q9-store-cache-lifetime", cached_unchanged=(before == after),
        fresh_store_sees_new=(len(fresh[1]) > 0),
        note="per-run store: a new store re-reads; an old store keeps its set")

    print("\n=== JSON ===")
    print(json.dumps(R, indent=1, default=str))


if __name__ == "__main__":
    main()
