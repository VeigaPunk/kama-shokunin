#!/usr/bin/env python3
"""Bounded probe 7: errata-path cross-store wrong type, and the
store-wide (garbage-inclusive) diagnosis scope.

Offline only.
Usage: probe7.py <frozen> <candidate> <fixed> <scratch-root>
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


def run_auditor(auditor, lane, fleet, errata=None, report=None):
    argv = [sys.executable, str(auditor), "--lane-repo", str(lane),
            "--fleet-repo", str(fleet), "--rounds", "1", "--json"]
    if errata:
        argv += ["--errata", str(errata)]
    else:
        argv += ["--no-errata"]
    if report:
        argv += ["--report", report]
    p = subprocess.run(argv, capture_output=True, env=env(),
                       cwd=str(Path(lane).parent))
    out = p.stdout.decode(errors="replace")
    try:
        doc = json.loads(out)
    except Exception:
        doc = None
    kinds = []
    invalid = []
    if doc:
        for res in doc.get("results", []):
            kinds.extend(sorted(f"{d['kind']}:{d['token'][:12]}"
                                for d in res["defects"]))
        invalid = doc.get("errata_invalid", [])
    return (p.returncode, kinds, invalid,
            p.stderr.decode(errors="replace").strip())


def dangling_tree(repo, tag):
    p = subprocess.run(["git", "-C", str(repo), "mktree", "--missing"],
                       input=f"040000 tree {tag}\td\n".encode(),
                       capture_output=True, env=env())
    if p.returncode:
        raise SystemExit("mktree --missing failed: " + p.stderr.decode())
    return p.stdout.decode().strip()


def build(base, name, *, blob_in="none", fake_landed=False):
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
    if fake_landed:
        lines.append(f"- {FAKE}")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", "\n".join(lines) + "\n")
    return lane, fleet, tip, blob


def main():
    frozen, cand, fixed = (Path(sys.argv[1]).resolve(),
                           Path(sys.argv[2]).resolve(),
                           Path(sys.argv[3]).resolve())
    base = Path(sys.argv[4]).resolve() / "fixtures"
    base.mkdir(parents=True, exist_ok=True)
    out = {}

    def show(label, res):
        print(f"{label}: exit={res[0]} kinds={res[1]} invalid={res[2]}")
        if res[3]:
            print(f"    err: {res[3][:170]}")
        out[label] = (res[0], res[1], res[2])

    # E1: an ERRATA correction that is a blob held only by the FLEET.
    # The errata path calls lookup(stores, ..., "^{commit}") too.
    l, f, tip, blob = build(base, "E1", blob_in="fleet")
    err = base / "E1.tsv"
    err.write_text(f"1\tlanded-unresolved\t{FAKE}\t{blob}\tev\n")
    show("E1-errata-correction-is-fleet-blob",
         run_auditor(cand, l, f, errata=err))
    show("E1-frozen",
         run_auditor(frozen, l, f, errata=err))
    show("E1-fixed",
         run_auditor(fixed, l, f, errata=err))

    # E2: the same wrong-type blob as a plain Landed citation, no errata
    l, f, tip, blob = build(base, "E2", blob_in="fleet")
    show("E2-cand", run_auditor(cand, l, f))
    show("E2-frozen", run_auditor(frozen, l, f))
    show("E2-fixed", run_auditor(fixed, l, f))

    # G1: store-wide scope: a DANGLING tree (unreachable from any ref)
    # enlarges the hole set and flips the verdict.
    l, f, tip, _ = build(base, "G1", fake_landed=True)
    dangling_tree(l, "1" * 40)
    show("G1-dangling-garbage-cand", run_auditor(cand, l, f))
    show("G1-dangling-garbage-frozen", run_auditor(frozen, l, f))
    show("G1-dangling-garbage-fixed", run_auditor(fixed, l, f))

    # G2: the garbage is only garbage: after gc --prune=now it is gone
    # and the verdict must return to the ordinary one.
    l, f, tip, _ = build(base, "G2", fake_landed=True)
    dangling_tree(l, "2" * 40)
    before = run_auditor(cand, l, f)
    git(l, "gc", "--prune=now", "-q", check=False)
    after = run_auditor(cand, l, f)
    print(f"G2-gc-flip: with_garbage={before[0]} after_gc={after[0]} "
          f"flips={before[0] != after[0]} after_kinds={after[1]}")
    out["G2-gc-flip"] = (before[0], after[0])

    # G3: does the garbage hole affect the FLEET-side rounds too?
    l, f, tip, _ = build(base, "G3", fake_landed=True)
    dangling_tree(l, "3" * 40)
    res = run_auditor(cand, l, f)
    print(f"G3-lane-garbage-blocks-fleet-round: exit={res[0]} "
          f"err={res[3][:150]}")
    out["G3"] = res[0]

    print("\n=== JSON ===")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
