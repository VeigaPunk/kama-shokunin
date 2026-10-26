#!/usr/bin/env python3
"""S9Flags: build flag-map.tsv for round-44 C1 flag placement.

Inputs (read-only): preregistration population, corpus/SOURCES.md registry rows,
corpus/knowledge/*.md entries at the lane freeze commit 77d1bbf5.
Output: flag-map.tsv (id, entry, line_of_claim) and placement-notes.tsv.

line_of_claim is the 1-based line, in the entry at the freeze commit, whose
sentence states the SOURCES row's `teaches` statement; for a table row it is
the row. Placement notes carry the enclosing block (where the flag paragraph
must be inserted so the table/list is not split) and whether the id already
appears on that line (the frozen counter's flag leg needs one line carrying
the id and b11889, so a new line is required where id_on_claim_line=0).
"""
import json
import os
import re
import subprocess
import sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "77d1bbf55c62a1d5fc08fcbd682f22277a5cdb40"
OUT = os.path.join(LANE, ".ufo/waves/round-44/w1/out/S9Flags")

# id -> entry -> claim line (chosen by reading the entry against the row's
# SOURCES `teaches`; see the report for the per-row justification)
MAP = {
    "corpus/knowledge/runtime-health-surface-matrix.md": {
        "S001": 14, "S035": 63, "S036": 65, "S037": 65},
    "corpus/knowledge/serving-metrics-crosswalk.md": {
        "S001": 14},
    "corpus/knowledge/served-identity-crosswalk.md": {
        "S001": 27, "S035": 144, "S036": 143, "S037": 143},
    "corpus/knowledge/endpoint-identity.md": {
        "S035": 184, "S036": 203, "S037": 201},
    "corpus/knowledge/llamacpp-loading-lifecycle.md": {
        "S035": 166, "S036": 27, "S037": 24, "S042": 164, "S043": 174,
        "S047": 218, "S054": 250, "S056": 271},
    "corpus/knowledge/gguf-runtime-compatibility-boundary.md": {
        "S015": 19},
    "corpus/knowledge/gguf-declared-identity.md": {
        "S060": 27},
    "corpus/knowledge/context-capacity.md": {
        "S060": 54, "S106": 84, "S107": 59, "S108": 64, "S109": 131,
        "S110": 65, "S111": 79, "S112": 68, "S113": 72,
        "S131": 258, "S132": 258, "S133": 258, "S134": 258, "S135": 258},
    "corpus/knowledge/echo-discriminating-counters.md": {
        "S137": 50},
    "corpus/knowledge/chat-adapter-outcomes.md": {
        "S180": 38, "S181": 37, "S182": 34, "S183": 35, "S184": 36,
        "S185": 36, "S186": 32, "S187": 31, "S188": 32, "S189": 43,
        "S190": 23, "S191": 24},
    "corpus/knowledge/context-capacity-engine-sides.md": {
        "S479": 21},
}

NOTE = {
    ("S186", "corpus/knowledge/chat-adapter-outcomes.md"):
        "claim absent: the entry cites server-common.cpp:1519 and :1521 but never "
        "1517, so S186's taught line is unstated in this used-by entry; anchor 32 "
        "is the logprobs bullet it belongs to and the flag is its only id-bearing line",
    ("S479", "corpus/knowledge/context-capacity-engine-sides.md"):
        "id appears only on the source header (line 1); anchor 21 is the sentence "
        "that states S479's claim, so the flag must be a new line naming S479",
    ("S035", "corpus/knowledge/endpoint-identity.md"):
        "id appears only on the section source line (line 184); the claim it grounds "
        "is the round-16 paragraph at 200-208 and 210-216",
}


def show(path):
    return subprocess.run(["git", "-C", LANE, "show", f"{FREEZE}:{path}"],
                          capture_output=True, check=True).stdout.decode()


def main():
    pop = json.load(open(os.path.join(
        LANE, ".ufo/waves/round-44/preregistration.json")))["claims"][0]["population"]
    rows = {}
    for i, l in enumerate(open(os.path.join(LANE, "corpus/SOURCES.md"),
                               encoding="utf-8").read().split("\n"), 1):
        m = re.match(r"^ {0,3}\|\s*(S\d{3,})\s*\|", l)
        if m:
            rows[m.group(1)] = (i, [c.strip() for c in l.strip().strip("|").split("|")])
    pairs = []
    for sid in pop:
        for u in [x.strip() for x in rows[sid][1][-1].split(",")]:
            if (re.fullmatch(r"corpus/knowledge/[\w.\-]+\.md", u)
                    and os.path.isfile(os.path.join(LANE, u))):
                pairs.append((sid, u))
    bad = []
    for sid, e in pairs:
        if sid not in MAP.get(e, {}):
            bad.append(f"no claim line chosen for {sid} in {e}")
    body = {e: show(e).split("\n") for e in MAP}
    lines = []
    notes = []
    for sid, e in pairs:
        n = MAP[e][sid]
        src = body[e]
        if n < 1 or n > len(src) or not src[n - 1].strip():
            bad.append(f"{sid} {e}:{n} is empty or out of range")
            continue
        lines.append(f"{sid}\t{e}\t{n}")
        # enclosing block: scan to the next blank line (flag goes after it)
        b = n
        while b <= len(src) and src[b - 1].strip():
            b += 1
        # b-1 is the block's last non-blank line
        kind = ("table" if src[n - 1].lstrip().startswith("|")
                else "list" if re.match(r"^\s*([-*]|\d+\.)\s", src[n - 1])
                else "paragraph")
        id_on = 1 if re.search(rf"\b{sid}\b", src[n - 1]) else 0
        notes.append(f"{sid}\t{e}\t{n}\t{kind}\t{n}-{b-1}\t{id_on}\t{NOTE.get((sid, e), '')}")
    if bad:
        print("\n".join(bad), file=sys.stderr)
        return 1
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "flag-map.tsv"), "w", encoding="utf-8") as fh:
        fh.write("id\tentry\tline_of_claim\n")
        fh.write("\n".join(lines) + "\n")
    with open(os.path.join(OUT, "placement-notes.tsv"), "w", encoding="utf-8") as fh:
        fh.write("id\tentry\tline_of_claim\tblock_kind\tblock_lines\tid_on_claim_line\tnote\n")
        fh.write("\n".join(notes) + "\n")
    print(f"pairs={len(pairs)} rows={len(lines)} files={len({e for _, e in pairs})}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
