#!/usr/bin/env python3
"""Round-83 C2: six sealed round-82 facts and value-bound corrections.

PREDICATE: plans/round-83-claims.md §C2. Declared facts are read at
b1ba614b51255a3dcfe3e0946f32f8e31bd65c09; receipt witnesses are read at
the graded tip, except F5's population, which is bound to that sealed revision.
Exactly one dated correction per stale fact must name its old and witness tokens,
sealed revision, and a non-lesson fix path carrying the whole new token outside
LOG-CORRECTION lines and #### round-N correction blocks. Holding and unknown
facts cannot be corrected. All input bytes come from git show, not the worktree.
Exit 0: answered; 1: mismatches/unbacked corrections; 2: unreadable evidence.
"""
from __future__ import annotations

import argparse
import datetime
import json
import re
import subprocess
import sys
from pathlib import PurePosixPath

SEALED = "b1ba614b51255a3dcfe3e0946f32f8e31bd65c09"
LESSON = "corpus/lessons/round-83.md"
C1_RECEIPT = ".ufo/waves/round-82/measured/after/c1-selftest.out"
DEBT_RECEIPT = ".ufo/waves/round-82/measured/after/c2-debt-selftest.out"
DELTA_RECEIPT = ".ufo/waves/round-82/measured/after/c2-late-delta.out"
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
    if proc.returncode:
        return None
    return proc.stdout


def section(text, heading, exact=False):
    lines = text.splitlines()
    for start, line in enumerate(lines):
        if (line == heading if exact else line.startswith(heading)):
            end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
            return "\n".join(lines[start:end])
    return ""


def number(text, pattern, label):
    match = re.search(pattern, text, re.S)
    if not match:
        raise CouldNotEvaluate(f"missing or malformed {label}")
    return int(match.group(1))


def required(read, rev, path):
    text = read(rev, path)
    if text is None:
        raise CouldNotEvaluate(f"no {path} at {rev}")
    return text


def registry_rows(text):
    return sum(bool(re.match(r"^ {0,3}\|[ \t]*S[0-9]{3,}\b", line)) for line in text.splitlines())


def extract_facts(read):
    log = section(required(read, SEALED, "LOG.md"), "## Round 82 —")
    score = required(read, SEALED, "SCORECARD.md")
    score82 = section(score, "## Round 82 —")
    axes = section(score, "## Axes", exact=True)
    c1 = log.split("- **C1", 1)[-1].split("- **C2", 1)[0]
    c2 = log.split("- **C2", 1)[-1]
    row = next((line for line in score82.splitlines() if line.startswith("| C1")), "")
    calibration = next((line for line in axes.splitlines() if line.startswith("| calibration |")), "")
    declared = [
        number(c1, r"selftest `pass=(\d+) fail=0`", "F1 log C1 tally"),
        number(row, r"selftest `pass=(\d+) fail=0`", "F2 scorecard C1 tally"),
        number(calibration, r"--selftest` → `pass=(\d+) fail=0`", "F3 calibration tally"),
        number(c2, r"APPEND_DEBT_SELFTEST pass=\d+ → pass=(\d+)", "F4 debt tally"),
        number(log, r"Frontier: registry \d+ → (\d+) rows", "F5 frontier"),
        number(c2, r"LATE_DELTA round=82\s+base=\w+ population=\d+\s+carried=\d+ new=(\d+) bad=0", "F6 late delta"),
    ]
    tally = number(required(read, "TIP", C1_RECEIPT), r"SELFRECORD_R81_SELFTEST pass=(\d+) fail=0\b", "C1 receipt")
    debt = number(required(read, "TIP", DEBT_RECEIPT), r"APPEND_DEBT_SELFTEST pass=(\d+) fail=0\b", "debt receipt")
    population = registry_rows(required(read, SEALED, "corpus/SOURCES.md"))
    if not population:
        raise CouldNotEvaluate("empty sealed SOURCES registry")
    delta = number(required(read, "TIP", DELTA_RECEIPT), r"LATE_DELTA round=82\s+base=\w+ population=\d+\s+carried=\d+ new=(\d+) bad=0\b", "delta receipt")
    keys = ["log82-c1-selftest", "sc82c1-selftest", "calib82-selftest", "log82-c2-debt-selftest", "log82-frontier-rows", "log82-late-delta"]
    return [(f"F{i}", f"{key}={old}", f"{key}={new}") for i, (key, old, new) in enumerate(zip(keys, declared, [tally, tally, tally, debt, population, delta]), 1)]


