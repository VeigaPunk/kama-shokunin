#!/usr/bin/env python3
"""build-survivors.py — round-73 pre-freeze control fixtures (KQ118(a)).

Builds the five fixtures the round's three frozen claims must kill, so the control that
skips the claimed work can be scored before any seat runs:

  c1_clean   a clean repo with round-73 and round-71 freeze plans (both counters: green)
  c1_a5      linked-worktree dirt, primary checkout clean (r72 survivor A5)
  c1_a6e     a valid older-round label (71) while ignored work sits in .ufo/waves/round-72
             (r72 survivor A6)
  c1_a7sub2  a submodule whose .gitmodules sets submodule.sub.ignore=all while the
             submodule worktree holds a modified tracked file and an untracked file
             (r72 survivor A7)
  c2_b6      a receipt graded at revision X and a record-only commit that cites it while
             saying "at the report tip" (r72 survivor B6)
  c3_stale   a PROVINCE.md host-identity block that records a Windows triple on this host

Every fixture is a throwaway git repository under $KAMA_R73_SCRATCH (default
/fast/scratch/hyaku/kama-r73/controls-work). No git mutation runs outside a fixture dir, every
git call names -C <fixture>, and the toplevel is asserted before the first commit.

Usage:
    python3 build-survivors.py [--work DIR] [--meta OUT.json]
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

GITID = ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
         "-c", "commit.gpgsign=false"]


def sh(argv, cwd=None, check=True):
    r = subprocess.run(argv, cwd=None if cwd is None else str(cwd),
                       capture_output=True, text=True)
    if check and r.returncode != 0:
        raise RuntimeError("{} -> {}\n{}\n{}".format(" ".join(argv), r.returncode,
                                                     r.stdout, r.stderr))
    return r


def git(d: Path, *args, check=True):
    r = sh(["git", "-C", str(d), *GITID, *args], check=check)
    return r


def rev(d: Path) -> str:
    return git(d, "rev-parse", "HEAD").stdout.strip()


def porcelain(d: Path, *extra) -> str:
    return git(d, "status", "--porcelain", "-uall", *extra).stdout


def init(d: Path) -> Path:
    d.mkdir(parents=True, exist_ok=True)
    git(d, "init", "-q", "-b", "master")
    top = Path(git(d, "rev-parse", "--show-toplevel").stdout.strip()).resolve()
    assert top == d.resolve(), "toplevel {} != fixture {}".format(top, d)
    return d


def put(d: Path, rel: str, text: str) -> None:
    p = d / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


def commit(d: Path, msg: str) -> str:
    git(d, "add", "-A")
    git(d, "commit", "-q", "-m", msg)
    return rev(d)


SEED_FILES = {
    ".gitignore": "*.log\n",
    "LOG.md": "# kama fixture LOG\n",
    "SCORECARD.md": "# kama fixture SCORECARD\n",
    "plans/round-71-claims.md": "# kama round 71 — frozen claims\n\nfixture\n",
    "plans/round-73-claims.md": "# kama round 73 — frozen claims\n\nfixture\n",
    ".ufo/waves/round-71/keep.txt": "committed receipt\n",
    "corpus/lessons/round-73.md": "# kama round 73 — lesson\n",
}


def build_seed(root: Path) -> Path:
    seed = init(root / "seed")
    for rel, text in SEED_FILES.items():
        put(seed, rel, text)
    commit(seed, "seed")
    return seed


def clone(seed: Path, dest: Path) -> Path:
    if dest.exists():
        shutil.rmtree(dest)
    sh(["git", "clone", "-q", "--shared", str(seed), str(dest)])
    return dest


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--work", default=os.environ.get("KAMA_R73_SCRATCH",
                                                     "/fast/scratch/hyaku/kama-r73/controls-work"))
    ap.add_argument("--meta", default=None)
    args = ap.parse_args(argv)

    root = Path(args.work).resolve()
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    seed = build_seed(root)
    meta = {}

    # --- c1_clean: both tools must stay green on the clean reference ---------------
    clean = clone(seed, root / "fixtures/c1_clean")
    meta["c1_clean"] = {"fixture": str(clean), "round": 73, "porcelain": porcelain(clean)}

    # --- c1_a5: linked worktree dirt, primary clean --------------------------------
    a5 = clone(seed, root / "fixtures/c1_a5")
    wt = root / "fixtures/c1_a5-wt"
    if wt.exists():
        shutil.rmtree(wt)
    git(a5, "worktree", "add", "-q", "--detach", str(wt))
    (wt / "LOG.md").write_text("# kama fixture LOG\ndirty in linked worktree\n")
    (wt / "stray-in-wt.txt").write_text("untracked in linked worktree\n")
    meta["c1_a5"] = {
        "fixture": str(a5),
        "worktree": str(wt),
        "round": 73,
        "porcelain_primary": porcelain(a5),
        "porcelain_worktree": porcelain(wt),
    }

    # --- c1_a6e: valid older label, ignored work in a later round -----------------
    a6e = clone(seed, root / "fixtures/c1_a6e")
    put(a6e, ".ufo/waves/round-72/hidden.log", "ignored work in round 72\n")
    meta["c1_a6e"] = {
        "fixture": str(a6e),
        "round": 71,
        "porcelain": porcelain(a6e),
        "porcelain_ignored": porcelain(a6e, "--ignored", "--", ".ufo/waves"),
    }

    # --- c1_a7sub2: submodule ignore=all hides dirty content ----------------------
    subrepo = init(root / "fixtures/c1_a7_subrepo")
    put(subrepo, "child.txt", "base\n")
    commit(subrepo, "subrepo base")
    a7 = clone(seed, root / "fixtures/c1_a7sub2")
    sh(["git", "-C", str(a7), "-c", "protocol.file.allow=always", "submodule", "add", "-q",
        str(subrepo), "sub"])
    git(a7, "config", "-f", ".gitmodules", "submodule.sub.ignore", "all")
    commit(a7, "add submodule with ignore=all")
    (a7 / "sub/child.txt").write_text("modified inside the submodule\n")
    (a7 / "sub/leak.txt").write_text("untracked inside the submodule\n")
    meta["c1_a7sub2"] = {
        "fixture": str(a7),
        "round": 73,
        "porcelain": porcelain(a7),
        "porcelain_ignoring_none": porcelain(a7, "--ignore-submodules=none"),
        "submodule_porcelain": git(a7 / "sub", "status", "--porcelain", "-uall").stdout,
        "gitmodules": (a7 / ".gitmodules").read_text(),
    }

    # --- c2_b6: receipt measured at X, record-only commit claims "at the report tip" -
    b6 = init(root / "fixtures/c2_b6")
    put(b6, "LOG.md", "# kama fixture LOG\n")
    put(b6, ".ufo/waves/round-72/measured/a.out", "# rev=PLACEHOLDER\nverdict: green\n")
    x = commit(b6, "receipt at X")
    put(b6, ".ufo/waves/round-72/measured/a.out",
        "# rev={}\nverdict: green\n".format(x))
    commit(b6, "receipt header names X")
    put(b6, "SCORECARD.md",
        "# kama fixture SCORECARD\n\n## Round 72 — fixture\n\n- C1 evidence, no receipt.\n")
    put(b6, "corpus/lessons/round-72.md", "# kama round 72 — fixture lesson\n")
    commit(b6, "round-72 record with no receipt citation")
    put(b6, "SCORECARD.md",
        "# kama fixture SCORECARD\n\n## Round 72 — fixture\n\n"
        "- C1 evidence: `.ufo/waves/round-72/measured/a.out` — the gate ran at the report tip.\n")
    y = commit(b6, "record-only edit adds the tip claim")
    meta["c2_b6"] = {
        "fixture": str(b6),
        "round": 72,
        "receipt_rev": x,
        "tip": y,
        "porcelain": porcelain(b6),
    }

    # --- c3_stale: a host-identity block recording a Windows triple ---------------
    c3 = root / "fixtures/c3_stale"
    c3.mkdir(parents=True)
    (c3 / "PROVINCE.md").write_text(
        "# kama fixture PROVINCE\n\n"
        "Round-73 host-identity block (2026-11-03). Host triple: `uname -s` -> `Windows`; "
        "`uname -m` -> `AMD64`; `/etc/os-release` `ID` -> `win`.\n")
    meta["c3_stale"] = {"fixture": str(c3)}

    meta_path = Path(args.meta) if args.meta else root / "fixtures-meta.json"
    meta_path.write_text(json.dumps(meta, indent=1, sort_keys=True) + "\n")
    for name in ("c1_clean", "c1_a5", "c1_a6e", "c1_a7sub2", "c2_b6", "c3_stale"):
        print("FIXTURE {} {}".format(name, meta[name]["fixture"]))
    print("META {}".format(meta_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
