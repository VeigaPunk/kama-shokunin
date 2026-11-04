#!/usr/bin/env python3
"""round81-selfrecord-round80.py - round-81 C1 (calibration): the round-80 self-record's facts.

PREDICATE (frozen: plans/round-81-claims.md section C1):

    `python3 tools/round81-selfrecord-round80.py --repo <lane>` prints one `SELFRECORD_R80
    claims=6 mismatches=0 corrected=6 unbacked=0` line and exits 0 only when each of the six
    facts the round-80 self-record declares re-derives from the tree at the sealed revision
    a2af1af59faf6cf66fe854559293c4e4b441aff3 and matches the same fact re-derived at the tip,
    or is answered by exactly one committed `corrected F<n> old=<value> new=<value> at=<40-hex>
    date=<ISO>` block in `corpus/lessons/round-81.md` `## Corrections` whose `old` is the sealed
    value, whose `at` is the sealed revision, whose `new` equals the fact's tip value, and whose
    superseded tally is named by the appended round-81 correction block in the record file the
    fact reads; it exits 1 naming every unanswered fact otherwise.

The six facts (declared by the record, observed from the tree):

  F1 c1 row          §Round 80 C1 row's selftest tally vs `.ufo/waves/round-80/measured/after/
                     c1-selftest.out` at the sealed revision (`SELFRECORD_R79_SELFTEST pass=11`)
  F2 c3 row          §Round 80 C3 row's selftest tally vs `…/after/c3-selftest.out` (`pass=12`)
  F3 calibration row `## Axes` calibration row's `--selftest` tally vs the C1 receipt (`pass=11`)
  F4 log row         `LOG.md` §Round 80 C1 bullet's tally vs the C1 receipt (`pass=11`)
  F5 coverage cell   `## Axes` coverage row's last-change cell vs the round its evidence names
  F6 closure pointer `## Axes` calibration row's "newest non-author closure" vs the newest
                     `corpus/lessons/round-*-verifier-spotcheck.md` at the graded tip

F1–F5 are graded at the sealed revision; F6 is tip-bound (the record states it in the present
tense, and the round-80 closure lands after the sealed revision — the round-80 F5 precedent).

Every fact is read with `git show <rev>:<path>`, never from the worktree: the round's own record
commit cannot refute a fact. The correction container is `corpus/lessons/round-81.md` section
`## Corrections`; blocks outside it are prose, not corrections (the round-80 RV01 attack). Each
correction must also be named by the appended record block whose heading contains
`round-81 correction` in the file the fact reads.

Usage: round81-selfrecord-round80.py --repo DIR [--sealed REV] [--tip REV] [--lesson PATH]
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
from pathlib import Path

SEALED = "a2af1af59faf6cf66fe854559293c4e4b441aff3"
LESSON = "corpus/lessons/round-81.md"
SCORECARD = "SCORECARD.md"
LOG = "LOG.md"
C1_RECEIPT = ".ufo/waves/round-80/measured/after/c1-selftest.out"
C3_RECEIPT = ".ufo/waves/round-80/measured/after/c3-selftest.out"
CLOSURE_GLOB = re.compile(r"^corpus/lessons/(round-([0-9]+)-verifier-spotcheck\.md)$")
CORRECTION = re.compile(
    r"corrected\s+(F[0-9]+)\s+old=(\S+)\s+new=(\S+)\s+at=(\S+)\s+date=(\d{4}-\d{2}-\d{2})")
SELFTEST_RE = re.compile(r"pass=([0-9]+) fail=([0-9]+)")
ROUND_RE = re.compile(r"round[ -]([0-9]+)")


class CouldNotEvaluate(Exception):
    pass


class Repo:
    def __init__(self, path: Path):
        self.path = path
        self.cache = {}

    def git(self, *args: str) -> str:
        proc = subprocess.run(["git", "-C", str(self.path), *args], capture_output=True,
                              text=True, timeout=180)
        if proc.returncode != 0:
            raise CouldNotEvaluate(f"git {' '.join(args)} exit={proc.returncode}: "
                                   f"{proc.stderr.strip()}")
        return proc.stdout

    def show(self, rev: str, path: str) -> str | None:
        key = (rev, path)
        if key not in self.cache:
            proc = subprocess.run(["git", "-C", str(self.path), "show", f"{rev}:{path}"],
                                  capture_output=True, text=True, timeout=180)
            self.cache[key] = proc.stdout if proc.returncode == 0 else None
        return self.cache[key]

    def newest_closure(self, tip: str) -> str | None:
        listing = self.git("ls-tree", "-r", "--name-only", tip, "corpus/lessons/").splitlines()
        best = None
        for path in listing:
            if not CLOSURE_GLOB.match(path):
                continue
            stamp = self.git("log", "-1", "--format=%ct", tip, "--", path).strip()
            key = (int(stamp or 0), path)
            if best is None or key > best:
                best = key
        return best[1] if best else None


class Fixture:
    """Offline blob fixture for the selftest: rev -> {path: text}."""

    def __init__(self, blobs, closures=None):
        self.blobs = blobs
        self.closures = closures or {}

    def show(self, rev: str, path: str) -> str | None:
        return self.blobs.get(rev, {}).get(path)

    def newest_closure(self, tip: str) -> str | None:
        return self.closures.get(tip)


def section(text: str, prefix: str) -> str:
    """Every `## <prefix>` section joined: a record may append a correction entry under a
    second heading with the same round prefix (the LOG does exactly that)."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("## "):
            inside = line[3:].strip().startswith(prefix)
        if inside:
            out.append(line)
    return "\n".join(out)


