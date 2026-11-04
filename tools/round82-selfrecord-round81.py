#!/usr/bin/env python3
"""round82-selfrecord-round81.py - round-82 C1 (calibration): the round-81 self-record's facts.

PREDICATE (frozen: plans/round-82-claims.md section C1):

    `python3 tools/round82-selfrecord-round81.py --repo <lane>` prints one `SELFRECORD_R81
    claims=6 mismatches=0 corrected=5 unbacked=0` line and exits 0 only when each of the six
    facts the round-81 self-record declares re-derives from the tree at the sealed revision
    1b64f66ddea89c57b71165eacd14b0e1d6f24e11 and matches the same fact re-derived at the graded
    tip, or is answered by exactly one committed `corrected F<n> old=<token> new=<token>
    at=<40-hex> date=<ISO> fix=<path>` block in `corpus/lessons/round-82.md` `## Corrections`
    whose `old` is the sealed declared token, whose `at` is the sealed revision, whose `new`
    equals the fact's tip witness token, and whose `fix` path's tip bytes contain the literal
    `new` token; it exits 1 naming every unanswered fact otherwise. A fact that holds at the
    sealed revision needs no correction; a correction for a holding or unnamed fact, a duplicated
    correction, a correction outside `## Corrections`, a wrong `at`, a wrong `old`, or a `fix`
    whose tip bytes lack the token is `unbacked` and is also a mismatch.

The six facts (declared by the round-81 record, observed from the tree):

  F1 sc81c2-pending   `SCORECARD.md` §Round 81 C2 row, the `-> exit 0` cell's `pending=` value,
                      against `.ufo/waves/round-81/measured/after/debt-green.out` (`pending=4`)
  F2 log81-frontier   `LOG.md` §Round 81 `Frontier: registry 297 -> <n> rows`, against the registry
                      row count at the round's declared base revision (302) -- a population snapshot
                      is a property of the revision the record describes, not of the grading tip
                      (the round-82 freeze divergence: the plan's witness cell said "tip count"; the
                      round's own three rows would make the record's honest value unstatable)
  F3 skill81-gate     `SKILL.md` pre-report-gate row `(ten arms, ...)`, against
                      `.ufo/waves/round-81/measured/after/gate.out` (`arms=11`)
  F4 calib81-closure  `SCORECARD.md` `## Axes` calibration row's "newest non-author closure",
                      against the newest `corpus/lessons/round-*-verifier-spotcheck.md` at the tip
  F5 logcorr81-pending  `LOG.md` `LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=<n>`,
                      against the same debt receipt (`pending=4`)
  F6 sc81c1-selftest  `SCORECARD.md` §Round 81 C1 row's `pass=<n> fail=0`, against
                      `.ufo/waves/round-81/measured/after/c1-selftest.out` (`pass=13`)

F1-F3, F5 and F6 are graded at the sealed revision against the receipt they cite (or the tip registry
count); F4 is tip-bound (the record states it in the present tense and the round-81 closure lands after
the sealed revision -- the round-80 F5 and round-81 F6 precedent). Every fact is read with
`git show <rev>:<path>`, never from the worktree: the round's own record commit cannot refute a fact.
The correction container is `corpus/lessons/round-82.md` section `## Corrections`; blocks outside it
are prose, not corrections.

Usage: round82-selfrecord-round81.py --repo DIR [--sealed REV] [--tip REV] [--lesson PATH]
       [--no-corrections] [--enumerate] [--json] | --selftest

Exit: 0 every fact re-derives or is answered; 1 at least one unanswered fact or unbacked
correction; 2 could-not-evaluate (git failure, unreadable input) -- never silently 0.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys

SEALED = "1b64f66ddea89c57b71165eacd14b0e1d6f24e11"
LESSON = "corpus/lessons/round-82.md"
LESSON_ROUND = 82
SCORECARD = "SCORECARD.md"
LOG = "LOG.md"
SKILL = "SKILL.md"
DEBT_RECEIPT = ".ufo/waves/round-81/measured/after/debt-green.out"
GATE_RECEIPT = ".ufo/waves/round-81/measured/after/gate.out"
C1_RECEIPT = ".ufo/waves/round-81/measured/after/c1-selftest.out"
CLOSURE_GLOB = re.compile(r"^corpus/lessons/(round-([0-9]+)-verifier-spotcheck\.md)$")
WORD_NUM = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
            "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
            "fourteen": 14, "fifteen": 15, "sixteen": 16}


class CouldNotEvaluate(Exception):
    pass


def git(repo, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise CouldNotEvaluate(f"git {' '.join(args)}: {proc.stderr.strip()[:200]}")
    return proc.stdout


def show(repo, rev, path):
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True)
    if proc.returncode != 0:
        return None
    return proc.stdout


def section(text, prefix):
    """The `## <prefix>...` section: from its heading line to the next `## ` heading."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.startswith("## ") and prefix in line:
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def line_with(text, needle):
    for line in text.splitlines():
        if needle in line:
            return line
    return None


