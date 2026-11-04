#!/usr/bin/env python3
"""Round-78 C1: the round-77 self-record's six declared facts, graded at the live tree.

Each fact value is the frozen fixed string (plans/round-78-claims.md §C1); a fact re-derives
when the tree's own derivation equals it, and a non-re-deriving fact is answered only by a
committed correction block in `corpus/lessons/round-78.md` §Corrections of the exact shape::

    - `corrected <fact>` old=`<old value>` new=`<new value>` at=`<40-hex>` date=`YYYY-MM-DD`
    <one prose line>

`at` must be the sealed revision `6c1550a14babaca092cfcc3106f792d695652200` and the stated
`old` must re-derive there from committed blobs (`git show <at>:<path>`, never a checkout);
the stated `new` must equal the frozen value and the live derivation. Two blocks naming one
fact are one correction; the second is reported `duplicate` (frozen counting rule (b), which
the kill rule requires to be red).

Derivation grounds (current state = worktree bytes; `at` re-derivation = blobs):
  F1 the `## Axes` score table in `SCORECARD.md`;
  F2 the newest `Capabilities — canonical list as of round <N>` table in `SCORECARD.md`;
  F3 `SKILL.md`'s `| Pre-report gate |` row, bound to the gate module's own arm count and
     newest arm (AST over `tools/pre-report-gate.py` `ARM_SPECS`/`ARM_ORDER`) and to the
     round-77 gate-selftest tally read from the committed receipt
     `.ufo/waves/round-77/measured/after/gate-selftest.out` at the sealed revision —
     never by running `pre-report-gate.py` (frozen scope ruling (c));
  F4 the record section's LAST `corpus/lessons/round-77.md` §<location> sentence
     (frozen scope ruling (d): an appended correction supersedes a stale pointer);
  F5 the knowledge entries introduced in (record base .. sealed revision] under
     `corpus/knowledge/` (record-declared base, `git log --diff-filter=A`), each carrying a
     `source:`/`source-correction:` line citing an `S###` row id;
  F6 coverage-map rows for that population in `corpus/README.md`
     (entry cells `` `knowledge/<name>` `` or `` `corpus/knowledge/<name>` ``).

Exits: 0 only with zero findings; 1 printing
`SELFRECORD_R77_FINDING <mismatch|unbacked|cheat|duplicate> <fact>` per finding (`cheat` =
a graded fact whose in-tree ground structure is absent, so a pass would be ignoring the
ground); 2 on could-not-evaluate (missing/unreadable self-record, gate module, gate receipt,
registry or knowledge population; CLI misuse). A missing `round-78.md` lesson is not exit 2:
it simply carries no corrections, which is the unrepaired base state.

Selftest (`--selftest`): builds a sealed-base fixture under `--work`/TMPDIR — the fixture
commits via plumbing-adjacent `git add`/`git commit` inside its own scratch root only, with
`rev-parse --show-toplevel` asserted, mirroring the committed `round76-selfrecord-facts.py`
harness; the lane itself is never touched. Arms: base-red, green-control, and the six frozen
kill arms cheat-constant, stale-uncorrected, correction-wrong-value, unbacked, pointer-wrong,
duplicate-correction.
"""
from __future__ import annotations

import argparse
import ast
import importlib.util
import io
import os
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
_SPEC = importlib.util.spec_from_file_location(
    "round76_selfrecord_facts", Path(__file__).with_name("round76-selfrecord-facts.py"))
_PREVIOUS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_PREVIOUS)
CouldNotEvaluate = _PREVIOUS.CouldNotEvaluate
git, blob, text = _PREVIOUS.git, _PREVIOUS.blob, _PREVIOUS.text
match, section = _PREVIOUS.match, _PREVIOUS.section

SEALED = "6c1550a14babaca092cfcc3106f792d695652200"
RECORD = "SCORECARD.md"
RECORD_ROUND_RE = re.compile(r"^## Round 77[^\n]*", re.M)
SKILL = "SKILL.md"
GATE_MODULE = "tools/pre-report-gate.py"
GATE_ROW_PREFIX = "| Pre-report gate |"
TALLY_RECEIPT = ".ufo/waves/round-77/measured/after/gate-selftest.out"
TALLY_RE = re.compile(r"^PRE_REPORT_SELFTEST pass=(\d+) fail=0", re.M)
CORRECTIONS = "corpus/lessons/round-78.md"
AXIS_ORDER = ("operability", "freshness", "depth", "coverage", "calibration", "adjacency")
NUM_WORDS = {2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven",
             8: "eight", 9: "nine", 10: "ten", 11: "eleven", 12: "twelve"}