def marked_section(text: str, needle: str) -> str:
    """From the heading line containing `needle` to the next heading of level <= 2 (`## `)."""
    out, inside = [], False
    for line in text.splitlines():
        if line.startswith("## ") or line.startswith("#### "):
            if inside:
                break
            inside = needle in line
        if inside:
            out.append(line)
    return "\n".join(out)


def axis_row(text: str, name: str) -> list[str] | None:
    for line in section(text, "Axes").splitlines():
        if line.startswith(f"| {name} |") or line.startswith(f"| **{name}** |"):
            return line.split("|")
    return None


def block_row(text: str, prefix: str, ident: str) -> str | None:
    for line in section(text, prefix).splitlines():
        if line.startswith(f"| {ident}"):
            return line
    return None


# ---------------------------------------------------------------- fact derivation

def f1(repo, rev: str) -> tuple[str, str]:
    row = block_row(repo.show(rev, SCORECARD) or "", "Round 80", "C1")
    declared = "c1-selftest=absent"
    if row:
        m = re.search(r"selftest `pass=([0-9]+) fail=([0-9]+)`", row)
        if m:
            declared = f"c1-selftest=pass={m.group(1)}"
    receipt = repo.show(rev, C1_RECEIPT) or ""
    m = re.search(r"SELFRECORD_R79_SELFTEST pass=([0-9]+)", receipt)
    observed = f"c1-selftest=pass={m.group(1)}" if m else "c1-selftest=absent"
    return declared, observed


def f2(repo, rev: str) -> tuple[str, str]:
    row = block_row(repo.show(rev, SCORECARD) or "", "Round 80", "C3")
    declared = "c3-selftest=absent"
    if row:
        m = re.search(r"selftest `pass=([0-9]+) fail=([0-9]+)`", row)
        if m:
            declared = f"c3-selftest=pass={m.group(1)}"
    receipt = repo.show(rev, C3_RECEIPT) or ""
    m = re.search(r"OLLAMA_CENSUS_SELFTEST pass=([0-9]+)", receipt)
    observed = f"c3-selftest=pass={m.group(1)}" if m else "c3-selftest=absent"
    return declared, observed


