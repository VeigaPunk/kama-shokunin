#!/usr/bin/env python3
"""Differential: frozen r23 vs candidate vs corrected, on the same fixtures.

Offline only.
Usage: diffprobe.py <frozen> <candidate> <fixed> <scratch-root>
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


def run_auditor(auditor, lane, fleet):
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
    err = p.stderr.decode(errors="replace").strip()
    return p.returncode, kinds, err


def dangling_tree(repo, tag):
    p = subprocess.run(["git", "-C", str(repo), "mktree", "--missing"],
                       input=f"040000 tree {tag}\td\n".encode(),
                       capture_output=True, env=env())
    if p.returncode:
        raise SystemExit("mktree --missing failed: " + p.stderr.decode())
    return p.stdout.decode().strip()


def build(base, name, *, blob_in="none", fake_landed=False, fake_notes=False):
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
    if fake_notes:
        lines += ["", "## Notes", "", f"fabricated {FAKE}"]
    commit(fleet, "fleet", 2000, "round-1: report",
           ".ufo/reports/round-1/kama.md", "\n".join(lines) + "\n")
    return lane, fleet, tip


CASES = {}


def main():
    frozen, cand, fixed = (Path(sys.argv[1]).resolve(),
                           Path(sys.argv[2]).resolve(),
                           Path(sys.argv[3]).resolve())
    base = Path(sys.argv[4]).resolve() / "fixtures"
    base.mkdir(parents=True, exist_ok=True)

    def case(label, lane, fleet):
        rf = run_auditor(frozen, lane, fleet)
        rc = run_auditor(cand, lane, fleet)
        rf2 = run_auditor(fixed, lane, fleet)
        agree_c = (rf[0] == rc[0] and rf[1] == rc[1])
        agree_f = (rf[0] == rf2[0] and rf[1] == rf2[1])
        print(f"{label}: frozen=({rf[0]},{rf[1]}) cand=({rc[0]},{rc[1]}) "
              f"fixed=({rf2[0]},{rf2[1]}) cand==frozen:{agree_c} "
              f"fixed==frozen:{agree_f}")
        if not agree_c:
            print(f"    cand stderr: {rc[2][:170]}")
        CASES[label] = (rf[0], rf[1], rc[0], rc[1], rf2[0], rf2[1])

    # C1: wrong-type blob in the FLEET store only
    l, f, _ = build(base, "C1", blob_in="fleet")
    case("C1-wrongtype-in-fleet", l, f)

    # C2: wrong-type blob in the LANE store only
    l, f, _ = build(base, "C2", blob_in="lane")
    case("C2-wrongtype-in-lane", l, f)

    # C3: fabricated token in Landed, no hole
    l, f, _ = build(base, "C3", fake_landed=True)
    case("C3-fabricated-landed-no-hole", l, f)

    # C4: fabricated token + blob-only hole
    l, f, _ = build(base, "C4", fake_landed=True)
    commit(l, "kama-shokunin", 1050, "round-1: u", "notes/u.txt", "u\n")
    blob = git(l, "rev-parse", "HEAD:notes/u.txt").strip()
    Path(gitdir(l) / "objects" / blob[:2] / blob[2:]).unlink()
    case("C4-fabricated-plus-blob-hole", l, f)

    # C5: fabricated token + a MISSING TREE hole (opaque)
    l, f, _ = build(base, "C5", fake_landed=True)
    commit(l, "kama-shokunin", 1050, "round-1: t", "d/f", "opaque\n")
    dt = git(l, "rev-parse", "HEAD:d").strip()
    Path(gitdir(l) / "objects" / dt[:2] / dt[2:]).unlink()
    case("C5-fabricated-plus-opaque-hole", l, f)

    # C6: DANGLING tree hole (no ref reaches it) + fabricated token
    l, f, _ = build(base, "C6", fake_landed=True)
    dangling_tree(l, "1" * 40)
    case("C6-dangling-tree-hole", l, f)

    # C7: same as C6 but the hole is garbage only (no citation) -> all resolve
    l, f, _ = build(base, "C7", fake_landed=False)
    dangling_tree(l, "2" * 40)
    case("C7-dangling-hole-no-citation", l, f)

    # C8: a real tag whose target is unavailable (unknown must stay)
    l, f, _ = build(base, "C8")
    ident = env(GIT_AUTHOR_NAME="k", GIT_COMMITTER_NAME="k",
                GIT_AUTHOR_EMAIL="a@x", GIT_COMMITTER_EMAIL="a@x")
    tree = git(l, "rev-parse", "HEAD^{tree}").strip()
    target = git(l, "commit-tree", tree, "-m", "tag target", **ident).strip()
    git(l, "tag", "-a", "-m", "hole", "v-hole", target, **ident)
    tag_oid = git(l, "rev-parse", "v-hole").strip()
    Path(gitdir(l) / "objects" / target[:2] / target[2:]).unlink()
    draft = base / "C8-draft.md"
    draft.write_text("## Landed changes\n- `" + tag_oid + "` tag\n")
    argv = [sys.executable, str(cand), "--lane-repo", str(l),
            "--fleet-repo", str(f), "--rounds", "1", "--json",
            "--no-errata", "--report", f"1={draft}"]
    p = subprocess.run(argv, capture_output=True, env=env())
    print(f"C8-tag-unavailable-target: cand_exit={p.returncode} "
          f"err={p.stderr.decode(errors='replace').strip()[:130]}")

    print("\n=== JSON ===")
    print(json.dumps(CASES, indent=1, default=str))


if __name__ == "__main__":
    main()
