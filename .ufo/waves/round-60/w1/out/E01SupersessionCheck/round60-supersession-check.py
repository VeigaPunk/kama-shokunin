#!/usr/bin/env python3
"""Round-60 supersession check: does every `supersedes S0NN` row carry a marked flip?

Usage:
    python3 round60-supersession-check.py --repo REPO --tip REV
    python3 round60-supersession-check.py --selftest

Contract (read from corpus/SOURCES.md at REV with `git show`):

  A *pair* is a registry row whose `teaches` cell begins `supersedes S0NN`
  (the superseding row). For every pair the tool requires:

    (a) the target row S0NN exists in the registry at REV;
    (b) if the target's `status` is `rejected`, the target's `used-by` cell
        cites at least one `corpus/lessons/*.md` path that exists at REV and
        whose text names both the target id and the superseding id and the
        word `flip` (a word-boundary match, case-insensitive, so a lesson that
        only says "flipping" does not count);
    (c) the superseding row's `status` is not `rejected`.

  Registry parsing mirrors scripts/sources-census.sh: only rows inside the
  `## Registry` section, table rows with 0-3 leading ASCII spaces; 4 or more
  leading spaces are indented code and ignored; a row must carry exactly
  11 cells (13 fields when split on `|`).

Output (one line on stdout):
    pairs=P unresolved=U ids=<comma list> met=<True|False>

  P is the number of pairs, U the number of pairs failing (a), (b) or (c),
  and ids the sorted, de-duplicated target ids of the failing pairs (a
  missing target is itself an id). Per-pair reasons go to stderr.

Exit: 0 iff U == 0; 1 when U > 0; 2 on parse/IO/environment error (never 0).

Selftest (`--selftest`) builds 12 fixture repositories under $TMPDIR and
commits one fixture per commit; it refuses a temporary directory that
resolves to /tmp. Python 3 standard library only.
"""

import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROW_RE = re.compile(r"^ {0,3}\|")
HEAD_RE = re.compile(r"^ {0,3}##[ \t]")
TOP_HEAD_RE = re.compile(r"^ {0,3}#[ \t]")
ID_RE = re.compile(r"^S\d{3,}$")
SUP_RE = re.compile(r"supersedes\s+(S\d{3,})\b")
LESSON_RE = re.compile(r"^corpus/lessons/[^/]+\.md$")
SEP_CELL_RE = re.compile(r"^:?-+:?$")
FLIP_RE = re.compile(r"\bflip\b", re.IGNORECASE)

REGISTRY_PATH = "corpus/SOURCES.md"
EMPTY_CELL = "\u2014"  # em dash used by the lane as "no value"


class CheckError(Exception):
    """Parse, IO or environment error: exit 2, never a pass."""


def git_env():
    """A git environment with GIT_* injection stripped (SOURCES S510/S511)."""
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env["GIT_CONFIG_NOSYSTEM"] = "1"
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_TERMINAL_PROMPT"] = "0"
    return env


def git(repo, *args):
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            env=git_env(),
        )
    except OSError as exc:
        raise CheckError(f"git could not be executed: {exc}") from exc


def blob_at(repo, rev, path):
    """Return the blob text at REV:path, or None when the path is absent."""
    proc = git(repo, "show", f"{rev}:{path}")
    if proc.returncode != 0:
        return None
    return proc.stdout.decode("utf-8", "replace")