FACT_VALUES = {
    "F1": "scores=operability:8/freshness:8/depth:7/coverage:9/calibration:7/adjacency:7",
    "F2": "capabilities=34/max-round=77",
    "F3": "gate=arms:9/word:nine/newest:round77-instruments/tally:22",
    "F4": "pointer=section:Freeze divergences item 3",
    "F5": "provenance=missing:none",
    "F6": "coverage-map=missing:none",
}
FACT_ORDER = ("F1", "F2", "F3", "F4", "F5", "F6")
PREDICATE = """`python3 tools/round78-selfrecord-round77.py --repo <lane>` prints one
`SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0` line and exits 0 only when each
of six declared facts of the round-77 self-record re-derives from the tree — F1 the `## Axes`
score vector equals the record's declared vector `operability 8, freshness 8, depth 7,
coverage 9, calibration 7, adjacency 7`; F2 the canonical capability table carries 34 data
rows and its highest first-working round is 77; F3 `SKILL.md`'s pre-report-gate row carries the
gate module's own arm count in prose and in its `arms=` token, names the newest arm
`round77-instruments`, and carries the self-test tally of the round-77 gate-selftest receipt;
F4 the record's last freeze-divergence sentence points the C3 predicate/ruling divergence at
`corpus/lessons/round-77.md` §Freeze divergences item 3; F5 every knowledge entry added by
round 77 carries a `source:` or `source-correction:` line citing at least one `S###` row id;
F6 every knowledge entry added by round 77 has a coverage-map row in `corpus/README.md` — and
each fact that does not re-derive is answered by a committed
correction block naming the fact id, the old value re-derived at the sealed revision
`6c1550a14babaca092cfcc3106f792d695652200`, the new value and the date; it exits 1 naming
`SELFRECORD_R77_FINDING <mismatch|unbacked|cheat> <fact>` for a non-re-deriving fact with no
valid correction, a correction whose stated new value does not re-derive, or a graded fact
whose ground the counter ignores; and 2 on could-not-evaluate (missing self-record or lesson,
unreadable gate module, CLI misuse)."""


class GroundAbsent(Exception):
    """A graded fact's in-tree ground structure is missing; passing would ignore it."""


def worktree(repo, relpath):
    try:
        return (Path(repo) / relpath).read_bytes().decode("utf-8")
    except FileNotFoundError as exc:
        raise CouldNotEvaluate(f"missing worktree file: {relpath}") from exc
    except (OSError, UnicodeError) as exc:
        raise CouldNotEvaluate(f"unreadable worktree file {relpath}: {exc}") from exc


def record_section(source):
    found = RECORD_ROUND_RE.search(source)
    if not found:
        raise CouldNotEvaluate(f"{RECORD} carries no '## Round 77' section")
    end = re.search(r"^## ", source[found.end():], re.M)
    stop = found.end() + end.start() if end else len(source)
    return source[found.start():stop]


# ------------------------------------------------------------------ derivations
AXES_HEADER_RE = re.compile(r"^\| Axis \|[^\n]*\n", re.M)
AXES_ROW_RE = re.compile(r"^\|\s*\*{0,2}([a-z]+)\*{0,2}\s*\|\s*\*{0,2}(\d+)\*{0,2}\s*\|")
CANONICAL_RE = re.compile(
    r"^[#\s*]*Capabilities\s+—\s+canonical list as of round (\d+)[^\n]*", re.M)
ARMS_TOKEN_RE = re.compile(r"arms=(\d+)")
PASS_TOKEN_RE = re.compile(r"pass=(\d+)")
PROSE_RE = re.compile(r"\b(" + "|".join(NUM_WORDS.values()) + r")\s+arms\b")
POINTER_RE = re.compile(r"corpus/lessons/round-77\.md`?\s*§\s*([^\n.;!?]+)")
COVERAGE_CELL_RE = re.compile(r"^\|\s*`(?:corpus/)?knowledge/([^`\n]+)`", re.M)
SOURCE_ID_RE = re.compile(r"\bS\d{3}\b")


def derive_axes(source):
    try:
        axes, _ = section(source, r"^## Axes\s*$")
    except CouldNotEvaluate as exc:
        raise GroundAbsent(f"F1: {exc}") from exc
    header = AXES_HEADER_RE.search(axes)
    if not header:
        raise GroundAbsent("F1: the '## Axes' section carries no score table")
    scores = {}
    for line in axes[header.end():].splitlines():
        row = AXES_ROW_RE.match(line)
        if not row:
            if scores:
                break
            continue
        scores[row.group(1)] = row.group(2)
    lacking = [axis for axis in AXIS_ORDER if axis not in scores]
    if lacking:
        raise GroundAbsent("F1: the '## Axes' score table lacks " + ", ".join(lacking))
    return "scores=" + "/".join(f"{axis}:{scores[axis]}" for axis in AXIS_ORDER)


def derive_capabilities(source):
    best = None
    for found in CANONICAL_RE.finditer(source):
        number = int(found.group(1))
        if best is None or number >= best[0]:
            best = (number, found)
    if best is None:
        raise GroundAbsent("F2: the scorecard carries no canonical capability list")
    rows, started = [], False
    for line in source[best[1].end():].splitlines():
        if line.startswith("|"):
            started = True
            rows.append(line)
        elif not started:
            if line.strip():
                raise GroundAbsent("F2: the newest canonical capability list carries no table")
        else:
            break
    data = rows[2:]
    if not data:
        raise GroundAbsent("F2: the newest canonical capability list carries no data rows")
    rounds = []
    for row in data:
        cells = [cell.strip() for cell in row.strip().strip("|").split("|")]
        found = re.match(r"^(\d+)", cells[-1]) if cells else None
        if not found:
            raise GroundAbsent("F2: a canonical capability row lacks a first-working round")
        rounds.append(int(found.group(1)))
    return f"capabilities={len(data)}/max-round={max(rounds)}"


