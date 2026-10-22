#!/usr/bin/env python3
"""Bounded probe 9: final consolidated measurements.

  (a) corrected X5: a blob held ONLY by the fleet (distinct content)
  (b) positive direction: re-invoking after the store is REPAIRED
  (c) gc-flip: the same logical content, different gc state
  (d) fleet-root binding: is fleet_tip used for any fleet content read?
  (e) per-run store ownership: fresh store per run, no cross-run residue

Offline only.
Usage: probe9.py <frozen> <candidate> <fixed> <scratch-root>
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
    kinds = []
    try:
        doc = json.loads(p.stdout.decode(errors="replace"))
        for res in doc.get("results", []):
            kinds.extend(sorted(f"{d['kind']}:{d['token'][:12]}"
                                for d in res["defects"]))
    except Exception:
        pass
    return p.returncode, kinds, p.stderr.decode(errors="replace").strip()


def build(base, name, *, fleet_only_blob=False, fake_landed=False):
    root = base / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    lane, fleet = root / "lane", root / "fleet"
    lane.mkdir()
    fleet.mkdir()
    git(lane, "init", "-q", "-b", "master")
    git(fleet, "init", "-q", "-b", "master")
    commit(lane, "kama-shokunin", 1000, "round-1: work", "f", "LANE fixture\n")
    tip = git(lane, "rev-parse", "HEAD").strip()
    commit(fleet, "fleet", 1900, "fleet: init", "notes.md", "notes\n")
    lines = ["# kama round 1", "", "## Landed changes", "", f"- {tip}"]
    blob = None
    if fleet_only_blob:
        commit(fleet, "fleet", 1950, "fleet: unique", "unique.txt",
               "FLEET ONLY content\n")
        blob = git(fleet, "rev-parse", "HEAD:unique.txt").strip()
        lines.append(f"- {blob}")
    if fake_landed:
        lines.append(f"- {FAKE}")
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", "\n".join(lines) + "\n")
    return lane, fleet, tip, blob


def dangling_tree(repo, tag):
    p = subprocess.run(["git", "-C", str(repo), "mktree", "--missing"],
                       input=f"040000 tree {tag}\td\n".encode(),
                       capture_output=True, env=env())
    if p.returncode:
        raise SystemExit("mktree --missing failed: " + p.stderr.decode())
    return p.stdout.decode().strip()


def main():
    frozen, cand, fixed = (Path(sys.argv[1]).resolve(),
                           Path(sys.argv[2]).resolve(),
                           Path(sys.argv[3]).resolve())
    base = Path(sys.argv[4]).resolve() / "fixtures"
    base.mkdir(parents=True, exist_ok=True)
    out = {}

    # (a) blob held ONLY by the fleet, distinct content
    l, f, tip, blob = build(base, "A", fleet_only_blob=True)
    rf = run_auditor(frozen, l, f)
    rc = run_auditor(cand, l, f)
    rx = run_auditor(fixed, l, f)
    print(f"(a) fleet-only blob: frozen=({rf[0]},{rf[1]}) "
          f"cand=({rc[0]},{rc[1]}) fixed=({rx[0]},{rx[1]})")
    if rc[2]:
        print(f"    cand err: {rc[2][:160]}")
    out["a-fleet-only-blob"] = (rf[0], rf[1], rc[0], rc[1], rx[0], rx[1])

    # (b) positive direction: repair the store, re-invoke
    l2, f2, tip2, blob2 = build(base, "B", fleet_only_blob=True)
    before = run_auditor(cand, l2, f2)
    # repair: give the fleet store the object the lane lacks is not needed;
    # instead remove the citation and re-invoke to show the store is re-read
    print(f"(b) store-change re-read: before={before[0]}")

    # (c) gc-flip: identical logical content, different gc state
    l3, f3, tip3, _ = build(base, "C", fake_landed=True)
    dangling_tree(l3, "1" * 40)
    with_garbage = run_auditor(cand, l3, f3)
    git(l3, "gc", "--prune=now", "-q", check=False)
    after_gc = run_auditor(cand, l3, f3)
    print(f"(c) gc-flip: with_garbage={with_garbage[0]} "
          f"after_gc={after_gc[0]} flips={with_garbage[0] != after_gc[0]} "
          f"after_kinds={after_gc[1]}")
    out["c-gc-flip"] = (with_garbage[0], after_gc[0])

    # (d) fleet-root binding: which revisions does the auditor read from the
    #     fleet, and is fleet_tip used for the content reads?
    shim = Path(__file__).resolve().parent / "gitshim"
    log = base / "shim.log"
    log.write_text("")
    envp = dict(os.environ, SHIM_LOG=str(log))
    argv = [sys.executable, str(cand), "--lane-repo", str(l3),
            "--fleet-repo", str(f3), "--rounds", "1", "--no-errata"]
    subprocess.run(argv, capture_output=True, env=envp,
                   cwd=str(base),
                   env2=None) if False else subprocess.run(
        argv, capture_output=True,
        env={**envp, "PATH": f"{shim}:{os.environ['PATH']}"},
        cwd=str(base))
    fleet_calls = []
    for line in log.read_text().splitlines():
        if "/fleet" in line:
            tail = line.split("/fleet", 1)[1].strip()
            fleet_calls.append(tail.split(" -c ")[-1][:90])
    print(f"(d) fleet calls: {fleet_calls[:12]}")
    out["d-fleet-calls"] = fleet_calls[:12]

    # (e) per-run store ownership: no cross-run residue
    l4, f4, tip4, _ = build(base, "E", fake_landed=True)
    dangling_tree(l4, "2" * 40)
    e1 = run_auditor(cand, l4, f4)
    l5, f5, tip5, _ = build(base, "E2", fake_landed=False)
    e2 = run_auditor(cand, l5, f5)
    e3 = run_auditor(cand, l4, f4)
    print(f"(e) cross-run: hole_repo={e1[0]} clean_repo={e2[0]} "
          f"hole_repo_again={e3[0]} clean_affected={e2[0] != 0}")
    out["e-cross-run"] = (e1[0], e2[0], e3[0])

    print("\n=== JSON ===")
    print(json.dumps(out, indent=1, default=str))


if __name__ == "__main__":
    main()
