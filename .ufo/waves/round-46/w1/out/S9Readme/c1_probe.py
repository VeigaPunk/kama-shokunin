#!/usr/bin/env python3
"""Independent read-only probe of the C1 population at b11906.

For every row of registry/release-recheck-b11889.tsv (the 91-row round-44
population), report blob identity b11889..b11906 and whether the pinned
range text is text-equal at the same release line numbers, and if not,
whether the whitespace-collapsed pin-range text occurs anywhere in the
b11906 file (relocated / reworded) or is absent (drifted/removed).
No writes to the lane or the clone.
"""
import json
import re
import subprocess
import sys

BARE = "/fast/scratch/hyaku/kama-r46/L1/llama.git"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
PIN_LEDGER = LANE + "/registry/release-recheck-b11889.tsv"
B11889 = "d854d98bae598388ecea1ed84396587e5edc326d"
B11906 = "4d71b42fd87db24b8b7c808c151b713aa4459cfd"


def git(*args):
    return subprocess.run(["git", "-C", BARE, *args], capture_output=True, text=True, check=False)


def blob(commit, path):
    r = git("rev-parse", f"{commit}:{path}")
    return r.stdout.strip() if r.returncode == 0 else None


def lines_at(commit, path):
    r = git("show", f"{commit}:{path}")
    if r.returncode != 0:
        return None
    return r.stdout.splitlines()


def ws(s):
    return re.sub(r"\s+", " ", s).strip()


def parse_ranges(cell):
    out = []
    for part in cell.split(","):
        part = part.strip()
        if not part or part == "-":
            continue
        if "-" in part:
            a, b = part.split("-")
            out.append((int(a), int(b)))
        else:
            out.append((int(part), int(part)))
    return out


def range_text(lines, ranges):
    chunks = []
    for a, b in ranges:
        chunks.extend(lines[a - 1:b])
    return "\n".join(chunks)


rows = []
with open(PIN_LEDGER) as fh:
    header = fh.readline().rstrip("\n").split("\t")
    for line in fh:
        line = line.rstrip("\n")
        if not line:
            continue
        cells = line.split("\t")
        rows.append(dict(zip(header, cells)))

cache = {}
result = []
for row in rows:
    rid, path = row["id"], row["path"]
    pin_commit = row["pin_commit"]
    pin_blob = blob(pin_commit, path)
    b89_blob = blob(B11889, path)
    b06_blob = blob(B11906, path)
    pin_ranges = parse_ranges(row["pin_lines"])
    b89_ranges = parse_ranges(row["release_lines"])
    if path not in cache:
        cache[path] = {B11889: lines_at(B11889, path), B11906: lines_at(B11906, path)}
    if ("pin:" + pin_commit) not in cache[path]:
        cache[path]["pin:" + pin_commit] = lines_at(pin_commit, path)
    pin_lines = cache[path]["pin:" + pin_commit]
    b89_lines = cache[path][B11889]
    b06_lines = cache[path][B11906]
    pin_text = range_text(pin_lines, pin_ranges) if pin_lines else ""
    b89_text = range_text(b89_lines, b89_ranges) if b89_lines else ""
    relocated = False
    same_pairs = None
    absent = False
    if b06_lines is None:
        absent = True
        same_pairs = "missing-file"
    else:
        try:
            b06_same = range_text(b06_lines, b89_ranges)
        except IndexError:
            b06_same = None
        if b06_same is not None:
            # per-element equality against the pin ranges (same index)
            elems_pin = [range_text(pin_lines, [r]) for r in pin_ranges]
            elems_b06 = [range_text(b06_lines, [r]) for r in b89_ranges]
            same_pairs = all(a == b for a, b in zip(elems_pin, elems_b06))
        flat_b06 = ws("\n".join(b06_lines))
        relocated = ws(pin_text) in flat_b06
    result.append({
        "id": rid,
        "path": path,
        "pin_blob": pin_blob,
        "b89_blob": b89_blob,
        "b06_blob": b06_blob,
        "pin_changed_at_b06": pin_blob != b06_blob,
        "b89_b06_same": b89_blob == b06_blob,
        "same_line_text_equal": same_pairs,
        "pin_text_present_at_b06": relocated,
        "b11889_verdict": row["verdict"],
    })

print(json.dumps({"rows": len(result), "detail": result}, indent=1))