def derive_gate_row(source, newest_arm):
    for line in source.splitlines():
        if line.startswith(GATE_ROW_PREFIX):
            arms, word, tally = ARMS_TOKEN_RE.search(line), PROSE_RE.search(line), PASS_TOKEN_RE.search(line)
            return dict(
                value="gate=arms:{}/word:{}/newest:{}/tally:{}".format(
                    arms.group(1) if arms else "absent",
                    word.group(1) if word else "absent",
                    newest_arm,
                    tally.group(1) if tally else "absent"),
                arms=int(arms.group(1)) if arms else None,
                word=word.group(1) if word else None,
                mentions=bool(newest_arm in line),
                tally=int(tally.group(1)) if tally else None)
    raise GroundAbsent(f"F3: {SKILL} carries no '{GATE_ROW_PREFIX}' row")


def derive_pointer(record):
    targets = POINTER_RE.findall(record)
    if not targets:
        raise GroundAbsent("F4: the record names no corpus/lessons/round-77.md §location")
    return "pointer=section:" + targets[-1].strip()


def record_base(record):
    found = re.search(r"base `([0-9a-f]{40})`", record)
    if not found:
        raise CouldNotEvaluate("the round-77 record declares no base revision")
    return found.group(1)


def knowledge_population(repo, base, sealed):
    ancestry = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                               base, sealed], capture_output=True)
    if ancestry.returncode:
        raise CouldNotEvaluate(f"declared record base {base} is not ancestral to {sealed}")
    out = git(repo, "log", f"{base}..{sealed}", "--diff-filter=A", "--format=%H",
              "--name-only", "--", "corpus/knowledge/").decode("utf-8", "replace")
    names = sorted({line.strip() for line in out.splitlines()
                    if line.strip().endswith(".md")
                    and "engine-sides" not in line and "processes" not in line})
    if not names:
        raise CouldNotEvaluate("no knowledge entry is introduced in (base..sealed]; "
                               "a check that collects nothing cannot pass")
    return names


def derive_provenance(repo, population, rev=None):
    missing = []
    for entry in population:
        value = text(repo, rev, entry) if rev else worktree(repo, entry)
        if not any(stripped.startswith(("source:", "source-correction:"))
                   and SOURCE_ID_RE.search(stripped)
                   for stripped in (line.strip() for line in value.splitlines())):
            missing.append(entry)
    return "provenance=missing:" + (",".join(missing) if missing else "none")


def derive_coverage(repo, population, rev=None):
    source = text(repo, rev, "corpus/README.md") if rev else worktree(repo, "corpus/README.md")
    mapped = set(COVERAGE_CELL_RE.findall(source))
    missing = [entry for entry in population if Path(entry).name not in mapped]
    return "coverage-map=missing:" + (",".join(missing) if missing else "none")


def gate_grounds(repo, rev=None):
    if rev is not None:
        try:
            source = text(repo, rev, GATE_MODULE)
        except CouldNotEvaluate as exc:
            raise CouldNotEvaluate(f"unreadable gate module at {rev}: {exc}") from exc
    else:
        path = Path(repo) / GATE_MODULE
        try:
            source = path.read_bytes().decode("utf-8")
        except (OSError, UnicodeError) as exc:
            raise CouldNotEvaluate(f"unreadable gate module {GATE_MODULE}: {exc}") from exc
    try:
        tree = ast.parse(source)
    except SyntaxError as exc:
        raise CouldNotEvaluate(f"unparsable gate module {GATE_MODULE}: {exc}") from exc
    specs = order = None
    for node in tree.body:
        if isinstance(node, ast.Assign):
            names = {getattr(target, "id", None) for target in node.targets}
            if "ARM_SPECS" in names and isinstance(node.value, ast.List):
                specs = node.value.elts
            elif "ARM_ORDER" in names:
                order = node.value
    if specs is None or order is None:
        raise CouldNotEvaluate(f"gate module {GATE_MODULE} carries no ARM_SPECS/ARM_ORDER")
    literals = []

    def walk(node):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            walk(node.left)
            walk(node.right)
        elif isinstance(node, (ast.List, ast.Tuple)):
            literals.extend(elt.value for elt in node.elts
                            if isinstance(elt, ast.Constant) and isinstance(elt.value, str))
    walk(order)
    if isinstance(order, ast.BinOp) and isinstance(order.op, ast.Add):
        count = len(specs) + len(literals)
    elif isinstance(order, ast.List):
        count = len(literals)
    else:
        raise CouldNotEvaluate(f"gate module {GATE_MODULE}: ARM_ORDER is not a literal arm list")
    if not literals:
        raise CouldNotEvaluate(f"gate module {GATE_MODULE}: ARM_ORDER names no arms")
    return count, literals[-1]


