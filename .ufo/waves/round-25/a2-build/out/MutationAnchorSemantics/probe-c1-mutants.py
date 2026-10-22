#!/usr/bin/env python3
"""Probe the C1 counting command (preregistration.json C1.command).

The command treats a mutant as non-stale when `src.count(old) == 1` on
tools/report-landing-audit.py.  This probe attacks that criterion: for each
of the 28 registered mutants at the tip it checks whether the single match
still leaves the mutant ineffective:

  1. applies   - whether src.count(old) == 1 (the command's own criterion)
  2. compiles  - whether the mutated source parses (ast.parse)
  3. changed   - the lines the replacement actually changes (difflib)
  4. inert     - whether the matched occurrence lies inside a STRING or
                 COMMENT token of the original source (the replacement then
                 alters no executable code)
  5. identical - whether new == old (replacement is a no-op)
  6. element   - the enclosing def of the matched occurrence, so a match
                 that lands on a different element (not the one the id
                 claims) is visible

Run:  python3 probe-c1-mutants.py
Out:  JSON table to stdout, human-readable table to stderr.
"""
from __future__ import annotations

import ast
import difflib
import importlib.util
import io
import json
import sys
import tokenize
from pathlib import Path
LANE = Path(__file__).resolve().parents[6]
if len(sys.argv) > 1:
    LANE = Path(sys.argv[1]).resolve()
INSTRUMENT = LANE / "tests/report-audit/isolation-mutants.py"
AUDIT = LANE / "tools/report-landing-audit.py"

spec = importlib.util.spec_from_file_location("iso_mutants", INSTRUMENT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def offsets_to_abs(lines, row, col):
    """(row, col) 1-based -> absolute char offset."""
    return sum(len(l) for l in lines[: row - 1]) + col


def tok_spans(src):
    """Merged absolute [start, end) spans of STRING and COMMENT tokens."""
    raw = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(src).readline):
            if tok.type in (tokenize.STRING, tokenize.COMMENT):
                lines = src.splitlines(keepends=True)
                s = offsets_to_abs(lines, *tok.start)
                e = offsets_to_abs(lines, *tok.end)
                raw.append((s, e))
    except tokenize.TokenError:
        pass
    raw.sort()
    merged = []
    for s, e in raw:
        if merged and s <= merged[-1][1]:
            merged[-1] = (merged[-1][0], max(merged[-1][1], e))
        else:
            merged.append((s, e))
    return merged


def fully_covered(occ, old_len, spans):
    """True if the whole match [occ, occ+old_len) lies inside merged tokens."""
    for s, e in spans:
        if s <= occ and occ + old_len <= e:
            return True
    return False


def occ_line(src, i):
    return src.count("\n", 0, i) + 1


def enclosing_def(src, occ_start):
    """Name of the def whose body contains occ_start, or 'module'."""
    tree = ast.parse(src)
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.lineno <= src.count("\n", 0, occ_start) + 1 <= (
                getattr(node, "end_lineno", node.lineno)
            ):
                return node.name
    return "module"


def run_probe():
    src = AUDIT.read_text()
    spans = tok_spans(src)
    rows = []
    for name, old, new in m.MUTANTS:
        count = src.count(old)
        row = {
            "id": name,
            "count": count,
            "applies": count == 1,
            "identical": old == new,
        }
        if count == 0:
            row.update(compiles=None, changed=None, inert=None, element=None,
                       occurrences=[])
            rows.append(row)
            continue
        occs = []
        start = 0
        while True:
            i = src.find(old, start)
            if i < 0:
                break
            occs.append(i)
            start = i + len(old)
        inert = all(fully_covered(i, len(old), spans) for i in occs)
        mutated = src.replace(old, new, 1)
        try:
            ast.parse(mutated)
            compiles = True
        except SyntaxError as exc:
            compiles = f"{exc.msg} at line {exc.lineno}"
        a = src.splitlines()
        b = mutated.splitlines()
        sm = difflib.SequenceMatcher(None, a, b)
        changed = []
        for tag, i1, i2, j1, j2 in sm.get_opcodes():
            if tag != "equal":
                changed.append((tag, i1 + 1, i2, j1 + 1, j2))
        row.update(
            compiles=compiles,
            changed=changed,
            inert=inert,
            element=[enclosing_def(src, i) for i in occs],
            occurrences=[{"offset": i, "line": occ_line(src, i)} for i in occs],
        )
        rows.append(row)
    return rows


def main():
    rows = run_probe()
    print(json.dumps(rows, indent=1))
    hdr = f"{'id':30s} {'cnt':>3} {'applies':>7} {'compiles':>8} {'inert':>5} {'identical':>8} element"
    print(hdr, file=sys.stderr)
    for r in rows:
        print(
            f"{r['id']:30s} {r['count']:>3} {str(r['applies']):>7} "
            f"{str(r['compiles']):>8} {str(r['inert']):>5} "
            f"{str(r['identical']):>8} {r['element']}",
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
