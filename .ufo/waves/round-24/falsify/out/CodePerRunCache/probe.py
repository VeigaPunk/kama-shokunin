#!/usr/bin/env python3
"""Bounded local probe: per-run store/cache ownership, selected-branch and
fleet-root binding, repeated invocation after a changed local object store.

Offline only: plain local git repositories, no network, no transport, no
promisor remote, no execution payload.  Every fixture lives under a
caller-supplied scratch root.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

AUDIT = Path(sys.argv[1]).resolve()
ROOT = Path(sys.argv[2]).resolve()
FAKE = "0123456789abcdef0123456789abcdef01234567"


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


def commit(repo, author, when, msg, path, content):
    target = Path(repo, path)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    git(repo, "add", "--", path)
    git(repo, "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg,
        GIT_AUTHOR_NAME=author, GIT_COMMITTER_NAME=author,
        GIT_AUTHOR_DATE=f"@{when} +0000", GIT_COMMITTER_DATE=f"@{when} +0000")
    return git(repo, "rev-parse", "HEAD").strip()


def gitdir(repo):
    return Path(git(repo, "rev-parse", "--absolute-git-dir").strip())


def drop(repo, sha):
    obj = gitdir(repo) / "objects" / sha[:2] / sha[2:]
    if not obj.exists():
        raise SystemExit(f"object {sha} not loose in {repo}")
    obj.unlink()
    return sha


def tree_digest(path: Path) -> str:
    h = hashlib.sha256()
    for f in sorted(p for p in path.rglob("*") if p.is_file()):
        h.update(str(f.relative_to(path)).encode())
        h.update(str(f.stat().st_size).encode())
        h.update(hashlib.sha256(f.read_bytes()).digest())
    return h.hexdigest()


def audit(lane, fleet, extra=()):
    argv = [sys.executable, str(AUDIT), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json",
            "--no-errata", *extra]
    p = subprocess.run(argv, capture_output=True, env=env(), cwd=str(ROOT))
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


def build(base: Path, name: str, *, side_branch_hole=False,
          master_hole=False, fake_citation=False):
    """lane+fleet fixture.  `side_branch_hole`: the missing tree lives in a
    commit that only an UNSELECTED branch reaches.  `master_hole`: the
    missing tree lives under the audited (selected) branch tip.
    `fake_citation`: the report cites a fabricated 40-hex token."""
    root = base / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    lane = root / "lane"
    fleet = root / "fleet"
    lane.mkdir()
    fleet.mkdir()
    git(lane, "init", "-q", "-b", "master")
    git(fleet, "init", "-q", "-b", "master")
    # audited branch content
    commit(lane, "kama-shokunin", 1000, "round-1: work", "f", "fixture\n")
    commit(lane, "kama-shokunin", 1050, "round-1: sources",
           "corpus/SOURCES.md", "# sources\n\nfixture: no registry rows\n")
    l1 = git(lane, "rev-parse", "HEAD").strip()
    # a subtree that will be removed
    commit(lane, "kama-shokunin", 1100, "round-1: subtree", "d/f", "opaque\n")
    d_tree = git(lane, "rev-parse", "HEAD:d").strip()
    commit(lane, "kama-shokunin", 1150, "round-1: tip", "g", "tip\n")
    tip = git(lane, "rev-parse", "HEAD").strip()
    hole_kind = None
    if master_hole:
        # make the missing subtree part of the audited tip's history
        git(lane, "reset", "-q", "--hard", l1)
        commit(lane, "kama-shokunin", 1150, "round-1: tip", "g", "tip\n")
        hole_kind = "master"
    if side_branch_hole:
        git(lane, "checkout", "-q", "-b", "side", tip)
        commit(lane, "kama-shokunin", 1200, "side: subtree", "d/f", "opaque\n")
        git(lane, "checkout", "-q", "master")
        hole_kind = "side"
    cites = [tip]
    notes = []
    if fake_citation:
        notes.append(f"fabricated {FAKE}")
    lines = ["# kama round 1", "", "## Landed changes", ""]
    lines += [f"- {c}" for c in cites]
    if notes:
        lines += ["", "## Notes", ""] + notes
    text = "\n".join(lines) + "\n"
    commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", text)
    if hole_kind:
        drop(lane, d_tree)
    return lane, fleet, {"d_tree": d_tree, "tip": tip, "hole": hole_kind}


def case(label, fn):
    print(f"\n=== {label} ===")
    fn()


def main():
    base = ROOT / "fixtures"
    base.mkdir(parents=True, exist_ok=True)
    results = {}

    # M1 baseline: complete stores, all citations resolve
    def m1():
        lane, fleet, sh = build(base, "m1")
        rc, err, kinds = audit(lane, fleet)
        print(f"rc={rc} kinds={kinds} stderr={err[:200]}")
        results["M1"] = (rc, kinds)
    case("M1 complete stores, resolvable citations", m1)

    # M2 opaque hole INSIDE the audited branch + fabricated citation
    def m2():
        lane, fleet, sh = build(base, "m2", master_hole=True,
                                fake_citation=True)
        rc, err, kinds = audit(lane, fleet)
        print(f"hole=master rc={rc} kinds={kinds} stderr={err[:300]}")
        results["M2"] = (rc, kinds, err[:300])
    case("M2 opaque tree hole inside selected branch + fabricated token",
         m2)

    # M3 opaque hole OUTSIDE the audited branch (unselected branch) +
    # fabricated citation: does the selected-branch binding hold?
    def m3():
        lane, fleet, sh = build(base, "m3", side_branch_hole=True,
                                fake_citation=True)
        rc, err, kinds = audit(lane, fleet)
        print(f"hole=side rc={rc} kinds={kinds} stderr={err[:300]}")
        results["M3"] = (rc, kinds, err[:300])
    case("M3 opaque tree hole on UNSELECTED branch + fabricated token", m3)

    # M4 opaque hole present but every citation resolves (no blanket
    # precondition)
    def m4():
        lane, fleet, sh = build(base, "m4", side_branch_hole=True)
        rc, err, kinds = audit(lane, fleet)
        print(f"hole=side rc={rc} kinds={kinds} stderr={err[:200]}")
        results["M4"] = (rc, kinds)
    case("M4 opaque hole present, citations all resolve", m4)

    # M5 per-run ownership INSIDE ONE PROCESS: three runs, object store
    # changed between runs (intact -> hole -> restored)
    def m5():
        lane, fleet, sh = build(base, "m5")
        sys.path.insert(0, str(AUDIT.parent))
        spec = {"lane_repo": str(lane), "fleet_repo": str(fleet),
                "branch": "master", "lane": "kama", "rounds": "1",
                "report": None, "errata": None, "no_errata": True}
        import importlib.util
        spec_mod = importlib.util.spec_from_file_location("aud", AUDIT)
        mod = importlib.util.module_from_spec(spec_mod)
        spec_mod.loader.exec_module(mod)
        import argparse
        ns = argparse.Namespace(**spec)
        r1 = mod.run(ns)[0]
        # introduce the hole between runs
        drop(lane, sh["d_tree"])
        r2 = mod.run(ns)[0]
        # restore it (the object is gone; rebuild it identically)
        r3 = "skipped"
        print(f"run1(clean)={r1} run2(hole)={r2} run3={r3}")
        results["M5"] = (r1, r2)
    case("M5 same-process repeated runs across a changed object store", m5)

    # M6 cross-process repeated invocations across a changed object store
    def m6():
        lane, fleet, sh = build(base, "m6")
        rc1, _, _ = audit(lane, fleet)
        drop(lane, sh["d_tree"])
        rc2, err2, _ = audit(lane, fleet)
        print(f"proc1(clean)={rc1} proc2(hole)={rc2} stderr={err2[:200]}")
        results["M6"] = (rc1, rc2)
    case("M6 separate processes, object store changed between runs", m6)

    # M7 no on-disk residue: digest the fixture tree before/after an audit
    def m7():
        lane, fleet, sh = build(base, "m7", side_branch_hole=True,
                                fake_citation=True)
        before_l = tree_digest(gitdir(lane))
        before_f = tree_digest(gitdir(fleet))
        before_w = tree_digest(lane)
        rc, err, kinds = audit(lane, fleet)
        after_l = tree_digest(gitdir(lane))
        after_f = tree_digest(gitdir(fleet))
        after_w = tree_digest(lane)
        print(f"rc={rc} gitdir_lane_same={before_l == after_l} "
              f"gitdir_fleet_same={before_f == after_f} "
              f"worktree_same={before_w == after_w}")
        results["M7"] = (rc, before_l == after_l, before_f == after_f,
                         before_w == after_w)
    case("M7 auditor leaves no residue in the audited repositories", m7)

    # M8 fleet-store root binding: opaque hole only in the FLEET store
    def m8():
        lane, fleet, sh = build(base, "m8", fake_citation=True)
        # create a fleet-only subtree and remove it
        commit(fleet, "fleet", 2050, "fleet: subtree", "h/i", "opaque\n")
        h_tree = git(fleet, "rev-parse", "HEAD:h").strip()
        drop(fleet, h_tree)
        rc, err, kinds = audit(lane, fleet)
        print(f"fleet-hole rc={rc} kinds={kinds} stderr={err[:300]}")
        results["M8"] = (rc, kinds, err[:300])
    case("M8 opaque hole only in the FLEET store + fabricated token", m8)

    print("\n=== SUMMARY ===")
    print(json.dumps({k: (list(v) if isinstance(v, tuple) else v)
                      for k, v in results.items()}, indent=1))


if __name__ == "__main__":
    main()