def parse_registry(text):
    """Parse the ## Registry table; raise CheckError on anything ambiguous."""
    rows = {}
    in_registry = False
    saw_registry = False
    for raw in text.split("\n"):
        if HEAD_RE.match(raw):
            line = raw.lstrip(" ")
            in_registry = line[2:].strip() == "Registry"
            saw_registry = saw_registry or in_registry
            continue
        if TOP_HEAD_RE.match(raw):
            in_registry = False
            continue
        if not in_registry or not ROW_RE.match(raw):
            continue
        line = raw.lstrip(" ")
        parts = line.split("|")
        if len(parts) >= 2 and parts[1].strip() == "id":
            continue
        if len(parts) >= 3 and all(SEP_CELL_RE.match(c) for c in parts[1:-1]):
            continue
        if len(parts) != 13:
            raise CheckError(
                f"malformed registry row ({len(parts) - 2} cells, want 11): {line[:80]!r}"
            )
        cells = [c.strip() for c in parts[1:-1]]
        rid = cells[0]
        if not ID_RE.match(rid):
            raise CheckError(f"malformed registry id {rid!r}: {line[:80]!r}")
        if rid in rows:
            raise CheckError(f"duplicate registry row {rid}")
        rows[rid] = {
            "id": rid,
            "teaches": cells[6],
            "status": cells[7],
            "usedby": cells[10],
        }
    if not saw_registry:
        raise CheckError("no '## Registry' section in " + REGISTRY_PATH)
    if not rows:
        raise CheckError("registry table has no rows")
    return rows


def cites_flip_lesson(repo, rev, target, superseder_id):
    """(b): does a cited, existing corpus/lessons/*.md name both ids and `flip`?"""
    for path in (p.strip() for p in target["usedby"].split(",")):
        if not path or path == EMPTY_CELL or not LESSON_RE.match(path):
            continue
        text = blob_at(repo, rev, path)
        if text is None:
            continue
        if (
            re.search(rf"\b{re.escape(target['id'])}\b", text)
            and re.search(rf"\b{re.escape(superseder_id)}\b", text)
            and FLIP_RE.search(text)
        ):
            return path
    return None


def evaluate(repo, rev, rows):
    pairs = 0
    problems = []  # (target_id, superseder_id, reason)
    for sid in sorted(rows):
        row = rows[sid]
        match = SUP_RE.match(row["teaches"])
        if not match:
            continue
        pairs += 1
        tid = match.group(1)
        reasons = []
        target = rows.get(tid)
        if target is None:
            reasons.append(f"target {tid} is missing from the registry")
        elif target["status"] == "rejected":
            lesson = cites_flip_lesson(repo, rev, target, sid)
            if lesson is None:
                reasons.append(
                    f"target {tid} is rejected and its used-by cell cites no "
                    f"corpus/lessons/*.md at {rev} naming both {tid} and {sid} "
                    f"and the word flip"
                )
        if row["status"] == "rejected":
            reasons.append(f"superseding row {sid} is rejected")
        if reasons:
            problems.append((tid, sid, "; ".join(reasons)))
    ids = sorted({tid for tid, _sid, _reason in problems})
    return pairs, ids, problems


def run_check(repo, rev):
    """Run the contract and return (pairs, ids, problems); raise CheckError."""
    if not os.path.isdir(str(repo)):
        raise CheckError(f"--repo is not a directory: {repo}")
    text = blob_at(repo, rev, REGISTRY_PATH)
    if text is None:
        raise CheckError(f"{REGISTRY_PATH} does not exist at {rev!r} in {repo}")
    rows = parse_registry(text)
    return evaluate(repo, rev, rows)


# ---------------------------------------------------------------- selftest ---

FIXTURE_HEADER = """# SOURCES fixture

## Registry

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
"""


def fixture_row(rid, teaches, status="mined", usedby=EMPTY_CELL, indent=""):
    return (
        f"{indent}| {rid} | source {rid} | docs | A | scope | anchor | {teaches} "
        f"| {status} | 2026-10-27 | 90d | {usedby} |"
    )


def fixture_sources(*rows):
    return FIXTURE_HEADER + "\n".join(rows) + "\n"


RESOLVED_TARGET = fixture_row(
    "S901", "the old fact", status="rejected", usedby="corpus/lessons/fix.md"
)
RESOLVED_SUPERSEDER = fixture_row("S902", "supersedes S901 \u2014 the corrected fact")


