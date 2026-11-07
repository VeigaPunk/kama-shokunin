#!/usr/bin/env python3
"""Generate single-point mutants of tools/round91-threshold-rows.py.

Every mutant is one textual replacement applied to the pristine counter bytes; the
generator asserts the old text occurs exactly once and records a unified diff.
Usage: make-mutants.py --counter <pristine.py> --out <mutants-dir>
"""
import argparse
import difflib
import hashlib
import sys
from pathlib import Path

# (id, rule, old, new)
MUTANTS = [
    ("M01", "B2 value-in-literal dropped",
     '    if not nums or not any(n in lit for n in nums):',
     '    if False:  # M01 drop B2 value-in-literal'),
    ("M02", "B4 moving-ref check dropped",
     '    if any(x in url for x in MOVING):',
     '    if False:  # M02 drop B4 moving-ref'),
    ("M03", "B4 pin-in-URL check dropped",
     '    if pin not in url:',
     '    if False:  # M03 drop B4 pin-in-url'),
    ("M04", "B4 engine-in-URL check dropped",
     '    if engine.split()[0].lower() not in url.lower():',
     '    if False:  # M04 drop B4 engine-in-url'),
    ("M05", "B5 sha256 compare dropped",
     '    if hashlib.sha256(body).hexdigest() != h.group(1):',
     '    if False:  # M05 drop B5 sha compare'),
    ("M06", "B6 line off-by-one",
     '    if not 1 <= n <= len(lines) or lit not in lines[n - 1]:',
     '    if not 1 <= n <= len(lines) or lit not in lines[n]:  # M06 off-by-one'),
    ("M07", "comment stripping disabled",
     '        while "<!--" in line:',
     '        while False:  # M07 comment stripping disabled'),
    ("M08", "fence detection disabled",
     '        if s.startswith("```") or s.startswith("~~~"):',
     '        if False:  # M08 fence detection disabled'),
    ("M09", "duplicate rule removed",
     '        if rid in seen_id or (pair and pair in seen_pair):',
     '        if False:  # M09 duplicate rule removed'),
    ("M10", "B7 name-in-literal dropped",
     '    if not any(t in lit for t in names):',
     '    if False:  # M10 drop B7 name-in-literal'),
    ("M11", "MIN_ENGINES 3 -> 1",
     'MIN_ENGINES = 3',
     'MIN_ENGINES = 1  # M11'),
    ("M12", "MIN_ROWS 10 -> 1",
     'MIN_ROWS = 10',
     'MIN_ROWS = 1  # M12'),
    ("M13", "8-cell arity check dropped",
     '    if len(cells) != 8:',
     '    if False:  # M13 drop cell-arity check'),
    ("M14", "fetch failure counts as bound",
     '    if body is None:\n        return False, "fetch-failed", "fetch"',
     '    if body is None:\n        return True, "bound-unfetched", None  # M14'),
    ("M15", "empty-cell `-` marker dropped",
     '    if any(not c or c == "-" for c in cells):',
     '    if any(not c for c in cells):  # M15 drop the "-" marker'),
    ("M16", "source status/tier check dropped",
     '    if status != "mined" or tier not in ("A", "B"):',
     '    if False:  # M16 drop status/tier check'),
    ("M17", "section heading matched by prefix",
     '            inside = line.rstrip() == HEAD',
     '            inside = line.rstrip().startswith(HEAD)  # M17 prefix match'),
    ("M18", "duplicate: id half dropped (pair kept)",
     '        if rid in seen_id or (pair and pair in seen_pair):',
     '        if pair and pair in seen_pair:  # M18 id half dropped'),
    ("M19", "duplicate: pair half dropped (id kept)",
     '        if rid in seen_id or (pair and pair in seen_pair):',
     '        if rid in seen_id:  # M19 pair half dropped'),
    ("M20", "backticks not stripped from literal",
     '    lit = literal.strip().strip("`")',
     '    lit = literal.strip()  # M20 keep backticks'),
    ("M21", "always-green exit code",
     '    return 0 if met else 1',
     '    return 0  # M21 always green'),
    ("M22", "empty-string cell check dropped",
     '    if any(not c or c == "-" for c in cells):',
     '    if any(c == "-" for c in cells):  # M22 drop empty-string check'),
]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--counter", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    src = Path(a.counter).read_text()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    base = hashlib.sha256(src.encode()).hexdigest()
    print(f"pristine_sha256={base} bytes={len(src)}")
    index = []
    diffs = []
    for mid, rule, old, new in MUTANTS:
        n = src.count(old)
        assert n == 1, f"{mid}: old text occurs {n} times"
        mut = src.replace(old, new, 1)
        assert mut != src, mid
        p = out / f"{mid}.py"
        p.write_text(mut)
        h = hashlib.sha256(mut.encode()).hexdigest()
        d = "".join(difflib.unified_diff(
            src.splitlines(keepends=True), mut.splitlines(keepends=True),
            fromfile=f"pristine/{a.counter}", tofile=f"mutants/{mid}.py", n=2))
        diffs.append(f"### {mid} {rule}\n{d}")
        index.append(f"{mid}\t{h}\t{rule}")
        print(f"{mid} sha256={h} rule={rule}")
    (out / "index.tsv").write_text("\n".join(index) + "\n")
    (out / "mutants.diff").write_text("\n".join(diffs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