def corrections(text):
    return CORRECTION.findall(section(text or "", "## Corrections", exact=True))


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


def grade(facts, corr, read, sealed=SEALED):
    by_fact = {}
    for entry in corr:
        by_fact.setdefault(entry[0], []).append(entry)
    mismatches = corrected = unbacked = 0
    rows = []
    for fid, declared, witness in facts:
        entries = by_fact.get(fid, [])
        state = "holds"
        if declared == witness:
            if entries:
                mismatches += 1
                unbacked += len(entries)
                state = "unbacked-correction-holds"
        elif not entries:
            mismatches += 1
            state = "unanswered"
        elif len(entries) != 1:
            mismatches += 1
            unbacked += len(entries)
            state = "duplicate-corrections"
        else:
            _, old, new, at, date, fix = entries[0]
            path = PurePosixPath(fix)
            valid_path = not path.is_absolute() and ".." not in path.parts and not str(path).startswith("corpus/lessons/")
            fixed = read("TIP", str(path)) if valid_path else None
            try:
                datetime.date.fromisoformat(date)
                valid_date = bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", date))
            except ValueError:
                valid_date = False
            # A valid non-lesson fix containing the token already proves the required
            # outside-lessons occurrence; no repository-wide substring scan is needed.
            backed = fixed is not None and whole_token(new, outside_restatements(fixed))
            if old != declared or new != witness or at != sealed or not valid_date or not backed:
                mismatches += 1
                unbacked += 1
                state = "unbacked-correction"
            else:
                corrected += 1
                state = "corrected"
        rows.append((fid, state, declared, witness))
    for fid in sorted(set(by_fact) - {fact[0] for fact in facts}):
        mismatches += 1
        unbacked += len(by_fact[fid])
        rows.append((fid, "unknown-fact", "", ""))
    return mismatches, corrected, unbacked, rows


