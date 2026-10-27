#!/usr/bin/env python3
"""ablate_ledger.py - round-51 seat J8OneClass: derive the three C2 ablation ledgers.

Input is the lane's registry/append-only-disclosures.tsv at 138af25b (166 data rows:
160 in-place-edit, 5 revert, 1 removal). One variant per invocation:

  in-place-edit  every data row's class cell (5th) rewritten to `in-place-edit`
  drop-row       original rows minus the row whose line_sha256 starts with --drop
  junk           original rows plus one appended row with --junk-sha (a sha256 no
                 line of any blob has), on the event of --junk-commit/--junk-file

The header line is copied verbatim; cells are tab separated; the file ends with a
newline. Printing goes to stdout as `key=value` lines for the receipt.
"""
from __future__ import annotations

import argparse
import collections
import hashlib
import sys

HEADER = "commit\tfile\tline_sha256\tcount\tclass\tnote"


def read_rows(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    if b"\r" in raw:
        raise SystemExit("source ledger carries CR bytes")
    lines = raw.decode("utf-8").split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    if not lines or lines[0] != HEADER:
        raise SystemExit("source ledger header is not the frozen header")
    rows = [ln.split("\t") for ln in lines[1:]]
    for r in rows:
        if len(r) != 6:
            raise SystemExit(f"row has {len(r)} cells: {r[:3]}")
    return rows


def write_rows(path, rows):
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write(HEADER + "\n")
        for r in rows:
            fh.write("\t".join(r) + "\n")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--src", required=True, help="original ledger (read-only)")
    ap.add_argument("--dst", required=True, help="variant ledger to write")
    ap.add_argument("--variant", required=True, choices=("in-place-edit", "drop-row", "junk"))
    ap.add_argument("--drop", default=None, help="drop-row: line_sha256 prefix")
    ap.add_argument("--junk-sha", default=None, help="junk: 64 hex chars")
    ap.add_argument("--junk-commit", default=None, help="junk: commit of a real deletion event")
    ap.add_argument("--junk-file", default=None, help="junk: file of that event")
    a = ap.parse_args(argv)
    rows = read_rows(a.src)
    before = collections.Counter(r[4] for r in rows)
    note = ""
    if a.variant == "in-place-edit":
        for r in rows:
            r[4] = "in-place-edit"
        note = f"classes rewritten to in-place-edit; before={dict(sorted(before.items()))}"
    elif a.variant == "drop-row":
        if not a.drop:
            raise SystemExit("drop-row needs --drop")
        kept = [r for r in rows if not r[2].startswith(a.drop)]
        if len(kept) != len(rows) - 1:
            raise SystemExit(f"--drop matched {len(rows) - len(kept)} rows, want 1")
        dropped = [r for r in rows if r[2].startswith(a.drop)][0]
        rows = kept
        note = f"dropped={dropped[0]} {dropped[1]} {dropped[2]} {dropped[4]}"
    else:
        if not (a.junk_sha and a.junk_commit and a.junk_file):
            raise SystemExit("junk needs --junk-sha, --junk-commit, --junk-file")
        if any(r[2] == a.junk_sha for r in rows):
            raise SystemExit("junk sha already present")
        rows = rows + [[a.junk_commit, a.junk_file, a.junk_sha, "1", "removal",
                        "r51 J8OneClass ablation: junk row, no such line"]]
        note = f"appended junk={a.junk_commit} {a.junk_file} {a.junk_sha}"
    after = collections.Counter(r[4] for r in rows)
    write_rows(a.dst, rows)
    digest = hashlib.sha256(open(a.dst, "rb").read()).hexdigest()
    print(f"variant={a.variant}")
    print(f"rows_before={sum(before.values())} classes_before={dict(sorted(before.items()))}")
    print(f"rows_after={sum(after.values())} classes_after={dict(sorted(after.items()))}")
    print(f"ledger_sha256={digest}")
    print(f"note={note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