def last_int(line, pattern):
    hits = re.findall(pattern, line)
    return int(hits[-1]) if hits else None


def first_int(text, pattern):
    match = re.search(pattern, text)
    return int(match.group(1)) if match else None


def newest_closure(repo, tip):
    names = git(repo, "ls-tree", "-r", "--name-only", tip, "corpus/lessons").splitlines()
    best = None
    for name in names:
        match = CLOSURE_GLOB.match(name.strip())
        if match:
            number = int(match.group(2))
            if best is None or number > best[0]:
                best = (number, match.group(1))
    if best is None:
        raise CouldNotEvaluate("no round-*-verifier-spotcheck.md at the tip")
    return best[1]


def registry_rows(text):
    """Rows of the SOURCES.md registry table: 0-3 leading spaces, a pipe, an S-id cell."""
    return sum(1 for line in text.splitlines() if re.match(r"^ {0,3}\|[ \t]*S[0-9]{3,}\b", line))


# --- facts -----------------------------------------------------------------

def fact_f1(read):
    line = line_with(read(SEALED, SCORECARD) or "",
                     "C2 — the append-only acceptance population")
    if line is None:
        raise CouldNotEvaluate("SCORECARD.md carries no Round 81 C2 row")
    # The row's second `APPEND_DEBT` line (the `-> exit 0` cell) is its last pending value.
    value = last_int(line, r"pending=(\d+)")
    declared = f"sc81c2-pending={value}"
    receipt = read("TIP", DEBT_RECEIPT)
    if receipt is None:
        raise CouldNotEvaluate("the debt receipt is absent at the tip")
    witness = f"sc81c2-pending={first_int(receipt, r'pending=(\d+)')}"
    return declared, witness


def fact_f2(read):
    text = read(SEALED, LOG) or ""
    block = section(text, "Round 81 —")
    if block is None:
        raise CouldNotEvaluate("LOG.md carries no Round 81 section")
    line = line_with(block, "Frontier: registry 297")
    if line is None:
        raise CouldNotEvaluate("the Round 81 frontier line is absent")
    value = last_int(line, r"→\s*([0-9]+)\s*rows")
    declared = f"log81-frontier-rows={value}"
    rows = registry_rows(read("BASE", "corpus/SOURCES.md") or "")
    if rows == 0:
        raise CouldNotEvaluate("the base registry is unreadable")
    return declared, f"log81-frontier-rows={rows}"


def fact_f3(read):
    line = line_with(read(SEALED, SKILL) or "", "Pre-report gate | gate:")
    if line is None:
        raise CouldNotEvaluate("SKILL.md carries no pre-report-gate row")
    match = re.search(r"\((\w+) arms,", line)
    if not match:
        raise CouldNotEvaluate("the gate row states no arm count")
    word = match.group(1)
    number = WORD_NUM.get(word)
    if number is None:
        number = int(word) if word.isdigit() else None
    declared = f"skill81-gate-arms={number}"
    receipt = read("TIP", GATE_RECEIPT)
    if receipt is None:
        raise CouldNotEvaluate("the gate receipt is absent at the tip")
    witness = f"skill81-gate-arms={first_int(receipt, r'PRE_REPORT round=81 arms=(\d+)')}"
    return declared, witness


def fact_f4(read):
    line = line_with(read(SEALED, SCORECARD) or "", "| calibration |")
    if line is None:
        raise CouldNotEvaluate("SCORECARD.md carries no calibration row")
    match = re.search(r"newest non-author closure is `([^`]+)`", line)
    if not match:
        raise CouldNotEvaluate("the calibration row names no closure")
    declared = f"calib81-newest-closure={match.group(1).rsplit('/', 1)[-1]}"
    witness = f"calib81-newest-closure={read('NEWEST_CLOSURE', None).rsplit('/', 1)[-1]}"
    return declared, witness


