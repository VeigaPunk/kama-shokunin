#!/usr/bin/env python3
"""Account for frozen append-only events and preserve the first register cutoff.

Inputs are committed at the audit's explicit `to` revision, never worktree TSVs.
The frozen v6 audit does not serialize exempt sections or an exemption class:
we re-derive parent sections using its own parser and name that class exempt-head.
Exit 0: accounted; 1: findings; 2: could-not-evaluate, including CLI misuse.
"""
from __future__ import annotations

import argparse
import copy
import importlib.util
import json
from pathlib import Path
import re
import subprocess
import sys

PREDICATE = "`python3 tools/round76-append-exempt.py --repo <lane>` prints one `APPEND_EXEMPT events=232 register=53 exempt=83 restored=91 disclosed=5 unaccounted=0 cutoff=<40-hex> introductions=1 rotation_safe=1` line and exits 0 only when every event the append-only audit reports is accounted for exactly once — by a line-bound row of `registry/append-only-accepted.tsv`, by a class-bound row of `registry/append-only-exempt.tsv` whose `class` is the audit's own mechanical exemption class and whose count equals the event's ungraded deleted lines, by restoration at the audit revision, or by a disclosure row — and the cutoff is the earliest commit adding any accepted-history register, so a later re-introduction of a register cannot re-open it; it exits 1 naming each `APPEND_EXEMPT_FINDING <unaccounted|wrong-class|wrong-count|duplicate|post-introduction|rotation> …`, and 2 on could-not-evaluate (audit run failure, missing register, CLI misuse)."
ACCEPTED = "registry/append-only-accepted.tsv"
EXEMPT = "registry/append-only-exempt.tsv"
HEADER = "commit\tfile\tclass\tcount\tsections\tnote"
CLASS = "exempt-head"


class CouldNotEvaluate(Exception):
    pass


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def git(repo, *args):
    process = subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                             text=True, timeout=120)
    if process.returncode:
        raise CouldNotEvaluate(process.stderr.strip())
    return process.stdout


def read_audit(repo):
    process = subprocess.run([sys.executable, str(repo / "tools/append-only-audit.py"),
                              "--repo", str(repo), "--json"], capture_output=True,
                             text=True, timeout=300)
    if process.returncode not in (0, 1):
        raise CouldNotEvaluate(f"audit exit={process.returncode}: {process.stderr.strip()}")
    data = json.loads(process.stdout)
    if not re.fullmatch(r"[0-9a-f]{40}", data.get("to", "")):
        raise CouldNotEvaluate("audit has no explicit to revision")
    return data


def exemption_sections(repo, data, audit_tool):
    rows = audit_tool.parse_contract(git(repo, "show", f"{data['to']}:{audit_tool.CONTRACT}"))
    result = {}
    for event in data["events"]:
        if event["status"] != "ungraded":
            continue
        commit, file = event["commit"], event["file"]
        parent = git(repo, "rev-parse", f"{commit}^1").strip()
        body = audit_tool._git(str(repo), "show", f"{parent}:{file}")
        sections = audit_tool.sections(audit_tool.split_lines(body))
        deleted = audit_tool.deleted_lines(str(repo), parent, commit, file)
        titles, _ = audit_tool.file_regions(rows, file)
        parents = {sections[pos - 1] for pos, _, _ in deleted}
        result[(commit, file)] = (sorted(t for t in parents if t is not None),
                                  bool(parents) and parents <= titles)
    return result


def introduction_history(repo, to):
    additions = set()
    for path in (ACCEPTED, EXEMPT):
        additions.update(git(repo, "log", "--diff-filter=A", "--format=%H", to,
                             "--", path).split())
    if not additions:
        raise CouldNotEvaluate("no register introduction")
    # Topological reverse order avoids clock-skewed commit dates reopening history.
    ordered = git(repo, "rev-list", "--topo-order", "--reverse", to).split()
    introductions = [c for c in ordered if c in additions]
    return introductions


def ancestor(repo, commit, cutoff):
    process = subprocess.run(["git", "-C", str(repo), "merge-base", "--is-ancestor",
                              commit, cutoff], capture_output=True, timeout=120)
    if process.returncode not in (0, 1):
        raise CouldNotEvaluate(f"cannot resolve row ancestry: {commit}")
    return process.returncode == 0