def f3(repo, rev: str) -> tuple[str, str]:
    cells = axis_row(repo.show(rev, SCORECARD) or "", "calibration")
    declared = "calibration-row-selftest=absent"
    if cells:
        m = re.search(r"`--selftest` → `pass=([0-9]+) fail=([0-9]+)`", "|".join(cells))
        if m:
            declared = f"calibration-row-selftest=pass={m.group(1)}"
    receipt = repo.show(rev, C1_RECEIPT) or ""
    m = re.search(r"SELFRECORD_R79_SELFTEST pass=([0-9]+)", receipt)
    observed = f"calibration-row-selftest=pass={m.group(1)}" if m else "calibration-row-selftest=absent"
    return declared, observed


def f4(repo, rev: str) -> tuple[str, str]:
    flat = " ".join(section(repo.show(rev, LOG) or "", "Round 80").split())
    declared = "log-c1-selftest=absent"
    m = re.search(r"C1 calibration.*?selftest `pass=([0-9]+) fail=([0-9]+)`", flat)
    if m:
        declared = f"log-c1-selftest=pass={m.group(1)}"
    receipt = repo.show(rev, C1_RECEIPT) or ""
    m = re.search(r"SELFRECORD_R79_SELFTEST pass=([0-9]+)", receipt)
    observed = f"log-c1-selftest=pass={m.group(1)}" if m else "log-c1-selftest=absent"
    return declared, observed


def f5(repo, rev: str) -> tuple[str, str]:
    cells = axis_row(repo.show(rev, SCORECARD) or "", "coverage")
    declared = "coverage-last-change=absent"
    observed = "coverage-last-change=absent"
    if cells and len(cells) >= 5:
        last = cells[4]
        m = re.search(r"evidence re-anchored round ([0-9]+)", last)
        if m:
            declared = f"coverage-last-change=round-{m.group(1)}"
        rounds = [int(r) for r in ROUND_RE.findall(cells[3])]
        if rounds:
            observed = f"coverage-last-change=round-{max(rounds)}"
    return declared, observed


def f6(repo, rev: str, tip: str) -> tuple[str, str]:
    cells = axis_row(repo.show(rev, SCORECARD) or "", "calibration")
    declared = "newest-closure=absent"
    if cells:
        m = re.search(r"newest non-author closure is `corpus/lessons/([^`]+)`", "|".join(cells))
        if m:
            declared = f"newest-closure={m.group(1)}"
    newest = repo.newest_closure(tip)
    if newest:
        newest = newest.rsplit("/", 1)[-1]
    observed = f"newest-closure={newest}" if newest else "newest-closure=absent"
    return declared, observed


FACTS = [("F1", "SCORECARD.md", f1), ("F2", "SCORECARD.md", f2),
         ("F3", "SCORECARD.md", f3), ("F4", "LOG.md", f4),
         ("F5", "SCORECARD.md", f5), ("F6", "SCORECARD.md", None)]

MARKERS = {
    "F1": (SCORECARD, "C1-selftest pass=9 -> pass=11", "block"),
    "F2": (SCORECARD, "C3-selftest pass=6 -> pass=12", "block"),
    "F3": (SCORECARD, "calibration-row pass=9 -> pass=11", "block"),
    "F4": (LOG, "selftest tallies pass=9/pass=6 -> pass=11/pass=12", "file"),
    "F5": (SCORECARD, "coverage-last-change round 79 -> round 80", "block"),
    "F6": (SCORECARD, "newest-closure round-79-verifier-spotcheck.md -> "
                      "round-80-verifier-spotcheck.md", "block"),
}
TIP_BOUND = {"F6"}


def derive(repo, rev: str, tip: str) -> dict[str, dict[str, str]]:
    out = {}
    for fact, _path, fn in FACTS:
        if fact == "F6":
            declared, observed = f6(repo, rev, tip)
        else:
            declared, observed = fn(repo, rev)
        out[fact] = {"declared": declared, "observed": observed,
                     "stale": declared != observed}
    return out


def corrections(repo, tip: str, lesson: str) -> list[dict[str, str]]:
    text = repo.show(tip, lesson)
    if text is None:
        return []
    blocks = []
    for m in CORRECTION.finditer(section(text, "Corrections")):
        blocks.append({"fact": m.group(1), "old": m.group(2), "new": m.group(3),
                       "at": m.group(4), "date": m.group(5)})
    return blocks


