#!/usr/bin/env python3
"""round83-pending-falls.py - round-83 C1 leg C (operability): round 82's pending count
must fall at the round-83 base.

PREDICATE (frozen: plans/round-83-claims.md, section C1 leg C):

    `python3 tools/round83-pending-falls.py --repo <lane> --round 83` prints one
    `PENDING_FALLS round=83 from=82 declared=8 window=8 accepted=8 unaccepted=0 falls=yes`
    line and exits 0 only when the count the round-82 final-gate receipt declares
    (`.ufo/waves/round-82/measured/after/gate.out` -> `pending=8`) equals the size of the
    population window that receipt's base opened (events with undisclosed lines committed
    after the receipt's base and at or before the round-83 base), every window event is
    covered by a committed `registry/append-only-late.tsv` row at the graded tip, and
    `unaccepted` is 0. A window event left uncovered is a finding and the leg exits 1: a
    `pending` count that does not fall at the next round's base is a finding, never a pass.

Mechanics. The population is recomputed with the frozen `tools/append-only-audit.py --json`
under the round-81 rule: events with undisclosed lines whose status is not `restored`. The
receipt's `base=<12-hex>` is expanded with `git rev-parse --verify <base>^{commit}`; the
window is the commit set of `git rev-list <base>..<declared base>` (strict descendants of
the receipt base that are ancestors-or-equal of the plan's declared base). The declared base
is read from the frozen plan `plans/round-<round>-claims.md` with the counters'
``Base revision `<40-hex>` `` rule. Coverage is triple-presence only: a committed late row
whose `(commit, file, line_sha256)` matches an undisclosed line of the event; row quality
(count, class, note, row introduction) remains round81-append-debt.py's job. The register is
read at the audited revision; an absent register covers nothing (a red leg, exit 1, not
could-not-evaluate). A missing receipt, a receipt naming another round, an ambiguous receipt,
or a receipt base that is not an ancestor of the declared base is could-not-evaluate
(exit 2) -- never a silent pass.

Usage: round83-pending-falls.py --repo DIR --round N [--json] | --selftest
Exit: 0 falls=yes; 1 falls=no; 2 could-not-evaluate.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

PLAN = "plans/round-{round}-claims.md"
RECEIPT = ".ufo/waves/round-{round}/measured/after/gate.out"
LATE = "registry/append-only-late.tsv"
HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
BASE_RE = re.compile(r"Base revision `([0-9a-f]{40})`")
AD_RE = re.compile(r"APPEND_DEBT round=(\d+)\b")
BASE_TOK = re.compile(r"\bbase=([0-9a-f]{12})\b")
PENDING_TOK = re.compile(r"\bpending=(\d+)\b")


class CouldNotEvaluate(Exception):
    pass


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True,
                          timeout=180)
    if proc.returncode != 0:
        raise CouldNotEvaluate(f"git {' '.join(args)} exit={proc.returncode}: "
                               f"{proc.stderr.strip()}")
    return proc.stdout


def is_ancestor(repo: Path, a: str, b: str) -> bool:
    return subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor", a, b],
                          capture_output=True, timeout=180).returncode == 0


def show(repo: Path, rev: str, path: str) -> str | None:
    proc = subprocess.run(["git", "-C", str(repo), "show", f"{rev}:{path}"],
                          capture_output=True, text=True, timeout=180)
    return proc.stdout if proc.returncode == 0 else None


def resolve_base(plan_text: str) -> str:
    match = BASE_RE.search(plan_text or "")
    if not match:
        raise CouldNotEvaluate("the frozen plan declares no `Base revision`")
    return match.group(1)


def parse_receipt(text: str, expected_round: int) -> tuple[str, int]:
    """(base 12-hex, declared pending) from the receipt's APPEND_DEBT round=<expected>
    line(s); a line naming another round, no line at all, or disagreeing lines refuse."""
    found: list[tuple[str, int]] = []
    for match in AD_RE.finditer(text or ""):
        if int(match.group(1)) != expected_round:
            raise CouldNotEvaluate(f"receipt names APPEND_DEBT round={match.group(1)}, "
                                   f"expected round={expected_round}")
        start = text.rfind("\n", 0, match.start()) + 1
        end = text.find("\n", match.start())
        line = text[start:end if end != -1 else len(text)]
        base, pending = BASE_TOK.search(line), PENDING_TOK.search(line)
        if base is None or pending is None:
            raise CouldNotEvaluate("receipt APPEND_DEBT line carries no base= or pending=")
        found.append((base.group(1), int(pending.group(1))))
    if not found:
        raise CouldNotEvaluate(f"receipt declares no APPEND_DEBT round={expected_round} line")
    if len(set(found)) > 1:
        raise CouldNotEvaluate(f"receipt is ambiguous: {sorted(set(found))}")
    return found[0]


def population(data: dict) -> dict:
    """The round-81 population rule: events with undisclosed lines, status not restored."""
    if not isinstance(data, dict) or data.get("schema") != "append-only-audit/v3":
        raise CouldNotEvaluate("expected append-only-audit/v3")
    out = {}
    for event in data.get("events") or []:
        commit, file = event.get("commit"), event.get("file")
        if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit) or not file:
            raise CouldNotEvaluate("audit event without a 40-hex commit or a file")
        if event.get("undisclosed") and event.get("status") != "restored":
            out[(commit, file)] = event
    return out


def parse_register(text: str | None) -> list[tuple[str, ...]]:
    if text is None:
        return []
    lines = text.splitlines()
    if not lines or lines[0] != HEADER:
        raise CouldNotEvaluate(f"{LATE} requires the six-column LF TSV header")
    rows = []
    for number, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 6:
            raise CouldNotEvaluate(f"{LATE} line {number}: expected six cells")
        rows.append(tuple(cells))
    return rows


def evaluate(population: dict, triples: set, in_window, declared: int) -> dict:
    """Pure falls verdict. in_window(commit) -> bool; triples = covered (commit, file,
    line_sha256). A window event counts as accepted only when every undisclosed line of the
    event is covered by a triple."""
    keys = sorted(key for key in population if in_window(key[0]))
    accepted, uncovered = 0, []
    for key in keys:
        missing = [entry["line_sha256"] for entry in population[key]["undisclosed"]
                   if (*key, entry["line_sha256"]) not in triples]
        if missing:
            uncovered.append({"commit": key[0], "file": key[1], "missing": len(missing)})
        else:
            accepted += 1
    window, unaccepted = len(keys), len(keys) - accepted
    return {"declared": declared, "window": window, "accepted": accepted,
            "unaccepted": unaccepted,
            "falls": declared == window and unaccepted == 0,
            "window_events": [{"commit": k[0], "file": k[1]} for k in keys],
            "uncovered": uncovered}


def render(result: dict) -> str:
    lines = [f"PENDING_FALLS round={result['round']} from={result['from']} "
             f"declared={result['declared']} window={result['window']} "
             f"accepted={result['accepted']} unaccepted={result['unaccepted']} "
             f"falls={'yes' if result['falls'] else 'no'}"]
    for entry in result["uncovered"]:
        lines.append(f"PENDING_FALLS_UNCOVERED {entry['commit'][:12]} {entry['file']} "
                     f"missing={entry['missing']}")
    return "\n".join(lines)


def verdict(result: dict) -> int:
    return 0 if result["falls"] else 1


# ---------------------------------------------------------------- selftest

def selftest() -> int:
    A, B = "a" * 40, "b" * 40
    H1, H2 = "1" * 64, "2" * 64
    pop = {(A, "LOG.md"): {"undisclosed": [
        {"line_sha256": H1, "count": 1, "classes": ["in-place-edit"]},
        {"line_sha256": H2, "count": 2, "classes": ["in-place-edit"]}]}}
    full = {(A, "LOG.md", H1), (A, "LOG.md", H2)}
    cases: list[tuple[str, dict, int, str | None]] = []

    def run(name, result, want_exit, want=None):
        cases.append((name, result, want_exit, want))

    # falls-green: the one window event is fully covered and declared matches
    run("falls-green", evaluate(pop, full, lambda c: c == A, 1), 0, None)
    # declared-mismatch: declared disagrees with the recomputed window
    run("declared-mismatch", evaluate(pop, full, lambda c: c == A, 2), 1, None)
    # window-uncovered: an uncovered line keeps the event unaccepted
    run("window-uncovered", evaluate(pop, {(A, "LOG.md", H1)}, lambda c: c == A, 1), 1,
        "uncovered")
    # receipt-wrong-round: the receipt names another round
    wrong = (f"PRE_REPORT_ARM x | APPEND_DEBT round=81 base={'a' * 12} events=1 pending=0\n"
             "EXIT=0\n")
    # receipt-missing: no APPEND_DEBT line at all
    for name, text, marker in (("receipt-wrong-round", wrong, "round=81"),
                               ("receipt-missing", "EXIT=0\n", "declares no APPEND_DEBT")):
        try:
            parse_receipt(text, 82)
            raised = None
        except CouldNotEvaluate as exc:
            raised = str(exc)
        ok = raised is not None and marker in raised
        run(name, {"falls": ok, "uncovered": []}, 0 if ok else 1, None)
    # receipt-parse: the frozen gate.out line shape parses to (base, pending)
    got = parse_receipt(f"PRE_REPORT_ARM round75-instruments exit=0 ok | APPEND_DEBT "
                        f"round=82 base=aaf974dbd3b6 events=68 accepted=53 late=15 pending=8 "
                        f"unaccepted=0 bad_rows=0\nEXIT=0\n", 82)
    run("receipt-parse", {"falls": got == ("aaf974dbd3b6", 8), "uncovered": []}, 0, None)
    # receipt-ambiguous: two agreeing-round lines that disagree refuse
    amb = ("APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 pending=8\n"
           "APPEND_DEBT round=82 base=aaf974dbd3b6 events=68 pending=9\n")
    try:
        parse_receipt(amb, 82)
        raised = None
    except CouldNotEvaluate:
        raised = "ambiguous"
    run("receipt-ambiguous", {"falls": raised == "ambiguous", "uncovered": []}, 0, None)

    fail = 0
    for name, result, want_exit, want in cases:
        got_exit = verdict(result)
        ok = got_exit == want_exit
        if want == "uncovered":
            ok = ok and result["uncovered"]
        if not ok:
            fail += 1
            print(f"PENDING_FALLS_SELFTEST_FAIL {name} exit={got_exit} want={want_exit} "
                  f"result={result}")
    print(f"PENDING_FALLS_SELFTEST pass={len(cases) - fail} fail={fail}")
    return 0 if fail == 0 else 1


# ---------------------------------------------------------------- main

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--round", type=int,
                        help="the graded round; the receipt is round-1's final gate")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.round is None:
        parser.error("--round is required (the receipt is round-1's final gate)")
    repo = Path(args.repo).resolve()
    try:
        to = git(repo, "rev-parse", "HEAD").strip()
        receipt_path = RECEIPT.format(round=args.round - 1)
        receipt_text = show(repo, to, receipt_path)
        if receipt_text is None:
            raise CouldNotEvaluate(f"no receipt at {to}:{receipt_path}")
        base12, declared = parse_receipt(receipt_text, args.round - 1)
        plan_path = PLAN.format(round=args.round)
        plan_text = show(repo, to, plan_path)
        if plan_text is None:
            raise CouldNotEvaluate(f"no frozen plan at {to}:{plan_path}")
        declared_base = resolve_base(plan_text)
        base = git(repo, "rev-parse", "--verify", f"{base12}^{{commit}}").strip()
        if not is_ancestor(repo, base, declared_base):
            raise CouldNotEvaluate(f"receipt base {base[:12]} is not an ancestor of the "
                                   f"declared base {declared_base[:12]}")
        process = subprocess.run([sys.executable, str(repo / "tools/append-only-audit.py"),
                                  "--repo", str(repo), "--json"],
                                 capture_output=True, text=True, timeout=900)
        if process.returncode not in (0, 1):
            raise CouldNotEvaluate(f"audit exit={process.returncode}: "
                                   f"{process.stderr.strip()[:200]}")
        try:
            data = json.loads(process.stdout)
        except ValueError as exc:
            raise CouldNotEvaluate(f"audit JSON unreadable: {exc}") from exc
        if data.get("to") != to:
            raise CouldNotEvaluate("audit revision differs from the captured graded tip")
        if not is_ancestor(repo, declared_base, to):
            raise CouldNotEvaluate("declared base is not an ancestor of the graded tip")
        window = set(git(repo, "rev-list", f"{base}..{declared_base}").split())
        triples = {(cells[0], cells[1], cells[2]) for cells in parse_register(show(repo, to, LATE))}
        result = evaluate(population(data), triples, lambda commit: commit in window, declared)
        result.update({"round": args.round, "from": args.round - 1, "base": base,
                       "declared_base": declared_base, "to": to,
                       "receipt": str(receipt_path)})
    except (CouldNotEvaluate, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2, sort_keys=True) if args.json else render(result))
    return verdict(result)


if __name__ == "__main__":
    sys.exit(main())
