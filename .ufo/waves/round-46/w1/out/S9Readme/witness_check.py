#!/usr/bin/env python3
"""Witness feasibility at b11906 for the three b11889 holds-reworded rows."""
import csv, re, subprocess
B = "/fast/scratch/hyaku/kama-r46/L1/llama.git"
LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
REL = "4d71b42fd87db24b8b7c808c151b713aa4459cfd"
def show(c, p):
    return subprocess.run(["git", "-C", B, "show", f"{c}:{p}"], capture_output=True, text=True).stdout
def ws(s):
    return re.sub(r"\s+", " ", s).strip()
def rtext(t, spec):
    L = t.splitlines(); out = []
    for el in spec.split(","):
        a, _, b = el.partition("-"); a = int(a); b = int(b or a); out.extend(L[a-1:b])
    return out
rows = {r["id"]: r for r in csv.DictReader(open(LANE + "/registry/release-recheck-b11889.tsv"), delimiter="\t")}
for rid in ("S037", "S043", "S108"):
    r = rows[rid]
    pin = show(r["pin_commit"], r["path"]); rel = show(REL, r["path"])
    P = rtext(pin, r["pin_lines"]); R = rtext(rel, r["release_lines"])
    PF = ws(pin); RF = ws(rel)
    wp = [ws(x) for x in P if len(ws(x)) >= 12 and ws(x) not in RF]
    wn = [ws(x) for x in R if len(ws(x)) >= 12 and ws(x) not in PF]
    print(f"{rid} witness_pin_candidates={len(wp)} witness_new_candidates={len(wn)} note_len={len(r['note'])}")
    print(f"  witness_pin: {wp[0] if wp else '-'}")
    print(f"  witness_new: {wn[0] if wn else '-'}")