def score(repo, sealed: str, tip: str, lesson: str, corrections_enabled: bool = True):
    facts = derive(repo, sealed, tip)
    blocks = corrections(repo, tip, lesson) if corrections_enabled else []
    by_fact = {}
    for block in blocks:
        by_fact.setdefault(block["fact"], []).append(block)
    errors, unbacked, corrected = [], [], 0
    for fact, info in facts.items():
        if not info["stale"]:
            continue
        blocks_here = by_fact.get(fact, [])
        if len(blocks_here) != 1:
            errors.append((fact, "no-correction" if not blocks_here else "duplicate-correction"))
            continue
        block = blocks_here[0]
        problem = None
        if block["old"] != info["declared"]:
            problem = f"old={block['old']} != declared {info['declared']}"
        elif block["new"] != info["observed"]:
            problem = f"new={block['new']} != observed {info['observed']}"
        elif block["at"] != sealed:
            problem = f"at={block['at']} != sealed {sealed}"
        if problem:
            unbacked.append((fact, problem))
            continue
        path, marker, scope = MARKERS[fact]
        record = repo.show(tip, path) or ""
        haystack = record if scope == "file" else marked_section(record, "round-81 correction")
        if marker not in haystack:
            unbacked.append((fact, f"record block names no `{marker}`"))
            continue
        corrected += 1
    for fact in by_fact:
        if fact not in facts:
            unbacked.append((fact, "correction names no fact"))
        elif not facts[fact]["stale"]:
            unbacked.append((fact, "correction for a fact that re-derives"))
    return facts, {
        "claims": len(facts),
        "stale": sum(1 for f in facts.values() if f["stale"]),
        "mismatches": len(errors),
        "corrected": corrected,
        "unbacked": len(unbacked),
        "errors": errors,
        "unbacked_detail": unbacked,
    }


# ---------------------------------------------------------------- selftest

SEALED_BLOBS = {
    SCORECARD: """# fixture SCORECARD

## Axes

| Axis | Score | Evidence pointer | Last change |
|---|---|---|---|
| calibration | **7** | round 80: run `python3 tools/round80-selfrecord-round79.py --repo .` → `SELFRECORD_R79 claims=6` and `--selftest` → `pass=9 fail=0`; the newest non-author closure is `corpus/lessons/round-79-verifier-spotcheck.md` (round 79) | score round 1 |
| coverage | **9** | round 80: one admitted entry; round 79: the census class | score round 10; evidence re-anchored round 79 |

## Round 80 — fixture record

| Claim | Axis | Before → after | Command | Verdict |
|---|---|---|---|---|
| C1 — fixture | calibration | exit 1 → exit 0 | `python3 tools/x.py` | **verified**; selftest `pass=9 fail=0` (`measured/after/c1-selftest.out`) |
| C3 — fixture | operability | exit 2 → exit 0 | `python3 tools/y.py` | **verified**; selftest `pass=6 fail=0` (`measured/after/c3-selftest.out`) |
""",
    LOG: """# fixture LOG

## Round 80 — fixture entry

- **C1 calibration (lowest assigned axis, 7)** — the record grades itself; exit 0; selftest
  `pass=9 fail=0`; the control prints `mismatches=3` exit 1.
- **C3 operability** — selftest `pass=6 fail=0`.
""",
    C1_RECEIPT: "SELFRECORD_R79_SELFTEST pass=11 fail=0\nEXIT=0\n",
    C3_RECEIPT: "OLLAMA_CENSUS_SELFTEST pass=12 fail=0\nEXIT=0\n",
}

TIP_BLOBS = dict(SEALED_BLOBS)
TIP_BLOBS[SCORECARD] = SEALED_BLOBS[SCORECARD] + """
#### round-81 correction (appended; the §Round 80 bytes stand)

- C1-selftest pass=9 -> pass=11
- C3-selftest pass=6 -> pass=12
- calibration-row pass=9 -> pass=11
- coverage-last-change round 79 -> round 80
- newest-closure round-79-verifier-spotcheck.md -> round-80-verifier-spotcheck.md
"""
TIP_BLOBS[LOG] = SEALED_BLOBS[LOG] + """
## Round 80 — correction (appended)

`LOG-CORRECTION round=80 selftest tallies pass=9/pass=6 -> pass=11/pass=12`
"""

