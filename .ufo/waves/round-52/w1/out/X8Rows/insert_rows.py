#!/usr/bin/env python3
"""X8Rows (round 52, lane kama): re-append the 10 remaining disclosure rows'
deleted lines verbatim in a fixture clone - the 7 corpus/SOURCES.md rows at the
end of the `## Registry` table, the 3 registry/report-landing-errata.tsv rows at
the end of that table - so the duplicate-id / duplicate-key defect can be shown.

Usage: insert_rows.py sources|errata <repo> <rows.json>
Edits the file in the working tree only; committing is the caller's step.
"""
import json
import sys

SOURCES = "corpus/SOURCES.md"
ERRATA = "registry/report-landing-errata.tsv"


def source_lines(rows):
    return [r for r in rows if r["file"] == SOURCES]


def errata_lines(rows):
    return [r for r in rows if r["file"] == ERRATA]


def main(which, repo, rows_json):
    rows = json.load(open(rows_json))["rows"]
    if which == "sources":
        sel = source_lines(rows)
        path = f"{repo}/{SOURCES}"
        with open(path, "rb") as fh:
            lines = fh.read().split(b"\n")
        heads = [i for i, ln in enumerate(lines) if ln.startswith(b"## ")]
        start = next(i for i in heads if lines[i].strip() == b"## Registry")
        end = next(i for i in heads if i > start)
        last = max(i for i in range(start, end) if lines[i].strip())
        block = [bytes.fromhex(m["bytes_hex"]) for r in sel for m in r["matches"]]
        new = lines[:last + 1] + block + lines[last + 1:]
        with open(path, "wb") as fh:
            fh.write(b"\n".join(new))
        print(f"inserted {len(block)} rows after line {last + 1} "
              f"({SOURCES}); registry section {start + 1}..{end}")
    else:
        sel = errata_lines(rows)
        path = f"{repo}/{ERRATA}"
        with open(path, "rb") as fh:
            data = fh.read()
        tail = b"" if data.endswith(b"\n") else b"\n"
        block = b"".join(bytes.fromhex(m["bytes_hex"]) + b"\n" for r in sel
                         for m in r["matches"])
        with open(path, "wb") as fh:
            fh.write(data + tail + block)
        print(f"appended {len(sel)} rows to {ERRATA}")


if __name__ == "__main__":
    main(*sys.argv[1:4])
