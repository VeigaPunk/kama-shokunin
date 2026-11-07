#!/usr/bin/env python3
"""Build mutants/summary.tsv from the battery logs + survivor-forgeries receipt.

Columns: id, hunks (difflib non-equal opcode blocks, must be 1), sha256, verdict
(killed:<controls> | survived), first failing battery case, evidence line, forgery.
"""
import difflib
import re
from pathlib import Path

OUT = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-93/w1/out/MT02SetterCounterMutants")
base = (OUT / "mutants/m2-counter.py").read_text().split("\n")
base_cases = {}
for l in (OUT / "logs/m2-counter.out").read_text().splitlines():
    m = re.match(r"C2_CONTROL (\S+) as_expected=(\d)", l)
    if m:
        base_cases[m.group(1)] = int(m.group(2))

forg = {}
for l in (OUT / "logs/survivor-forgeries.out").read_text().splitlines():
    m = re.match(r"FORGERY (F\d+) (\S+) rc=\d+ green=(\d) as_expected=\d+ :: (SETTER_ROWS .*)$", l)
    if m:
        forg[m.group(2)] = (m.group(1), m.group(3), m.group(4))

rows = []
for f in sorted((OUT / "mutants").glob("*.py")):
    if f.stem == "m2-counter":
        continue
    text = f.read_text().split("\n")
    hunks = sum(1 for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, base, text).get_opcodes() if tag != "equal")
    log = (OUT / f"logs/{f.stem}.out").read_text()
    cases = {}
    for l in log.splitlines():
        m = re.match(r"C2_CONTROL (\S+) as_expected=(\d) rc=(\d)", l)
        if m:
            cases[m.group(1)] = (int(m.group(2)), int(m.group(3)))
    killed = [c for c in base_cases if cases.get(c, (1, 1))[0] == 0]
    ev = ""
    if killed:
        first = killed[0]
        block = []
        for l in log.splitlines():
            if l.startswith(f"C2_CONTROL {first} "):
                block = [l]
                continue
            if block and l.startswith("  "):
                block.append(l.strip())
            elif block and not l.startswith("  "):
                break
        unbound = [b for b in block if " unbound " in b]
        summ = [b for b in block if b.startswith("SETTER_ROWS")]
        ev = " | ".join(unbound[:2] + summ[:1])[:220]
        verdict = "killed:" + ",".join(killed)
    else:
        verdict = "survived"
        g = forg.get(f.stem)
        if g:
            ev = f"forgery {g[0]}: frozen rejects, mutant green={g[1]}"
        elif f.stem == "07-opt-index-last":
            ev = "no forgery: 0 population add_opt blocks with >1 long option (opts[0]==opts[-1])"
        elif f.stem == "11-min-pop-1":
            ev = "no forgery: pinned archive fixes population=48; len(prow)==n is the live guard"
    desc = f.read_text().split("\n")[0]  # not the spec; description comes from manifest
    rows.append((f.stem, str(hunks), __import__("hashlib").sha256(f.read_bytes()).hexdigest(), verdict, ev))

man = {}
for l in (OUT / "mutants/manifest.tsv").read_text().splitlines():
    p = l.split("\t")
    man[p[0]] = p[1]
with (OUT / "mutants/summary.tsv").open("w") as fh:
    fh.write("id\thunks\tsha256\tverdict\tdescription\tevidence\n")
    for r in rows:
        fh.write("\t".join([r[0], r[1], r[2], r[3], man.get(r[0], ""), r[4]]) + "\n")
print(f"mutants={len(rows)} survived={sum(1 for r in rows if r[3]=='survived')} "
      f"killed={sum(1 for r in rows if r[3]!='survived')} hunks_not_1={[r[0] for r in rows if r[1]!='1']}")
