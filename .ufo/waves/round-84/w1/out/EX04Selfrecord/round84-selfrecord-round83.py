#!/usr/bin/env python3
"""Round-84 C2: eight sealed round-83 facts and value-bound corrections.

Declared SCORECARD bytes come from SEALED; witnesses, lesson and fix bytes come
from HEAD, never the worktree. BASE witnesses pin the six stale/two holding
classification. Corrections name BASE (not SEALED), as frozen in round-84 C2.
F2 uses one comma-joined token for its two coupled values. Exit 0: answered;
1: mismatches/unbacked; 2: unreadable evidence. --selftest uses disposable git
repositories under --work or TMPDIR; no production repository is modified.
"""
from __future__ import annotations

import argparse
import datetime
import os
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

SEALED = "ae4323171596126a9265f7f6c8af4164d499ba09"
BASE = "aca4f33ac1e2a8cf815d97daab3b3a5cfa0d78e0"
LESSON = "corpus/lessons/round-84.md"
PREFIX = ".ufo/waves/round-83/measured/final/"
CORRECTION = re.compile(r"corrected\s+(F[0-9]+)\s+old=(\S+)\s+new=(\S+)\s+at=(\S+)\s+date=(\S+)\s+fix=(\S+)")


class CouldNotEvaluate(Exception):
    pass


def git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode:
        raise CouldNotEvaluate(f"git {' '.join(args)}: {proc.stderr.strip()[:200]}")
    return proc.stdout


def show(repo, rev, path):
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"], capture_output=True, text=True)
    return None if proc.returncode else proc.stdout


def section(text, heading):
    lines = text.splitlines()
    for start, line in enumerate(lines):
        if line == heading or line.startswith(heading + " —"):
            end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
            return "\n".join(lines[start:end])
    return ""


def required(read, rev, path):
    text = read(rev, path)
    if text is None:
        raise CouldNotEvaluate(f"no {path} at {rev}")
    return text


def capture(text, pattern, label):
    match = re.search(pattern, text)
    if not match:
        raise CouldNotEvaluate(f"missing or malformed {label}")
    return match.group(1)


def row(axes, axis):
    return next((line for line in axes.splitlines() if re.match(r"^\|\s*\*{0,2}" + axis + r"\*{0,2}\s*\|", line)), "")


def summary(text, name):
    lines = [line for line in text.splitlines() if line.startswith(name + " ")]
    if len(lines) != 1:
        raise CouldNotEvaluate(f"expected one {name} summary")
    return lines[0]


def fields(text, keys, label):
    return ",".join(f"{key}={capture(text, r'(?<![\w-])' + key + r'=([0-9]+)(?![\w])', label)}" for key in keys)


def newest_closure(repo, tip, read):
    dated = []
    for path in git(repo, "ls-tree", "-r", "--name-only", tip, "corpus/lessons").splitlines():
        match = re.fullmatch(r"corpus/lessons/round-(\d+)-verifier-spotcheck\.md", path)
        if not match or int(match.group(1)) < 63:
            continue
        text = required(read, tip, path)
        lines = text.splitlines()
        raw = next((m.group(1) for line in lines[:10] if (m := re.fullmatch(r"date:\s*(\d{4}-\d{2}-\d{2})\s*", line.strip()))), None)
        if raw is None:
            heading = "\n".join(line for line in lines if line.startswith("#"))
            match_date = re.search(r"\d{4}-\d{2}-\d{2}", heading) or re.search(r"\d{4}-\d{2}-\d{2}", text)
            raw = match_date.group() if match_date else None
        try:
            date = datetime.date.fromisoformat(raw or "")
        except ValueError as exc:
            raise CouldNotEvaluate(f"undated or malformed closure {path}") from exc
        dated.append((date, int(match.group(1)), PurePosixPath(path).name))
    if not dated:
        raise CouldNotEvaluate("no closure population since round 63")
    return max(dated)[2]


