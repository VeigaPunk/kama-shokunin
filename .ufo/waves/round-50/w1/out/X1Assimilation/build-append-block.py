#!/usr/bin/env python3
"""Scratch-only transform: staged campaign rows -> fleet/census-schema append block.

Reads the kama staged package (READ-ONLY) and the lane mirror, writes an append
block plus a per-row decision log.  No lane or campaign file is modified.

Rules (each recorded per row in the decision log):
  R1 parse with a left/right anchored splitter; a row that does not resolve to
     exactly 11 cells (id|source|kind|tier|scope|anchor|teaches|status|opened|
     recheck|used-by) is EXCLUDED as unparseable (census E01 class, NF!=13).
  R2 id already in the lane registry -> EXCLUDED (id collision; the lane holds
     the row, adopt nothing).
  R3 (normalized url, scope) already in the lane registry and the lane row is
     not `rejected` -> EXCLUDED (census E04 without a `supersedes` teaches).
  R4 recheck prose -> the leading `NNd` token when present, else a bare ISO
     date, else symbolic cadence; the stripped prose is logged, not lost.
  R5 a cell still holding `|` after parsing -> the row is EXCLUDED (the census
     splits on every `|`, so the row cannot parse as 11 columns).
  R6 used-by paths are kept only when the file exists in the mirror; the merge
     package's knowledge/ tree is copied into the mirror first, so a path that
     exists only there resolves.
"""
import json
import os
import re
import shutil
import sys

APPEND = "/home/vgpnk/Projects/shokuknow/merge/kama/SOURCES.append.md"
KNOW = "/home/vgpnk/Projects/shokuknow/merge/kama/knowledge/corpus"
AMEND = "/home/vgpnk/Projects/shokuknow/merge/kama/amendments/corpus"
LANE_SOURCES = sys.argv[1]
MIRROR = sys.argv[2]
OUT = sys.argv[3]

STATUS = {"mined", "queued", "rejected"}
URL_RE = re.compile(r"https?://[^\s|]+")
ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
CAD = re.compile(r"^(\d+d|[A-Za-z][A-Za-z0-9 _-]*)$")


def cells_of(line):
    body = line.strip()
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|"):
        body = body[:-1]
    return [c.strip() for c in body.split("|")]


def parse_row(line):
    """Return (cells, reason) - cells is 11 strings or None."""
    parts = cells_of(line)
    if len(parts) < 11:
        return None, f"only {len(parts)} cells"
    if parts[0] in ("id",) or set(parts[0]) <= set("-: "):
        return None, "header/separator"
    right = len(parts) - 1          # used-by
    status_at = None
    for i in range(len(parts) - 2, 0, -1):
        if parts[i] in STATUS:
            status_at = i
            break
    if status_at is None:
        return None, "no status cell"
    if status_at < 7:
        return None, f"status cell at {status_at} < 7"
    lead = parts[:status_at]        # id..teaches must be 7 cells
    if len(lead) != 7:
        return None, f"{len(lead)} cells before status (want 7)"
    opened = parts[status_at + 1] if status_at + 1 <= right - 2 else ""
    recheck = "|".join(parts[status_at + 2:right])
    used = parts[right]
    cells = lead + [parts[status_at], opened, recheck, used]
    return cells, ""


def url_of(s):
    m = URL_RE.search(s)
    if not m:
        return ""
    u = m.group(0)
    u = re.sub(r"#[^ ]*$", "", u).rstrip("/")
    host, sep, rest = u.partition("/")
    return host.lower() + sep + rest


def main():
    lane_rows = {}
    lane_keys = set()
    with open(LANE_SOURCES, encoding="utf-8") as fh:
        in_reg = False
        for line in fh:
            if re.match(r"^ {0,3}##\s", line):
                in_reg = line.strip()[2:].strip() == "Registry"
                continue
            if re.match(r"^ {0,3}#\s", line):
                in_reg = False
                continue
            if not in_reg or not re.match(r"^ {0,3}\|", line):
                continue
            c = cells_of(line)
            if len(c) != 11 or not re.match(r"^S\d{3,}$", c[0]):
                continue
            lane_rows[c[0]] = c
            lane_keys.add((url_of(c[1]), c[4], c[7]))

    os.makedirs(os.path.join(MIRROR, "corpus", "knowledge"), exist_ok=True)
    for base in (KNOW, AMEND):
        for root, _dirs, files in os.walk(base):
            for fn in files:
                src = os.path.join(root, fn)
                rel = os.path.relpath(src, base)
                dst = os.path.join(MIRROR, "corpus", rel)
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if not os.path.exists(dst):
                    shutil.copy2(src, dst)

    adopted, log = [], []
    with open(APPEND, encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            if not re.match(r"^\s*\|", line) or not re.match(r"^\s*\|\s*S\d{3,}\s*\|", line):
                continue
            cells, why = parse_row(line)
            if cells is None:
                log.append({"line": lineno, "id": cells_of(line)[0] if cells_of(line) else "",
                            "decision": "excluded", "reason": f"R1 unparseable: {why}"})
                continue
            rid = cells[0]
            if rid in lane_rows:
                log.append({"line": lineno, "id": rid, "decision": "excluded",
                            "reason": "R2 id collision (lane holds the id)"})
                continue
            key = (url_of(cells[1]), cells[4], cells[7])
            if key in lane_keys and cells[7] != "rejected" and "supersedes S" not in cells[6]:
                log.append({"line": lineno, "id": rid, "decision": "excluded",
                            "reason": "R3 url+scope already in registry (E04)"})
                continue
            prose = cells[9]
            norm = prose
            if not (ISO.match(prose) or re.fullmatch(r"\d+d", prose) or CAD.match(prose)):
                m = re.match(r"^(\d+d)\b", prose)
                if m:
                    norm = m.group(1)
                elif ISO.match(prose[:10]):
                    norm = prose[:10]
                else:
                    norm = "90d"
            cells[9] = norm
            if any("|" in c for c in cells):
                log.append({"line": lineno, "id": rid, "decision": "excluded",
                            "reason": "R5 cell still holds a pipe (anchor/teaches/scope)",
                            "columns": [i for i, c in enumerate(cells) if "|" in c]})
                continue
            keep = []
            for path in [p.strip() for p in cells[10].split(",")]:
                if not path or path == "—":
                    continue
                if os.path.exists(os.path.join(MIRROR, path)):
                    keep.append(path)
                else:
                    log.append({"line": lineno, "id": rid, "decision": "used-by-dropped",
                                "reason": f"R6 {path} absent from mirror"})
            cells[10] = ", ".join(keep) if keep else "—"
            adopted.append(cells)
            log.append({"line": lineno, "id": rid, "decision": "adopted",
                        "reason": "", "recheck_prose": prose if prose != norm else ""})

    with open(OUT + "/append-block.md", "w", encoding="utf-8") as fh:
        for c in adopted:
            fh.write("| " + " | ".join(c) + " |\n")
    with open(OUT + "/append-decisions.json", "w", encoding="utf-8") as fh:
        json.dump({"staged_rows": sum(1 for x in log if x["decision"] != "used-by-dropped"),
                   "adopted": len(adopted), "log": log}, fh, ensure_ascii=False, indent=1)
    print(json.dumps({"adopted": len(adopted),
                      "excluded": sum(1 for x in log if x["decision"] == "excluded"),
                      "used_by_dropped": sum(1 for x in log if x["decision"] == "used-by-dropped")}))


if __name__ == "__main__":
    main()
