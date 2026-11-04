#!/usr/bin/env python3
"""Round-83 C1 leg C: rederive the previous round's pending window and repayment.

Frozen predicate: plans/round-83-claims.md C1 leg C. Population comes from the
frozen audit, not from receipt counts. Receipt, plan and register are read from
one committed graded tip; dirty worktree versions cannot change the window.
Coverage means every undisclosed (commit, file, line_sha256) triple is present.
Row count/class/note acceptance is separately graded by round81-append-debt.py.
Exit 0: falls=yes; 1: falls=no; 2: could-not-evaluate.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"
LATE = "registry/append-only-late.tsv"
BASE_RE = re.compile(r"Base revision `([0-9a-f]{40})`")


class CouldNotEvaluate(Exception):
    pass


def git(repo, *args):
    p = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                       text=True, timeout=180)
    if p.returncode:
        raise CouldNotEvaluate(f"git {' '.join(args)}: {p.stderr.strip()}")
    return p.stdout


def parse_receipt(text, expected_round):
    if text is None:
        raise CouldNotEvaluate("receipt missing")
    found = set()
    for line in text.splitlines():
        for match in re.finditer(r"\bAPPEND_DEBT round=(\d+)\b", line):
            if int(match[1]) != expected_round:
                raise CouldNotEvaluate(f"receipt wrong round={match[1]}")
            segment = line[match.end():].split(" | ", 1)[0]
            base = re.search(r"\bbase=([0-9a-f]{12})\b", segment)
            pending = re.search(r"\bpending=(\d+)\b", segment)
            if base is None or pending is None:
                raise CouldNotEvaluate("receipt lacks base or pending")
            found.add((base[1], int(pending[1])))
    if len(found) != 1:
        raise CouldNotEvaluate("receipt missing APPEND_DEBT or ambiguous")
    return found.pop()


def population(data):
    if not isinstance(data, dict) or data.get("schema") != "append-only-audit/v3":
        raise CouldNotEvaluate("expected append-only-audit/v3")
    if not isinstance(data.get("events"), list):
        raise CouldNotEvaluate("audit lacks events")
    out = {}
    for event in data["events"]:
        commit, file = event["commit"], event["file"]
        if not re.fullmatch(r"[0-9a-f]{40}", commit) or not isinstance(file, str) or not file:
            raise CouldNotEvaluate("audit event lacks commit/file")
        if not isinstance(event["undisclosed"], list):
            raise CouldNotEvaluate("audit event lacks undisclosed list")
        for entry in event["undisclosed"]:
            if not re.fullmatch(r"[0-9a-f]{64}", entry["line_sha256"]):
                raise CouldNotEvaluate("audit line lacks digest")
        if event["undisclosed"] and event["status"] != "restored":
            if (commit, file) in out:
                raise CouldNotEvaluate("duplicate audit event")
            out[(commit, file)] = event
    return out


def parse_register(text):
    lines = text.splitlines()
    if "\r" in text or not lines or lines[0] != HEADER:
        raise CouldNotEvaluate("late register requires six-column LF TSV header")
    triples = set()
    for number, line in enumerate(lines[1:], 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 6:
            raise CouldNotEvaluate(f"late register line {number}: expected six cells")
        triples.add(tuple(cells[:3]))
    return triples


def evaluate(events, triples, in_window, declared):
    keys = sorted(key for key in events if in_window(key[0]))
    uncovered = []
    for key in keys:
        missing = sum((*key, line["line_sha256"]) not in triples
                      for line in events[key]["undisclosed"])
        if missing:
            uncovered.append({"commit": key[0], "file": key[1], "missing": missing})
    window, unaccepted = len(keys), len(uncovered)
    return {"declared": declared, "window": window, "accepted": window - unaccepted,
            "unaccepted": unaccepted, "falls": declared == window and unaccepted == 0,
            "uncovered": uncovered,
            "window_events": [{"commit": c, "file": f} for c, f in keys]}


def render(result):
    return (f"PENDING_FALLS round={result['round']} from={result['from']} "
            f"declared={result['declared']} window={result['window']} "
            f"accepted={result['accepted']} unaccepted={result['unaccepted']} "
            f"falls={'yes' if result['falls'] else 'no'}")


def selftest():
    commit, digest = "a" * 40, "1" * 64
    events = {(commit, "LOG.md"): {"undisclosed": [{"line_sha256": digest}]}}
    full = {(commit, "LOG.md", digest)}
    cases = []
    for name, declared, triples, expected in (
        ("declared-mismatch", 0, full, False),
        ("window-uncovered", 1, set(), False),
        ("falls-green", 1, full, True),
    ):
        result = evaluate(events, triples, lambda c: c == commit, declared)
        cases.append((name, result["falls"] is expected))
    wrong = "APPEND_DEBT round=81 base=aaf974dbd3b6 pending=8"
    for name, text in (("receipt-wrong-round", wrong), ("receipt-missing", None)):
        try:
            parse_receipt(text, 82)
            ok = False
        except CouldNotEvaluate:
            ok = True
        cases.append((name, ok))
    for name, ok in cases:
        print(f"PENDING_FALLS_SELFTEST_ARM {name} {'pass' if ok else 'FAIL'}")
    fail = sum(not ok for _, ok in cases)
    print(f"PENDING_FALLS_SELFTEST pass={len(cases) - fail} fail={fail}")
    return int(bool(fail))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--round", type=int)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    repo = Path(args.repo).resolve()
    try:
        if args.round is None:
            raise CouldNotEvaluate("--round is required")
        tip = git(repo, "rev-parse", "HEAD").strip()
        receipt = f".ufo/waves/round-{args.round - 1}/measured/after/gate.out"
        base12, declared = parse_receipt(git(repo, "show", f"{tip}:{receipt}"), args.round - 1)
        plan = git(repo, "show", f"{tip}:plans/round-{args.round}-claims.md")
        match = BASE_RE.search(plan)
        if match is None:
            raise CouldNotEvaluate("frozen plan declares no Base revision")
        declared_base = match[1]
        base = git(repo, "rev-parse", "--verify", f"{base12}^{{commit}}").strip()
        git(repo, "merge-base", "--is-ancestor", base, declared_base)
        git(repo, "merge-base", "--is-ancestor", declared_base, tip)
        window = set(git(repo, "rev-list", f"{base}..{declared_base}").split())
        process = subprocess.run([sys.executable, str(repo / "tools/append-only-audit.py"),
                                  "--repo", str(repo), "--json"],
                                 capture_output=True, text=True, timeout=300)
        if process.returncode not in (0, 1):
            raise CouldNotEvaluate(f"audit exit={process.returncode}: {process.stderr.strip()}")
        data = json.loads(process.stdout)
        if data.get("to") != tip:
            raise CouldNotEvaluate("audit revision differs from captured graded tip")
        triples = parse_register(git(repo, "show", f"{tip}:{LATE}"))
        result = evaluate(population(data), triples, lambda c: c in window, declared)
        result.update({"schema": "pending-falls/v1", "round": args.round,
                       "from": args.round - 1, "base": base, "declared_base": declared_base,
                       "to": tip, "receipt": receipt})
    except (CouldNotEvaluate, OSError, ValueError, KeyError, TypeError,
            subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else render(result))
    return 0 if result["falls"] else 1


if __name__ == "__main__":
    sys.exit(main())
