#!/usr/bin/env python3
"""provenance.py - revision-bound stale-count provenance for the SCORECARD `## Axes` rows."""
import re, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"

def g(*args):
    return subprocess.run(["git", "-C", LANE, *args], capture_output=True, text=True).stdout

def row(sc, name):
    for l in sc.split("\n"):
        if l.startswith("|") and len(l.strip().strip("|").split("|")) == 4:
            c = [x.strip() for x in l.strip().strip("|").split("|")]
            if c[0].strip("* ").split(" ")[0].lower() == name:
                return c[2]
    return ""

def probe(rev):
    sc = g("show", f"{rev}:SCORECARD.md")
    cal, fresh = row(sc, "calibration"), row(sc, "freshness")
    m = re.search(r"verifier-spotcheck\.md'\)+\)\"` → `(\d+)`", cal)
    asserted = int(m.group(1)) if m else None
    actual = len([x for x in g("ls-tree", "--name-only", rev, "corpus/lessons/").split("\n")
                  if x.endswith("verifier-spotcheck.md")])
    mb = re.search(r"<=( \d+|\d+)", fresh)
    bound = int(mb.group(1)) if mb else None
    mf = re.search(r"recheck.*?→ `(\d+)`", fresh)
    f_assert = int(mf.group(1)) if mf else None
    src = g("show", f"{rev}:corpus/SOURCES.md")
    rows = [l for l in src.split("\n") if re.match(r"^\|\s*S\d+\s*\|", l)]
    ids = [int(re.match(r"^\|\s*S(\d+)\s*\|", l).group(1)) for l in rows]
    def rc(cap=None):
        n = 0
        for l in rows:
            i = int(re.match(r"^\|\s*S(\d+)\s*\|", l).group(1))
            if cap and i > cap: continue
            if len(l.split("|")) > 11 and l.split("|")[10].strip(): n += 1
        return n
    excl = len([i for i in ids if bound and i > bound])
    print(f"rev={rev[:8]} calibration_row_asserted={asserted} spotcheck_blobs={actual} "
          f"cal_ok={asserted == actual}")
    print(f"          freshness_row_bound=S{bound} row_asserted={f_assert} window_count={rc(bound)} "
          f"registry_rows={len(ids)} registry_max=S{max(ids)} recheck_all={rc()} excluded={excl} "
          f"fresh_stale={rc(bound) != rc()}")

for rev in sys.argv[1:]:
    probe(rev)