def receipt_tally(repo, sealed):
    try:
        value = text(repo, sealed, TALLY_RECEIPT)
    except CouldNotEvaluate as exc:
        raise CouldNotEvaluate(f"the committed round-77 gate-selftest receipt is unreadable "
                               f"at the sealed revision: {exc}") from exc
    found = TALLY_RE.search(value)
    if not found:
        raise CouldNotEvaluate(f"{TALLY_RECEIPT} at the sealed revision carries no tally")
    return int(found.group(1))


# ------------------------------------------------------------------ corrections
CORRECTIONS_HEADING_RE = re.compile(r"^##[^\n]*Corrections[^\n]*$", re.M)
CORRECTION_BULLET_RE = re.compile(
    r"^- `corrected (F[1-6])` old=`([^\n`]*)` new=`([^\n`]*)` "
    r"at=`([0-9a-f]{40})` date=`(\d{4}-\d{2}-\d{2})`[ \t]*$", re.M)


def correction_blocks(repo, sealed):
    try:
        value = worktree(repo, CORRECTIONS)
    except CouldNotEvaluate:
        return []  # a not-yet-landed lesson simply carries no corrections
    found = CORRECTIONS_HEADING_RE.search(value)
    if not found:
        return []
    body = value[found.end():]
    end = re.search(r"^## ", body, re.M)
    body = body[:end.start()] if end else body
    blocks = []
    for bullet in CORRECTION_BULLET_RE.finditer(body):
        prose = body[bullet.end():].lstrip("\n").split("\n", 1)[0]
        try:
            dated = date.fromisoformat(bullet.group(5)) is not None
        except ValueError:
            dated = False
        blocks.append(dict(
            fact=bullet.group(1), old=bullet.group(2), new=bullet.group(3),
            at=bullet.group(4), pos=bullet.start(),
            valid=bool(dated and prose.strip()
                       and not prose.lstrip().startswith(("-", "#", "|"))
                       and bullet.group(4) == sealed)))
    return blocks


def derive_at(repo, fact, rev):
    if fact == "F1":
        return derive_axes(text(repo, rev, RECORD))
    if fact == "F2":
        return derive_capabilities(text(repo, rev, RECORD))
    if fact == "F3":
        return derive_gate_row(text(repo, rev, SKILL), gate_grounds(repo, rev)[1])["value"]
    if fact == "F4":
        return derive_pointer(record_section(text(repo, rev, RECORD)))
    if fact == "F5":
        return derive_provenance(repo, knowledge_population(
            repo, record_base(record_section(text(repo, rev, RECORD))), rev), rev)
    return derive_coverage(repo, knowledge_population(
        repo, record_base(record_section(text(repo, rev, RECORD))), rev), rev)


# ------------------------------------------------------------------ audit
def audit(repo, sealed=SEALED):
    record = record_section(worktree(repo, RECORD))
    skill = worktree(repo, SKILL)
    population = knowledge_population(repo, record_base(record), sealed)
    module_count, module_newest = gate_grounds(repo)
    tally = receipt_tally(repo, sealed)
    blocks = correction_blocks(repo, sealed)

    graded = {}
    for fact in FACT_ORDER:
        try:
            if fact == "F1":
                graded[fact] = dict(value=derive_axes(worktree(repo, RECORD)), ground=None)
            elif fact == "F2":
                graded[fact] = dict(value=derive_capabilities(worktree(repo, RECORD)), ground=None)
            elif fact == "F3":
                graded[fact] = dict(derive_gate_row(skill, module_newest), ground=None)
            elif fact == "F4":
                graded[fact] = dict(value=derive_pointer(record), ground=None)
            elif fact == "F5":
                graded[fact] = dict(value=derive_provenance(repo, population), ground=None)
            else:
                graded[fact] = dict(value=derive_coverage(repo, population), ground=None)
        except GroundAbsent as exc:
            graded[fact] = dict(value=None, ground=str(exc))

    def holds(fact):
        entry = graded[fact]
        if entry["ground"] is not None:
            return False
        if entry["value"] != FACT_VALUES[fact]:
            return False
        if fact == "F3":
            return (entry["arms"] == module_count
                    and NUM_WORDS.get(module_count) == entry["word"]
                    and entry["mentions"]
                    and entry["tally"] == tally)
        return True

    first = {}
    duplicates = []
    for block in blocks:
        if block["fact"] in first:
            duplicates.append(block)
        else:
            first[block["fact"]] = block

    mismatches = corrected = unbacked = 0
    findings = []
    for fact in FACT_ORDER:
        block = first.get(fact)
        if graded[fact]["ground"] is not None:
            mismatches += 1
            findings.append(f"SELFRECORD_R77_FINDING cheat {fact} detail={graded[fact]['ground']}")
            continue
        value = graded[fact]["value"]
        if block is None:
            if holds(fact):
                continue
            mismatches += 1
            findings.append(f"SELFRECORD_R77_FINDING mismatch {fact} derived={value}")
            continue
        if not block["valid"]:
            mismatches += 1
            findings.append(
                f"SELFRECORD_R77_FINDING mismatch {fact} detail=invalid correction block "
                f"(fixed shape, one prose line, dated, at the sealed revision)")
            continue
        try:
            old = derive_at(repo, fact, block["at"])
        except GroundAbsent as exc:
            unbacked += 1
            findings.append(f"SELFRECORD_R77_FINDING unbacked {fact} detail={exc}")
            continue
        if old != block["old"]:
            unbacked += 1
            findings.append(f"SELFRECORD_R77_FINDING unbacked {fact} derived_old={old}")
            continue
        if block["new"] == FACT_VALUES[fact] and holds(fact):
            corrected += 1
            continue
        mismatches += 1
        findings.append(
            f"SELFRECORD_R77_FINDING mismatch {fact} derived={value} stated_new={block['new']}")
    for block in duplicates:
        findings.append(f"SELFRECORD_R77_FINDING duplicate {block['fact']} "
                        f"detail=second block naming one fact is not a second correction")

    print(f"SELFRECORD_R77 claims={len(FACT_ORDER)} mismatches={mismatches} "
          f"corrected={corrected} unbacked={unbacked}")
    for line in findings:
        print(line)
    return int(bool(mismatches + unbacked + len(duplicates)))


