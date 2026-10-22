#!/usr/bin/env python3
"""Bounded probe 5: cross-store refusal attribution, blob-hole filter walk,
and the exact refusal reason determinism.

Offline only.
Usage: probe5.py <auditor.py> <scratch-root>
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


def build(base, name, *, fake=True, notes=False):
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

    # S1: MISSING BLOB (not tree) + fabricated citation: PG22-shaped.
    # The opaque walk uses --filter=blob:none; does it succeed on a plain
    # repo with a missing blob, and what verdict results?
    lane, fleet, tip = build(base, "S1")
    commit(lane, "kama-shokunin", 1050, "round-1: unused", "notes/u.txt",
           "unused\n")
    blob = git(lane, "rev-parse", "HEAD:notes/u.txt").strip()
    Path(gitdir(lane) / "objects" / blob[:2] / blob[2:]).unlink()
    m = mod.missing_reachable(lane, tip)
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("S1-missing-blob-plus-fabrication", missing=sorted(m[0]),
        opaque=sorted(m[1]), rc=rc, kinds=kinds, err=err[:180])

    # S2: cross-store attribution: LANE has an opaque hole, the citation
    # is in the FLEET report. Which store does the refusal name?
    lane, fleet, tip = build(base, "S2")
    lane_hole = dangling_tree(lane, "a" * 40)
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("S2-lane-hole-names-lane", rc=rc, names_lane_hole=lane_hole in err,
        names_fleet_path=("fleet" in err), err=err[:200])

    # S3: FLEET has an opaque hole, citation in the fleet report.
    lane, fleet, tip = build(base, "S3")
    fleet_hole = dangling_tree(fleet, "b" * 40)
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("S3-fleet-hole-names-fleet", rc=rc, names_fleet_hole=fleet_hole in err,
        err=err[:200])

    # S4: refusal reason determinism across repeated invocations
    lane, fleet, tip = build(base, "S4")
    dangling_tree(lane, "c" * 40)
    seen = set()
    for _ in range(3):
        rc, err, _ = audit(auditor, lane, fleet)
        seen.add(err)
    rec("S4-reason-determinism", distinct_reasons=len(seen), rc=rc)

    # S5: does the LANE store's opaque hole refuse a round whose ONLY
    # unresolved token is a fleet-side object?  (cross-repo citation)
    lane, fleet, tip = build(base, "S5")
    dangling_tree(lane, "d" * 40)
    rc, err, kinds = audit(auditor, lane, fleet)
    rec("S5-lane-hole-blocks-fleet-round", rc=rc, err=err[:200])

    # S6: verifier -- the auditor's own repo has no alternates; check the
    # store path resolution: does the auditor resolve a repo path once and
    # reuse it?  (per-run binding of lane/fleet roots)
    lane, fleet, tip = build(base, "S6")
    real = Path(lane).resolve()
    s = mod.build_store(lane, tip)
    rec("S6-store-path", store_path=str(s.path), resolved=(Path(s.path)
                                                            == real),
        root_is_tip=(s.root == tip))

    # S7: two stores for the SAME repo path (would share state?)
    s1 = mod.build_store(lane, tip)
    s2 = mod.build_store(lane, tip)
    rec("S7-store-identity", distinct=("path" in s1.__slots__),
        same_object=(s1 is s2))

    print("\n=== JSON ===")
    print(json.dumps(R, indent=1, default=str))


if __name__ == "__main__":
    main()