CORRECTION_TEXT = """# fixture lesson

## Corrections

`corrected F1 old=c1-selftest=pass=9 new=c1-selftest=pass=11 at=SEALED date=2026-11-04`
`corrected F2 old=c3-selftest=pass=6 new=c3-selftest=pass=12 at=SEALED date=2026-11-04`
`corrected F3 old=calibration-row-selftest=pass=9 new=calibration-row-selftest=pass=11 at=SEALED date=2026-11-04`
`corrected F4 old=log-c1-selftest=pass=9 new=log-c1-selftest=pass=11 at=SEALED date=2026-11-04`
`corrected F5 old=coverage-last-change=round-79 new=coverage-last-change=round-80 at=SEALED date=2026-11-04`
`corrected F6 old=newest-closure=round-79-verifier-spotcheck.md new=newest-closure=round-80-verifier-spotcheck.md at=SEALED date=2026-11-04`
"""


def selftest() -> int:
    sealed, tip = "a" * 40, "b" * 40
    lesson_text = CORRECTION_TEXT.replace("SEALED", sealed)
    base_blobs = {sealed: SEALED_BLOBS, tip: {**TIP_BLOBS, LESSON: lesson_text}}
    closures = {sealed: "corpus/lessons/round-79-verifier-spotcheck.md",
                tip: "corpus/lessons/round-80-verifier-spotcheck.md"}
    cases = []

    def run(blobs=None, closures_=None, enabled=True):
        fixture = Fixture(blobs or base_blobs, closures_ or closures)
        return score(fixture, sealed, tip, LESSON, enabled)

    facts, result = run()
    cases.append(("honest", result, 0))
    cases.append(("stale-count", {"stale": result["stale"]}, 6))
    cases.append(("corrected-count", {"corrected": result["corrected"]}, 6))

    # a correction block outside `## Corrections` is prose
    moved = lesson_text.replace("## Corrections", "## Notes")
    blobs = {sealed: SEALED_BLOBS, tip: {**TIP_BLOBS, LESSON: moved}}
    cases.append(("outside-container", run(blobs)[1], 6))
    # wrong `at`
    bad_at = lesson_text.replace(f"at={sealed}", "at=" + "c" * 40, 1)
    cases.append(("wrong-at", run({sealed: SEALED_BLOBS,
                                   tip: {**TIP_BLOBS, LESSON: bad_at}})[1], 1))
    # wrong `new`
    bad_new = lesson_text.replace("new=c1-selftest=pass=11", "new=c1-selftest=pass=99")
    cases.append(("wrong-new", run({sealed: SEALED_BLOBS,
                                    tip: {**TIP_BLOBS, LESSON: bad_new}})[1], 1))
    # wrong `old`
    bad_old = lesson_text.replace("old=c1-selftest=pass=9", "old=c1-selftest=pass=7")
    cases.append(("wrong-old", run({sealed: SEALED_BLOBS,
                                    tip: {**TIP_BLOBS, LESSON: bad_old}})[1], 1))
    # missing correction
    missing = lesson_text.replace(
        "`corrected F2 old=c3-selftest=pass=6 new=c3-selftest=pass=12 at="
        f"{sealed} date=2026-11-04`\n", "")
    cases.append(("missing-correction", run({sealed: SEALED_BLOBS,
                                             tip: {**TIP_BLOBS, LESSON: missing}})[1], 1))
    # duplicate correction
    duplicate = lesson_text + lesson_text.split("## Corrections\n", 1)[1].splitlines()[1] + "\n"
    cases.append(("duplicate-correction", run({sealed: SEALED_BLOBS,
                                               tip: {**TIP_BLOBS, LESSON: duplicate}})[1], 1))
    # record block missing the marker
    stripped = TIP_BLOBS[SCORECARD].replace("- C1-selftest pass=9 -> pass=11\n", "")
    cases.append(("marker-missing", run({sealed: SEALED_BLOBS,
                                         tip: {**TIP_BLOBS, SCORECARD: stripped,
                                               LESSON: lesson_text}})[1], 1))
    # a worktree-independent fact: a corrected record has nothing stale
    fixed_sealed = dict(SEALED_BLOBS)
    fixed_sealed[SCORECARD] = SEALED_BLOBS[SCORECARD].replace(
        "selftest `pass=9 fail=0`", "selftest `pass=11 fail=0`", 1)
    cases.append(("not-stale", run({sealed: fixed_sealed,
                                    tip: {**TIP_BLOBS, LESSON: lesson_text}})[1], 1))
    # no-corrections mode restores the full mismatch count
    _, result_nc = run(enabled=False)
    cases.append(("no-corrections", {"mismatches": result_nc["mismatches"]}, 6))
    # tip without the round-80 closure: F6 is not stale
    _, result_tip = run(closures_={sealed: "corpus/lessons/round-79-verifier-spotcheck.md",
                                  tip: "corpus/lessons/round-79-verifier-spotcheck.md"})
    cases.append(("f6-not-tip-stale", {"stale": result_tip["stale"]}, 5))
    fail = 0
    for name, result, want in cases:
        if name in ("honest",):
            got = 0 if (result["mismatches"] == 0 and result["unbacked"] == 0
                        and result["corrected"] == 6) else 1
        elif name == "stale-count":
            got = result["stale"]
        elif name == "corrected-count":
            got = result["corrected"]
        elif name == "no-corrections":
            got = result["mismatches"]
        elif name == "f6-not-tip-stale":
            got = result["stale"]
        elif name == "outside-container":
            got = result["mismatches"]
        else:
            got = result["unbacked"] if result["mismatches"] == 0 else result["mismatches"]
        if got != want:
            fail += 1
            print(f"SELFRECORD_R80_SELFTEST_FAIL {name} got={got} want={want} "
                  f"summary={{'stale': {result.get('stale')}, "
                  f"'mismatches': {result.get('mismatches')}, "
                  f"'corrected': {result.get('corrected')}, "
                  f"'unbacked': {result.get('unbacked')}}}")
    print(f"SELFRECORD_R80_SELFTEST pass={len(cases) - fail} fail={fail}")
    return 0 if fail == 0 else 1