# ------------------------------------------------------------------ selftest
def _write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _fixture_commit(root, message):
    check = subprocess.run(["git", "-C", str(root), "rev-parse", "--show-toplevel"],
                           check=True, capture_output=True)
    if os.path.realpath(check.stdout.decode().strip()) != os.path.realpath(root):
        raise CouldNotEvaluate("fixture repository root mismatch")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True, capture_output=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-q", "-m", message],
                   check=True, capture_output=True)
    return git(root, "rev-parse", "HEAD").decode().strip()


STALE_ROW = (
    "| Pre-report gate | gate: `python3 tools/pre-report-gate.py --repo . --round N --tip master` "
    "(eight arms, fixed order: selfdesc reconciler, newest-closure counter, receipt-pointer audit, "
    "worktree-landing check, round-scope counter, round-worktree cleanliness, arm 7 `round74-v2` "
    "composing `tools/round74-selfdesc-canon.py`, `tools/round74-receipt-claim-binding.py` and "
    "`tools/round74-province-host-drift.py`, and arm 8 `round75-instruments` composing "
    "`tools/round75-interpretation-pins.py`, `tools/round75-survivor-probe.py` and "
    "`tools/round75-append-accepted.py`; an absent module fails its arm closed, never vacuously "
    "green) | 0 iff all eight arms green and `uncommitted=0`, i.e. the line reads "
    "`PRE_REPORT round=<N> arms=8 failed=0 uncommitted=0`; 1 names every failed arm; 2 CLI misuse "
    "| `python3 tools/pre-report-gate.py --selftest` → `PRE_REPORT_SELFTEST pass=18 fail=0` "
    "| Removed temp fixtures only |")
GREEN_ROW = (
    "| Pre-report gate | gate: `python3 tools/pre-report-gate.py --repo . --round N --tip master` "
    "(nine arms, fixed order: selfdesc reconciler, newest-closure counter, receipt-pointer audit, "
    "worktree-landing check, round-scope counter, round-worktree cleanliness, arm 7 `round74-v2` "
    "composing `tools/round74-selfdesc-canon.py`, `tools/round74-receipt-claim-binding.py` and "
    "`tools/round74-province-host-drift.py`, arm 8 `round75-instruments` composing "
    "`tools/round75-interpretation-pins.py`, `tools/round75-survivor-probe.py` and "
    "`tools/round75-append-accepted.py`, and arm 9 `round77-instruments` composing "
    "`tools/round77-citation-baseline.py`, `tools/round77-append-registers.py` and "
    "`tools/round77-selfrecord-round76.py`; an absent module fails its arm closed, never vacuously "
    "green) | 0 iff all nine arms green and `uncommitted=0`, i.e. the line reads "
    "`PRE_REPORT round=<N> arms=9 failed=0 uncommitted=0`; 1 names every failed arm; 2 CLI misuse "
    "| `python3 tools/pre-report-gate.py --selftest` → `PRE_REPORT_SELFTEST pass=22 fail=0` "
    "(round-77 measurement, receipt `.ufo/waves/round-77/measured/after/gate-selftest.out`) "
    "| Removed temp fixtures only |")
GATE_MODULE_SOURCE = (
    '"""Fixture gate module (nine top-level arms)."""\n'
    'ARM_TIMEOUT = 600\n'
    'ARM_SPECS = [\n'
    '    ("selfdesc", ("round42-selfdesc-reconcile.py", "--repo", "{repo}")),\n'
    '    ("newest-closure", ("round69-newest-closure-counter.py", "--repo", "{repo}")),\n'
    '    ("receipt-audit", ("round68-receipt-pointer-audit.py", "--repo", "{repo}")),\n'
    '    ("worktree-landing", ("round67-worktree-landing-check.py", "--repo", "{repo}")),\n'
    '    ("round-scope", ("round73-round-scope-cases.py", "--repo", "{repo}")),\n'
    ']\n'
    'ARM_ORDER = [name for name, _ in ARM_SPECS] + ["round-clean", "round74-v2",\n'
    '              "round75-instruments", "round77-instruments"]\n')