def extract_facts(repo, read, sealed, tip):
    score = required(read, sealed, "SCORECARD.md")
    authority = capture(score, r"(\*\*Current authority[^\n]+)", "authority")
    axes = section(score, "## Axes")
    operability, freshness, calibration = (row(axes, axis) for axis in ("operability", "freshness", "calibration"))
    round82 = section(score, "## Round 82")
    c2row = next((line for line in round82.splitlines() if line.startswith("| C2")), "")
    late = capture(authority, r"late=(\d+)", "F1 authority")
    if capture(operability, r"late=(\d+)", "F1 axis") != late:
        raise CouldNotEvaluate("F1 sealed containers disagree")
    pending = capture(operability, r"(PENDING_FALLS[^`]+)", "F2 declared")
    declared = [
        f"r83c1-late={late}",
        f"r83c1-window={capture(pending, r'window=(\d+)', 'F2 window')},r83c1-falls={capture(pending, r'falls=(yes|no)', 'F2 falls')}",
        "r83c1-delta=" + "/".join(capture(operability, r"(?<![\w-])" + key + r"=(\d+)", "F3 " + key) for key in ("population", "carried", "new", "bad")),
        "r82c2-new=" + capture(c2row, r"new=(\d+)", "F4 declared"),
        "r83c3-selftest=" + capture(freshness, r"selftest `pass=(\d+)", "F5 declared"),
        "r83c2=" + fields(capture(authority, r"(SELFRECORD_R82[^`]+)", "F6 declared"), ("claims", "mismatches", "corrected", "unbacked"), "F6 declared fields"),
        "r83c3=" + fields(capture(freshness, r"(PIN_RECHECK rows=[^`]+)", "F7 declared"), ("rows", "graded", "holds", "reworded", "moved", "drifted", "ungraded", "bad"), "F7 declared fields"),
        "r83-closure=" + capture(calibration, r"latest outside closure `corpus/lessons/(round-\d+-verifier-spotcheck\.md)`", "F8 declared"),
    ]
    def receipt(name, marker):
        return summary(required(read, tip, PREFIX + name), marker)
    debt = receipt("c1-legA.out", "APPEND_DEBT")
    pending = receipt("c1-pending.out", "PENDING_FALLS")
    delta = receipt("c1-delta.out", "LATE_DELTA")
    delta82 = summary(required(read, tip, ".ufo/waves/round-82/measured/before/c2-late-delta-base.out"), "LATE_DELTA")
    witness = [
        "r83c1-late=" + capture(debt, r"late=(\d+)", "F1 witness"),
        f"r83c1-window={capture(pending, r'window=(\d+)', 'F2 witness window')},r83c1-falls={capture(pending, r'falls=(yes|no)', 'F2 witness falls')}",
        "r83c1-delta=" + "/".join(capture(delta, r"(?<![\w-])" + key + r"=(\d+)", "F3 witness " + key) for key in ("population", "carried", "new", "bad")),
        "r82c2-new=" + capture(delta82, r"new=(\d+)", "F4 witness"),
        "r83c3-selftest=" + capture(receipt("c3-selftest.out", "PIN_RECHECK_SELFTEST"), r"pass=(\d+)", "F5 witness"),
        "r83c2=" + fields(receipt("c2.out", "SELFRECORD_R82"), ("claims", "mismatches", "corrected", "unbacked"), "F6 witness"),
        "r83c3=" + fields(receipt("c3.out", "PIN_RECHECK"), ("rows", "graded", "holds", "reworded", "moved", "drifted", "ungraded", "bad"), "F7 witness"),
        "r83-closure=" + newest_closure(repo, tip, read),
    ]
    return [(f"F{i}", old, new) for i, (old, new) in enumerate(zip(declared, witness), 1)]


def corrections(text):
    return CORRECTION.findall(section(text or "", "## Corrections"))


def whole_token(token, text):
    return re.search(r"(?<![0-9A-Za-z_.~=-])" + re.escape(token) + r"(?![0-9A-Za-z_.~-])", text) is not None


def outside_restatements(text):
    kept = []
    correction_depth = None
    for line in text.splitlines():
        heading = re.match(r"^(#{1,6})\s+", line)
        if heading and correction_depth is not None and len(heading.group(1)) <= correction_depth:
            correction_depth = None
        if re.match(r"^#### round-\d+ correction(?:\s|$)", line):
            correction_depth = 4
        if correction_depth is None and "LOG-CORRECTION" not in line:
            kept.append(line)
    return "\n".join(kept)


