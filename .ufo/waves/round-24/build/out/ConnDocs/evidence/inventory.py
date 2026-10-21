#!/usr/bin/env python3
"""Enumerate every cross-document callsite that states or pins the round-23
blanket partial-clone refusal. Read-only over the lane tree.

Output TSV columns:
  id  file  line  kind  text
kind in {refusal-list, trade, pin, verdict-trend, open-item, protection, none}
"""
import re
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/kama-shokunin")
DOCS = ["SKILL.md", "README.md", "SCORECARD.md", "corpus/README.md",
        "corpus/QUALITY.md", "corpus/lessons/round-23.md",
        "corpus/lessons/round-24.md",
        "corpus/knowledge/error-is-not-a-verdict.md"]

PATTERNS = [
    ("refusal-list", re.compile(r"partial clone|promisor|partialclone|blobless", re.I)),
    ("pin", re.compile(r"population|f29fab8d|da5041a8|13 controls|31 single-literal|30/31|26/26|13/13|4/4", re.I)),
    ("trend", re.compile(r"quality \*\*improved|quality.*harmed|operability is \*\*traded|rejected-harmed", re.I)),
    ("trust", re.compile(r"untrusted|trusted lane|trusted repositor|KQ32", re.I)),
]

def main():
    rows = []
    for d in DOCS:
        p = LANE / d
        if not p.exists():
            rows.append(("MISSING", d, 0, "none", "file absent"))
            continue
        for i, line in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
            hits = {k for k, rx in PATTERNS if rx.search(line)}
            if "refusal-list" in hits:
                kind = "refusal-list"
            elif "trend" in hits:
                kind = "verdict-trend"
            elif "pin" in hits:
                kind = "pin"
            elif "trust" in hits:
                kind = "protection"
            else:
                continue
            rows.append((d, d, i, kind, line.strip()))
    for d, f, i, kind, text in rows:
        print(f"{f}\t{i}\t{kind}\t{text}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
