#!/usr/bin/env python3
"""Independent KQ22 cross-check: raw-byte registry cell identity per commit pair.

Not the guard's code (tools/sources-append-only.py). Stdlib only, read-only:
it runs `git -C REPO show REV:PATH` and nothing else.

Usage:
  kq22-bytecheck.py --repo REPO [--path corpus/SOURCES.md] FROM:TO [FROM:TO ...]

Rows are lines matching `^| S<digits> |`; each is split on every `|`
(census-style, awk -F'|'), so the eleven contract columns give 13 fields.
The seven immutable cells (and the id cell) are compared as raw bytes with no
strip, because KQ22 says "byte-identical"; the guard compares stripped cells.
status/recheck/used-by changes are reported old->new. An added row's
placement is reported: appended after every carried-over row, or inserted
between them.

Exit 0: no removed row and no immutable byte change in any pair.
Exit 1: at least one removed row or immutable byte change (a verdict).
Exit 2: could not evaluate (git failure, not UTF-8, header missing, repeated
        or not the contract's eleven columns in order, a row line that does
        not split into 13 fields, duplicate id). An error, never a verdict.
"""

import argparse
import json
import re
import subprocess
import sys

COLS = ("id", "source", "kind", "tier", "scope", "anchor", "teaches",
        "status", "opened", "recheck", "used-by")
MUTABLE = frozenset({"status", "recheck", "used-by"})
ROW_RE = re.compile(r"^\| S[0-9]+ \|")
HDR_RE = re.compile(r"^\| id \|")


class CannotEvaluate(Exception):
    pass


def blob(repo, rev, path):
    if rev.startswith("-") or ":" in rev:
        raise CannotEvaluate(f"invalid revision {rev!r}")
    proc = subprocess.run(["git", "-C", repo, "show", f"{rev}:{path}"],
                          capture_output=True)
    if proc.returncode != 0:
        raise CannotEvaluate(f"git show {rev}:{path} rc={proc.returncode}: "
                             f"{proc.stderr.decode('utf-8', 'replace').strip()}")
    try:
        return proc.stdout.decode("utf-8")
    except UnicodeDecodeError:
        raise CannotEvaluate(f"{rev}:{path} is not UTF-8") from None


def parse(text, rev):
    lines = text.split("\n")
    hdrs = [i for i, line in enumerate(lines) if HDR_RE.match(line)]
    if len(hdrs) != 1:
        raise CannotEvaluate(f"{rev}: {len(hdrs)} `| id |` header lines")
    names = tuple(c.strip() for c in lines[hdrs[0]].split("|")[1:-1])
    if names != COLS:
        raise CannotEvaluate(f"{rev}: header {list(names)} != {list(COLS)}")
    rows = {}
    for idx, line in enumerate(lines):
        if not ROW_RE.match(line):
            continue
        fields = line.split("|")
        if len(fields) != 13:
            raise CannotEvaluate(f"{rev}:{idx + 1}: {len(fields)} fields, want 13")
        cells = dict(zip(COLS, fields[1:-1]))
        rid = cells["id"].strip()
        if rid in rows:
            raise CannotEvaluate(f"{rev}:{idx + 1}: duplicate id {rid}")
        rows[rid] = (idx + 1, cells)
    if not rows:
        raise CannotEvaluate(f"{rev}: no registry rows")
    return rows


def compare(old, new):
    removed = sorted(set(old) - set(new))
    added = sorted(set(new) - set(old))
    immutable, mutable = [], []
    for rid in sorted(set(old) & set(new)):
        a, b = old[rid][1], new[rid][1]
        for col in COLS:
            if a[col] == b[col]:
                continue
            rec = {"id": rid, "cell": col, "from": a[col], "to": b[col]}
            if col in MUTABLE:
                mutable.append(rec)
            else:
                rec["whitespace_only"] = a[col].strip() == b[col].strip()
                immutable.append(rec)
    carried = [new[r][0] for r in old if r in new]
    last_carried = max(carried) if carried else 0
    placement = {
        rid: {"line": new[rid][0],
              "appended_after_all_carried_rows": new[rid][0] > last_carried}
        for rid in added
    }
    return {"rows_from": len(old), "rows_to": len(new), "removed": removed,
            "added": added, "added_placement": placement,
            "immutable_byte_changes": immutable, "mutable_changes": mutable}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--repo", required=True)
    ap.add_argument("--path", default="corpus/SOURCES.md")
    ap.add_argument("pairs", nargs="+", metavar="FROM:TO")
    args = ap.parse_args(argv)
    report, verdict = [], 0
    try:
        for pair in args.pairs:
            frm, sep, to = pair.partition(":")
            if not sep or not frm or not to:
                raise CannotEvaluate(f"pair {pair!r} is not FROM:TO")
            res = compare(parse(blob(args.repo, frm, args.path), frm),
                          parse(blob(args.repo, to, args.path), to))
            res = {"from": frm, "to": to, **res}
            report.append(res)
            if res["removed"] or res["immutable_byte_changes"]:
                verdict = 1
    except CannotEvaluate as e:
        print(json.dumps({"error": str(e), "verdict": None}))
        return 2
    print(json.dumps({"pairs": report, "verdict": verdict}, indent=2,
                     ensure_ascii=False))
    return verdict


if __name__ == "__main__":
    sys.exit(main())
