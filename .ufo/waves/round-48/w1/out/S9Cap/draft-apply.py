#!/usr/bin/env python3
"""S9Cap round-48 capability draft: canonical block + head mirror + PROVINCE token.

Reads <out>/round48-canonical-block.md, derives the two reworded rows, then edits
SCORECARD.md and PROVINCE.md in the scratch clone:
  1. PROVINCE.md - the round-42 reconcile `province` fact needs every tools/ token a
     canon row cites to appear there; the round-48 C1 counter is new.
  2. SCORECARD.md - the head `## Axes` coverage row pins PROVINCE.md's sha256, so the
     PROVINCE edit moves that digest (line count is unchanged: no line is added).
  3. SCORECARD.md - head `## Capabilities` mirror intro names the round it mirrors.
  4. SCORECARD.md - the two mirror rows, keyed by row name, inside the head section
     only; the historical and earlier-round tables keep their bytes.
  5. SCORECARD.md - the round-48 canonical block appended at EOF.
Writes the proposed full text and unified diffs. No git calls.
"""
import difflib
import hashlib
import os
import sys

OUT = ("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap"
       if len(sys.argv) < 3 else sys.argv[2])
LANE = sys.argv[1]  # scratch clone root
OLD_INTRO = ("Mirror of the round-47 canonical capability list that \u00a7Round 47 carries")
NEW_INTRO = ("Mirror of the round-48 canonical capability list that \u00a7Round 48 carries"
             " (a mirror, not the canonical source: the counters resolve the highest-numbered"
             " canonical heading below this line). Registry counts are not restated here:"
             " `scripts/sources-census.sh census --file corpus/SOURCES.md` derives them.")
OLD_PV_SHA = "929f3e3eef20fa90429ca0c5a96a63821cff6aeca912ac55bad3a82b4bd3a079"

SRC = "/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-48/w1/out/S9Cap"
block = open(os.path.join(SRC, "round48-canonical-block.md"), encoding="utf-8").read()
block_rows = {}
for line in block.split("\n"):
    if line.startswith("| ") and line.count("|") >= 5:
        name = line.split("|")[1].strip().strip("`")
        if name and name != "Capability":
            block_rows[name] = line
assert len(block_rows) == 11, len(block_rows)


def udiff(old, new, rel):
    d = difflib.unified_diff(old.split("\n"), new.split("\n"),
                             fromfile="a/" + rel, tofile="b/" + rel, n=2, lineterm="")
    open(os.path.join(OUT, "proposed-%s.diff" % rel.split(".")[0]), "w",
         encoding="utf-8").write("\n".join(d) + "\n")


# ---- PROVINCE.md -------------------------------------------------------------
PPATH = os.path.join(LANE, "PROVINCE.md")
pold = open(PPATH, encoding="utf-8").read()
POLD = "`tools/round47-append-audit-v2-check.py` (append-only audit of the"
PNEW = ("`tools/round47-append-audit-v2-check.py`, `tools/round48-append-audit-v3-check.py`"
        " (append-only audit of the")
POLD2 = "round 46, v2 round 47); `tools/kama-live-replay.py`"
PNEW2 = ("round 46, v2 round 47, v3 round 48 with per-row regions, binding declarations"
         " and `regressed` in the exit semantics); `tools/kama-live-replay.py`")
assert pold.count(POLD) == 1 and pold.count(POLD2) == 1
pnew = pold.replace(POLD, PNEW).replace(POLD2, PNEW2)
open(os.path.join(OUT, "PROVINCE.md.proposed"), "w", encoding="utf-8").write(pnew)
udiff(pold, pnew, "PROVINCE.md")
new_pv_sha = hashlib.sha256(pnew.encode()).hexdigest()
assert pold.count("\n") == pnew.count("\n"), "PROVINCE line count moved"
open(PPATH, "w", encoding="utf-8").write(pnew)

# ---- SCORECARD.md -----------------------------------------------------------
path = os.path.join(LANE, "SCORECARD.md")
old = open(path, encoding="utf-8").read()
lines = old.split("\n")

changed = 0
for i, line in enumerate(lines):
    if OLD_PV_SHA in line:
        lines[i] = line.replace(OLD_PV_SHA, new_pv_sha)
        changed += 1
assert changed == 1, changed

# head mirror only: the first "## Capabilities" section up to the next "## " heading
start = lines.index("## Capabilities")
end = next(i for i in range(start + 1, len(lines)) if lines[i].startswith("## "))
mirrored = 0
for i in range(start, end):
    line = lines[i]
    if line.startswith(OLD_INTRO):
        lines[i] = NEW_INTRO
        mirrored += 1
    elif line.startswith("| ") and line.count("|") >= 5:
        name = line.split("|")[1].strip().strip("`")
        if name in block_rows and block_rows[name] != line:
            lines[i] = block_rows[name]
            mirrored += 1
assert mirrored == 3, mirrored

new = "\n".join(lines)
assert new.endswith("\n"), "unexpected tail"
new += "\n" + block

open(os.path.join(OUT, "SCORECARD.md.proposed"), "w", encoding="utf-8").write(new)
udiff(old, new, "SCORECARD.md")
open(path, "w", encoding="utf-8").write(new)
print("mirror_edits=%d head_digest_edits=%d province_edits=2 block_bytes=%d new_pv_sha=%s"
      % (mirrored, changed, len(block), new_pv_sha))
