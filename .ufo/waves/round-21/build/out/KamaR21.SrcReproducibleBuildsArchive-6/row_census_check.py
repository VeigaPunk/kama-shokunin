#!/usr/bin/env python3
"""KamaR21.SrcReproducibleBuildsArchive-6 - census-style check of the S066 draft row (stdlib only).

Mirrors the CORPUS.md census for one row: 11 cells (awk NF == 13 with the outer pipes),
id unused in corpus/SOURCES.md, kind and tier and status enums, no community row at tier A,
status/used-by consistency, ISO opened date, recheck cadence. Read-only on the registry.
The draft file also holds a Gate table whose first cell is S066; only the registry-shaped
line (13 split fields) is checked.
Exit 0: pass. Exit 1: a check fails. Exit 2: an input cannot be read.
"""
import pathlib
import re
import sys

OUT = pathlib.Path(__file__).resolve().parent
DRAFT = OUT / "row-draft-S066.md"
REGISTRY = pathlib.Path("/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md")
KINDS = {"spec", "docs", "paper", "code", "tool", "dataset", "talk", "book", "community", "own-work"}


def main():
    try:
        draft = DRAFT.read_text(encoding="utf-8").splitlines()
        reg = REGISTRY.read_text(encoding="utf-8").splitlines()
    except OSError as e:
        print("cannot read:", e)
        return 2
    rows = [line for line in draft
            if re.match(r"^\|\s*S066\s*\|", line) and len(line.split("|")) == 13]
    if len(rows) != 1:
        print("registry-shaped draft rows for S066:", len(rows))
        return 1
    raw = rows[0].split("|")
    cells = [c.strip() for c in raw[1:-1]]
    checks = {
        "NF == 13 (11 cells)": len(raw) == 13 and len(cells) == 11,
        "id S066 unused in registry": not any(re.match(r"^\|\s*S066\s*\|", line) for line in reg),
        "kind in enum": cells[2] in KINDS,
        "tier in A/B/C": cells[3] in {"A", "B", "C"},
        "community never A": not (cells[3] == "A" and cells[2] == "community"),
        "status in enum": cells[7] in {"queued", "mined", "rejected"},
        "queued has used-by dash": cells[7] != "queued" or cells[10] == "\u2014",
        "opened is ISO date": bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", cells[8])),
        "recheck is cadence or date": bool(re.fullmatch(r"\d+d|on-release|\d{4}-\d{2}-\d{2}", cells[9])),
    }
    ok = True
    for name, passed in checks.items():
        print(("ok  " if passed else "BAD ") + name)
        ok = ok and passed
    print("RESULT", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