def grade(facts, corr, read, at, baseline):
    by_fact = {}
    for entry in corr:
        by_fact.setdefault(entry[0], []).append(entry)
    mismatches = corrected = unbacked = 0
    rows = []
    for fid, old, new in facts:
        entries = by_fact.get(fid, [])
        state = "stale"
        if old == baseline[fid]:
            bad = old != new or bool(entries)
            mismatches += int(bad)
            unbacked += len(entries)
            state = "stale" if bad else "holds"
        else:
            valid = False
            if len(entries) == 1:
                _, declared, witness, revision, date, fix = entries[0]
                path = PurePosixPath(fix)
                valid_path = not path.is_absolute() and ".." not in path.parts and not str(path).startswith("corpus/lessons/")
                fixed = read("TIP", str(path)) if valid_path else None
                try:
                    datetime.date.fromisoformat(date)
                    valid_date = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", date))
                except ValueError:
                    valid_date = False
                valid = (declared == old and witness == new == baseline[fid] and revision == at and valid_date
                         and fixed is not None and whole_token(new, outside_restatements(fixed)))
            if valid:
                corrected += 1
                state = "corrected"
            else:
                mismatches += 1
                unbacked += max(1, len(entries))
        rows.append((fid, state, old, new))
    for fid in sorted(set(by_fact) - {fact[0] for fact in facts}):
        mismatches += 1
        unbacked += len(by_fact[fid])
        rows.append((fid, "stale", "unknown", "unknown"))
    return mismatches, corrected, unbacked, rows


def evaluate(repo, sealed=SEALED, tip="HEAD", at=BASE, no_corrections=False):
    cache = {}
    def read(rev, path):
        rev = tip if rev == "TIP" else rev
        key = rev, path
        if key not in cache:
            cache[key] = show(repo, rev, path)
        return cache[key]
    facts = extract_facts(repo, read, sealed, tip)
    baseline = {fid: new for fid, _, new in extract_facts(repo, read, sealed, at)}
    corr = [] if no_corrections else corrections(read("TIP", LESSON))
    return grade(facts, corr, read, at, baseline)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--work", help="parent for selftest temporary repositories (otherwise TMPDIR)")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--no-corrections", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.selftest:
            return selftest(args.work)
        tip = git(args.repo, "rev-parse", "HEAD^{commit}").strip()
        git(args.repo, "rev-parse", SEALED + "^{commit}")
        git(args.repo, "rev-parse", BASE + "^{commit}")
        mismatches, corrected, unbacked, rows = evaluate(args.repo, tip=tip, no_corrections=args.no_corrections)
        for fid, state, old, new in rows:
            print(f"SELFRECORD_R83_FACT {fid} {state} declared={old} witness={new}")
        print(f"SELFRECORD_R83 claims=8 mismatches={mismatches} corrected={corrected} unbacked={unbacked}")
        return int(bool(mismatches or unbacked))
    except (CouldNotEvaluate, OSError, UnicodeError) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2


