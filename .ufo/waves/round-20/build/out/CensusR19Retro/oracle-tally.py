#!/usr/bin/env python3
"""Independent tally of the ## Registry table in a corpus/SOURCES.md; never calls sources-census.sh.

usage: oracle-tally.py FILE|-   prints rows, id range, tier and status counts; exit 0, or 2 if
the input is unreadable. Follows only the contract shape: 0-3 leading spaces, '## Registry'
opens the section, '#'/'##' headings close it, rows start '| S<3+ digits> |'.
"""
import collections
import re
import sys

ROW = re.compile(r"^ {0,3}\|\s*(S\d{3,})\s*\|")
HEADING = re.compile(r"^ {0,3}(#{1,2})[ \t]+(.*?)\s*$")


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: oracle-tally.py FILE|-", file=sys.stderr)
        return 2
    try:
        if argv[1] == "-":
            text = sys.stdin.read()
        else:
            with open(argv[1], encoding="utf-8") as handle:
                text = handle.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"unreadable: {exc}", file=sys.stderr)
        return 2
    section, ids = None, []
    tiers, statuses = collections.Counter(), collections.Counter()
    for line in text.splitlines():
        heading = HEADING.match(line)
        if heading:
            section = heading.group(2) if heading.group(1) == "##" else None
            continue
        if section != "Registry" or not ROW.match(line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        ids.append(cells[0])
        tiers[cells[3]] += 1
        statuses[cells[7]] += 1
    first, last = (ids[0], ids[-1]) if ids else ("-", "-")
    print(f"rows {len(ids)} unique {len(set(ids))} first {first} last {last}")
    print("tier " + " ".join(f"{key}={value}" for key, value in sorted(tiers.items())))
    print("status " + " ".join(f"{key}={value}" for key, value in sorted(statuses.items())))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