def grade(data, accepted, exempt, sections, introductions, precedes, accepted_tool):
    accepted_tool.validate_audit(data)
    findings = []
    def bad(kind, detail):
        findings.append({"class": kind, "detail": detail})

    prior = accepted_tool.grade(data, accepted, precedes)
    for finding in prior["findings"]:
        kind = finding["class"]
        bad({"class-mismatch": "wrong-class", "post-introduction": "post-introduction",
             "duplicate": "duplicate"}.get(kind, "wrong-count"), finding["detail"])
    events = {(e["commit"], e["file"]): e for e in data["events"]}
    seen, valid, invalid = set(), set(), set()
    lines = exempt.splitlines()
    if not lines or lines[0] != HEADER or "\r" in exempt:
        bad("wrong-class", "exempt register requires six-column LF TSV header")
    for number, line in enumerate(lines[1:] if lines and lines[0] == HEADER else lines, 2):
        if not line.strip():
            continue
        cells = line.split("\t")
        if len(cells) != 6:
            bad("wrong-class", f"exempt line {number}: expected six columns")
            continue
        commit, file, klass, count, titles, note = cells
        key = (commit, file)
        detail = f"{commit} {file}"
        if key in seen:
            invalid.add(key)
            bad("duplicate", detail)
            continue
        seen.add(key)
        event = events.get(key)
        expected_sections, eligible = sections.get(key, ([], False))
        if (event is None or event["status"] != "ungraded" or event["graded"] != 0
                or event["ungraded"] != event["deleted"] or not eligible
                or klass != CLASS or titles != "|".join(expected_sections) or not note.strip()):
            bad("wrong-class", detail)
            invalid.add(key)
            continue
        if not re.fullmatch(r"[1-9][0-9]*", count) or int(count) != event["ungraded"]:
            bad("wrong-count", detail)
            invalid.add(key)
            continue
        if not precedes(commit):
            bad("rotation" if len(introductions) > 1 else "post-introduction", detail)
            invalid.add(key)
            continue
        valid.add(key)
    # Both ledgers are bound by the earliest introduction, even after a delete/re-add.
    for text in (accepted, exempt):
        for line in text.splitlines()[1:]:
            cells = line.split("\t")
            if len(cells) == 6 and re.fullmatch(r"[0-9a-f]{40}", cells[0]):
                if not precedes(cells[0]):
                    bad("rotation" if len(introductions) > 1 else "post-introduction",
                        f"{cells[0]} {cells[1]} younger than cutoff {introductions[0]}")
    valid -= invalid
    buckets = {"register": prior["summary"]["accepted"], "exempt": len(valid),
               "restored": 0, "disclosed": 0}
    for key, event in events.items():
        if event["status"] == "restored":
            if event["held_at_to"] == event["graded"]:
                buckets["restored"] += 1
            else:
                bad("unaccounted", f"{key[0]} {key[1]} restoration not held at audit revision")
        elif event["status"] == "disclosed":
            buckets["disclosed"] += 1
        elif event["status"] == "ungraded" and key not in valid:
            bad("unaccounted", f"{key[0]} {key[1]} missing valid exempt row")
    for name in ("bad_declarations", "bad_disclosures", "binary", "vanished", "unmatched"):
        if data["summary"].get(name, 0):
            bad("unaccounted", f"audit {name}={data['summary'][name]}")
    unaccounted = len(events) - sum(buckets.values())
    rotation_safe = int(not any(f["class"] in {"rotation", "post-introduction"} for f in findings))
    return {"schema": "append-exempt/v1", "predicate": PREDICATE,
            "summary": {"events": len(events), **buckets, "unaccounted": unaccounted,
                        "cutoff": introductions[0], "introductions": len(introductions),
                        "rotation_safe": rotation_safe}, "findings": findings}


def verdict(result):
    return int(bool(result["findings"] or result["summary"]["unaccounted"]))


def render(result):
    return "\n".join(["APPEND_EXEMPT " + " ".join(f"{k}={v}" for k, v in result["summary"].items()),
                      *(f"APPEND_EXEMPT_FINDING {f['class']} {f['detail']}" for f in result["findings"])])


def class_register(data, sections, precedes):
    """Rows the frozen rule admits: ungraded events whose every ungraded line sits in an
    exempt head section of the file's contract row. A non-strict event is not admissible
    and stays a finding (round-76 C3 honest miss: 31 wrong-class + 5 post-introduction)."""
    rows = [HEADER]
    for event in data["events"]:
        if event["status"] != "ungraded":
            continue
        titles, strict = sections[(event["commit"], event["file"])]
        if not strict or not precedes(event["commit"]):
            continue
        rows.append("\t".join([event["commit"], event["file"], CLASS,
                                 str(event["ungraded"]), "|".join(titles),
                                 "contract-exempt head re-derivation"]))
    return "\n".join(rows) + "\n"