def selftest_fixtures():
    """(name, files, expected stdout line, expected exit code)."""
    resolved_lesson = (
        "S902 supersedes S901. The flip condition fired and the pair is marked.\n"
    )
    return [
        (
            "resolved-pair",
            {
                REGISTRY_PATH: fixture_sources(RESOLVED_TARGET, RESOLVED_SUPERSEDER),
                "corpus/lessons/fix.md": resolved_lesson,
            },
            "pairs=1 unresolved=0 ids= met=True",
            0,
        ),
        (
            "used-by-dash",
            {
                REGISTRY_PATH: fixture_sources(
                    fixture_row("S901", "the old fact", status="rejected", usedby=EMPTY_CELL),
                    RESOLVED_SUPERSEDER,
                ),
                # Uncited lesson naming both ids and flip: a global scan would
                # wrongly resolve the pair.
                "corpus/lessons/uncited.md": resolved_lesson,
            },
            "pairs=1 unresolved=1 ids=S901 met=False",
            1,
        ),
        (
            "lesson-names-one-id",
            {
                REGISTRY_PATH: fixture_sources(RESOLVED_TARGET, RESOLVED_SUPERSEDER),
                "corpus/lessons/fix.md": "S902 is the superseding row; flip.\n",
            },
            "pairs=1 unresolved=1 ids=S901 met=False",
            1,
        ),
        (
            "lesson-without-flip-word",
            {
                REGISTRY_PATH: fixture_sources(RESOLVED_TARGET, RESOLVED_SUPERSEDER),
                "corpus/lessons/fix.md": (
                    "S902 supersedes S901; the flipping condition fired and the "
                    "pair is marked.\n"
                ),
            },
            "pairs=1 unresolved=1 ids=S901 met=False",
            1,
        ),
        (
            "missing-target",
            {
                REGISTRY_PATH: fixture_sources(
                    fixture_row("S903", "supersedes S999 \u2014 a phantom correction")
                ),
            },
            "pairs=1 unresolved=1 ids=S999 met=False",
            1,
        ),
        (
            "rejected-superseder",
            {
                REGISTRY_PATH: fixture_sources(
                    fixture_row("S904", "an untouched fact"),
                    fixture_row(
                        "S905",
                        "supersedes S904 \u2014 a rejected correction",
                        status="rejected",
                        usedby=EMPTY_CELL,
                    ),
                ),
            },
            "pairs=1 unresolved=1 ids=S904 met=False",
            1,
        ),
        (
            "no-pairs",
            {
                REGISTRY_PATH: fixture_sources(
                    fixture_row("S908", "a plain fact", usedby=EMPTY_CELL)
                ),
            },
            "pairs=0 unresolved=0 ids= met=True",
            0,
        ),
        (
            "four-space-indent-ignored",
            {
                REGISTRY_PATH: fixture_sources(
                    RESOLVED_TARGET,
                    RESOLVED_SUPERSEDER,
                    # Four leading spaces: indented code, ignored by the census.
                    fixture_row(
                        "S907",
                        "supersedes S906 \u2014 must never be parsed",
                        indent="    ",
                    ),
                ),
                "corpus/lessons/fix.md": resolved_lesson,
            },
            "pairs=1 unresolved=0 ids= met=True",
            0,
        ),
        (
            "non-lesson-citation",
            {
                REGISTRY_PATH: fixture_sources(
                    fixture_row(
                        "S901",
                        "the old fact",
                        status="rejected",
                        usedby="corpus/knowledge/not-a-lesson.md",
                    ),
                    RESOLVED_SUPERSEDER,
                ),
                "corpus/knowledge/not-a-lesson.md": resolved_lesson,
            },
            "pairs=1 unresolved=1 ids=S901 met=False",
            1,
        ),
        (
            "cited-lesson-missing",
            {
                REGISTRY_PATH: fixture_sources(
                    fixture_row(
                        "S901",
                        "the old fact",
                        status="rejected",
                        usedby="corpus/lessons/absent.md",
                    ),
                    RESOLVED_SUPERSEDER,
                ),
            },
            "pairs=1 unresolved=1 ids=S901 met=False",
            1,
        ),
        (
            "multi-unresolved-sorted",
            {
                REGISTRY_PATH: fixture_sources(
                    fixture_row("S901", "the old fact", status="rejected", usedby=EMPTY_CELL),
                    RESOLVED_SUPERSEDER,
                    fixture_row("S903", "supersedes S999 \u2014 a phantom correction"),
                ),
            },
            "pairs=2 unresolved=2 ids=S901,S999 met=False",
            1,
        ),
        (
            "sources-missing",
            {"corpus/lessons/fix.md": resolved_lesson},
            None,
            2,
        ),
    ]