FIXTURE_SCORECARD = """# kama-shokunin — SCORECARD

## Axes

Round-41 reconciliation anchors the table below; scores are the lane's last-declared assessment.

| Axis | Score | Evidence pointer (re-derivable at the measured commit) | Last change |
|---|---|---|---|
| **operability** | **8** | registry gate | round 1 |
| **freshness** | **8** | snapshot harness | round 2 |
| depth | **7** | `SKILL.md` | round 1 |
| coverage | **9** | corpus surface | round 10 |
| calibration | **7** | counters | round 40 |
| adjacency | **7** | cross-lane scope | round 1 |

## Capabilities — canonical list as of round 77

| Capability | What it can now do | Evidence pointer | First-working round |
|---|---|---|---|
{rows}

## Round 77 — baseline receipts bind, two registers account, the round-76 facts are graded (2026-11-04)

Frozen plan `plans/round-77-claims.md` (base `{{base}}`, freeze `7d60e2ab58866a0366937d61c9712483be57b36e`); work tip `{{worktip}}`;
receipts commit `0f56ad5a58866a0366937d61c9712483be57b36e`.

| Claim | Axis | Before → after (measured) | Counting command | Evidence |
|---|---|---|---|---|
| C1 — baseline receipts bind | operability | before exit 1; after exit 0 | `python3 tools/round77-citation-baseline.py --repo . --round 75` | receipt |

**Verdicts.** C1 and C2 verify on committed bytes with the frozen lines printed verbatim.

Axis harm check: operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7 — no
score dropped, no axis retired.

**Freeze divergence recorded.** The C3 plan bullet named the closure-sealed boundary without
naming the record-path set; the counter uses the inherited round-76 set and therefore derives
`work-tip = {{worktip8}}`. That is the divergence that produced the third correction; it is
documented in `corpus/lessons/round-77.md` §Mistakes 4.

Population at `rev={{sealed8}}`: sources registry 290 rows with the census exit 0
(S549 rejected as a duplicate, S550 admitted own-work); filtered knowledge entries 49 (two new);
gate `PRE_REPORT_SELFTEST pass=22 fail=0`.
"""

FIXTURE_SKILL = """# kama-shokunin — SKILL

| Capability | Invocation | Exit semantics | Selftest | Notes |
|---|---|---|---|---|
{row}
"""

FIXTURE_README = """# kama-shokunin corpus — index

Every entry cites its source. Coverage map and open gaps grow with rounds.

## Coverage map

| Entry | Covers | Round |
|---|---|---|
| `knowledge/endpoint-identity.md` | identity vs liveness decision table | 1 |
| `knowledge/receipt-tip-binding.md` | receipt-to-revision binding | 72 |
"""

FIXTURE_BASELINE_ENTRY = """source: S550 — own re-runnable round-77 baseline counter; mechanics held by S073 and S175.

# Baseline receipts bind to their introduction, not subsequent work

A `measured/before/` receipt binds by header ancestry plus byte identity at introduction and tip.
"""

FIXTURE_CUTOFF_ENTRY = """source: own-work — plans/round-77-claims.md (frozen C2 design); tools/append-only-audit.py carriage regions. No external source is asserted for lane policy.

# Independent register cutoffs do not authorize rotation

Each register's first addition is discovered independently with `--diff-filter=A`.
"""

CORRECTIONS_TEMPLATE = """# kama-shokunin corpus lesson — round 78

## Corrections

- `corrected F3` old=`gate=arms:8/word:eight/newest:round77-instruments/tally:18` new=`gate=arms:9/word:nine/newest:round77-instruments/tally:22` at=`{sealed}` date=`2026-11-04`
  The sealed row declared the retired eight-arm gate and the round-75 tally; the landed gate module carries nine arms with `round77-instruments` newest and the round-77 receipt prints `PRE_REPORT_SELFTEST pass=22 fail=0`.
- `corrected F4` old=`pointer=section:Mistakes 4` new=`pointer=section:Freeze divergences item 3` at=`{sealed}` date=`2026-11-04`
  The record's last pointer sentence named §Mistakes 4, which holds the L1 mutating-git breach; the C3 predicate/ruling divergence is §Freeze divergences item 3.
- `corrected F5` old=`provenance=missing:corpus/knowledge/register-cutoff-split.md` new=`provenance=missing:none` at=`{sealed}` date=`2026-11-04`
  The register-cutoff entry now carries an appended `source-correction:` line citing S073, whose added-path ground is the entry's introduction-discovery mechanics.
- `corrected F6` old=`coverage-map=missing:corpus/knowledge/baseline-receipt-binding.md,corpus/knowledge/register-cutoff-split.md` new=`coverage-map=missing:none` at=`{sealed}` date=`2026-11-04`
  Appended coverage-map rows index both round-77 entries in `corpus/README.md`; appended, so no existing line moves.
"""

POINTER_CORRECTION = (
    "\nFreeze-divergence pointer correction (2026-11-04): the C3 predicate/ruling divergence is\n"
    "documented in `corpus/lessons/round-77.md` §Freeze divergences item 3; the earlier\n"
    "§Mistakes 4 pointer named the L1 mutating-git breach and stays as filed history.\n")