def fact_f5(read):
    text = read(SEALED, LOG) or ""
    match = re.search(r"LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=(\d+)", text)
    if not match:
        raise CouldNotEvaluate("LOG.md carries no round-81 C2 correction line")
    declared = f"logcorr81-c2-pending={match.group(1)}"
    receipt = read("TIP", DEBT_RECEIPT)
    if receipt is None:
        raise CouldNotEvaluate("the debt receipt is absent at the tip")
    witness = f"logcorr81-c2-pending={first_int(receipt, r'pending=(\d+)')}"
    return declared, witness


def fact_f6(read):
    line = line_with(read(SEALED, SCORECARD) or "",
                     "C1 — the round-80 self-record's six declared facts")
    if line is None:
        raise CouldNotEvaluate("SCORECARD.md carries no Round 81 C1 row")
    value = last_int(line, r"pass=(\d+) fail=0")
    declared = f"sc81c1-selftest={value}"
    receipt = read("TIP", C1_RECEIPT)
    if receipt is None:
        raise CouldNotEvaluate("the C1 receipt is absent at the tip")
    witness = f"sc81c1-selftest={first_int(receipt, r'pass=(\d+)')}"
    return declared, witness


FACTS = [
    ("F1", fact_f1),
    ("F2", fact_f2),
    ("F3", fact_f3),
    ("F4", fact_f4),
    ("F5", fact_f5),
    ("F6", fact_f6),
]

CORRECTION = re.compile(
    r"corrected\s+(F[0-9]+)\s+old=(\S+)\s+new=(\S+)\s+at=(\S+)\s+date=(\d{4}-\d{2}-\d{2})"
    r"\s+fix=(\S+)")


def section_exact(text, heading):
    """The section whose heading line, stripped, is exactly `## <heading>`."""
    lines = text.splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "## " + heading:
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## "):
            end = index
            break
    return "\n".join(lines[start:end])


def corrections(lesson_text):
    """Only blocks inside a heading that is exactly `## Corrections` are corrections."""
    block = section_exact(lesson_text or "", "Corrections") or ""
    return CORRECTION.findall(block)


def grade(facts, corr, read, sealed=SEALED):
    """facts: [(id, declared, witness)]; corr: [(id, old, new, at, date, fix)].
    read(rev, path) -> text|None. Returns (mismatches, corrected, unbacked, rows)."""
    by_fact = {}
    for entry in corr:
        by_fact.setdefault(entry[0], []).append(entry)
    unbacked = 0
    corrected = 0
    mismatches = 0
    rows = []
    known = {f[0] for f in facts}
    for fid, declared, witness in facts:
        entries = by_fact.get(fid, [])
        stale = declared != witness
        if not stale:
            if entries:
                unbacked += len(entries)
                mismatches += 1
                rows.append((fid, "unbacked-correction-holds", declared, witness))
            else:
                rows.append((fid, "holds", declared, witness))
            continue
        if not entries:
            mismatches += 1
            rows.append((fid, "unanswered", declared, witness))
            continue
        if len(entries) > 1:
            unbacked += len(entries)
            mismatches += 1
            rows.append((fid, "duplicate-corrections", declared, witness))
            continue
        _, old, new, at, _date, fix = entries[0]
        problems = []
        if old != declared:
            problems.append(f"old={old} does-not-equal-declared")
        if new != witness:
            problems.append(f"new={new} does-not-equal-witness")
        if at != sealed:
            problems.append(f"at={at[:12]} is not the sealed revision")
        fixed = read("TIP", fix)
        if fix == LESSON:
            problems.append(f"fix={fix} is the corrections container itself")
        elif fixed is None or re.search(re.escape(new) + r"(?![0-9A-Za-z_.~-])", fixed) is None:
            problems.append(f"fix={fix} does not carry the new token as a whole token at the tip")
        if problems:
            unbacked += 1
            mismatches += 1
            rows.append((fid, "unbacked-correction", declared, witness))
        else:
            corrected += 1
            rows.append((fid, "corrected", declared, witness))
    for fid in sorted(set(by_fact) - known):
        unbacked += len(by_fact[fid])
        mismatches += 1
        rows.append((fid, "unknown-fact", "", ""))
    return mismatches, corrected, unbacked, rows


