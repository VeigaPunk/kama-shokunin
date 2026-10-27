#!/usr/bin/env python3
"""consolidated.py - independent count assertion audit of SCORECARD.md + SHONEN.md at one revision.

Every check derives its value from the tree at the same revision; no lane tool is
imported. Prints one PASS/FAIL line per assertion and exits 1 on any FAIL.
"""
from __future__ import annotations
import collections, csv, glob, io, os, re, subprocess, sys

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REV = sys.argv[1] if len(sys.argv) > 1 else None

def show(path):
    if REV:
        return subprocess.run(["git", "-C", LANE, "show", f"{REV}:{path}"],
                              capture_output=True, text=True).stdout
    return open(os.path.join(LANE, path)).read()

def ls(rev, path):
    return subprocess.run(["git", "-C", LANE, "ls-tree", "--name-only", rev, path],
                          capture_output=True, text=True).stdout.split("\n")

sc = show("SCORECARD.md")
shonen = show("SHONEN.md")
fails = 0
def chk(name, asserted, derived, note=""):
    global fails
    ok = asserted == derived
    fails += 0 if ok else 1
    print(f"{'PASS' if ok else 'FAIL'} {name}: asserted={asserted!r} derived={derived!r} {note}")

def table_after(marker_re):
    lines = sc.split("\n")
    for i, l in enumerate(lines):
        if re.search(marker_re, l, re.I):
            rows = []
            for l2 in lines[i + 1:]:
                if l2.startswith("|"):
                    rows.append([c.strip() for c in l2.strip().strip("|").split("|")])
                elif rows:
                    break
            return rows[2:] if len(rows) >= 2 else []
    return []

AX = {"operability", "freshness", "depth", "coverage", "calibration", "adjacency"}
axes = {}
for l in sc.split("\n")[sc.split("\n").index("## Axes"):]:
    if l.startswith("#") and axes:
        break
    if l.startswith("|") and len(l.strip().strip("|").split("|")) == 4:
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        n = c[0].strip("* ").split(" ")[0].lower()
        if n in AX and n not in axes:
            axes[n] = int(re.findall(r"\d+", c[1])[-1])
print("axes_derived=", axes)

# canonical capability table: highest "canonical list as of round N"
best, crows = -1, []
lines = sc.split("\n")
for i, l in enumerate(lines):
    m = re.search(r"canonical list as of round\s+(\d+)\*\*", l, re.I)
    if m and int(m.group(1)) > best:
        best = int(m.group(1))
        rows = []
        for l2 in lines[i + 1:]:
            if l2.startswith("|"):
                rows.append([c.strip() for c in l2.strip().strip("|").split("|")])
            elif rows:
                break
        crows = rows[2:] if len(rows) >= 2 else []
cnames = [r[0].strip("` *") for r in crows]
cfirst = [int(re.findall(r"\d+", r[3])[-1]) for r in crows]
print(f"canonical_round={best} canonical_rows={len(crows)}")

# ---- checks ----
chk("axes_count(Retired '6 axes')", 6, len(axes))
m = re.search(r"(\d+) capabilities remain active", sc)
chk("capabilities_count(Retired)", int(m.group(1)) if m else None, len(cnames))

sat = "\n".join(sc.split("## Saturation")[1].split("## ")[0].split("\n")[:6])
mvec = re.search(r"score vector ([^.]+?) \(from", sat)
if mvec:
    pairs = re.findall(r"([a-z]+) (\d+)", mvec.group(1))
    chk("saturation_vector", dict(pairs), {k: str(v) for k, v in axes.items()})
mfirst = re.search(r"first-working rounds ([0-9, ]+) \(", sat)
if mfirst:
    chk("saturation_first_rounds", [int(x) for x in re.findall(r"\d+", mfirst.group(1))], cfirst)

# banner: highest Round section that cites its own .ufo/waves/round-N/measured/ receipt dir
secs = re.split(r"^## Round (\d+)", sc, flags=re.M)
measured = [int(secs[i]) for i in range(1, len(secs) - 1, 2)
            if f".ufo/waves/round-{int(secs[i])}/measured/" in secs[i + 1]]
chk("latest_measured_round", int(re.search(r"Latest measured round: (\d+)", sc).group(1)), max(measured),
    f"(max Round heading={max(int(x) for x in re.findall(r'^## Round (\d+)', sc, re.M))})")

# calibration glob count
m = re.search(r"verifier-spotcheck\.md'\)+\)\"` → `(\d+)`", sc)
if m:
    if REV:
        n = len([x for x in ls(REV, "corpus/lessons/") if x.endswith("verifier-spotcheck.md")])
    else:
        n = len(glob.glob(os.path.join(LANE, "corpus/lessons/*verifier-spotcheck.md")))
    chk("calibration_spotcheck_glob", int(m.group(1)), n)

# freshness window
fr = [l for l in sc.split("\n") if l.startswith("| **freshness**")][0]
bound = int(re.search(r"<=( \d+|\d+)", fr).group(1))
fassert = int(re.search(r"recheck.*?→ `(\d+)`", fr).group(1))
src = show("corpus/SOURCES.md")
rows = [l for l in src.split("\n") if re.match(r"^\|\s*S\d+\s*\|", l)]
ids = [int(re.match(r"^\|\s*S(\d+)\s*\|", l).group(1)) for l in rows]
rcall = sum(1 for l in rows if len(l.split("|")) > 11 and l.split("|")[10].strip())
rcwin = sum(1 for l in rows if int(re.match(r"^\|\s*S(\d+)\s*\|", l).group(1)) <= bound
            and len(l.split("|")) > 11 and l.split("|")[10].strip())