def selftest(work=None):
    # Every attack is committed in a real fixture repo; evaluation still uses git show.
    with tempfile.TemporaryDirectory(prefix="selfrecord-r83-", dir=work) as directory:
        repo = Path(directory).resolve()
        git(repo, "init", "-q")
        def mutate(*args):
            if Path(git(repo, "rev-parse", "--show-toplevel").strip()).resolve() != repo:
                raise CouldNotEvaluate("fixture git root mismatch")
            return git(repo, *args)
        def put(path, text):
            target = repo / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
        def commit():
            mutate("add", "-A")
            mutate("-c", "user.name=fixture", "-c", "user.email=fixture@invalid", "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
            return git(repo, "rev-parse", "HEAD").strip()
        score = ("**Current authority (round 83):** late=23 SELFRECORD_R82 claims=6 mismatches=0 corrected=3 unbacked=0`\n"
                 "## Axes\n| operability | late=23 out_of_population=0 PENDING_FALLS window=8 accepted=8 falls=yes` population=123 carried=103 new=20 bad=0 |\n"
                 "| freshness | PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0 ungraded=1 bad=0` selftest `pass=11 fail=0` |\n"
                 "| calibration | latest outside closure `corpus/lessons/round-82-verifier-spotcheck.md` |\n"
                 "## Round 82 — fixture\n| C2 | new=0 |\n")
        put("SCORECARD.md", score)
        receipts = {
            "c1-legA.out": "APPEND_DEBT late=22 bad_rows=10\n",
            "c1-pending.out": "PENDING_FALLS window=7 accepted=7 falls=no\n",
            "c1-delta.out": "LATE_DELTA population=113 carried=103 new=10 bad=10\n",
            "c2.out": "SELFRECORD_R82 claims=6 mismatches=0 corrected=3 unbacked=0\n",
            "c3.out": "PIN_RECHECK rows=5 graded=4 holds=4 reworded=0 moved=0 drifted=0 ungraded=1 bad=0\n",
            "c3-selftest.out": "PIN_RECHECK_SELFTEST pass=14 fail=0\n",
        }
        for name, text in receipts.items():
            put(PREFIX + name, text)
        put(".ufo/waves/round-82/measured/before/c2-late-delta-base.out", "LATE_DELTA new=15\n")
        put("corpus/lessons/round-83-verifier-spotcheck.md", "# Closure (2026-11-04)\n")
        sealed = commit()
        facts = extract_facts(repo, lambda rev, path: show(repo, rev, path), sealed, sealed)
        stale = [fact for fact in facts if fact[1] != fact[2]]
        lines = [f"corrected {fid} old={old} new={new} at={sealed} date=2026-11-04 fix=FIX.md" for fid, old, new in stale]
        lesson = "## Corrections\n" + "\n".join(lines) + "\n## Mistakes\n"
        backing = "\n".join(new for _, _, new in stale)
        cases = []
        def run(name, text=lesson, fix=backing, expected=(0, 6, 0), edit=None, dirty=False):
            mutate("reset", "--hard", sealed)
            if text is not None:
                put(LESSON, text)
            put("FIX.md", fix)
            if edit:
                edit()
            commit()
            if dirty:
                put("FIX.md", "worktree-only")
                put(LESSON, "worktree-only")
            try:
                actual = evaluate(repo, sealed, "HEAD", sealed)[:3]
            except CouldNotEvaluate:
                actual = "unreadable"
            ok = actual == expected
            cases.append(ok)
            print(f"{'PASS' if ok else 'FAIL'} {name} actual={actual} expected={expected}")
        run("clean-green")
        run("missing-lesson", text=None, expected=(6, 0, 6))
        run("wrong-old", text=lesson.replace("old=r83c1-late=23", "old=r83c1-late=99"), expected=(1, 5, 1))
        hold = facts[5]
        holding = f"corrected F6 old={hold[1]} new={hold[2]} at={sealed} date=2026-11-04 fix=FIX.md\n"
        run("correction-on-hold", text=lesson.replace("## Mistakes", holding + "## Mistakes"), expected=(1, 6, 1))
        run("unknown-fact", text=lesson.replace("## Mistakes", holding.replace("F6", "F9") + "## Mistakes"), expected=(1, 6, 1))
        run("correction-block-only-token", fix="#### round-84 correction\n" + backing, expected=(6, 0, 6))
        run("log-correction-only-token", fix="\n".join("LOG-CORRECTION " + line for line in backing.splitlines()), expected=(6, 0, 6))
        run("wrong-revision", text=lesson.replace("at=" + sealed, "at=" + "0" * 40), expected=(6, 0, 6))
        run("duplicate-correction", text=lesson.replace("## Mistakes", lines[0] + "\n## Mistakes"), expected=(1, 5, 2))
        run("invalid-date", text=lesson.replace("date=2026-11-04", "date=2026-13-04"), expected=(6, 0, 6))
        run("lesson-fix", text=lesson.replace("fix=FIX.md", "fix=" + LESSON), expected=(6, 0, 6))
        run("near-token", fix=backing.replace("r83c1-late=22", "r83c1-late=224"), expected=(1, 5, 1))
        run("worktree-not-evidence", dirty=True)
        run("sealed-revision-drift", edit=lambda: put("SCORECARD.md", score.replace("late=23", "late=22")))
        run("witness-rewrite", edit=lambda: put(PREFIX + "c1-legA.out", "APPEND_DEBT late=23 bad_rows=0\n"), expected=(1, 5, 1))
        run("missing-receipt", edit=lambda: (repo / (PREFIX + "c1-legA.out")).unlink(), expected="unreadable")
        failures = sum(not ok for ok in cases)
        print(f"SELFRECORD_R83_SELFTEST pass={len(cases) - failures} fail={failures}")
        return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