SOURCE_CORRECTION_LINE = (
    "source-correction: S073 — git-log `--diff-filter` added-path selection "
    "(https://git-scm.com/docs/git-log, opened 2026-10-21, `corpus/SOURCES.md:85`) supplies the "
    "introduction-discovery mechanics this entry describes; correcting the earlier \"no external "
    "source is asserted\" scoping, appended 2026-11-04.\n")

README_ADDITION = """
## Coverage map — round 78 addition (C1 self-record repairs)

Appended rather than inserted, so no existing line moves (the rule the round-10 addition states).

| Entry | Covers | Round |
|---|---|---|
| `corpus/knowledge/baseline-receipt-binding.md` | Round-77 baseline receipt introduction ancestry and introduction-to-tip byte identity | 78 |
| `corpus/knowledge/register-cutoff-split.md` | Round-77 independent register introductions, exclusive carriage classes and rotation rejection | 78 |
"""


def build_fixture(root):
    subprocess.run(["git", "-C", str(root), "init", "-q"], check=True, capture_output=True)
    if os.path.realpath(git(root, "rev-parse", "--show-toplevel").decode().strip()) \
            != os.path.realpath(root):
        raise CouldNotEvaluate("fixture repository root mismatch")
    rows = "\n".join(
        f"| cap-{index:02d} | filler capability {index} | `tools/filler{index}.py` | {10 + index} |"
        for index in range(33))
    rows += "\n| selfrecord-round76 | Re-derive six sealed round-76 facts | " \
            "`tools/round77-selfrecord-round76.py` | 77 |"
    _write(root / RECORD, FIXTURE_SCORECARD.format(rows=rows))
    _write(root / SKILL, FIXTURE_SKILL.format(row=STALE_ROW))
    _write(root / GATE_MODULE, GATE_MODULE_SOURCE)
    _write(root / TALLY_RECEIPT, "# rev=fixture\nPRE_REPORT_SELFTEST pass=22 fail=0\nexit=0\n")
    _write(root / "corpus/README.md", FIXTURE_README)
    base = _fixture_commit(root, "fixture base")
    _write(root / RECORD, FIXTURE_SCORECARD.format(rows=rows)
           .replace("%BASE%", base).replace("{base}", base)
           .replace("{worktip}", base).replace("{worktip8}", base[:8])
           .replace("{sealed8}", base[:8]))
    _write(root / "corpus/knowledge/baseline-receipt-binding.md", FIXTURE_BASELINE_ENTRY)
    _write(root / "corpus/knowledge/register-cutoff-split.md", FIXTURE_CUTOFF_ENTRY)
    sealed = _fixture_commit(root, "fixture sealed round-77 record")
    return base, sealed


def apply_repairs(root, sealed):
    _write(root / SKILL, FIXTURE_SKILL.format(row=GREEN_ROW))
    scorecard = (root / RECORD).read_text(encoding="utf-8")
    (root / RECORD).write_text(scorecard + POINTER_CORRECTION, encoding="utf-8")
    entry = root / "corpus/knowledge/register-cutoff-split.md"
    entry.write_text(entry.read_text(encoding="utf-8") + SOURCE_CORRECTION_LINE, encoding="utf-8")
    readme = root / "corpus/README.md"
    readme.write_text(readme.read_text(encoding="utf-8") + README_ADDITION, encoding="utf-8")
    _write(root / CORRECTIONS, CORRECTIONS_TEMPLATE.format(sealed=sealed))


