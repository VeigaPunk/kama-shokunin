#!/usr/bin/env python3
"""Build C1 (selfrecord) fixture repos under $S/fixtures/c1.

Scenarios:
  good              three valid corrections at=sealed        -> pristine exit 0
  ancestor-at       three corrections at=<middle commit>     -> pristine exit 1 (at-not-sealed)
  garbage-on-fresh  good + bogus F1 correction block         -> pristine exit 1 (unbacked=1, mismatches=0)
  outside-container corrections under "## Notes", no "## Corrections" heading -> probes container scope
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(sys.argv[1])

SCORECARD = """# SCORECARD

## Axes

| Axis | Score | Evidence |
|---|---|---|
| **operability** | **8** | x |
| **freshness** | **8** | x |
| **depth** | **7** | x |
| **coverage** | **9** | x |
| **calibration** | **7** | x |
| **adjacency** | **7** | x |

## Round 79 — fixture

| Claim | Axis | Before → after (measured) | Counting command | Verdict |
|---|---|---|---|---|
| C1 — fixture | calibration | `SELFRECORD_R78 claims=6 mismatches=0` | `python3 tools/x.py` | **verified** |
| C2 — fixture | operability | `ARM_ORDER` 9 arms, `PRE_REPORT_SELFTEST pass=26 fail=0` | `python3 tools/pre-report-gate.py --selftest` | **verified** |
"""

LOG = """# LOG

## Round 79 — fixture

Three claims, three distinct axes, all verified on their receipts.
"""

SOURCES = ("# SOURCES\n\n| id | source |\n|---|---|\n"
           + "".join(f"| S{i:03d} | fixture |\n" for i in range(1, 4)))

SPEC = json.dumps({"items": [
    {"role": "executor"}, {"role": "executor"}, {"role": "scribe"},
    {"role": "reviewer"}, {"role": "critic"}, {"role": "mutation-tester"}]})

GATE = "PRE_REPORT round=79 arms=10 failed=1 uncommitted=0\n"
SELFTEST = "PRE_REPORT_SELFTEST pass=22 fail=0\n"

FILES = {
    "SCORECARD.md": SCORECARD,
    "LOG.md": LOG,
    "corpus/SOURCES.md": SOURCES,
    "corpus/knowledge/a.md": "a\n",
    "corpus/knowledge/b.md": "b\n",
    "corpus/knowledge/engine-sides.md": "filtered\n",
    ".ufo/waves/round-79/w1-spec.json": SPEC,
    ".ufo/waves/round-79/measured/after/c2-gate.out": GATE,
    ".ufo/waves/round-79/measured/before/c2-gate-selftest.out": SELFTEST,
}


def run(root, *args):
    proc = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"git {' '.join(args)} failed: {proc.stderr}")
    return proc.stdout


def commit(root, message):
    run(root, "add", "-A")
    run(root, "commit", "-q", "-m", message)
    return run(root, "rev-parse", "HEAD").strip()


def lesson(at, heading="Corrections"):
    return f"""# round-80 fixture lesson

## {heading}

`corrected F4 old=c2=verified new=c2=not-verified:failed=1 at={at} date=2026-11-04`

`corrected F5 old=before-selftest=pass=26 new=before-selftest=pass=22 at={at} date=2026-11-04`

`corrected F6 old=log=all-verified new=log=c2-not-verified at={at} date=2026-11-04`
"""


def build(name, at_mode, extra=None, heading="Corrections"):
    root = ROOT / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    run(root, "init", "-q")
    run(root, "config", "user.name", "fixture")
    run(root, "config", "user.email", "fixture@example.invalid")
    run(root, "config", "commit.gpgsign", "false")
    for path, text in FILES.items():
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    sealed = commit(root, "sealed")
    if at_mode == "sealed":
        at = sealed
    elif at_mode == "middle":
        (root / "NOTES.md").write_text("middle\n")
        at = commit(root, "middle")
    else:
        raise SystemExit(f"bad at_mode {at_mode}")
    text = lesson(at, heading)
    if extra is not None:
        text = text + extra.format(sealed=sealed)
    lesson_path = root / "corpus/lessons/round-80.md"
    lesson_path.parent.mkdir(parents=True, exist_ok=True)
    lesson_path.write_text(text)
    tip = commit(root, "lesson")
    return {"repo": str(root), "sealed": sealed, "tip": tip, "at": at}


index = {
    "good": build("good", "sealed"),
    "ancestor-at": build("ancestor-at", "middle"),
    "garbage-on-fresh": build(
        "garbage-on-fresh", "sealed",
        "\n`corrected F1 old=lowest-axis=calibration:7 new=lowest-axis=calibration:9 "
        "at={sealed} date=2026-11-04`\n"),
    "outside-container": build("outside-container", "sealed", heading="Notes"),
}
(ROOT / "index.json").write_text(json.dumps(index, indent=2) + "\n")
print(json.dumps(index, indent=2))
