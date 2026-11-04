#!/usr/bin/env python3
"""round82-late-delta.py - round-82 C2 (operability): the late register's round-82 delta.

PREDICATE (frozen: plans/round-82-claims.md section C2):

    `python3 tools/round82-late-delta.py --repo <lane> --round 82` prints one `LATE_DELTA
    round=82 base=<12-hex> population=<p> carried=<c> new=<n> bad=0` line and exits 0 only when
    the committed `registry/append-only-late.tsv` at the tip carries, for every undeclared
    deletion line of every event ancestral to the round's base that neither frozen register
    accepts, exactly one row whose five data cells equal the frozen generator's
    (`tools/round81-late-rows.py generate`) output; a row present at the base revision keeps its
    base-revision bytes unchanged (`carried`), a row first introduced by this round carries a
    note naming round 82 as the accepting round with an accepting round greater than the
    deletion round (`new`), and a missing, extra, duplicated, cell-mismatched or mis-noted row is
    a `bad` finding; it exits 1 naming each.

Why a delta and not the round-81 `--check`: the round-81 register was written whole by one round;
a later round must append its own rows without rewriting the rows an earlier round introduced
(`registry/append-only-late.tsv` records WHICH round accepted what). The generator is the frozen
round-81 module, imported, not re-implemented.

Usage: round82-late-delta.py --repo DIR --round 82 [--base REV] [--to REV] [--late FILE]
       [--audit-json FILE] [--json] | --selftest

Exit: 0 every population row is carried or newly accepted; 1 at least one bad row; 2
could-not-evaluate.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path

LATE = "registry/append-only-late.tsv"
PLAN = "plans/round-{round}-claims.md"
BASE_RE = re.compile(r"Base revision `([0-9a-f]{40})`")
NOTE_RE = re.compile(r"round-([0-9]+)\s+accepts\s+round-([0-9]+)\b")
HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
GENERATOR = "tools/round81-late-rows.py"


class CouldNotEvaluate(Exception):
    pass


def load_generator(repo: Path):
    path = repo / GENERATOR
    if not path.exists():
        raise CouldNotEvaluate(f"{GENERATOR} is absent")
    spec = importlib.util.spec_from_file_location("late_rows_generator", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    for name in ("audit", "generate", "frozen_covered"):
        if not callable(getattr(module, name, None)):
            raise CouldNotEvaluate(f"{GENERATOR} does not export {name}()")
    return module


def git(repo: Path, *args):
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise CouldNotEvaluate(f"git {' '.join(args)}: {proc.stderr.strip()[:200]}")
    return proc.stdout


def show(repo: Path, rev: str, path: str):
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True)
    return proc.stdout if proc.returncode == 0 else None


def parse_rows(text, source):
    if text is None:
        return None
    lines = text.splitlines()
    if not lines or lines[0] != HEADER:
        raise CouldNotEvaluate(f"{source}: header is not the late-register header")
    rows = []
    for number, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 6:
            raise CouldNotEvaluate(f"{source} line {number}: {len(cells)} cells, expected 6")
        rows.append((tuple(cells), number))
    return rows


def check(want, have, base_rows, round_number, base):
    """want: generator rows; have: [(cells, line)] tip; base_rows: [(cells, line)] at the base.

    Returns (bad, carried, new, findings)."""
    findings = []
    base_by_key = {row[0][:3]: row[0] for row in (base_rows or [])}
    have_by_key = {}
    bad = 0
    for cells, number in have or []:
        key = cells[:3]
        if key in have_by_key:
            bad += 1
            findings.append(f"duplicate {cells[0]} {cells[1]} {cells[2][:16]} "
                            f"(lines {have_by_key[key][1]} and {number})")
            continue
        have_by_key[key] = (cells, number)
    want_keys = set()
    carried = 0
    new = 0
    for row in want:
        key = row[:3]
        want_keys.add(key)
        if key in base_by_key:
            carried += 1
            hit = have_by_key.get(key)
            if hit is None:
                bad += 1
                findings.append(f"missing {row[0]} {row[1]} {row[2][:16]}")
                continue
            cells = hit[0]
            if cells != base_by_key[key]:
                bad += 1
                findings.append(f"rewritten {row[0]} {row[1]} {row[2][:16]}: a carried row's "
                                f"bytes changed")
            continue
        new += 1
        hit = have_by_key.get(key)
        if hit is None:
            bad += 1
            findings.append(f"missing {row[0]} {row[1]} {row[2][:16]} (new row expected)")
            continue
        cells = hit[0]
        if list(cells[:5]) != [str(cell) for cell in row[:5]]:
            bad += 1
            findings.append(f"cell-mismatch {row[0]} {row[1]} {row[2][:16]}: "
                            f"have {cells[3]}/{cells[4]} want {row[3]}/{row[4]}")
        match = NOTE_RE.search(cells[5])
        if not match:
            bad += 1
            findings.append(f"note-no-round {row[0]} {row[1]} {row[2][:16]}")
            continue
        accepting, deletion = int(match.group(1)), int(match.group(2))
        if accepting != round_number:
            bad += 1
            findings.append(f"note-wrong-round {row[0]} {row[1]} {row[2][:16]}: "
                            f"accepting round {accepting}, expected {round_number}")
        if accepting <= deletion:
            bad += 1
            findings.append(f"note-not-later {row[0]} {row[1]} {row[2][:16]}: "
                            f"round {accepting} does not follow round {deletion}")
    for key, (cells, number) in have_by_key.items():
        if key not in want_keys:
            bad += 1
            findings.append(f"extra {cells[0][:12]} {cells[1]} {cells[2][:16]} (line {number})")
    return bad, carried, new, findings


def evaluate(repo: Path, round_number: int, to=None, late=LATE, audit_json=None):
    generator = load_generator(repo)
    data = generator.audit(repo, audit_json)
    revision = to or data.get("to")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise CouldNotEvaluate("the audit carries no explicit `to` revision")
    plan = show(repo, revision, PLAN.format(round=round_number))
    if plan is None:
        raise CouldNotEvaluate(f"no frozen plan at {revision}")
    match = BASE_RE.search(plan)
    if not match:
        raise CouldNotEvaluate("the frozen plan declares no `Base revision`")
    base = match.group(1)
    population = {(event["commit"], event["file"]): event for event in data["events"]
                  if event["undisclosed"] and event["status"] != "restored"}
    want = generator.generate(repo, round_number, revision, base, population)
    have = parse_rows(show(repo, revision, late), f"{late} at {revision[:12]}")
    base_rows = parse_rows(show(repo, base, late), f"{late} at {base[:12]}")
    bad, carried, new, findings = check(want, have or [], base_rows or [], round_number, base)
    return {"round": round_number, "base": base, "population": len(want),
            "carried": carried, "new": new, "bad": bad, "findings": findings}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--round", type=int, required=False)
    parser.add_argument("--base")
    parser.add_argument("--to")
    parser.add_argument("--late", default=LATE)
    parser.add_argument("--audit-json")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest(args.repo)
    if args.round is None:
        print("could-not-evaluate: --round is required", file=sys.stderr)
        return 2
    repo = Path(args.repo).resolve()
    try:
        result = evaluate(repo, args.round, args.to, args.late, args.audit_json)
        if args.base and args.base != result["base"]:
            raise CouldNotEvaluate(f"--base differs from the frozen plan's {result['base']}")
    except (CouldNotEvaluate, OSError, subprocess.TimeoutExpired, ImportError) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(result, indent=2))
        return 0 if result["bad"] == 0 else 1
    for finding in result["findings"]:
        print(f"LATE_DELTA_FINDING {finding}")
    print(f"LATE_DELTA round={result['round']} base={result['base'][:12]} "
          f"population={result['population']} carried={result['carried']} "
          f"new={result['new']} bad={result['bad']}")
    return 0 if result["bad"] == 0 else 1


# --- selftest --------------------------------------------------------------

def row(commit, file, digest, count, klass, note):
    return (commit, file, digest, count, klass, note)


def selftest(repo="."):
    commit_a, commit_b = "a" * 40, "b" * 40
    want = [row(commit_a, "SCORECARD.md", "11" * 32, "1", "in-place-edit",
                'round-82 accepts round-81 "x"; accepted'),
            row(commit_b, "LOG.md", "22" * 32, "2", "removal",
                'round-82 accepts round-81 "y"; accepted')]
    base_have = [(row(commit_a, "SCORECARD.md", "11" * 32, "1", "in-place-edit",
                      'round-81 accepts round-80 "x"; accepted'), 2)]
    tip_have = base_have + [(want[1], 3)]

    cases = []

    def run(name, w, tip, base, round_number=82, want_bad=0, want_new=None, want_carried=None):
        bad, carried, new, _findings = check(w, tip, base, round_number, "f" * 40)
        ok = bad == want_bad
        if want_new is not None:
            ok = ok and new == want_new
        if want_carried is not None:
            ok = ok and carried == want_carried
        cases.append((name, ok, bad, carried, new))

    run("honest", want, tip_have, base_have, want_new=1, want_carried=1)
    run("missing-new", want, base_have, base_have, want_bad=1)
    run("missing-carried", want, [(want[1], 3)], base_have, want_bad=1)
    run("extra", want, tip_have + [(row("c" * 40, "X.md", "33" * 32, "1", "removal",
                                        "round-82 accepts round-81 z; x"), 4)],
        base_have, want_bad=1)
    run("duplicate", want, tip_have + [(want[1], 5)], base_have, want_bad=1)
    wrong_count = [(row(want[1][0], want[1][1], want[1][2], "9", want[1][4], want[1][5]), 3)]
    run("wrong-count", want, base_have + wrong_count, base_have, want_bad=1)
    wrong_class = [(row(want[1][0], want[1][1], want[1][2], want[1][3], "in-place-edit",
                        want[1][5]), 3)]
    run("wrong-class", want, base_have + wrong_class, base_have, want_bad=1)
    rewritten = [(row(want[0][0], want[0][1], want[0][2], "1", "in-place-edit",
                      'round-80 accepts round-79 "x"; accepted'), 2),
                 (want[1], 3)]
    run("carried-rewritten", want, rewritten, base_have, want_bad=1)
    old_note = [(row(want[1][0], want[1][1], want[1][2], want[1][3], want[1][4],
                     'round-81 accepts round-80 "y"; accepted'), 3)]
    run("new-note-wrong-round", want, base_have + old_note, base_have, want_bad=1)
    same_round = [(row(want[1][0], want[1][1], want[1][2], want[1][3], want[1][4],
                       'round-82 accepts round-82 "y"; accepted'), 3)]
    run("note-not-later", want, base_have + same_round, base_have, want_bad=1)
    no_round = [(row(want[1][0], want[1][1], want[1][2], want[1][3], want[1][4],
                     "accepted history; no round"), 3)]
    run("note-no-round", want, base_have + no_round, base_have, want_bad=1)

    # integration arm: the frozen generator is importable and its generator is the one used
    try:
        module = load_generator(Path(repo).resolve())
        integrated = (module.HEADER == HEADER and callable(module.generate)
                      and callable(module.audit) and callable(module.frozen_covered))
    except (CouldNotEvaluate, OSError, ImportError):
        integrated = False
    cases.append(("generator-import", integrated, "", "", ""))
    failures = [case for case in cases if not case[1]]
    for name, ok, bad, carried, new in cases:
        print(f"{'PASS' if ok else 'FAIL'} {name} bad={bad} carried={carried} new={new}")
    print(f"LATE_DELTA_SELFTEST pass={len(cases) - len(failures)} fail={len(failures)}")
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(main())