def run_selftest(repo, work):
    root = Path(work).resolve() / "selfrecord-r77-fixture"
    if root.exists():
        raise CouldNotEvaluate(f"fixture directory already exists: {root}")
    root.mkdir(parents=True)
    passed = failed = 0

    def check(name, condition):
        nonlocal passed, failed
        passed += bool(condition)
        failed += not condition
        print(f"SELFRECORD_R77_SELFTEST {name} {'PASS' if condition else 'FAIL'}")

    try:
        _, sealed = build_fixture(root)

        def probe():
            stream = io.StringIO()
            with redirect_stdout(stream):
                try:
                    code = audit(root, sealed)
                except CouldNotEvaluate as exc:
                    print(f"SELFRECORD_R77 CouldNotEvaluate: {exc}")
                    code = 2
            return code, stream.getvalue()

        def summary(output):
            return output.splitlines()[0] if output.splitlines() else ""

        # base-red: the sealed-analog fixture with no repairs is red on all four stale facts.
        code, output = probe()
        check("base-red", code == 1 and summary(output) ==
              "SELFRECORD_R77 claims=6 mismatches=4 corrected=0 unbacked=0"
              and all(f"SELFRECORD_R77_FINDING mismatch {fact}" in output
                      for fact in ("F3", "F4", "F5", "F6")))

        apply_repairs(root, sealed)
        code, output = probe()
        check("green-control", code == 0 and summary(output) ==
              "SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0")

        # cheat-constant: with F3's ground row deleted the counter must be red naming cheat,
        # and a constant printer cannot produce a red-with-findings verdict.
        (root / SKILL).write_text(FIXTURE_SKILL.format(row="| Keeper | keeps the file non-empty | 0 | ok | ok |"),
                                  encoding="utf-8")
        code, output = probe()
        cheat = root / "cheat.py"
        cheat.write_text('print("SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0")\n',
                         encoding="utf-8")
        result = subprocess.run([sys.executable, str(cheat), "--repo", str(root)],
                                capture_output=True, text=True)
        check("cheat-constant",
              code == 1 and "SELFRECORD_R77_FINDING cheat F3" in output
              and not (result.returncode == 1 and "SELFRECORD_R77_FINDING" in result.stdout))
        (root / SKILL).write_text(FIXTURE_SKILL.format(row=GREEN_ROW), encoding="utf-8")

        # stale-uncorrected: one sealed value reverted, no correction block change.
        (root / SKILL).write_text(FIXTURE_SKILL.format(row=STALE_ROW), encoding="utf-8")
        code, output = probe()
        check("stale-uncorrected",
              code == 1 and "SELFRECORD_R77_FINDING mismatch F3" in output
              and summary(output) == "SELFRECORD_R77 claims=6 mismatches=1 corrected=3 unbacked=0")
        (root / SKILL).write_text(FIXTURE_SKILL.format(row=GREEN_ROW), encoding="utf-8")

        # correction-wrong-value: the block's stated new value does not re-derive.
        corrections = root / CORRECTIONS
        original = corrections.read_text(encoding="utf-8")
        wrong = original.replace("new=`gate=arms:9/word:nine/newest:round77-instruments/tally:22`",
                                 "new=`gate=arms:10/word:ten/newest:round77-instruments/tally:22`")
        corrections.write_text(wrong, encoding="utf-8")
        code, output = probe()
        check("correction-wrong-value",
              code == 1 and "SELFRECORD_R77_FINDING mismatch F3" in output
              and "unbacked F3" not in output)
        corrections.write_text(original, encoding="utf-8")

        # unbacked: the block's old value re-derives nowhere.
        wrong = original.replace("old=`gate=arms:8/word:eight/newest:round77-instruments/tally:18`",
                                 "old=`gate=arms:7/word:seven/newest:round75-instruments/tally:11`")
        corrections.write_text(wrong, encoding="utf-8")
        code, output = probe()
        check("unbacked", code == 1 and "SELFRECORD_R77_FINDING unbacked F3" in output
              and summary(output) == "SELFRECORD_R77 claims=6 mismatches=0 corrected=3 unbacked=1")
        corrections.write_text(original, encoding="utf-8")

        # pointer-wrong: the record's LAST divergence pointer sentence names §Mistakes 4.
        scorecard = (root / RECORD).read_text(encoding="utf-8")
        (root / RECORD).write_text(
            scorecard + "\nLater filing: the divergence is documented in "
            "`corpus/lessons/round-77.md` §Mistakes 4.\n", encoding="utf-8")
        code, output = probe()
        check("pointer-wrong", code == 1 and "SELFRECORD_R77_FINDING mismatch F4" in output)
        (root / RECORD).write_text(scorecard, encoding="utf-8")

        # duplicate-correction: a second valid block naming one fact is red, counted once.
        again = original.replace("## Corrections\n", "## Corrections\n", 1)
        second = again.rstrip("\n") + (
            "\n- `corrected F3` old=`gate=arms:8/word:eight/newest:round77-instruments/tally:18` "
            "new=`gate=arms:9/word:nine/newest:round77-instruments/tally:22` "
            f"at=`{sealed}` date=`2026-11-04`\n"
            "  Duplicate filing of the same correction; one fact, one correction.\n")
        corrections.write_text(second, encoding="utf-8")
        code, output = probe()
        check("duplicate-correction",
              code == 1 and "SELFRECORD_R77_FINDING duplicate F3" in output
              and summary(output) == "SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0")
    finally:
        shutil.rmtree(root, ignore_errors=True)
    print(f"SELFRECORD_R77_SELFTEST pass={passed} fail={failed}")
    return int(bool(failed))


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="round78-selfrecord-round77.py",
        description="Grade the round-77 self-record's six declared facts at the live tree.")
    parser.add_argument("--repo", default=".", help="repository to grade (default: .)")
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--work", help="scratch root for selftest fixtures (default: TMPDIR)")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 2
    try:
        repo = Path(args.repo).resolve()
        if args.selftest:
            owned = None
            if not args.work:
                owned = tempfile.mkdtemp(prefix="selfrecord-r77-root-",
                                         dir=os.environ.get("TMPDIR") or tempfile.gettempdir())
            try:
                return run_selftest(repo, args.work or owned)
            finally:
                if owned:
                    shutil.rmtree(owned, ignore_errors=True)
        return audit(repo)
    except (CouldNotEvaluate, OSError, UnicodeError, ValueError,
            subprocess.CalledProcessError) as exc:
        print(f"SELFRECORD_R77 CouldNotEvaluate: {exc}")
        return 2


if __name__ == "__main__":
    sys.exit(main())
