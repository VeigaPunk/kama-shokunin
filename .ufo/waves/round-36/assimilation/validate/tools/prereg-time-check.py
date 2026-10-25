#!/usr/bin/env python3
"""prereg-time-check.py -- falsifier for the 'false timestamp repeated' mistake class.

Given a git repo, a path and a revision, read every recognized UTC time
(YYYY-MM-DDTHH:MM[:SS]Z, YYYY-MM-DD HH:MM[:SS]Z, or YYYY-MM-DD ~HH:MM[:SS]Z —
the T form, a plain-space form and a tilde form) that occurs in the file at
that revision and compare
each against the committer time of the commit that introduced that version of
the file:

    git -C <repo> log -1 --format=%cI <rev> -- <path>

Exit codes:
    0  no timestamp is later than that committer time (within the horizon below)
    1  at least one timestamp is later than that committer time
    2  could not evaluate (bad revision/path, git failure, unreadable file)

Horizon: a timestamp later than the committer time is flagged only when it is
at most --max-future seconds (default 86400) after it. The round-26 tip holds a
legitimately future timestamp (a provider 429 'resets 2026-10-25T14:27:28Z',
~48 h past its commit); treating every later time as a false timestamp would
fail genuine scheduled-future data. --strict disables the horizon and flags ANY
later timestamp, which is the literal reading and also flags such data.

Usage:
    prereg-time-check.py --repo DIR --path PATH --rev REV [--max-future N] [--strict]
    prereg-time-check.py --selftest [--scratch DIR]
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Round 29 (mined mistake): round-28 A1 text "Written 2026-10-23 ~08:45Z" (75b78bb4, committed
# 08:38:16Z) used a space/tilde form this regex missed, so the tool passed a false time. The date
# may now be followed by "T", " " or " ~" (approximate) before HH:MM[:SS]Z.
TIME_RE = re.compile(r"\d{4}-\d{2}-\d{2}(?:T| ~| )\d{2}:\d{2}(?::\d{2})?Z")
DEFAULT_SCRATCH = "/fast/scratch/hyaku/kama-r26/ExecPreregTimeCheck"
DEFAULT_MAX_FUTURE = 86400  # seconds; a guessed 'now' is minutes, not days, ahead

EXIT_CLEAN = 0
EXIT_FLAGGED = 1
EXIT_ERROR = 2


@dataclass
class Finding:
    line: int
    text: str
    when: datetime
    flagged: bool
    reason: str


def run_git(repo: str, args: list[str]) -> tuple[int, str, str]:
    try:
        p = subprocess.run(
            ["git", "-C", repo, *args],
            capture_output=True, text=True, timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as e:
        return 127, "", str(e)
    return p.returncode, p.stdout, p.stderr


def parse_iso(text: str) -> datetime | None:
    """Parse YYYY-MM-DD(T| | ~)HH:MM[:SS]Z strictly; None if out of range/invalid."""
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})(?:T| ~| )(\d{2}):(\d{2})(?::(\d{2}))?Z", text)
    if not m:
        return None
    y, mo, d, h, mi, s = (int(g) if g else 0 for g in m.groups())
    try:
        return datetime(y, mo, d, h, mi, s, tzinfo=timezone.utc)
    except ValueError:
        return None


def committer_time(repo: str, rev: str, path: str) -> tuple[datetime | None, str]:
    rc, out, err = run_git(repo, ["log", "-1", "--format=%cI", rev, "--", path])
    if rc != 0:
        return None, f"git log failed rc={rc}: {err.strip() or out.strip()}"
    line = out.strip()
    if not line:
        return None, f"no commit touches {path} at {rev}"
    try:
        return datetime.fromisoformat(line), ""
    except ValueError:
        return None, f"unparseable %cI {line!r}"


def file_text(repo: str, rev: str, path: str) -> tuple[str | None, str]:
    rc, out, err = run_git(repo, ["show", f"{rev}:{path}"])
    if rc != 0:
        return None, f"git show failed rc={rc}: {err.strip()}"
    return out, ""


def check(repo: str, path: str, rev: str, max_future: int) -> tuple[int, list[str]]:
    """Returns (exit_code, report_lines)."""
    lines: list[str] = []
    ctime, err = committer_time(repo, rev, path)
    if ctime is None:
        return EXIT_ERROR, [f"ERROR could not evaluate: {err}"]
    text, err = file_text(repo, rev, path)
    if text is None:
        return EXIT_ERROR, [f"ERROR could not evaluate: {err}"]

    horizon = timedelta(seconds=max_future) if max_future >= 0 else None
    findings: list[Finding] = []
    for lineno, line in enumerate(text.splitlines(), 1):
        for m in TIME_RE.finditer(line):
            when = parse_iso(m.group(0))
            if when is None:
                continue
            delta = (when - ctime).total_seconds()
            if delta <= 0:
                findings.append(Finding(lineno, m.group(0), when, False, "at/before commit"))
            elif horizon is None or delta <= horizon.total_seconds():
                findings.append(Finding(lineno, m.group(0), when, True,
                                        f"later than commit by {delta:.0f}s"))
            else:
                findings.append(Finding(lineno, m.group(0), when, False,
                                        f"future beyond horizon (+{delta:.0f}s)"))

    flagged = [f for f in findings if f.flagged]
    lines.append(f"rev={rev} path={path}")
    lines.append(f"committer_time={ctime.isoformat()} max_future={max_future}")
    for f in findings:
        mark = "FLAG" if f.flagged else "ok  "
        lines.append(f"  {mark} line {f.line}: {f.text} ({f.reason})")
    if not findings:
        lines.append("  no ISO-8601 UTC timestamps found")
    if flagged:
        lines.append(f"RESULT fail: {len(flagged)} timestamp(s) later than the committer time")
        return EXIT_FLAGGED, lines
    lines.append("RESULT pass: no timestamp later than the committer time")
    return EXIT_CLEAN, lines


# ---------------------------------------------------------------- selftest --

def git_env(committer_iso: str) -> dict[str, str]:
    env = dict(os.environ)
    env.update({
        "GIT_AUTHOR_NAME": "selftest", "GIT_AUTHOR_EMAIL": "selftest@local",
        "GIT_COMMITTER_NAME": "selftest", "GIT_COMMITTER_EMAIL": "selftest@local",
        "GIT_AUTHOR_DATE": committer_iso, "GIT_COMMITTER_DATE": committer_iso,
    })
    return env


def sgit(repo: Path, args: list[str], env: dict[str, str]) -> None:
    p = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, env=env, timeout=30)
    if p.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} rc={p.returncode}: {p.stderr}")


def selftest(scratch: str) -> int:
    root = Path(tempfile.mkdtemp(prefix="ptc-selftest-", dir=scratch))
    env = git_env("2026-10-23T03:19:43+00:00")
    sgit(root, ["init", "-q"], env)
    sgit(root, ["config", "user.name", "selftest"], env)
    sgit(root, ["config", "user.email", "selftest@local"], env)

    ok = True

    def case(name: str, content: str, expect: int, mf: int = DEFAULT_MAX_FUTURE,
             commit_ts: str = "2026-10-23T03:19:43+00:00") -> None:
        nonlocal ok
        (root / "f.json").write_text(content)
        e = git_env(commit_ts)
        sgit(root, ["add", "f.json"], e)
        sgit(root, ["commit", "-q", "--allow-empty", "-m", name], e)
        rc = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"],
                            capture_output=True, text=True, env=e, timeout=30)
        rev = rc.stdout.strip()
        code, lines = check(str(root), "f.json", rev, mf)
        status = "PASS" if code == expect else "FAIL"
        if code != expect:
            ok = False
        print(f"[{status}] {name}: expect {expect}, got {code}")
        for l in lines:
            print(f"        {l}")

    case("clean: timestamp before commit",
         '{"frozen_at_utc": "2026-10-23T03:18:51Z"}\n', EXIT_CLEAN)
    case("flag: minute-precision guess after commit",
         '{"frozen_at_utc": "2026-10-23T03:45Z"}\n', EXIT_FLAGGED)
    case("flag: seconds-precision guess after commit",
         '{"written_utc": "2026-10-23T03:25:00Z"}\n', EXIT_FLAGGED)
    case("clean: legitimate far-future data beyond horizon",
         '{"resets": "2026-10-25T14:27:28Z"}\n', EXIT_CLEAN)
    case("flag: strict mode flags far-future too",
         '{"resets": "2026-10-25T14:27:28Z"}\n', EXIT_FLAGGED, mf=-1)
    case("clean: mixed past and present-boundary times",
         '{"a": "2026-10-23T03:19:43Z", "b": "2026-10-23T03:00:00Z"}\n',
         EXIT_CLEAN)
    case("clean: no timestamps at all", '{"note": "no times here"}\n', EXIT_CLEAN)
    case("flag: space-tilde approximate time after commit (round-28 A1 form)",
         '{"note": "Written 2026-10-23 ~03:45Z by the L1"}\n', EXIT_FLAGGED)
    case("clean: space-separated time before commit",
         '{"note": "frozen 2026-10-23 03:10Z"}\n', EXIT_CLEAN)
    case("flag: space-separated seconds-precision time 7 s after commit",
         '{"note": "frozen 2026-10-23 03:19:50Z"}\n', EXIT_FLAGGED)
    case("clean: malformed Z-suffix lookalike is skipped",
         '{"x": "2026-13-40T03:45Z"}\n', EXIT_CLEAN)

    code, lines = check(str(root), "missing.json", "HEAD", DEFAULT_MAX_FUTURE)
    status = "PASS" if code == EXIT_ERROR else "FAIL"
    if code != EXIT_ERROR:
        ok = False
    print(f"[{status}] missing path: expect 2, got {code} ({lines[0] if lines else ''})")

    code, lines = check(str(root), "f.json", "deadbeef" * 5, DEFAULT_MAX_FUTURE)
    status = "PASS" if code == EXIT_ERROR else "FAIL"
    if code != EXIT_ERROR:
        ok = False
    print(f"[{status}] bad revision: expect 2, got {code} ({lines[0] if lines else ''})")

    print(f"selftest repo: {root}")
    print("SELFTEST " + ("PASS" if ok else "FAIL"))
    return EXIT_CLEAN if ok else EXIT_FLAGGED


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--repo", default=".", help="git repo path (default: cwd)")
    ap.add_argument("--path", help="repo-relative path to inspect")
    ap.add_argument("--rev", help="revision (commit, tag, ...)")
    ap.add_argument("--max-future", type=int, default=DEFAULT_MAX_FUTURE,
                    help="seconds after committer time still treated as a 'now' "
                         f"guess (default {DEFAULT_MAX_FUTURE}); -1 = unlimited")
    ap.add_argument("--strict", action="store_true",
                    help="flag ANY timestamp later than the committer time")
    ap.add_argument("--selftest", action="store_true",
                    help="build a temp repo and verify expected exit codes")
    ap.add_argument("--scratch", default=DEFAULT_SCRATCH,
                    help=f"scratch dir for --selftest (default {DEFAULT_SCRATCH})")
    a = ap.parse_args()

    if a.selftest:
        Path(a.scratch).mkdir(parents=True, exist_ok=True)
        return selftest(a.scratch)

    if not a.path or not a.rev:
        ap.error("--path and --rev are required (or use --selftest)")
    code, lines = check(a.repo, a.path, a.rev, -1 if a.strict else a.max_future)
    for l in lines:
        print(l)
    return code


if __name__ == "__main__":
    sys.exit(main())
