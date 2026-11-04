#!/usr/bin/env python3
"""Build the detector fixtures MT01Mutants scores mutants with.

Shapes mirror .ufo/waves/round-72/controls/{round-scope,receipt-tip}-control.py.
Every repo is created under $S/fixtures and every git call is -C-scoped with a
toplevel assertion before the first commit.
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

FIX = Path("/fast/scratch/hyaku/kama-r72/MT01Mutants/fixtures")
ROUND = 72

SCOPE_FILES = {
    "SCORECARD.md": "# scorecard\n\n## Axes\n\n| axis | score |\n|---|---|\n| calibration | 7 |\n",
    "LOG.md": "# log\n",
    "SKILL.md": "# skill\n",
    "PROVINCE.md": "# province\n",
    "corpus/SOURCES.md": "# sources\n",
    ".gitignore": ".ufo/waves/round-72/*.log\n",
    "plans/round-72-claims.md": "# kama round 72 \u2014 frozen claims\n\nbody\n",
    ".ufo/waves/round-72/evidence.txt": "committed evidence\n",
}


def run(argv, cwd):
    return subprocess.run(argv, cwd=str(cwd), capture_output=True, text=True)


def git(repo: Path, *args, commit=False):
    base = ["git", "-C", str(repo)]
    if commit:
        base += ["-c", "user.name=fixture", "-c", "user.email=fixture@invalid",
                 "-c", "commit.gpgsign=false"]
    p = run(base + list(args), repo.parent)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr.strip()}")
    return p.stdout


def init(repo: Path):
    repo.mkdir(parents=True, exist_ok=False)
    run(["git", "init", "-q", "-b", "master", str(repo)], repo.parent)
    top = git(repo, "rev-parse", "--show-toplevel").strip()
    import os
    if os.path.realpath(top) != os.path.realpath(str(repo)):
        raise RuntimeError(f"toplevel {top!r} != {str(repo)!r}")
    git(repo, "config", "core.autocrlf", "false")


def commit_all(repo: Path, msg: str):
    git(repo, "add", "-A")
    git(repo, "commit", "-q", "-m", msg, commit=True)
    return git(repo, "rev-parse", "HEAD").strip()


def write(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def scope_fixture(case: str) -> Path:
    root = FIX / f"scope-{case}" / "repo"
    if (FIX / f"scope-{case}").exists():
        shutil.rmtree(FIX / f"scope-{case}")
    init(root)
    for rel, body in SCOPE_FILES.items():
        write(root / rel, body)
    if case == "clean":
        pass
    elif case == "label-missing":
        (root / "plans/round-72-claims.md").unlink()
    elif case == "label-wrong":
        write(root / "plans/round-72-claims.md", "# kama round 71 \u2014 frozen claims\n\nbody\n")
    elif case == "label-later":
        write(root / "plans/round-72-claims.md",
              "# kama round 71 \u2014 frozen claims\n\n## kama round 72 \u2014 frozen claims\n\nbody\n")
    elif case == "ignored-root":
        write(root / ".gitignore", "*.log\n")
    elif case in ("stray", "stray-dir", "wave-uncommitted", "ignored-root",
                  "wave-record", "label-later", "rename"):
        pass
    elif case == "ignored":
        pass
    else:
        raise SystemExit(f"unknown scope case {case}")
    commit_all(root, "fixture")
    if case == "stray":
        write(root / "stray-note.md", "uncommitted round work outside the wave dir\n")
    if case == "wave-uncommitted":
        write(root / ".ufo/waves/round-72/uncommitted.txt", "uncommitted wave work\n")
    if case == "wave-record":
        write(root / ".ufo/waves/round-72/records/new.out", "uncommitted record\n")
    if case == "ignored-root":
        write(root / "notes.log", "ignored outside the wave dir\n")
    if case == "rename":
        git(root, "mv", "LOG.md", "LOG2.md")
    if case == "stray-dir":
        write(root / "newdir/a.txt", "untracked dir member a\n")
        write(root / "newdir/b.txt", "untracked dir member b\n")
    if case == "ignored":
        write(root / ".ufo/waves/round-72/scratch.log", "ignored evidence\n")
    return root


def binding_fixture(case: str) -> Path:
    root = FIX / f"bind-{case}" / "repo"
    if (FIX / f"bind-{case}").exists():
        shutil.rmtree(FIX / f"bind-{case}")
    init(root)
    write(root / "tools/probe.py", "print('instrument v1')\n")
    receipt = root / ".ufo/waves/round-72/measured/a.out"
    write(receipt, "RESULT pass=1\n")
    write(root / "corpus/lessons/round-72.md",
          "receipt `.ufo/waves/round-72/measured/a.out`\n")
    write(root / "SCORECARD.md", "# scorecard\n\n## Round 72\n\nreceipt `%s`\n"
          % ".ufo/waves/round-72/measured/a.out")
    first = commit_all(root, "base")
    if case == "stale":
        subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached",
                        ".ufo/waves/round-72/measured/a.out"], check=True)
        receipt.unlink()
        commit_all(root, "drop receipt")
    if case in ("unbound", "shifted"):
        if case == "shifted":
            write(receipt, f"# tip={first}\nRESULT pass=1\n")
            write(root / "tools/probe.py", "print('instrument v2')\n")
        else:
            # header-less receipt; the land commit touches a record path only, so the
            # missing header is the single defect under test.
            write(root / "corpus/lessons/round-72.md",
                  "receipt `.ufo/waves/round-72/measured/a.out`\n\nlanded.\n")
        commit_all(root, "land")
    if case == "clean":
        # header names the base rev; the delta base..tip touches only record paths.
        write(receipt, f"# tip={first}\nRESULT pass=1\n")
        commit_all(root, "land")
    if case == "nonancestor":
        # a real commit of this repo that is NOT an ancestor of the tip
        git(root, "checkout", "-q", "-b", "side")
        write(root / "corpus/lessons/side-note.md", "side branch work\n")
        commit_all(root, "side")
        side = git(root, "rev-parse", "HEAD").strip()
        git(root, "checkout", "-q", "master")
        write(receipt, "# tip=%s\nRESULT pass=1\n" % side)
        commit_all(root, "land")
    if case == "brace":
        write(root / ".ufo/waves/round-72/measured/b.out", "RESULT pass=1\n")
        write(root / "corpus/lessons/round-72.md",
              "receipts `.ufo/waves/round-72/{measured/a.out,measured/b.out}`\n")
        first2 = commit_all(root, "base2")
        write(receipt, "# tip=%s\nRESULT pass=1\n" % first2)
        write(root / ".ufo/waves/round-72/measured/b.out", "# tip=%s\nRESULT pass=1\n" % first2)
        commit_all(root, "land")
    if case == "conflict":
        git(root, "checkout", "-q", "-b", "side")
        write(root / "corpus/lessons/side-note.md", "side branch work\n")
        commit_all(root, "side")
        side = git(root, "rev-parse", "HEAD").strip()
        git(root, "checkout", "-q", "master")
        write(receipt, "# tip=%s\n# rev=%s\nRESULT pass=1\n" % (first, side))
        commit_all(root, "land")
    if case == "late-header":
        body = "".join("filler line %d\n" % i for i in range(10))
        write(receipt, body + "# tip=%s\nRESULT pass=1\n" % first)
        commit_all(root, "land")
    if case == "nonscoped":
        # header names a rev that is not an ancestor of the tip (different root).
        write(receipt, "# tip=" + "0" * 40 + "\nRESULT pass=1\n")
        commit_all(root, "land")
    return root


if __name__ == "__main__":
    out = {}
    for case in ("clean", "label-missing", "label-wrong", "label-later", "stray",
                 "stray-dir", "wave-uncommitted", "wave-record", "ignored", "ignored-root",
                 "rename"):
        r = scope_fixture(case)
        out[f"scope-{case}"] = str(r)
    for case in ("clean", "unbound", "shifted", "stale", "nonancestor", "brace",
                 "late-header", "conflict"):
        r = binding_fixture(case)
        out[f"bind-{case}"] = str(r)
    print(json.dumps(out, indent=1))