def fixture_git(repo, *args, check=True):
    proc = git(repo, *args)
    if check and proc.returncode != 0:
        raise CheckError(
            f"fixture git {' '.join(args)} failed: "
            + proc.stderr.decode("utf-8", "replace").strip()
        )
    return proc


def write_fixture_file(root, rel, text):
    path = os.path.join(root, rel)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(text)


def selftest():
    tmpdir = os.environ.get("TMPDIR") or tempfile.gettempdir()
    real = os.path.realpath(tmpdir)
    if real == "/tmp" or real.startswith("/tmp" + os.sep):
        raise CheckError(
            f"temporary directory resolves to {real}; set TMPDIR to a scratch dir "
            "(this tool never writes under /tmp)"
        )
    os.makedirs(real, exist_ok=True)
    root = tempfile.mkdtemp(prefix="round60-supersession-", dir=real)
    written = set()
    tested = 0
    failures = 0
    try:
        fixture_git(root, "init", "-q")
        top = fixture_git(root, "rev-parse", "--show-toplevel").stdout.decode().strip()
        if os.path.realpath(top) != os.path.realpath(root):
            raise CheckError(f"fixture toplevel {top!r} is not {root!r}")
        tool = os.path.abspath(__file__)
        for name, files, expected_stdout, expected_rc in selftest_fixtures():
            for rel in written - set(files):
                path = os.path.join(root, rel)
                if os.path.exists(path):
                    os.unlink(path)
            for rel, text in files.items():
                write_fixture_file(root, rel, text)
            written = set(files)
            fixture_git(root, "add", "-A")
            fixture_git(
                root,
                "-c", "user.name=fx",
                "-c", "user.email=fx@fx",
                "-c", "commit.gpgsign=false",
                "commit", "-q", "-m", name,
            )
            rev = fixture_git(root, "rev-parse", "HEAD").stdout.decode().strip()
            proc = subprocess.run(
                [sys.executable, tool, "--repo", root, "--tip", rev],
                stdin=subprocess.DEVNULL,
                capture_output=True,
                text=True,
                env=os.environ.copy(),
            )
            tested += 1
            ok = proc.returncode == expected_rc and (
                expected_stdout is None or proc.stdout.strip() == expected_stdout
            )
            if ok:
                print(f"killed\t{name}")
            else:
                failures += 1
                got = proc.stdout.strip() or "<no stdout>"
                print(
                    f"SURVIVED\t{name}\twant=({expected_stdout!r}, rc {expected_rc}) "
                    f"got=({got!r}, rc {proc.returncode})"
                )
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"selftest={'PASS' if failures == 0 else 'FAIL'} fixtures={tested} fail={failures}")
    return 0 if failures == 0 and tested >= 8 else 1


# -------------------------------------------------------------------- main ---


def main(argv):
    parser = argparse.ArgumentParser(
        description="Check that every 'supersedes S0NN' row has a marked flip.",
        add_help=True,
    )
    parser.add_argument("--repo", help="lane repository to read with git show")
    parser.add_argument("--tip", help="revision to read corpus/SOURCES.md at")
    parser.add_argument("--selftest", action="store_true", help="run fixture controls")
    args = parser.parse_args(argv)

    if args.selftest:
        try:
            return selftest()
        except CheckError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    if not args.repo or not args.tip:
        parser.print_usage(sys.stderr)
        print("ERROR: --repo and --tip are required (or use --selftest)", file=sys.stderr)
        return 2

    try:
        pairs, ids, problems = run_check(args.repo, args.tip)
    except CheckError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    for tid, sid, reason in problems:
        print(f"unresolved {sid}->{tid}: {reason}", file=sys.stderr)
    print(
        f"pairs={pairs} unresolved={len(problems)} ids={','.join(ids)} "
        f"met={len(problems) == 0}"
    )
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
