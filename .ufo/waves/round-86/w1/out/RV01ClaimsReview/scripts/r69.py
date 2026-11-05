#!/usr/bin/env python3
"""Newest-closure counter (round 69).

Resolves the lane's newest non-author closure among
``corpus/lessons/round-<N>-verifier-spotcheck.md`` files in the repo tree at
``--rev`` and checks that the ``## Axes`` calibration row in SCORECARD.md
names that file as the ``latest outside closure``. The round-68 planned item
this instrument carries asked for exactly this: the calibration row's
latest-closure pointer had been re-anchored by hand twice (r66 -> r67 in
round 68) and the hand re-anchor was again stale at the round-68 tip (the row
named the round-67 spotcheck although the round-68 spotcheck -- admitted,
2026-11-01 -- was the newest closure in the same tree), so the check becomes
mechanical: exit 1 names the stale row, exit 0 certifies the row is current.

Closure dating, declared (the population's header shapes are heterogeneous --
only rounds 29-40 carry a ``date:`` field; headings carry a parenthesised ISO
date only from round 61 on): the first line matching ``^date: YYYY-MM-DD`` in
the first ten lines wins; otherwise the first ISO date inside a ``#`` heading
line; otherwise the first ISO date anywhere in the blob. Every candidate is
validated with ``datetime.date.fromisoformat`` (S541) -- a malformed date like
2026-13-99 is a refusal, never a string comparison. A population member with
no parsable ISO date at all is exit 2 (could-not-evaluate) naming the file:
an undated closure could be the true newest, so it is never silently skipped.
The declared ``--since-round`` scope boundary (the live contract pins 63, the
fresh-start era whose closures can still be the newest; rounds below it are
closed history) removes members from the population BEFORE dating, and the
selection scope is printed, not hidden.

Selection: newest = maximum by (date, round number) -- rounds 65-68 all close
on 2026-11-01, so the round-number tiebreak is load-bearing.

Output lines (one ``MEMBER`` line per in-scope closure, then the verdict):
    MEMBER corpus/lessons/<f> date=<iso> source=<date-field|heading|body>
    SCOPE population=rounds>=<N> members=<k>
    NEWEST_CLOSURE newest=<file> date=<iso> round=<n> row_names=<file> row_current=<true|false>
    STALE_CALIBRATION row_names=<file> newest=<file> newest_date=<iso>   (only when stale)

Fail-closed exit map (pinned):
  0  the calibration row names the newest in-scope closure (row_current=true)
  1  the row names an older, a newer, or a nonexistent closure
  2  could-not-evaluate: git failure, no in-scope population, an undated or
     malformed-dated in-scope closure, SCORECARD.md missing at --rev, the
     ``## Axes`` calibration row missing, or the row names no closure --
     never silently 0

Read-only and index-free: the tool issues only ``git ls-tree`` / ``git show``
against ``--rev`` (default HEAD); it never reads the index (unreliable on this
host) and never writes to the repository. ``--selftest`` builds throwaway git
repositories in tempfile fixtures (own ``git init`` there, ``core.autocrlf``
pinned false) and drives the same entry point the CLI uses; no lane path is
read or written.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
from datetime import date

AXES_SECTION_RE = re.compile(r"^## Axes\s*$", re.M)
CALIBRATION_ROW_RE = re.compile(r"^\|\s*\*{0,2}calibration\*{0,2}\s*\|", re.I)
CLOSURE_NAME_RE = re.compile(r"corpus/lessons/round-\d+-verifier-spotcheck\.md")
POPULATION_RE = re.compile(r"^round-(\d+)-verifier-spotcheck\.md$")
DATE_FIELD_RE = re.compile(r"^date:\s*(\d{4}-\d{2}-\d{2})\s*$")
ISO_DATE_RE = re.compile(r"\d{4}-\d{2}-\d{2}")


class CouldNotEvaluate(Exception):
    """Raised for fail-closed conditions; maps to exit 2."""


def _git(repo, *args):
    proc = subprocess.run(["git", "-C", repo, *args], capture_output=True)
    if proc.returncode != 0:
        raise CouldNotEvaluate(
            "git {} failed (rc={}): {}".format(
                " ".join(args[:2]), proc.returncode, proc.stderr.decode("utf-8", "replace").strip()
            )
        )
    return proc.stdout


def _read_blob(repo, rev, path):
    out = _git(repo, "show", "{}:{}".format(rev, path))
    try:
        return out.decode("utf-8")
    except UnicodeDecodeError as e:
        raise CouldNotEvaluate("blob {}:{} is not UTF-8: {}".format(rev, path, e))


def _parse_iso(raw, name):
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise CouldNotEvaluate(
            "closure {} carries a malformed ISO date {!r} (fromisoformat refuses it)".format(name, raw)
        )


def _closure_date(repo, rev, name):
    blob = _read_blob(repo, rev, "corpus/lessons/{}".format(name))
    lines = blob.split("\n")
    for line in lines[:10]:
        m = DATE_FIELD_RE.match(line.strip())
        if m:
            return _parse_iso(m.group(1), name), "date-field"
    for line in lines:
        if line.startswith("#"):
            m = ISO_DATE_RE.search(line)
            if m:
                return _parse_iso(m.group(0), name), "heading"
    m = ISO_DATE_RE.search(blob)
    if m:
        return _parse_iso(m.group(0), name), "body"
    raise CouldNotEvaluate(
        "closure {} carries no parsable ISO date (no date: field, none in a heading, none in the body)".format(name)
    )


def _closure_population(repo, rev, since_round):
    out = _git(repo, "ls-tree", "--name-only", "{}:corpus/lessons".format(rev))
    names = [n.decode("utf-8", "replace").strip() for n in out.splitlines()]
    found = []
    for name in names:
        m = POPULATION_RE.match(name)
        if m and int(m.group(1)) >= since_round:
            found.append((name, int(m.group(1))))
    if not found:
        raise CouldNotEvaluate(
            "no round-<N>-verifier-spotcheck.md population with round >= {} under corpus/lessons at {}".format(
                since_round, rev
            )
        )
    return sorted(found, key=lambda t: t[1])


def _calibration_row(repo, rev):
    text = _read_blob(repo, rev, "SCORECARD.md")
    m = AXES_SECTION_RE.search(text)
    if not m:
        raise CouldNotEvaluate("SCORECARD.md at {} has no '## Axes' section".format(rev))
    rest = text[m.end():]
    nxt = re.search(r"^## ", rest, re.M)
    section = rest[: nxt.start()] if nxt else rest
    for line in section.split("\n"):
        if CALIBRATION_ROW_RE.match(line):
            marker = line.find("latest outside closure")
            if marker < 0:
                raise CouldNotEvaluate(
                    "the calibration row at {} does not name a 'latest outside closure'".format(rev)
                )
            cm = CLOSURE_NAME_RE.search(line[marker:])
            if not cm:
                raise CouldNotEvaluate(
                    "the calibration row at {} names no corpus/lessons/round-<N>-verifier-spotcheck.md after 'latest outside closure'".format(rev)
                )
            return cm.group(0)
    raise CouldNotEvaluate("SCORECARD.md at {} has no calibration row in '## Axes'".format(rev))


def run_counter(repo, rev, since_round):
    population = _closure_population(repo, rev, since_round)
    dated = []
    for name, rnd in population:
        iso, source = _closure_date(repo, rev, name)
        print("MEMBER corpus/lessons/{} date={} source={}".format(name, iso.isoformat(), source))
        dated.append((iso, rnd, name))
    print("SCOPE population=rounds>={} members={}".format(since_round, len(dated)))
    dated.sort()
    newest_date, newest_round, newest_name = dated[-1]
    row_name = _calibration_row(repo, rev)
    current = row_name == "corpus/lessons/{}".format(newest_name)
    print(
        "NEWEST_CLOSURE newest=corpus/lessons/{} date={} round={} row_names={} row_current={}".format(
            newest_name, newest_date.isoformat(), newest_round, row_name,
            "true" if current else "false",
        )
    )
    if not current:
        print(
            "STALE_CALIBRATION row_names={} newest=corpus/lessons/{} newest_date={}".format(
                row_name, newest_name, newest_date.isoformat()
            )
        )
    return 0 if current else 1


# ---------------------------------------------------------------- selftest


def _init_repo(root):
    def run(*args, **kw):
        proc = subprocess.run(["git", *args], cwd=root, capture_output=True, **kw)
        assert proc.returncode == 0, proc.stderr.decode("utf-8", "replace")
        return proc.stdout

    run("init", "-q", "-b", "master", ".")
    run("config", "core.autocrlf", "false")
    run("config", "user.email", "selftest@example.invalid")
    run("config", "user.name", "selftest")
    return run


def _write(root, relpath, content):
    import os

    full = os.path.join(root, relpath.replace("/", os.sep))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "wb") as fh:
        fh.write(content.encode("utf-8"))


def _commit_all(run):
    run("add", "-A")
    run("commit", "-q", "-m", "fixture")


CAL_ROW = (
    "| calibration | **7** | run `python3 tools/capability-repertoire-audit.py --selftest` -> "
    "`CAP_SELFTEST pass=2 fail=0`; latest outside closure `{row}` (admitted -- both claims "
    "verified on re-derivation and re-measurement, scores held), including round {rn} | "
    "score round 1; evidence re-anchored round {an} |\n"
)


def _fixture(root, closures, row=None, scorecard=True):
    """closures: list of (filename, first-line content)."""
    run = _init_repo(root)
    for name, heading in closures:
        _write(root, "corpus/lessons/" + name, heading + "\nauthor: fixture\nbody\n")
    if scorecard:
        _write(root, "SCORECARD.md", "# scorecard\n\n## Axes\n\n" + CAL_ROW.format(**row))
    _commit_all(run)
    return run


def run_selftest():
    import io

    arms = []

    def arm(name):
        def deco(fn):
            arms.append((name, fn))
            return fn

        return deco

    def capture(root, since_round=1):
        buf = io.StringIO()
        saved = sys.stdout
        sys.stdout = buf
        try:
            rc = run_counter(root, "HEAD", since_round)
        finally:
            sys.stdout = saved
        return rc, buf.getvalue()

    D68 = "# Round 68 verifier spotcheck — kama (2026-11-01)"
    D67 = "# Round 67 verifier spotcheck — kama (2026-10-31)"

    @arm("clean control: row names the newest closure, exit 0")
    def _clean(root):
        _fixture(root, [("round-68-verifier-spotcheck.md", D68)],
                 row={"row": "corpus/lessons/round-68-verifier-spotcheck.md", "rn": 68, "an": 68})
        rc, out = capture(root)
        return rc == 0 and "row_current=true" in out and "round-68-verifier-spotcheck.md" in out

    @arm("stale row: two closures, row names the older, exit 1 names both")
    def _stale(root):
        _fixture(root,
                 [("round-67-verifier-spotcheck.md", D67), ("round-68-verifier-spotcheck.md", D68)],
                 row={"row": "corpus/lessons/round-67-verifier-spotcheck.md", "rn": 67, "an": 68})
        rc, out = capture(root)
        return (rc == 1 and "row_current=false" in out and "STALE_CALIBRATION" in out
                and "newest=corpus/lessons/round-68-verifier-spotcheck.md" in out)

    @arm("date tie is broken by round number (both 2026-11-01)")
    def _tie(root):
        _fixture(root,
                 [("round-67-verifier-spotcheck.md", "# Round 67 verifier spotcheck — kama (2026-11-01)"),
                  ("round-68-verifier-spotcheck.md", D68)],
                 row={"row": "corpus/lessons/round-67-verifier-spotcheck.md", "rn": 67, "an": 68})
        rc, out = capture(root)
        return rc == 1 and "date=2026-11-01 round=68" in out

    @arm("date: field beats the heading; body date used only when both are absent")
    def _sources(root):
        _fixture(root,
                 [("round-68-verifier-spotcheck.md",
                   "# Round 68 verifier spotcheck — kama (2019-12-04)\nauthor: fixture\ndate: 2026-11-01\n")],
                 row={"row": "corpus/lessons/round-68-verifier-spotcheck.md", "rn": 68, "an": 68})
        rc, out = capture(root)
        return rc == 0 and "date=2026-11-01 source=date-field" in out

    @arm("empty population is exit 2, never 0")
    def _empty(root):
        _fixture(root, [], row={"row": "corpus/lessons/round-68-verifier-spotcheck.md", "rn": 68, "an": 68})
        try:
            capture(root)
            return False
        except CouldNotEvaluate:
            return True

    @arm("undated in-scope closure is exit 2 fail-closed, naming the file")
    def _undated(root):
        _fixture(root, [("round-68-verifier-spotcheck.md", "# Round 68 verifier spotcheck — kama (no date here)")],
                 row={"row": "corpus/lessons/round-68-verifier-spotcheck.md", "rn": 68, "an": 68})
        try:
            capture(root)
            return False
        except CouldNotEvaluate as e:
            return "no parsable ISO date" in str(e)

    @arm("malformed ISO date (2026-13-99) is exit 2, not a string compare")
    def _malformed(root):
        _fixture(root, [("round-68-verifier-spotcheck.md", "# Round 68 verifier spotcheck — kama (2026-13-99)")],
                 row={"row": "corpus/lessons/round-68-verifier-spotcheck.md", "rn": 68, "an": 68})
        try:
            capture(root)
            return False
        except CouldNotEvaluate:
            return True

    @arm("declared --since-round boundary excludes a closed-era undated file")
    def _since(root):
        _fixture(root,
                 [("round-50-verifier-spotcheck.md", "# round-50 spot-check (orchestrator, no date)\nbody without dates\n"),
                  ("round-68-verifier-spotcheck.md", D68)],
                 row={"row": "corpus/lessons/round-68-verifier-spotcheck.md", "rn": 68, "an": 68})
        try:
            rc_in, _ = capture(root, 1)
            refused_in_scope = rc_in == 2
        except CouldNotEvaluate:
            refused_in_scope = True  # the run_counter entry raises; the CLI maps it to exit 2
        rc_out, out = capture(root, 63)
        return (refused_in_scope and rc_out == 0 and "population=rounds>=63 members=1" in out
                and "row_current=true" in out)

    @arm("row naming a nonexistent closure is exit 1 (stale/naming-missing)")
    def _missing_row_target(root):
        _fixture(root, [("round-68-verifier-spotcheck.md", D68)],
                 row={"row": "corpus/lessons/round-99-verifier-spotcheck.md", "rn": 99, "an": 68})
        rc, out = capture(root)
        return (rc == 1 and "row_names=corpus/lessons/round-99-verifier-spotcheck.md" in out
                and "row_current=false" in out)

    @arm("missing SCORECARD.md is exit 2, never 0")
    def _no_scorecard(root):
        _fixture(root, [("round-68-verifier-spotcheck.md", D68)], scorecard=False)
        try:
            capture(root)
            return False
        except CouldNotEvaluate:
            return True

    failures = 0
    for name, fn in arms:
        buf = tempfile.TemporaryDirectory()
        try:
            ok = fn(buf.name)
        except Exception as e:  # a crashing arm is a FAIL line, not an abort
            ok = False
            print("FAIL: {} (crash: {}: {})".format(name, type(e).__name__, e))
            buf.cleanup()
            continue
        buf.cleanup()
        if not ok:
            failures += 1
        print("{}: {}".format("ok" if ok else "FAIL", name))
    total = len(arms)
    print("{}/{} selftest arms passed".format(total - failures, total))
    return 1 if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Check that the calibration row names the newest non-author closure (round 69)."
    )
    ap.add_argument("--repo", default=".", help="repository to evaluate (default: current directory)")
    ap.add_argument("--rev", default="HEAD", help="revision whose blobs are evaluated (default: HEAD)")
    ap.add_argument(
        "--since-round",
        type=int,
        default=1,
        help="population scope boundary: only closures with round >= N are dated (default: 1, all)",
    )
    ap.add_argument("--selftest", action="store_true", help="run the fail-closed fixture selftest")
    args = ap.parse_args(argv)
    if args.selftest:
        return run_selftest()
    try:
        return run_counter(args.repo, args.rev, args.since_round)
    except CouldNotEvaluate as e:
        print("COULD_NOT_EVALUATE {}".format(e))
        return 2


if __name__ == "__main__":
    sys.exit(main())