def evaluate(repo, sealed, tip, lesson_path, no_corrections=False):
    cache = {}
    def read(rev, path):
        revision = tip if rev == "TIP" else sealed
        key = revision, path
        if key not in cache:
            cache[key] = show(repo, revision, path)
        return cache[key]
    facts = extract_facts(read)
    corr = [] if no_corrections else corrections(read("TIP", lesson_path))
    return facts, grade(facts, corr, read, sealed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--sealed", default=SEALED)
    parser.add_argument("--tip", default="master")
    parser.add_argument("--lesson", default=LESSON)
    for flag in ("no-corrections", "enumerate", "json", "selftest"):
        parser.add_argument("--" + flag, action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    try:
        tip = git(args.repo, "rev-parse", args.tip + "^{commit}").strip()
        sealed = git(args.repo, "rev-parse", args.sealed + "^{commit}").strip()
        facts, (mismatches, corrected, unbacked, rows) = evaluate(args.repo, sealed, tip, args.lesson, args.no_corrections)
    except (CouldNotEvaluate, OSError) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    if args.enumerate:
        stale = sum(old != new for _, old, new in facts)
        print(f"SELFRECORD_R82_ENUM claims={len(facts)} stale={stale} corrected=0")
        return int(bool(stale))
    if args.json:
        print(json.dumps(dict(claims=len(facts), mismatches=mismatches, corrected=corrected, unbacked=unbacked,
                              facts=[dict(zip(("id", "state", "declared", "witness"), row)) for row in rows]), indent=2))
    else:
        for fid, state, old, new in rows:
            print(f"SELFRECORD_R82_FACT {fid} {state} declared={old} witness={new}")
        print(f"SELFRECORD_R82 claims={len(facts)} mismatches={mismatches} corrected={corrected} unbacked={unbacked}")
    return int(bool(mismatches))


def selftest():
    keys = ["log82-c1-selftest", "sc82c1-selftest", "calib82-selftest", "log82-c2-debt-selftest", "log82-frontier-rows", "log82-late-delta"]
    old_values = [18, 22, 22, 25, 305, 15]
    new_values = [23, 23, 23, 25, 305, 15]
    facts = [(f"F{i}", f"{key}={old}", f"{key}={new}") for i, (key, old, new) in enumerate(zip(keys, old_values, new_values), 1)]
    lines = [f"corrected {fid} old={old} new={new} at={SEALED} date=2026-11-04 fix={'LOG.md' if fid == 'F1' else 'SCORECARD.md'}" for fid, old, new in facts[:3]]
    lesson = "## Corrections\n" + "\n".join(lines) + "\n## Mistakes\n"
    backing = {"LOG.md": facts[0][2], "SCORECARD.md": "\n".join(f[2] for f in facts[1:3])}
    cases = []
    def run(name, text, files, expected, disabled=False):
        got = grade(facts, [] if disabled else corrections(text), lambda rev, path: files.get(path))
        actual = got[0], got[2], got[1]
        cases.append((name, actual == expected, actual, expected))
    run("honest", lesson, backing, (0, 0, 3))
    run("correction-outside-container", lesson.replace(lines[0] + "\n", "").replace("## Mistakes", "## Mistakes\n" + lines[0]), backing, (1, 0, 2))
    run("wrong-at", lesson.replace("at=" + SEALED, "at=" + "2" * 40, 1), backing, (1, 1, 2))
    run("wrong-old", lesson.replace("old=" + facts[0][1], "old=x=0", 1), backing, (1, 1, 2))
    run("wrong-new", lesson.replace("new=" + facts[0][2], "new=x=9", 1), backing, (1, 1, 2))
    run("fix-without-token", lesson, dict(backing, **{"LOG.md": "no token"}), (1, 1, 2))
    run("near-token-new", lesson, dict(backing, **{"LOG.md": facts[0][2] + "4"}), (1, 1, 2))
    run("fix-self-referential", lesson.replace("fix=LOG.md", "fix=" + LESSON), dict(backing, **{LESSON: lesson}), (1, 1, 2))
    run("near-corrections-heading", lesson.replace("## Corrections\n", "## Corrections considered\n"), backing, (3, 0, 0))
    run("duplicate-correction", lesson.replace("## Mistakes", lines[0] + "\n## Mistakes"), backing, (1, 2, 2))
    holding = f"corrected F4 old={facts[3][1]} new={facts[3][2]} at={SEALED} date=2026-11-04 fix=LOG.md"
    run("correction-for-holding-fact", lesson.replace("## Mistakes", holding + "\n## Mistakes"), backing, (1, 1, 3))
    run("unknown-fact", lesson.replace("## Mistakes", holding.replace("F4", "F9") + "\n## Mistakes"), backing, (1, 1, 3))
    run("no-corrections", lesson, backing, (3, 0, 0), disabled=True)
    run("lesson-only-token", lesson.replace("fix=LOG.md", "fix=corpus/lessons/other.md"), {"SCORECARD.md": backing["SCORECARD.md"], "corpus/lessons/other.md": facts[0][2]}, (1, 1, 2))
    run("token-only-in-correction-region", lesson, {"LOG.md": "LOG-CORRECTION " + facts[0][2], "SCORECARD.md": "#### round-83 correction\n" + backing["SCORECARD.md"]}, (3, 3, 0))
    # Exercise extraction itself: sealed population 305, graded tip 311.
    mapping = {
        (SEALED, "LOG.md"): "## Round 82 — fixture\n- **C1 selftest `pass=18 fail=0`\n- **C2 APPEND_DEBT_SELFTEST pass=22 → pass=25\nLATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0\nFrontier: registry 302 → 305 rows\n",
        (SEALED, "SCORECARD.md"): "## Axes\n| calibration | --selftest` → `pass=22 fail=0` |\n## Round 82 — fixture\n| C1 | selftest `pass=22 fail=0` |\n",
        (SEALED, "corpus/SOURCES.md"): "".join(f"| S{i:03d} | row |\n" for i in range(1, 306)),
        ("TIP", "corpus/SOURCES.md"): "".join(f"| S{i:03d} | row |\n" for i in range(1, 312)),
        ("TIP", C1_RECEIPT): "SELFRECORD_R81_SELFTEST pass=23 fail=0\n",
        ("TIP", DEBT_RECEIPT): "APPEND_DEBT_SELFTEST pass=25 fail=0\n",
        ("TIP", DELTA_RECEIPT): "LATE_DELTA round=82 base=aaf974dbd3b6 population=103 carried=88 new=15 bad=0\n",
    }
    extracted = extract_facts(lambda rev, path: mapping.get((rev, path)))
    got = grade(extracted, corrections(lesson), lambda rev, path: backing.get(path))
    actual = got[0], got[2], got[1]
    cases.append(("registry-base-bound", extracted == facts and actual == (0, 0, 3), actual, (0, 0, 3)))
    for name, ok, actual, expected in cases:
        print(f"{'PASS' if ok else 'FAIL'} {name} mismatches={actual[0]} unbacked={actual[1]} corrected={actual[2]} expected={expected}")
    failures = sum(not case[1] for case in cases)
    print(f"SELFRECORD_R82_SELFTEST pass={len(cases) - failures} fail={failures}")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
