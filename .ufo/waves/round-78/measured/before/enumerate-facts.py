#!/usr/bin/env python3
"""round-78 pre-freeze fact enumeration — wave evidence, not the claim counter.

Derives the six declared facts of the round-77 self-record from the tree at
the base revision and prints one line per fact plus a summary line. The claim
counter (`tools/round78-selfrecord-round77.py`, built by this round) must print
the frozen `SELFRECORD_R77 claims=6 mismatches=0 corrected=4 unbacked=0` line;
this script only establishes, before the freeze, which facts are stale and how
many corrections the round owes.

Run from the lane root:
  python3 .ufo/waves/round-78/measured/before/enumerate-facts.py
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

BASE = "c62ffd3aea930b98375f805cc3dfb821a703148b"
R77_BASE = "cc6e1d3cf202ee3e17cd07f42fc63d2dca5f3bb7"
SEALED = "6c1550a14babaca092cfcc3106f792d695652200"
DECLARED_SCORES = {
    "operability": 8,
    "freshness": 8,
    "depth": 7,
    "coverage": 9,
    "calibration": 7,
    "adjacency": 7,
}
DECLARED_CAP_ROWS = 34
DECLARED_CAP_MAX_ROUND = 77


def git(*args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(REPO), *args], capture_output=True, text=True, check=True
    ).stdout


REPO = Path(__file__).resolve().parents[5]
FACTS: list[tuple[str, bool, str]] = []


def record(fact: str, ok: bool, detail: str) -> None:
    FACTS.append((fact, ok, detail))
    print(f"FACT {fact} {'ok' if ok else 'stale'} derived={detail}")


def scores() -> None:
    text = (REPO / "SCORECARD.md").read_text(encoding="utf-8")
    section = text.split("## Axes", 1)[1].split("### Historical axes table", 1)[0]
    got = {}
    for line in section.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip().strip("*") for c in line.strip("|").split("|")]
        if len(cells) < 2 or cells[0] not in DECLARED_SCORES:
            continue
        try:
            got[cells[0]] = int(cells[1].strip("*"))
        except ValueError:
            continue
    ok = got == DECLARED_SCORES
    vals = "/".join(f"{a}:{got.get(a, '?')}" for a in DECLARED_SCORES)
    record("F1-scores", ok, f"scores={vals}")


def capabilities() -> None:
    text = (REPO / "SCORECARD.md").read_text(encoding="utf-8")
    canon = text.split("## Capabilities", 1)[1].split("## Saturation", 1)[0]
    rows, rounds = [], []
    for line in canon.splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if not cells or cells[0].lower() == "capability":
            continue
        rows.append(cells)
        try:
            rounds.append(int(cells[3]))
        except (IndexError, ValueError):
            rounds.append(-1)
    ok = len(rows) == DECLARED_CAP_ROWS and (max(rounds) if rounds else -1) == DECLARED_CAP_MAX_ROUND
    record("F2-capability-count", ok, f"capabilities={len(rows)}/max-round={max(rounds) if rounds else '?'}")


def gate_shape() -> None:
    skill = (REPO / "SKILL.md").read_text(encoding="utf-8").splitlines()
    row = next((l for l in skill if l.startswith("| Pre-report gate |")), None)
    if row is None:
        record("F3-gate-shape", False, "gate-row-missing")
        return
    cells = [c.strip() for c in row.strip("|").split("|")]
    src = (REPO / "tools/pre-report-gate.py").read_text(encoding="utf-8")
    specs = re.findall(r'\(\s*"([a-z0-9-]+)",\s*\(', src.split("ARM_SPECS = [", 1)[1].split("\n]", 1)[0])
    extra = re.search(r"ARM_ORDER = \[name for name, _ in ARM_SPECS\] \+ \[(.*?)\]", src, re.S)
    arms = specs + (re.findall(r'"([a-z0-9-]+)"', extra.group(1)) if extra else [])
    words = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
             "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12}
    token = re.search(r"arms=(\d+)", cells[2] if len(cells) > 2 else "")
    word = re.search(r"\((one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve) arms", cells[1])
    tally = re.search(r"pass=(\d+)", cells[3] if len(cells) > 3 else "")
    receipt = REPO / ".ufo/waves/round-77/measured/after/gate-selftest.out"
    want_tally = None
    if receipt.exists():
        m = re.search(r"PRE_REPORT_SELFTEST pass=(\d+) fail=0", receipt.read_text(encoding="utf-8"))
        want_tally = m.group(1) if m else None
    newest = arms[-1] if arms else None
    ok = (
        len(arms) > 0
        and token is not None
        and int(token.group(1)) == len(arms)
        and word is not None
        and words[word.group(1)] == len(arms)
        and newest is not None
        and newest in cells[1]
        and want_tally is not None
        and tally is not None
        and tally.group(1) == want_tally
    )
    record(
        "F3-gate-shape",
        ok,
        f"gate=arms:{token.group(1) if token else '?'}/word:{word.group(1) if word else '?'}"
        f"/newest:{newest}/tally:{tally.group(1) if tally else '?'}"
        f" (module arms={len(arms)}, newest named={bool(newest and newest in cells[1])}, receipt tally={want_tally})",
    )


def closure_pointer() -> None:
    text = (REPO / "SCORECARD.md").read_text(encoding="utf-8")
    hits = [l for l in text.splitlines() if "documented in `corpus/lessons/round-77.md`" in l]
    line = hits[-1] if hits else None
    lesson = (REPO / "corpus/lessons/round-77.md").read_text(encoding="utf-8")
    has_section = "## Freeze divergences" in lesson
    item3 = re.search(r"\n3\. \*\*C3 correction scope", lesson) is not None
    pointed = None
    if line is not None:
        m = re.search(r"§([^.\n]+)", line)
        pointed = m.group(1).strip() if m else None
    ok = pointed is not None and pointed.startswith("Freeze divergences item 3") and has_section and item3
    record("F4-closure-pointer", ok, f"pointer=section:{pointed} (lesson section={has_section}, item3={item3})")


def round77_entries() -> list[str]:
    out = git("log", "--diff-filter=A", "--format=", "--name-only", f"{R77_BASE}..{SEALED}", "--", "corpus/knowledge/")
    return [l.strip() for l in out.splitlines() if l.strip().startswith("corpus/knowledge/")]


def knowledge_provenance() -> None:
    entries = round77_entries()
    missing = []
    for rel in entries:
        head = "\n".join((REPO / rel).read_text(encoding="utf-8").splitlines()[:8])
        src = [l for l in head.splitlines() if l.startswith(("source:", "source-correction:"))]
        if not any(re.search(r"\bS\d{3,}\b", l) for l in src):
            missing.append(rel)
    record(
        "F5-knowledge-provenance",
        not missing,
        f"provenance=missing:{','.join(missing) if missing else 'none'}",
    )


def coverage_map() -> None:
    entries = round77_entries()
    readme = (REPO / "corpus/README.md").read_text(encoding="utf-8")
    unmapped = [rel for rel in entries if not re.search(r"^\| `" + re.escape(rel) + r"`", readme, re.M)]
    record(
        "F6-coverage-map",
        not unmapped,
        f"coverage-map=missing:{','.join(unmapped) if unmapped else 'none'}",
    )


def main() -> int:
    scores()
    capabilities()
    gate_shape()
    closure_pointer()
    knowledge_provenance()
    coverage_map()
    stale = sum(1 for _, ok, _ in FACTS if not ok)
    print(f"SELFRECORD_R77_ENUM claims={len(FACTS)} stale={stale} corrected=0")
    return 0 if stale == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
