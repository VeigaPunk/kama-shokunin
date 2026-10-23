#!/usr/bin/env python3
"""gate-registry-check.py -- falsifier for the 'counter has no gate registry row' mistake class.

Every round counter is a lane instrument; an instrument that SKILL.md never
mentions cannot be graded, re-run or retired by a reader. This check lists the
counters the lane tracks and reports the ones its own SKILL.md does not name.

Contract:
    - The counter population is every tracked path matching
      ``.ufo/waves/round-*/count-*.py`` (one directory level below
      ``.ufo/waves/``, extension ``.py``).
    - The registry is SKILL.md at the evaluated revision. A path is
      ``registered`` iff its repo-relative text occurs verbatim in that file.
    - Each missing path prints ``unregistered <path>`` (sorted). The final line
      is always ``registered R unregistered U``.

Exit codes:
    0  U == 0: every tracked counter is named in SKILL.md
    1  U > 0: at least one tracked counter is not named
    2  could not evaluate (not a git repo, bad revision, missing SKILL.md,
       unreadable file, git failure/timeout)

Read-only: the tool issues only ``git rev-parse --show-toplevel``,
``git ls-tree``, ``git ls-files`` and ``git show``; it never writes to the
repository. That rev-parse is the sole non-show/non-ls-tree command and exists
only to resolve ``--repo`` (default ``.``) and to read the working-tree
SKILL.md at the repository root.

Boundary, stated because it bounds the verdict: this is an occurrence check,
not a table-row check. A path named in prose (e.g. a wave-artifact paragraph)
counts exactly like a registry row, and a registry row's columns -- entry
command, verdict map, self-test, pinned values -- are not inspected. The
round-27 defect requires such a row; this tool can only prove the path is
absent or present.

Usage:
    gate-registry-check.py [--repo DIR] [--rev REV]

    --repo DIR   Repository to evaluate (default: current directory).
    --rev REV    Git revision whose tree and SKILL.md are evaluated.
                 Default: the working tree (tracked files from the index,
                 SKILL.md from the filesystem).
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

COUNTER_RE = re.compile(r"^\.ufo/waves/round-[^/]+/count-[^/]+\.py$")
SKILL_PATH = "SKILL.md"

EXIT_CLEAN = 0
EXIT_UNREGISTERED = 1
EXIT_ERROR = 2

GIT_TIMEOUT = 30


def run_git(root: str, args: list[str]) -> tuple[int, bytes, str]:
    try:
        p = subprocess.run(
            ["git", "-C", root, *args],
            capture_output=True,
            timeout=GIT_TIMEOUT,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, b"", str(e)
    return p.returncode, p.stdout, p.stderr.decode("utf-8", "replace").strip()


def git_root(repo: str) -> tuple[str | None, str]:
    rc, out, err = run_git(repo, ["rev-parse", "--show-toplevel"])
    if rc != 0:
        return None, f"not a git working tree at {repo!r}: {err or f'rc={rc}'}"
    root = out.decode("utf-8", "surrogateescape").strip()
    if not root:
        return None, f"empty repository root for {repo!r}"
    return root, ""


def tracked_counters(root: str, rev: str | None) -> tuple[list[str] | None, str]:
    if rev is None:
        rc, out, err = run_git(root, ["ls-files", "-z"])
    else:
        rc, out, err = run_git(root, ["ls-tree", "-r", "-z", "--name-only", "--full-tree", rev])
    if rc != 0:
        what = "git ls-files" if rev is None else f"git ls-tree {rev}"
        return None, f"{what} failed: {err or f'rc={rc}'}"
    paths = [
        p.decode("utf-8", "surrogateescape")
        for p in out.split(b"\0")
        if p
    ]
    return sorted(p for p in paths if COUNTER_RE.match(p)), ""


def skill_text(root: str, rev: str | None) -> tuple[str | None, str]:
    if rev is None:
        path = Path(root) / SKILL_PATH
        try:
            return path.read_text(encoding="utf-8", errors="surrogateescape"), ""
        except OSError as e:
            return None, f"cannot read {path}: {e}"
    rc, out, err = run_git(root, ["show", f"{rev}:{SKILL_PATH}"])
    if rc != 0:
        return None, f"git show {rev}:{SKILL_PATH} failed: {err or f'rc={rc}'}"
    return out.decode("utf-8", "surrogateescape"), ""


def evaluate(repo: str, rev: str | None) -> tuple[int, list[str], str]:
    root, err = git_root(repo)
    if root is None:
        return EXIT_ERROR, [], err
    counters, err = tracked_counters(root, rev)
    if counters is None:
        return EXIT_ERROR, [], err
    text, err = skill_text(root, rev)
    if text is None:
        return EXIT_ERROR, [], err

    unregistered = [p for p in counters if p not in text]
    registered = len(counters) - len(unregistered)
    lines = [f"unregistered {p}" for p in unregistered]
    lines.append(f"registered {registered} unregistered {len(unregistered)}")
    return (EXIT_CLEAN if not unregistered else EXIT_UNREGISTERED), lines, ""


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(
        description="Report tracked round counters that SKILL.md does not name.",
    )
    ap.add_argument("--repo", default=".", help="repository to evaluate (default: .)")
    ap.add_argument(
        "--rev",
        default=None,
        help="git revision to evaluate (default: the working tree)",
    )
    args = ap.parse_args(argv)

    code, lines, err = evaluate(args.repo, args.rev)
    if code == EXIT_ERROR:
        print(f"ERROR could not evaluate: {err}", file=sys.stderr)
        return EXIT_ERROR
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main())
