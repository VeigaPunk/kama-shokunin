#!/usr/bin/env python3
"""Round-50 lesson, Gate rows: is each quoted sentence verbatim in its source copy,
and is it <= 25 words?  Also checks the SOURCES.md row quote against the copy (the
row's own quote is a claim like any other)."""
import re

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
COPIES = {
    "S496": f"{LANE}/.ufo/waves/round-50/c1/proc_pid_maps.5.txt",
    "S497": f"{LANE}/.ufo/waves/round-50/c1/PR_SET_PDEATHSIG.2const.txt",
    "S498": f"{LANE}/.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt",
}
GATE = {
    "S496": "dev is the device (major:minor); inode is the inode on that device.",
    "S497": ("The parent-death signal is sent upon subsequent termination of the parent thread "
             "and also upon termination of each subreaper process"),
    "S498": "A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~).",
}
ROW = {
    "S496": "dev is the device (major:minor); inode is the inode on that device",
    "S497": ("The parent-death signal is sent upon subsequent termination of the parent thread "
             "and also upon termination of each subreaper process ... to which the caller is "
             "subsequently reparented."),
    "S498": "A code fence is a sequence of at least three consecutive backtick characters or tildes.",
}


def norm(p):
    return re.sub(r"\s+", " ", open(p, encoding="utf-8", errors="replace").read())


bad = 0
for row in ("S496", "S497", "S498"):
    body = norm(COPIES[row])
    q = GATE[row]
    words = len(q.split())
    ok_len = words <= 25
    present = q in body
    # the row's own quote: strip the ellipsis form and test each quoted fragment
    frag = ROW[row].replace(" ... ", " ")
    row_present = frag in body
    row_present_parts = True
    if not row_present:
        parts = [x.strip() for x in ROW[row].split("...")]
        row_present_parts = all(x and x in body for x in parts)
    print("%s gate quote: words=%d <=25=%s verbatim=%s" % (row, words, ok_len, present))
    print("%s row quote (%s...): verbatim=%s verbatim_in_parts=%s"
          % (row, ROW[row][:48].replace("\n", " "), row_present, row_present_parts))
    if not (ok_len and present):
        bad += 1
print("RESULT gate_quotes_bad=%d" % bad)
raise SystemExit(1 if bad else 0)