# ---------------------------------------------------------------- main

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
    repo = Repo(Path(args.repo).resolve())
    try:
        tip = repo.git("rev-parse", "--verify", f"{args.tip}^{{commit}}").strip()
        sealed = repo.git("rev-parse", "--verify", f"{args.sealed}^{{commit}}").strip()
        facts, result = score(repo, sealed, tip, args.lesson,
                             corrections_enabled=not args.no_corrections)
    except (CouldNotEvaluate, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps({"facts": facts, "summary": result}, indent=2))
        return 0 if (result["mismatches"] == 0 and result["unbacked"] == 0) else 1
    if args.enumerate:
        print(f"SELFRECORD_R80_ENUM claims={result['claims']} stale={result['stale']} "
              f"corrected={result['corrected']}")
        for fact, info in facts.items():
            if info["stale"]:
                print(f"SELFRECORD_R80_STALE {fact} declared={info['declared']} "
                      f"observed={info['observed']}")
        return 0 if result["stale"] == result["corrected"] and result["unbacked"] == 0 else 1
    print(f"SELFRECORD_R80 claims={result['claims']} mismatches={result['mismatches']} "
          f"corrected={result['corrected']} unbacked={result['unbacked']}")
    for fact, reason in result["errors"]:
        print(f"SELFRECORD_R80_UNANSWERED {fact} {reason}")
    for fact, detail in result["unbacked_detail"]:
        print(f"SELFRECORD_R80_UNBACKED {fact} {detail}")
    return 0 if (result["mismatches"] == 0 and result["unbacked"] == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
