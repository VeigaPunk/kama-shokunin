#!/usr/bin/env python3
"""Grade append-only accepted history without changing the frozen audit.

Usage: round75-append-accepted.py --repo DIR [--audit-json FILE]
       [--register FILE] [--json] | --selftest

The default audit reads committed HEAD blobs, not worktree declarations. Commit
contract/declaration changes before expecting bad_declarations=0. --audit-json
is an explicit offline input for fixtures and retained audit receipts. The
register's class remains the audit's class, including normalization events:
CRLF->LF is an acceptance reason, not a replacement mechanical class.
Exit 0: covered; 1: findings; 2: could-not-evaluate / CLI misuse.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

PREDICATE = "`python3 tools/round75-append-accepted.py --repo <lane>` prints one `APPEND_ACCEPTED events=<e> accepted=<a> unaccepted=<u> bad_rows=<r> bad_declarations=<d>` line and exits 0 only when the byte-frozen `tools/append-only-audit.py --json` reports zero unbound contract declarations and every undisclosed deletion event that audit computes carries a committed `registry/append-only-accepted.tsv` row (`commit`, `file`, `line_sha256`, `count`, `class`, `note`) whose commit and file match an event, whose line hash and count match that event's `undisclosed` entries, and whose class is the mechanical class that event computes — the register never changes the audit's `unrestored` count, it grades each undisclosed event as accepted history with the commit subject and a one-line reason — it exits 1 naming `APPEND_ACCEPTED_FINDING <class> <detail>` and 2 on could-not-evaluate (audit unreadable or absent, register absent, CLI misuse)."
HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"


class CouldNotEvaluate(Exception):
    pass


def validate_audit(data):
    """Reject incomplete receipts rather than interpreting missing fields as zero."""
    if not isinstance(data, dict) or data.get("schema") != "append-only-audit/v3" or data.get("definition") != "v6":
        raise CouldNotEvaluate("expected append-only-audit/v3 definition v6")
    def require(condition):
        if not condition:
            raise CouldNotEvaluate("incomplete or inconsistent audit JSON")

    try:
        events, declarations, summary = data["events"], data["declarations"], data["summary"]
        require(isinstance(events, list) and isinstance(declarations, list))
        require(type(summary["bad_declarations"]) is int)
        require(summary["bad_declarations"] == sum(d["ok"] is False for d in declarations))
        require(all(type(d["ok"]) is bool for d in declarations))
        seen = set()
        for event in events:
            key = (event["commit"], event["file"])
            require(re.fullmatch(r"[0-9a-f]{40}", key[0]) and isinstance(key[1], str) and key[1])
            require(key not in seen)
            seen.add(key)
            require(event["status"] in {"ungraded", "restored", "disclosed", "unrestored", "partial"})
            require(isinstance(event["undisclosed"], list))
            hashes = set()
            for entry in event["undisclosed"]:
                require(re.fullmatch(r"[0-9a-f]{64}", entry["line_sha256"]))
                require(entry["line_sha256"] not in hashes)
                hashes.add(entry["line_sha256"])
                require(type(entry["count"]) is int and entry["count"] > 0)
                require(isinstance(entry["classes"], list) and entry["classes"])
                require(set(entry["classes"]) <= {"in-place-edit", "removal", "revert"})
    except (KeyError, TypeError) as exc:
        raise CouldNotEvaluate("incomplete or inconsistent audit JSON") from exc
    return data


def grade(data, register, precedes=None):
    """Grade the register against the audit. ``precedes(commit)`` is the temporal
    cutoff (sentinel SN01Register: a register row must not bless a deletion made at or
    after the register's own introduction); None skips it for offline fixtures."""
    validate_audit(data)
    all_events = {(e["commit"], e["file"]): e for e in data["events"]}
    pending = {key: e for key, e in all_events.items() if e["undisclosed"] and e["status"] != "restored"}
    expected = {(key[0], key[1], u["line_sha256"]): u for key, e in pending.items() for u in e["undisclosed"]}
    findings, seen, covered, invalid = [], set(), set(), set()
    bad_rows = 0

    def bad(kind, detail, key=None):
        nonlocal bad_rows
        bad_rows += 1
        findings.append({"class": kind, "detail": detail})
        if key in pending:
            invalid.add(key)

    lines = register.splitlines()
    if not lines or lines[0] != HEADER or "\r" in register:
        bad("hash-mismatch", "register requires the six-column LF TSV header")
    for number, line in enumerate(lines[1:] if lines and lines[0] == HEADER else lines, 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 6:
            bad("hash-mismatch", f"line {number}: expected six cells including a line hash")
            continue
        commit, file, digest, count, klass, note = cells
        key, row_key = (commit, file), (commit, file, digest)
        detail = f"line {number}: {commit} {file} {digest}"
        if row_key in seen:
            bad("duplicate", detail, key)
            continue
        seen.add(row_key)
        event = all_events.get(key)
        if event is None:
            bad("unknown-event", detail, key)
            continue
        if event["status"] == "restored":
            bad("restored-event", detail, key)
            continue
        entry = expected.get(row_key)
        if entry is None or not re.fullmatch(r"[0-9a-f]{64}", digest):
            bad("hash-mismatch", detail, key)
            continue
        if not re.fullmatch(r"[1-9][0-9]*", count) or int(count) != entry["count"]:
            bad("count-short", f"{detail}: count={count} expected={entry['count']}", key)
            continue
        if klass not in entry["classes"]:
            bad("class-mismatch", f"{detail}: class={klass} expected={entry['classes']}", key)
            continue
        if not note.strip() or "; " not in note or not all(part.strip() for part in note.split("; ", 1)):
            bad("hash-mismatch", f"{detail}: note requires commit subject; acceptance reason", key)
            continue
        if precedes is not None and not precedes(row_key[0]):
            bad("post-introduction", f"{detail}: commit is not an ancestor of the "
                f"register's introduction commit", key)
            continue
        covered.add(row_key)
    accepted = 0
    for key, event in pending.items():
        missing = [u for u in event["undisclosed"] if (*key, u["line_sha256"]) not in covered]
        if not missing and key not in invalid:
            accepted += 1
        for entry in missing:
            findings.append({"class": "count-short", "detail": f"{key[0]} {key[1]} {entry['line_sha256']}: missing {entry['count']}"})
    for declaration in data["declarations"]:
        if not declaration["ok"]:
            findings.append({"class": "bad-declaration", "detail": f"{declaration.get('path')} {declaration.get('declared_at')}: {declaration.get('reason')}"})
    result = {"events": len(pending), "accepted": accepted, "unaccepted": len(pending) - accepted,
              "bad_rows": bad_rows, "bad_declarations": data["summary"]["bad_declarations"]}
    return {"schema": "append-accepted/v1", "predicate": PREDICATE, "summary": result,
            "audit_summary": data["summary"], "findings": findings}


def verdict(result):
    s = result["summary"]
    return int(bool(s["unaccepted"] or s["bad_rows"] or s["bad_declarations"]))


def render(result):
    lines = ["summary " + " ".join(f"{k}={v}" for k, v in result["audit_summary"].items()),
             "APPEND_ACCEPTED " + " ".join(f"{k}={v}" for k, v in result["summary"].items())]
    lines.extend(f"APPEND_ACCEPTED_FINDING {f['class']} {f['detail']}" for f in result["findings"])
    return "\n".join(lines)


def selftest():
    digest = hashlib.sha256(b"lost line").hexdigest()
    commit, restored = "a" * 40, "b" * 40
    event = {"commit": commit, "file": "LOG.md", "status": "unrestored",
             "undisclosed": [{"line_sha256": digest, "count": 2, "classes": ["in-place-edit"]}]}
    data = {"schema": "append-only-audit/v3", "definition": "v6", "events": [event,
            {"commit": restored, "file": "LOG.md", "status": "restored", "undisclosed": []}],
            "summary": {"bad_declarations": 0, "unrestored": 1}, "declarations": []}
    row = [commit, "LOG.md", digest, "2", "in-place-edit", "subject; accepted history"]

    def register(rows):
        return HEADER + "\n" + "\n".join("\t".join(r) for r in rows) + "\n"

    cases = [("honest", grade(data, register([row]), lambda c: True), 0, None),
             ("post-introduction", grade(data, register([row]), lambda c: False), 1,
              "post-introduction")]
    for name, column, value, finding in [("wrong-hash", 2, "0" * 64, "hash-mismatch"),
            ("restored-event", 0, restored, "restored-event"),
            ("wrong-class", 4, "removal", "class-mismatch"),
            ("short-count", 3, "1", "count-short"),
            ("excess-count", 3, "3", "count-short"),
            ("unknown-event", 0, "c" * 40, "unknown-event")]:
        changed = row.copy()
        changed[column] = value
        cases.append((name, grade(data, register([changed])), 1, finding))
    cases.append(("wc-l-cheat-53", grade(data, "\n".join([commit] * 53) + "\n"), 1, "hash-mismatch"))
    cases.append(("duplicate", grade(data, register([row, row])), 1, "duplicate"))
    cases.append(("missing-entry", grade(data, register([])), 1, "count-short"))
    bad_decl = copy.deepcopy(data)
    bad_decl["summary"]["bad_declarations"] = 1
    bad_decl["declarations"] = [{"ok": False, "path": "LOG.md", "declared_at": "NOTES.md:1", "reason": "unbound"}]
    cases.append(("bad-declaration", grade(bad_decl, register([row])), 1, "bad-declaration"))
    failed = 0
    for name, result, want, finding in cases:
        actual = verdict(result)
        ok = actual == want and (finding is None or any(f["class"] == finding for f in result["findings"]))
        failed += not ok
        print(f"APPEND_ACCEPTED_SELFTEST {name} {'PASS' if ok else 'FAIL'} exit={actual} expected={want}")
    print(f"APPEND_ACCEPTED_SELFTEST pass={len(cases) - failed} fail={failed}")
    return int(bool(failed))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--audit-json", help="read a retained frozen audit JSON instead of executing it")
    parser.add_argument("--register", help="default: <repo>/registry/append-only-accepted.tsv")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args(argv)
    if args.selftest:
        return selftest()
    repo = Path(args.repo).resolve()
    try:
        if args.audit_json:
            audit_text = Path(args.audit_json).read_text(encoding="utf-8")
        else:
            process = subprocess.run([sys.executable, str(repo / "tools/append-only-audit.py"),
                                      "--repo", str(repo), "--json"], capture_output=True, text=True, timeout=300)
            if process.returncode not in (0, 1):
                raise CouldNotEvaluate(f"audit exit={process.returncode}: {process.stderr.strip()}")
            audit_text = process.stdout
        data = json.loads(audit_text)
        to_rev = data.get("to")
        if not isinstance(to_rev, str) or not re.fullmatch(r"[0-9a-f]{40}", to_rev):
            raise CouldNotEvaluate("audit JSON carries no explicit `to` revision")
        if args.register:
            register_text = Path(args.register).read_text(encoding="utf-8")
            precedes = None
        else:
            shown = subprocess.run(["git", "-C", str(repo), "show",
                                    f"{to_rev}:registry/append-only-accepted.tsv"],
                                   capture_output=True, text=True, timeout=120)
            if shown.returncode != 0:
                raise CouldNotEvaluate(
                    "the register is not committed at the audit revision "
                    f"{to_rev}: {shown.stderr.strip()}")
            register_text = shown.stdout
            added = subprocess.run(["git", "-C", str(repo), "log", "--diff-filter=A",
                                    "--format=%H", "--", "registry/append-only-accepted.tsv"],
                                   capture_output=True, text=True, timeout=120)
            commits = [c for c in added.stdout.split() if c]
            if added.returncode != 0 or not commits:
                raise CouldNotEvaluate("cannot resolve the register's introduction commit")
            intro = commits[-1]
            cache = {}

            def precedes(commit, _intro=intro):
                if commit not in cache:
                    ok = commit != _intro and subprocess.run(
                        ["git", "-C", str(repo), "merge-base", "--is-ancestor", commit, _intro],
                        capture_output=True, timeout=120).returncode == 0
                    cache[commit] = ok
                return cache[commit]
        result = grade(data, register_text, precedes)
    except (CouldNotEvaluate, OSError, ValueError, subprocess.TimeoutExpired) as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2) if args.json else render(result))
    return verdict(result)


if __name__ == "__main__":
    sys.exit(main())
