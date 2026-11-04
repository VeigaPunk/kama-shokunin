#!/usr/bin/env python3
"""Round-75 C1: executable interpretation boundaries and their reversed readings.

Only fixtures and mutated copies under --work are written. Imports suppress
bytecode. P1 reuses the r42 parser through r74; P2 runs the full r74 CLI,
including its frozen base leg. --json adds machine-readable measurements after
the summary. --keep retains work; otherwise the owned work directory is removed.
The selftest also runs a copied counter with P1's declared value changed to the
mutant's value: this must escape and return 1, not certify itself green.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

PREDICATE = "`python3 tools/round75-interpretation-pins.py --repo <lane>` prints one `INTERPRETATION_PINS pins=2 declared=2 killed=2 escaped=0` line and exits 0 only when each of the lane's two routed interpretation debts is bound to a boundary fixture whose declared reading the committed module produces and whose reversed reading a mutated copy of that module is caught producing — P1 older-demonstrated: a capability table older than the canonical round that carries a name the canon lacks contributes no name to `total` (an older table with two extra names leaves `total` at the canonical row count) and the all-tables-union mutant scores above it; P2 revision-mention context: a paragraph whose only 40-hex token sits in a `recorded at` clause and is not introduced by `rev`/`revision` names no revision (the `nc2_recorded_at_hex` paragraph grades clean, exit 0) and the any-hex mutant reports `stale-revision` there — it exits 1 naming each `INTERPRETATION_PINS_FINDING <pin>` with the declared and observed values and 2 on could-not-evaluate (a module absent, a fixture build failure, CLI misuse)."

TOOLS = Path(__file__).resolve().parent
DECLARED_TOTAL = 3
MODULES = (
    "round42-selfdesc-reconcile.py",
    "round72-receipt-tip-binding.py",
    "round73-receipt-claim-binding.py",
    "round74-selfdesc-canon.py",
    "round74-receipt-claim-binding.py",
)
# Exact replacements from the frozen control's C1_MUTANTS entries.
MUTANTS = {
    "c1_f1b_older_union": (
        "round74-selfdesc-canon.py",
        "    total = set(canon_names) | demonstrated\n",
        "    _older: set = set()\n"
        "    for _r, _i, _k in tables:\n"
        "        if _r < canon_round:\n"
        "            _older.update(_names_below(lines, _i, mod))\n"
        "    total = set(canon_names) | demonstrated | _older\n",
    ),
    "c1_f2c_literal_hex": (
        "round74-receipt-claim-binding.py",
        'REVISION_RE = re.compile(r"\\brev(?:ision)?\\s+([0-9a-fA-F]{40})\\b", re.I)',
        'REVISION_RE = re.compile(r"(?<![0-9a-fA-F])([0-9a-fA-F]{40})(?![0-9a-fA-F])", re.I)',
    ),
}


class CouldNotEvaluate(RuntimeError):
    """Missing inputs or failed fixture construction, never a scored finding."""


def load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise CouldNotEvaluate(f"cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    previous = sys.dont_write_bytecode
    sys.dont_write_bytecode = True
    try:
        spec.loader.exec_module(module)
    finally:
        sys.dont_write_bytecode = previous
    return module


def run(command: list[str], work: Path) -> subprocess.CompletedProcess:
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", TMPDIR=str(work))
    return subprocess.run(command, cwd=work, env=env, capture_output=True,
                          text=True, timeout=300)


def copy_modules(destination: Path) -> None:
    destination.mkdir(parents=True)
    for name in MODULES:
        source = TOOLS / name
        if not source.is_file():
            raise CouldNotEvaluate(f"module absent beside counter: {source}")
        shutil.copyfile(source, destination / name)


def mutate(directory: Path, name: str) -> None:
    filename, old, new = MUTANTS[name]
    path = directory / filename
    source = path.read_text(encoding="utf-8")
    if source.count(old) != 1:
        raise CouldNotEvaluate(f"{name}: expected exactly one frozen mutation anchor")
    path.write_text(source.replace(old, new, 1), encoding="utf-8")


def evaluate(pins: list[dict]) -> dict:
    declared = sum(pin["observed"] == pin["declared"] for pin in pins)
    killed = sum(pin["mutant"] != pin["declared"] and pin["mutant_ok"] for pin in pins)
    escaped = len(pins) - killed
    return {"pins": len(pins), "declared": declared, "killed": killed,
            "escaped": escaped, "measurements": pins,
            "exit": 0 if declared == killed == len(pins) else 1}


def grade(work: Path) -> dict:
    work.mkdir(parents=True)
    mutants = work / "mutant-tools"
    copy_modules(mutants)
    for name in MUTANTS:
        mutate(mutants, name)

    canon = load(TOOLS / "round74-selfdesc-canon.py", "pins_pristine_canon")
    changed = load(mutants / "round74-selfdesc-canon.py", "pins_mutant_canon")
    # The r74 fixture's three canon names plus two strictly older-only names.
    older = (canon.BOLD71.replace("round 71", "round 60")
             .replace("**Capabilities — canonical list as of round 60**",
                      "### Capabilities demonstrated in round 60"))
    older += ("| older-one | Older only | `old-one` | 60 |\n"
              "| older-two | Older only | `old-two` | 60 |\n")
    scorecard = work / "SCORECARD.md"
    scorecard.write_text(canon.C1_HEAD + canon.BOLD71 + "\n" + older,
                         encoding="utf-8")
    text = scorecard.read_text(encoding="utf-8")
    p1 = canon.resolve(text, canon._load_r42())["total"]
    m1 = changed.resolve(text, changed._load_r42())["total"]

    binding = load(TOOLS / "round74-receipt-claim-binding.py", "pins_pristine_binding")
    fixture = binding.base_mod._Fixture(str(work), "nc2_recorded_at_hex")
    # The inherited helper asserts its own git toplevel before any commit.
    fixture.write("tools/counter.py", "# fixture instrument\n")
    fixture.write("plans/round-74-claims.md", "# fixture plan\n")
    c0 = fixture.commit("base")
    receipt = ".ufo/waves/round-74/r.out"
    fixture.write(receipt, f"# rev={c0}\nverdict: green\n")
    c1 = fixture.commit("receipt")
    binding._record(fixture, 74,
                    f"probe recorded at {c1} naming `r.out` (content id, not a run revision)\n")
    tip = fixture.commit("record content id, not a revision")
    results = []
    for script in (TOOLS / MODULES[-1], mutants / MODULES[-1]):
        command = [sys.executable, str(script), "--repo", fixture.path,
                   "--round", "74", "--tip", tip]
        proc = run(command, work)
        if proc.returncode not in (0, 1):
            raise CouldNotEvaluate(f"P2 command {command!r}: exit={proc.returncode} "
                                   f"{proc.stdout} {proc.stderr}")
        results.append({"command": command, "exit": proc.returncode,
                        "stdout": proc.stdout, "stderr": proc.stderr})
    pristine, mutant = results
    return evaluate([
        {"pin": "P1-older-demonstrated", "declared": DECLARED_TOTAL,
         "observed": p1, "mutant": m1, "mutant_ok": m1 == 5,
         "fixture": str(scorecard), "mutant_name": "c1_f1b_older_union"},
        {"pin": "P2-revision-mention-context", "declared": 0,
         "observed": pristine["exit"], "mutant": mutant["exit"],
         "mutant_ok": mutant["exit"] == 1 and
                       "RECEIPT_CLAIM_V2_FINDING stale-revision " in mutant["stdout"],
         "mutant_name": "c1_f2c_literal_hex", "runs": results},
    ])


def emit(document: dict, as_json: bool = False) -> None:
    print("INTERPRETATION_PINS pins={pins} declared={declared} killed={killed} "
          "escaped={escaped}".format(**document))
    for pin in document["measurements"]:
        if (pin["observed"] != pin["declared"] or
                pin["mutant"] == pin["declared"] or not pin["mutant_ok"]):
            print("INTERPRETATION_PINS_FINDING {pin} declared={declared} "
                  "mutant={mutant} observed={observed} mutant_ok={mutant_ok}".format(**pin))
    if as_json:
        print(json.dumps(document, sort_keys=True))


def plan_predicate(repo: Path) -> str:
    section = False
    body = []
    for line in (repo / "plans/round-75-claims.md").read_text(encoding="utf-8").splitlines():
        if line.startswith("## C1 "):
            section = True
        elif section and line.startswith("## "):
            break
        elif section and line.startswith("> "):
            body.append(line[2:])
        elif body:
            break
    return " ".join(body)


def selftest(repo: Path, work: Path, as_json: bool) -> int:
    clean = grade(work / "clean")
    emit(clean, as_json)
    variants = work / "cheat-tools"
    copy_modules(variants)
    source = Path(__file__).read_text(encoding="utf-8")
    anchor = "DECLARED_TOTAL = 3\n"
    if source.count(anchor) != 1:
        raise CouldNotEvaluate("cheat counter anchor is not unique")
    variant = variants / Path(__file__).name
    variant.write_text(source.replace(anchor, "DECLARED_TOTAL = 5\n", 1), encoding="utf-8")
    command = [sys.executable, str(variant), "--repo", str(repo),
               "--work", str(work / "cheat-work")]
    cheat = run(command, work)
    cheat_ok = (cheat.returncode == 1 and
                "INTERPRETATION_PINS pins=2 declared=1 killed=1 escaped=1" in cheat.stdout and
                "INTERPRETATION_PINS_FINDING P1-older-demonstrated declared=5 mutant=5" in cheat.stdout)
    arms = [("predicate", plan_predicate(repo) == PREDICATE),
            ("declared-and-kill", clean["exit"] == 0), ("cheat-escaped", cheat_ok)]
    for name, ok in arms:
        print(f"INTERPRETATION_PINS_ARM {name} {'ok' if ok else 'FAIL'}")
    print(f"INTERPRETATION_PINS_CHEAT exit={cheat.returncode}")
    print(cheat.stdout, end="")
    if cheat.stderr:
        print(cheat.stderr, file=sys.stderr, end="")
    if as_json:
        print(json.dumps({"cheat_command": command, "cheat_exit": cheat.returncode,
                          "cheat_stdout": cheat.stdout, "cheat_stderr": cheat.stderr}))
    failed = sum(not ok for _, ok in arms)
    print(f"INTERPRETATION_PINS_SELFTEST pass={len(arms) - failed} fail={failed}")
    return 1 if failed else 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--work", help="absent or empty owned work directory")
    parser.add_argument("--keep", action="store_true")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    work = None
    try:
        repo = Path(args.repo).expanduser().resolve()
        if not repo.is_dir():
            raise CouldNotEvaluate(f"repo is not a directory: {repo}")
        if args.work:
            candidate = Path(args.work).expanduser().resolve()
            if candidate.exists() and (not candidate.is_dir() or any(candidate.iterdir())):
                raise CouldNotEvaluate(f"--work must be absent or empty: {candidate}")
            candidate.mkdir(parents=True, exist_ok=True)
            work = candidate
        else:
            work = Path(tempfile.mkdtemp(prefix="interpretation-pins-",
                                         dir=os.environ.get("TMPDIR")))
        if args.selftest:
            return selftest(repo, work, args.json)
        document = grade(work / "pins")
        emit(document, args.json)
        return document["exit"]
    except Exception as exc:
        # Imported fixture helpers have distinct exception classes. At this CLI
        # boundary any inability to construct/execute the experiment is exit 2.
        print(f"INTERPRETATION_PINS could-not-evaluate: {exc}")
        return 2
    finally:
        if work is not None and not args.keep:
            shutil.rmtree(work)


if __name__ == "__main__":
    sys.exit(main())
