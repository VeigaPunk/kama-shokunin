#!/usr/bin/env python3
"""Bounded probe 8: does the minimal correction preserve every intended
unknown/unavailable case, across store orderings?

Offline only.
Usage: probe8.py <frozen> <candidate> <fixed> <scratch-root>
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

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


def run_auditor(auditor, lane, fleet, report=None):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json", "--no-errata"]
    if report:
        argv += ["--report", report]
    p = subprocess.run(argv, capture_output=True, env=env(),
                       cwd=str(Path(lane).parent))
    out = p.stdout.decode(errors="replace")
    kinds = []
    try:
        doc = json.loads(out)
        for res in doc.get("results", []):
            kinds.extend(sorted(f"{d['kind']}:{d['token'][:12]}"
                                for d in res["defects"]))
    except Exception:
        pass
    return p.returncode, kinds, p.stderr.decode(errors="replace").strip()


def build(base, name):
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
    lines = ["# kama round 1", "", "## Landed changes", "", f"- {tip}"]
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", "\n".join(lines) + "\n")
    return lane, fleet, tip


def main():
    frozen, cand, fixed = (Path(sys.argv[1]).resolve(),
                           Path(sys.argv[2]).resolve(),
                           Path(sys.argv[3]).resolve())
    base = Path(sys.argv[4]).resolve() / "fixtures"
    base.mkdir(parents=True, exist_ok=True)
    ident = env(GIT_AUTHOR_NAME="k", GIT_COMMITTER_NAME="k",
                GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")

    def row(label, lane, fleet, report=None):
        rf = run_auditor(frozen, lane, fleet, report)
        rc = run_auditor(cand, lane, fleet, report)
        rx = run_auditor(fixed, lane, fleet, report)
        print(f"{label}\n   frozen=({rf[0]},{rf[1]})\n   cand  =({rc[0]},{rc[1]})"
              f"\n   fixed =({rx[0]},{rx[1]})")
        if rc[2]:
            print(f"   cand err : {rc[2][:150]}")
        if rx[2]:
            print(f"   fixed err: {rx[2][:150]}")
        return rf, rc, rx

    # X1: a TAG whose target commit is unavailable, cited in the lane.
    # Must STAY unknown (exit 2) in the fixed version.
    l, f, tip = build(base, "X1")
    tree = git(l, "rev-parse", "HEAD^{tree}").strip()
    target = git(l, "commit-tree", tree, "-m", "tag target", **ident).strip()
    git(l, "tag", "-a", "-m", "hole", "v-hole", target, **ident)
    tag_oid = git(l, "rev-parse", "v-hole").strip()
    Path(gitdir(l) / "objects" / target[:2] / target[2:]).unlink()
    draft = base / "X1-draft.md"
    draft.write_text("## Landed changes\n- `" + tag_oid + "` tag\n")
    row("X1-tag-with-unavailable-target-must-stay-unknown", l, f,
        f"1={draft}")

    # X2: same, but the tag lives in the FLEET store, lane lacks it.
    l2, f2, tip2 = build(base, "X2")
    tree2 = git(f2, "rev-parse", "HEAD^{tree}").strip()
    target2 = git(f2, "commit-tree", tree2, "-m", "t", **ident).strip()
    git(f2, "tag", "-a", "-m", "h", "v-hole", target2, **ident)
    tag2 = git(f2, "rev-parse", "v-hole").strip()
    Path(gitdir(f2) / "objects" / target2[:2] / target2[2:]).unlink()
    draft2 = base / "X2-draft.md"
    draft2.write_text("## Landed changes\n- `" + tag2 + "` tag\n")
    row("X2-fleet-tag-with-unavailable-target", l2, f2, f"1={draft2}")

    # X3: a blob cited in the LANE (control for the fix).
    l3, f3, tip3 = build(base, "X3")
    blob3 = git(l3, "rev-parse", "HEAD:f").strip()
    d3 = base / "X3-draft.md"
    d3.write_text("## Landed changes\n- `" + blob3 + "` blob\n")
    row("X3-lane-blob-citation", l3, f3, f"1={d3}")

    # X4: the blob lives in BOTH stores (lane + fleet).
    l4, f4, tip4 = build(base, "X4")
    commit(f4, "fleet", 1950, "fleet: f", "f", "fixture\n")
    blob4 = git(f4, "rev-parse", "HEAD:f").strip()
    d4 = base / "X4-draft.md"
    d4.write_text("## Landed changes\n- `" + blob4 + "` blob\n")
    row("X4-blob-in-both-stores", l4, f4, f"1={d4}")

    # X5: the blob lives ONLY in the fleet (the regression).
    l5, f5, tip5 = build(base, "X5")
    commit(f5, "fleet", 1950, "fleet: f", "f", "fixture\n")
    blob5 = git(f5, "rev-parse", "HEAD:f").strip()
    d5 = base / "X5-draft.md"
    d5.write_text("## Landed changes\n- `" + blob5 + "` blob\n")
    row("X5-blob-only-in-fleet", l5, f5, f"1={d5}")


if __name__ == "__main__":
    main()