chk("freshness_window_count", fassert, rcwin, f"(bound=S{bound})")
_stale = rcwin == rcall
fails += 0 if _stale else 1
print(f"{'PASS' if _stale else 'FAIL'} freshness_scope_binds_live_registry: "
      f"window_asserted={rcwin} full_registry={rcall} rows={len(ids)} max=S{max(ids)} "
      f"excluded={len([i for i in ids if i > bound])}")

# depth / coverage / adjacency counts
def after_fact(cell, needle):
    m = re.search(re.escape(needle) + r".{0,600}?→ `(\d+)`", cell, re.S)
    return int(m.group(1)) if m else None
rowcell = lambda name: [l for l in sc.split("\n") if l.startswith("|") and len(l.strip().strip("|").split("|")) == 4
                        and l.strip().strip("|").split("|")[0].strip("* ").split(" ")[0].lower() == name][0]
dep = rowcell("depth"); cov = rowcell("coverage"); adj = rowcell("adjacency")
chk("depth_heading_count", after_fact(dep, "grep -c '^## ' SKILL.md"),
    len(re.findall(r"^## ", show("SKILL.md"), re.M)))
if REV:
    know = [x for x in ls(REV, "corpus/knowledge/")
            if x.endswith(".md") and "engine-sides" not in x and "processes" not in x]
else:
    know = [f for f in glob.glob(os.path.join(LANE, "corpus/knowledge/*.md"))
            if "engine-sides" not in f and "processes" not in f]
chk("coverage_knowledge_count", after_fact(cov, "corpus/knowledge/*.md"), len(know))
chk("adjacency_pipe_count", after_fact(adj, "cross-lane-scope.md"),
    sum(1 for l in show("corpus/knowledge/cross-lane-scope.md").split("\n") if l.startswith("|")))

# ledgers
vrows = list(csv.DictReader(io.StringIO(show("registry/verdict-ledger.tsv")), delimiter="\t"))
crows2 = list(csv.DictReader(io.StringIO(show("registry/claim-outcome-ledger.tsv")), delimiter="\t"))
chk("verdict_ledger_rows", 204, len(vrows))
chk("claim_outcome_ledger_rows", 126, len(crows2))
d = collections.defaultdict(dict)
for r in vrows:
    d[(r["round"], r["trend"])][r["side"]] = r["verdict"]
ORDER = {"harmed": 0, "unchanged": 1, "unprovable": 2, "unprovable-but-better": 3, "improved": 4}
cls = collections.Counter()
for v in d.values():
    s, o = v.get("self"), v.get("outside")
    if "absent" in (s, o): cls["absent"] += 1
    elif s == o: cls["agreement"] += 1
    elif ORDER.get(s, 9) > ORDER.get(o, 9): cls["overclaim"] += 1
    elif ORDER.get(s, 9) < ORDER.get(o, 9): cls["underclaim"] += 1
    else: cls["other"] += 1
chk("verdict_tally_agreement", (69, 87), (cls["agreement"], len(d) - cls["absent"]))
chk("verdict_tally_overclaim", 2, cls["overclaim"])
chk("verdict_tally_underclaim", 16, cls["underclaim"])
chk("verdict_tally_other", 0, cls["other"])
chk("verdict_tally_absent", 15, cls["absent"])

d2 = collections.defaultdict(dict)
for r in crows2:
    d2[(r["round"], r["claim"])][r["side"]] = r["outcome"]
co = {"met": 3, "partial": 2, "unprovable": 1, "not-met": 0, "absent": -1, "mixed": 99}
c2 = collections.Counter()
for v in d2.values():
    s, o = v.get("self"), v.get("outside")
    if "absent" in (s, o): c2["absent"] += 1
    elif "mixed" in (s, o): c2["other"] += 1
    elif s == o: c2["agreement"] += 1
    elif co.get(s, 9) > co.get(o, 9): c2["overclaim"] += 1
    else: c2["underclaim"] += 1
chk("claim_tally_agreement", (58, 61), (c2["agreement"], len(d2) - c2["absent"] - c2["other"]))
chk("claim_tally_overclaim", 1, c2["overclaim"])
chk("claim_tally_underclaim", 2, c2["underclaim"])
chk("claim_tally_other", 1, c2["other"])
chk("claim_tally_absent", 1, c2["absent"])

# capability mirror names
mirror = table_after(r"^## Capabilities\s*$")
mnames = [r[0].strip("` *") for r in mirror]
chk("capability_mirror_names", sorted(cnames), sorted(mnames))

# SHONEN receipt check counts
for label, path, want in (("r16 live receipt", ".ufo/waves/round-16/live/receipt.json", 10),
                          ("r17 receipt-1", ".ufo/waves/round-17/live/receipt-1.json", 11),
                          ("r17 receipt-2", ".ufo/waves/round-17/live/receipt-2.json", 11),
                          ("r17 receipt-3", ".ufo/waves/round-17/live/receipt-3.json", 11)):
    import json
    try:
        n = len(json.loads(show(path))["checks"])
    except Exception as e:
        n = f"error:{e}"
    chk(f"shonen_{label}_checks", want, n)
chk("shonen_r16_claimed", "10/10", re.search(r"(\d+/\d+) `kama-llamacpp-live/v1`", shonen).group(1))
chk("shonen_r17_claimed", "11/11", re.search(r"\((\d+/\d+) checks each", shonen).group(1))

print(f"FAILURES={fails}")
sys.exit(0 if fails == 0 else 1)
