#!/usr/bin/env python3
"""Census of the lane's real SCORECARD.md at the freeze commit: every line the
frozen selector drops (fence, comment, correction) that matches a cell shape, every
fence opener with a backtick in its info string, every fence/comment left open at
EOF, and the first rendered cells. Reads committed bytes only (git show)."""
import importlib.util
import pathlib
import re
import subprocess
import sys

SCRATCH = pathlib.Path("/fast/scratch/hyaku/kama-r86/EX01RenderedSelector")
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REV = "c07e1f909414aafb2d8de5605a81fd3bd4e3550e"

raw = subprocess.run(["git", "-C", LANE, "show", f"{REV}:SCORECARD.md"], text=True,
                     capture_output=True, check=True).stdout
(SCRATCH / "receipts" / "scorecard-at-freeze.md").write_text(raw)
spec = importlib.util.spec_from_file_location(
    "r86", subprocess.run(["git", "-C", LANE, "rev-parse", "--show-toplevel"], text=True,
                          capture_output=True).stdout.strip() + "/tools/round86-rendered-cells.py")
# the instrument is loaded from the lane working tree only for its pure functions; its bytes are
# identical to the freeze commit (see identity receipt), checked before import.
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

lines = raw.splitlines()
rendered_text = mod.rendered(raw)
rendered_set = set(rendered_text.splitlines())

CELL = re.compile(r"^\*\*Current authority \(round [0-9]+\):|^\|\s*calibration\s*\|")
print(f"lines={len(lines)} rendered_lines={len(rendered_text.splitlines())}")

dropped_cells = []
for i, line in enumerate(lines, 1):
    if CELL.search(line.lstrip()) and line not in rendered_set:
        dropped_cells.append((i, line[:90]))
print(f"cell-shaped lines dropped by rendered(): {len(dropped_cells)}")
for i, t in dropped_cells[:6]:
    print(f"  L{i}: {t}")
if len(dropped_cells) > 6:
    print(f"  ... {len(dropped_cells) - 6} more")

kept_cells = [(i, l[:110]) for i, l in enumerate(lines, 1)
              if CELL.search(l) and l in rendered_set]
print(f"column-0 cell-shaped lines kept by rendered(): {len(kept_cells)}")
for i, t in kept_cells[:12]:
    print(f"  L{i}: {t}")

# fences: opener/closer walk with CommonMark run-length and char rules
opens = []
state = None
for i, line in enumerate(lines, 1):
    m = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
    if state is None:
        if m:
            info = m.group(2)
            if m.group(1)[0] == "`" and "`" in info:
                opens.append((i, "BACKTICK-IN-INFO-NOT-A-FENCE-COMMONMARK", line[:80]))
                continue
            state = (m.group(1)[0], len(m.group(1)), i)
    else:
        c = re.match(r"^ {0,3}(`{3,}|~{3,})\s*$", line)
        if c and c.group(1)[0] == state[0] and len(c.group(1)) >= state[1]:
            state = None
if state is not None:
    opens.append((state[2], "UNCLOSED-AT-EOF", ""))
print(f"fence anomalies (backtick-in-info or unclosed at EOF): {len(opens)}")
for entry in opens:
    print(f"  L{entry[0]}: {entry[1]} {entry[2]}")

comment_open = sum(l.count("<!--") for l in lines)
comment_close = sum(l.count("-->") for l in lines)
print(f"comment markers: opens={comment_open} closes={comment_close}")
print(f"correction headings: {sum(1 for l in lines if mod.CORRECTION.match(l))}")
print(f"first col-0 authority lines: {[i for i, l in enumerate(lines, 1) if mod.AUTHORITY.match(l)][:3]}")
print(f"first col-0 calibration rows: {[i for i, l in enumerate(lines, 1) if mod.CALIBRATION.match(l)][:3]}")
print(f"'## Axes' headings: {[i for i, l in enumerate(lines, 1) if l.strip() == '## Axes']}")
print(f"blockquote lines (any '>' at col 0): {sum(1 for l in lines if l.startswith('>'))}")
print(f"indented (4+ spaces) non-blank lines: {sum(1 for l in lines if re.match(r'^ {4,}\S', l))}")