def evaluate(repo, sealed, tip, lesson_path, no_corrections=False):
    cache = {}

    base_holder = {}

    def base_revision():
        if "base" not in base_holder:
            plan = show(repo, tip, f"plans/round-{LESSON_ROUND}-claims.md") or ""
            match = re.search(r"Base revision `([0-9a-f]{40})`", plan)
            base_holder["base"] = match.group(1) if match else sealed
        return base_holder["base"]

    def read(rev, path):
        if path is None:
            return newest_closure(repo, tip)
        if rev == "NEWEST_CLOSURE":
            return cache.get(("closure", tip)) or cache.setdefault(
                ("closure", tip), newest_closure(repo, tip))
        revision = (tip if rev in ("TIP", "NEWEST_CLOSURE")
                    else base_revision() if rev == "BASE" else sealed)
        key = (revision, path)
        if key not in cache:
            cache[key] = show(repo, revision, path)
        return cache[key]

    facts = []
    for fid, extract in FACTS:
        declared, witness = extract(read)
        facts.append((fid, declared, witness))
    lesson = show(repo, tip, lesson_path) or ""
    corr = [] if no_corrections else corrections(lesson)
    return facts, grade(facts, corr, read, sealed)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--sealed", default=SEALED)
    parser.add_argument("--tip", default="master")
    parser.add_argument("--lesson", default=LESSON)
    parser.add_argument("--no-corrections", action="store_true")
    parser.add_argument("--enumerate", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    repo = args.repo
    try:
        if args.tip in ("master", "HEAD"):
            tip = git(repo, "rev-parse", args.tip).strip()
        else:
            tip = git(repo, "rev-parse", args.tip + "^{commit}").strip()
        facts, (mismatches, corrected, unbacked, rows) = evaluate(
            repo, args.sealed, tip, args.lesson, args.no_corrections)
    except (CouldNotEvaluate, OSError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    stale = sum(1 for _fid, declared, witness in facts if declared != witness)
    if args.enumerate:
        print(f"SELFRECORD_R81_ENUM claims={len(facts)} stale={stale} corrected=0")
        return 1 if stale else 0
    if args.json:
        print(json.dumps({"claims": len(facts), "mismatches": mismatches,
                          "corrected": corrected, "unbacked": unbacked,
                          "facts": [dict(zip(("id", "state", "declared", "witness"), row))
                                    for row in rows]}, indent=2))
        return 0 if mismatches == 0 else 1
    for fid, state, declared, witness in rows:
        print(f"SELFRECORD_R81_FACT {fid} {state} declared={declared} witness={witness}")
    print(f"SELFRECORD_R81 claims={len(facts)} mismatches={mismatches} "
          f"corrected={corrected} unbacked={unbacked}")
    return 0 if mismatches == 0 else 1


# --- selftest --------------------------------------------------------------

SCORECARD_GOOD = f"""# SCORECARD

| Axis | Score | Evidence pointer | Last change |
|---|---|---|---|
| calibration | **7** | round 81: newest non-author closure is `corpus/lessons/round-80-verifier-spotcheck.md` | round 81 |

| C1 — the round-80 self-record's six declared facts re-derive | calibration | before | selftest `pass=13 fail=0` |
| C2 — the append-only acceptance population is graded under a late-acceptance rule | operability | exit 1 `APPEND_DEBT round=81 pending=0 unaccepted=10` → exit 0 `APPEND_DEBT round=81 pending=1 unaccepted=0` |
"""

LOG_GOOD = """# LOG

## Round 81 — the round-80 record is graded (2026-11-04)

Frontier: registry 297 → 301 rows (S558, S559).

`LOG-CORRECTION round=81 claim=C2 pending=0 -> pending=1 at=deadbeef`

## Round 80 — earlier
"""

SKILL_GOOD = """| Pre-report gate | gate: `python3 tools/pre-report-gate.py` (ten arms, fixed order: selfdesc) |
"""


def fixture(read_map):
    def read(rev, path):
        if path is None:
            return read_map.get(("closure",))
        return read_map.get((rev, path))
    return read


def selftest():
    cases = []
    facts = [("F1", "sc81c2-pending=1", "sc81c2-pending=4"),
             ("F2", "log81-frontier-rows=301", "log81-frontier-rows=302"),
             ("F3", "skill81-gate-arms=10", "skill81-gate-arms=11"),
             ("F4", "calib81-newest-closure=round-80-verifier-spotcheck.md",
              "calib81-newest-closure=round-81-verifier-spotcheck.md"),
             ("F5", "logcorr81-c2-pending=1", "logcorr81-c2-pending=4"),
             ("F6", "sc81c1-selftest=13", "sc81c1-selftest=13")]
    sealed = "1" * 40

    def honest():
        return {
            ("TIP", LESSON): "## Corrections\n\n" + "\n".join([
                f"corrected F1 old=sc81c2-pending=1 new=sc81c2-pending=4 at={sealed} date=2026-11-04 fix=SCORECARD.md",
                f"corrected F2 old=log81-frontier-rows=301 new=log81-frontier-rows=302 at={sealed} date=2026-11-04 fix=SCORECARD.md",
                f"corrected F3 old=skill81-gate-arms=10 new=skill81-gate-arms=11 at={sealed} date=2026-11-04 fix=SCORECARD.md",
                f"corrected F4 old=calib81-newest-closure=round-80-verifier-spotcheck.md new=calib81-newest-closure=round-81-verifier-spotcheck.md at={sealed} date=2026-11-04 fix=SCORECARD.md",
                f"corrected F5 old=logcorr81-c2-pending=1 new=logcorr81-c2-pending=4 at={sealed} date=2026-11-04 fix=LOG.md",
            ]) + "\n\n## Mistakes\n",
            ("TIP", "SCORECARD.md"): "sc81c2-pending=4 log81-frontier-rows=302 skill81-gate-arms=11 calib81-newest-closure=round-81-verifier-spotcheck.md",
            ("TIP", "LOG.md"): "logcorr81-c2-pending=4",
        }

    def run(name, lesson, extra, want_mismatch, want_unbacked, want_corrected=5):
        read_map = honest()
        read_map[("TIP", LESSON)] = lesson(sealed) if callable(lesson) else lesson
        read_map.update(extra)
        mism, corrected, unbacked, _rows = grade(facts, corrections(read_map[("TIP", LESSON)]),
                                                 fixture(read_map), sealed)
        ok = (mism == want_mismatch and unbacked == want_unbacked
              and corrected == want_corrected)
        cases.append((name, ok, mism, unbacked, corrected))

    run("honest", honest()[("TIP", LESSON)], {}, 0, 0)

    def outside(sealed):
        text = honest()[("TIP", LESSON)]
        body = "\n".join(line for line in text.splitlines() if line.startswith("corrected F1 "))
        return text.replace(body + "\n", "").replace("## Mistakes\n",
                                                     "## Mistakes\n\n" + body + "\n")
    run("correction-outside-container", outside, {}, 1, 0, 4)

    def wrong_at(sealed):
        return honest()[("TIP", LESSON)].replace(f"F1 old=sc81c2-pending=1 new=sc81c2-pending=4 at={sealed}",
                                                 f"F1 old=sc81c2-pending=1 new=sc81c2-pending=4 at={'2' * 40}")
    run("wrong-at", wrong_at, {}, 1, 1, 4)

    def wrong_old(sealed):
        return honest()[("TIP", LESSON)].replace("F1 old=sc81c2-pending=1", "F1 old=sc81c2-pending=0")
    run("wrong-old", wrong_old, {}, 1, 1, 4)

    def wrong_new(sealed):
        return honest()[("TIP", LESSON)].replace("F1 old=sc81c2-pending=1 new=sc81c2-pending=4",
                                                 "F1 old=sc81c2-pending=1 new=sc81c2-pending=9")
    run("wrong-new", wrong_new, {}, 1, 1, 4)

    def unfixed(sealed):
        return honest()[("TIP", LESSON)].replace("fix=LOG.md", "fix=corpus/lessons/round-80.md")
    run("fix-without-token", unfixed,
        {("TIP", "corpus/lessons/round-80.md"): "no token here\n"}, 1, 1, 4)

    def near_token(sealed):
        return honest()[("TIP", LESSON)].replace("new=sc81c2-pending=4", "new=sc81c2-pending=44")
    run("near-token-new", near_token,
        {("TIP", "SCORECARD.md"): "sc81c2-pending=44 log81-frontier-rows=302 skill81-gate-arms=11 "
                                   "calib81-newest-closure=round-81-verifier-spotcheck.md"},
        1, 1, 4)

    def fix_self(sealed):
        return honest()[("TIP", LESSON)].replace("fix=SCORECARD.md", "fix=corpus/lessons/round-82.md")
    run("fix-self-referential", fix_self, {}, 4, 4, 1)

    def near_heading(sealed):
        return honest()[("TIP", LESSON)].replace("## Corrections\n", "## Corrections considered and rejected (not applied)\n")
    run("near-corrections-heading", near_heading, {}, 5, 0, 0)

    def insert(lesson, line):
        return lesson.replace("\n\n## Mistakes", "\n" + line + "\n\n## Mistakes")

    def duplicate(sealed):
        return insert(honest()[("TIP", LESSON)],
                      "corrected F1 old=sc81c2-pending=1 new=sc81c2-pending=4 "
                      f"at={sealed} date=2026-11-04 fix=SCORECARD.md")
    run("duplicate-correction", duplicate, {}, 1, 2, 4)

    def holding(sealed):
        return insert(honest()[("TIP", LESSON)],
                      "corrected F6 old=sc81c1-selftest=13 new=sc81c1-selftest=13 "
                      f"at={sealed} date=2026-11-04 fix=SCORECARD.md")
    run("correction-for-holding-fact", holding, {}, 1, 1, 5)

    def unknown(sealed):
        return insert(honest()[("TIP", LESSON)],
                      "corrected F9 old=x=1 new=x=2 "
                      f"at={sealed} date=2026-11-04 fix=SCORECARD.md")
    run("unknown-fact", unknown, {}, 1, 1, 5)

    def enabled_no_corrections(sealed):
        return "## Corrections\n"
    mism, corrected, unbacked, _rows = grade(facts, [], fixture(honest()), sealed)
    cases.append(("no-corrections", mism == 5 and corrected == 0 and unbacked == 0,
                  mism, unbacked, corrected))

    # extraction arms: the sealed readers must yield the declared tokens and the witnesses
    read_map = {("closure",): "corpus/lessons/round-81-verifier-spotcheck.md"}
    read_map[("TIP", "corpus/lessons/round-81-verifier-spotcheck.md")] = "closure"
    read_map[(SEALED, SCORECARD)] = SCORECARD_GOOD
    read_map[(SEALED, LOG)] = LOG_GOOD
    read_map[(SEALED, SKILL)] = SKILL_GOOD
    read_map[("TIP", DEBT_RECEIPT)] = "APPEND_DEBT round=81 pending=4 unaccepted=0\n"
    read_map[("TIP", GATE_RECEIPT)] = "PRE_REPORT round=81 arms=11 failed=0\n"
    read_map[("TIP", C1_RECEIPT)] = "SELFRECORD_R80_SELFTEST pass=13 fail=0\n"
    read_map[("BASE", "corpus/SOURCES.md")] = "| S001 | a |\n| S002 | b |\n"
    read = fixture(read_map)
    checks = [
        ("extract-f1", fact_f1(read)[0] == "sc81c2-pending=1"),
        ("extract-f2", fact_f2(read) == ("log81-frontier-rows=301", "log81-frontier-rows=2")),
        ("extract-f3", fact_f3(read) == ("skill81-gate-arms=10", "skill81-gate-arms=11")),
        ("extract-f4", fact_f4(read) == (
            "calib81-newest-closure=round-80-verifier-spotcheck.md",
            "calib81-newest-closure=round-81-verifier-spotcheck.md")),
        ("extract-f5", fact_f5(read) == ("logcorr81-c2-pending=1", "logcorr81-c2-pending=4")),
        ("extract-f6", fact_f6(read) == ("sc81c1-selftest=13", "sc81c1-selftest=13")),
        ("registry-rows", registry_rows(read_map[("BASE", "corpus/SOURCES.md")]) == 2),
    ]
    # F2's witness is the tip registry row count; give it the real 302-row shape.
    read_map[("BASE", "corpus/SOURCES.md")] = "".join(
        f"| S{index:03d} | row |\n" for index in range(1, 303))
    read_map[("TIP", "corpus/SOURCES.md")] = "".join(
        f"| S{index:03d} | row |\n" for index in range(1, 306))
    read = fixture(read_map)
    checks[1] = ("extract-f2", fact_f2(read) == ("log81-frontier-rows=301",
                                                 "log81-frontier-rows=302"))
    checks.append(("registry-rows-302", registry_rows(read_map[("BASE", "corpus/SOURCES.md")]) == 302))
    checks.append(("registry-base-bound",
                   fact_f2(read) == ("log81-frontier-rows=301", "log81-frontier-rows=302")))
    for name, ok in checks:
        cases.append((name, ok, "", "", ""))
    failures = [case for case in cases if not case[1]]
    for name, ok, mism, unbacked, corrected in cases:
        print(f"{'PASS' if ok else 'FAIL'} {name} mismatches={mism} unbacked={unbacked} "
              f"corrected={corrected}")
    print(f"SELFRECORD_R81_SELFTEST pass={len(cases) - len(failures)} fail={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