def selftest(repo, data, accepted, sections, introductions, precedes, accepted_tool):
    """Audit-backed fixtures: mutations must change both exit and named finding."""
    exempt = class_register(data, sections, precedes)
    rows = exempt.splitlines()
    # Green is reachable only on a fully-admissible population: the real audit carries
    # 31 wrong-class and 5 post-introduction events, so the baseline arm is red by design
    # (round-76 C3 honest miss) and a filtered fixture proves the pass path exists.
    def keep(key, event):
        if event["status"] == "restored":
            return event["held_at_to"] == event["graded"]
        if event["status"] == "disclosed":
            return True
        return (event["status"] == "ungraded" and sections.get(key, ([], False))[1]
                and precedes(event["commit"]))
    kept = {(e["commit"], e["file"]) for e in data["events"] if keep((e["commit"], e["file"]), e)}
    flat = lambda text: "\n".join(
        [text.splitlines()[0]] + [ln for ln in text.splitlines()[1:]
                                  if (ln.split("\t")[0], ln.split("\t")[1]) in kept]) + "\n"
    green_data = {**data, "events": [e for e in data["events"] if (e["commit"], e["file"]) in kept],
                  "summary": {**data["summary"], "events": len(kept)}}
    cases = [("audit-fixture-green", flat(exempt), introductions, precedes, 0, None),
             ("audit-fixture-baseline", exempt, introductions, precedes, 1, "unaccounted"),
             ("missing-row", "\n".join([rows[0], *rows[2:]]) + "\n", introductions, precedes, 1, "unaccounted")]
    for name, column, value, kind in (("wrong-count", 3, "999999", "wrong-count"),
                                      ("wrong-class", 2, "removal", "wrong-class")):
        changed = rows.copy()
        cells = changed[1].split("\t")
        cells[column] = value
        changed[1] = "\t".join(cells)
        cases.append((name, "\n".join(changed) + "\n", introductions, precedes, 1, kind))
    younger = rows[1].split("\t")[0]
    cases.append(("rotation-reintroduced", exempt, [*introductions, data["to"]],
                  lambda c: c != younger and precedes(c), 1, "rotation"))
    fails = 0
    for name, text, intros, predicate, expected, kind in cases:
        source = green_data if name == "audit-fixture-green" else data
        accepted_text = flat(accepted) if name == "audit-fixture-green" else accepted
        result = grade(source, accepted_text, text, sections, intros, predicate, accepted_tool)
        actual = verdict(result)
        ok = actual == expected and (kind is None or any(f["class"] == kind for f in result["findings"]))
        fails += not ok
        print(f"APPEND_EXEMPT_SELFTEST {name} {'PASS' if ok else 'FAIL'} exit={actual} expected={expected}")
    print(f"APPEND_EXEMPT_SELFTEST pass={len(cases) - fails} fail={fails}")
    return int(bool(fails))


class Parser(argparse.ArgumentParser):
    def error(self, message):
        raise CouldNotEvaluate(message)


def main(argv=None):
    parser = Parser(description=__doc__)
    parser.add_argument("--repo", default=".")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--selftest", action="store_true")
    errors = (CouldNotEvaluate, OSError, ValueError, KeyError, TypeError,
              subprocess.TimeoutExpired)
    try:
        args = parser.parse_args(argv)
        repo = Path(args.repo).resolve()
        audit_tool = load_module(repo / "tools/append-only-audit.py", "append_audit")
        accepted_tool = load_module(repo / "tools/round75-append-accepted.py", "append_accepted")
        errors += (audit_tool.AuditError, accepted_tool.CouldNotEvaluate)
        data = read_audit(repo)
        accepted_tool.validate_audit(data)
        accepted = git(repo, "show", f"{data['to']}:{ACCEPTED}")
        sections = exemption_sections(repo, data, audit_tool)
        introductions = introduction_history(repo, data["to"])
        cache = {}
        def precedes(commit):
            if commit not in cache:
                cache[commit] = ancestor(repo, commit, introductions[0])
            return cache[commit]
        if args.selftest:
            return selftest(repo, data, accepted, sections, introductions, precedes, accepted_tool)
        exempt = git(repo, "show", f"{data['to']}:{EXEMPT}")
        result = grade(data, accepted, exempt, sections, introductions, precedes, accepted_tool)
        print(json.dumps(result, indent=2) if args.json else render(result))
        return verdict(result)
    except errors as exc:
        print(f"could-not-evaluate: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
