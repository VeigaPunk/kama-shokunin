#!/usr/bin/env python3
"""round67-worktree-landing-check.py - the landed self-record is what HEAD holds.

Round-65 mistake 2: the round's SCORECARD record sat uncommitted and
CRLF-translated in the worktree while the report claimed it had landed; the
defect was caught only by the closure's manual worktree-vs-HEAD hash check.
This instrument makes that check runnable at round end, before the report: for
every declared path, the worktree bytes must be byte-identical to the HEAD
blob. It reads no index and runs no ``git status`` (both are unreliable on
this host); it compares bytes.

    WORKTREE_LANDING_CHECK paths=N clean=N dirty=N missing=N untracked=N unreadable=R
    clean <path>
    DIRTY <path>       tracked at HEAD, worktree bytes differ (any byte,
                       including a newline translation)
    MISSING <path>     tracked at HEAD, absent from the worktree
    UNTRACKED <path>   in the worktree, not in HEAD's tree
    UNREADABLE <path>  tracked at HEAD, worktree path cannot be read (OSError)

Exit: 0 every declared path is clean; 1 any DIRTY/MISSING/UNREADABLE/UNTRACKED
(a dirty landing is a defect, not a could-not-evaluate); 2 could-not-evaluate
(not a git work tree, HEAD unresolvable, git plumbing failure, an invalid
--paths token). Read-only on the evaluated repository: it reads the declared
worktree files and issues only ``git rev-parse``, ``git cat-file -e`` and
``git show``; it writes nothing there.

    --paths a,b,c  declare the paths to grade (comma-separated, repo-relative).
                   Default: the lane self-record set SCORECARD.md, LOG.md,
                   PROVINCE.md, SKILL.md, corpus/SOURCES.md.
    --selftest     fixture arms below; prints WLC_SELFTEST pass=N fail=M. The
                   fixture pins its own core.autocrlf=false so the committed
                   blob bytes are exactly the bytes written, on any host.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_PATHS = [
    "SCORECARD.md",
    "LOG.md",
    "PROVINCE.md",
    "SKILL.md",
    "corpus/SOURCES.md",
]
GIT_TIMEOUT = 60


def git(root: str, *args: str) -> tuple[int, bytes, bytes]:
    try:
        proc = subprocess.run(["git", "-C", root, *args], capture_output=True,
                              timeout=GIT_TIMEOUT)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return 127, b"", str(exc).encode("utf-8", "replace")
    return proc.returncode, proc.stdout, proc.stderr


def evaluate(repo: str, paths: list[str]) -> tuple[int, list[str]]:
    rc, out, err = git(repo, "rev-parse", "--show-toplevel")
    if rc != 0:
        return 2, [f"WORKTREE_LANDING_CHECK could-not-evaluate: "
                   f"not a git work tree: {err.decode('utf-8', 'replace').strip()}"]
    rc, out, err = git(repo, "rev-parse", "--verify", "HEAD")
    if rc != 0:
        return 2, [f"WORKTREE_LANDING_CHECK could-not-evaluate: "
                   f"HEAD unresolvable: {err.decode('utf-8', 'replace').strip()}"]
    lines: list[str] = []
    counts = {"clean": 0, "dirty": 0, "missing": 0, "untracked": 0, "unreadable": 0}
    bad = 0
    for rel in paths:
        pure = Path(rel)
        if pure.is_absolute() or ".." in pure.parts or not rel.strip():
            return 2, [f"WORKTREE_LANDING_CHECK could-not-evaluate: "
                       f"invalid path token {rel!r}"]
        rc, blob, _ = git(repo, "cat-file", "-e", f"HEAD:{rel}")
        in_head = rc == 0
        work = Path(repo) / pure
        try:
            data = work.read_bytes()
        except FileNotFoundError:
            # a worktree path that does not exist: MISSING when HEAD tracks it,
            # UNTRACKED when it does not (subclass order matters: FileNotFoundError
            # is an OSError)
            counts["missing" if in_head else "untracked"] += 1
            bad += 1
            lines.append(f"{'MISSING' if in_head else 'UNTRACKED'} {rel}")
            continue
        except OSError as exc:
            if in_head:
                counts["unreadable"] += 1
                bad += 1
                lines.append(f"UNREADABLE {rel} ({exc})")
            else:
                counts["untracked"] += 1
                bad += 1
                lines.append(f"UNTRACKED {rel}")
            continue
        if not in_head:
            counts["untracked"] += 1
            bad += 1
            lines.append(f"UNTRACKED {rel}")
            continue
        rc, blob, _ = git(repo, "show", f"HEAD:{rel}")
        if rc != 0:
            return 2, [f"WORKTREE_LANDING_CHECK could-not-evaluate: "
                       f"git show HEAD:{rel} failed"]
        if data == blob:
            counts["clean"] += 1
            lines.append(f"clean {rel}")
        else:
            counts["dirty"] += 1
            bad += 1
            lines.append(f"DIRTY {rel}")
    lines.append(
        f"WORKTREE_LANDING_CHECK paths={len(paths)} clean={counts['clean']} "
        f"dirty={counts['dirty']} missing={counts['missing']} "
        f"untracked={counts['untracked']} unreadable={counts['unreadable']}"
    )
    return (0 if bad == 0 else 1), lines


def selftest() -> int:
    passed = failed = 0

    def arm(label: str, want_code: int, want_line: str, repo: str,
            paths: list[str]) -> None:
        nonlocal passed, failed
        code, lines = evaluate(repo, paths)
        summary = lines[-1] if lines else ""
        ok = code == want_code and want_line in lines
        passed += int(ok)
        failed += int(not ok)
        print(f"{'PASS' if ok else 'FAIL'} {label}: exit={code} (want {want_code}) "
              f"summary={summary!r} want-line={want_line!r}")

    def commit(repo: str, files: dict[str, bytes]) -> None:
        for name, body in files.items():
            target = Path(repo) / name
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "wb") as fh:  # bytes: no newline translation (S538)
                fh.write(body)
        git(repo, "add", "--", *files.keys())
        git(repo, "-c", "user.name=wlc-selftest", "-c", "user.email=wlc@invalid",
            "-c", "commit.gpgsign=false", "commit", "-q", "-m", "fixture")

    with tempfile.TemporaryDirectory(prefix="wlc-selftest-") as tmp:
        repo = os.path.join(tmp, "r1")
        os.makedirs(repo)
        git(repo, "init", "-q")
        git(repo, "config", "core.autocrlf", "false")
        body = b"line one\nline two\nline three\n"
        commit(repo, {"a.md": body})
        arm("clean-control", 0, "WORKTREE_LANDING_CHECK paths=1 clean=1 dirty=0 "
            "missing=0 untracked=0 unreadable=0", repo, ["a.md"])

        with open(os.path.join(repo, "a.md"), "ab") as fh:
            fh.write(b"appended")
        arm("dirty-append", 1, "DIRTY a.md", repo, ["a.md"])

        with open(os.path.join(repo, "a.md"), "wb") as fh:
            fh.write(body.replace(b"\n", b"\r\n"))
        arm("dirty-crlf-translation", 1, "DIRTY a.md", repo, ["a.md"])

        os.remove(os.path.join(repo, "a.md"))
        code, lines = evaluate(repo, ["a.md"])
        ok = (code == 1
              and "MISSING a.md" in lines
              and "WORKTREE_LANDING_CHECK paths=1 clean=0 dirty=0 missing=1 "
                  "untracked=0 unreadable=0" in lines)
        passed += int(ok)
        failed += int(not ok)
        print(f"{'PASS' if ok else 'FAIL'} missing-worktree: exit={code} (want 1) "
              f"lines={[l for l in lines if l != lines[-1]]!r}")

        repo2 = os.path.join(tmp, "r2")
        os.makedirs(repo2)
        git(repo2, "init", "-q")
        git(repo2, "config", "core.autocrlf", "false")
        commit(repo2, {"base.md": body})
        with open(os.path.join(repo2, "u.md"), "wb") as fh:
            fh.write(body)
        arm("untracked-declared", 1, "UNTRACKED u.md", repo2, ["u.md"])

        repo3 = os.path.join(tmp, "r3")
        os.makedirs(repo3)
        git(repo3, "init", "-q")
        git(repo3, "config", "core.autocrlf", "false")
        commit(repo3, {"sub/dir/b.md": body})
        arm("nested-path-clean", 0, "WORKTREE_LANDING_CHECK paths=1 clean=1 dirty=0 "
            "missing=0 untracked=0 unreadable=0", repo3, ["sub/dir/b.md"])

    print(f"WLC_SELFTEST pass={passed} fail={failed}")
    return 0 if failed == 0 else 1


def main(argv: list[str]) -> int:
    args = list(argv)
    paths = list(DEFAULT_PATHS)
    repo = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if "--selftest" in args:
        return selftest()
    i = 0
    while i < len(args):
        if args[i] == "--paths":
            if i + 1 >= len(args):
                print("WORKTREE_LANDING_CHECK could-not-evaluate: --paths needs "
                      "a comma-separated value", file=sys.stderr)
                return 2
            paths = [p for p in args[i + 1].split(",") if p]
            i += 2
            continue
        if args[i] == "--repo":
            if i + 1 >= len(args):
                print("WORKTREE_LANDING_CHECK could-not-evaluate: --repo needs "
                      "a directory", file=sys.stderr)
                return 2
            repo = args[i + 1]
            i += 2
            continue
        print(f"WORKTREE_LANDING_CHECK could-not-evaluate: unknown argument "
              f"{args[i]!r}", file=sys.stderr)
        return 2
    if not paths:
        print("WORKTREE_LANDING_CHECK could-not-evaluate: empty path set",
              file=sys.stderr)
        return 2
    code, lines = evaluate(repo, paths)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
