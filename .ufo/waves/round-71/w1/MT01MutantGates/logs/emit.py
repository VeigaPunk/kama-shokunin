import json, hashlib
from pathlib import Path
S = Path("/fast/scratch/hyaku/kama-r71/MT01MutantGates")
W = Path("/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-71/w1/MT01MutantGates")
c1 = json.loads((S/"logs/c1-matrix-v2.json").read_text())
c2 = json.loads((S/"logs/c2-matrix-v2.json").read_text())
c3 = json.loads((S/"logs/c3-matrix.json").read_text())

def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

C1 = {
 "pre-report-gate-m1-exit0": ("result['exit'] = 0 (exit map gutted)", "selftest arms (a)-(f): all five defect arms exit=0 want 1; every external defect fixture also exits 0"),
 "pre-report-gate-m2-uncommitted0": ("uncommitted = 0 (ignore the round-dir count)", "selftest wave-uncommitted (uncommitted=0 want 1); fx-uncommitted prints failed=0 uncommitted=0"),
 "pre-report-gate-m3-fail-only-silent": ("arm ok = exit==0 or the arm printed anything", "selftest stale/missing/dirty/crlf arms (exit=0 want 1); the four external defect fixtures go green"),
 "pre-report-gate-m4-roundclean-ok": ("round-clean ok ignores the porcelain count", "selftest wave-uncommitted (failed=0 want 1, round-clean ok=True); fx-uncommitted failed=0"),
 "pre-report-gate-m5-failed0": ("failed = 0 hard-coded", "selftest five defect arms (failed=0); external defect fixtures print failed=0"),
 "pre-report-gate-m6-accept-dirty": ("worktree-landing nonzero accepted unless MISSING", "selftest dirty/crlf arms; external fx-dirty/fx-crlf print failed=0"),
}
C2 = {
 "census-waiver-boundary-m1-exit0": ("report exit_code = 0", "BAD, HOLE and LB exit 1 -> 0 (the report exit is gutted; `--selftest` computes its own exit and stays green)"),
 "census-waiver-boundary-m2-survivors0": ("survivors = 0", "HOLE: summary `killed=4 survivors=1` -> `killed=4 survivors=0` (exit 1 both; the survivors token is the only difference)"),
 "census-waiver-boundary-m3-killedfalse": ("killed = False per shim", "R (frozen counter) prints killed=0 survivors=5 exit=1; selftest shim arms fail"),
 "census-waiver-boundary-m4-drop-fail-waiver": ("waiver_never_covers_fail always held", "selftest case 6: `shim:s6w-waiver-swallows-failure:attributed` FAIL - the named check never fires (the shim stays killed by other checks)"),
 "census-waiver-boundary-m5-accepted-as-killed": ("killed = attributed = True", "HOLE: a compliant census in a shim slot is counted killed -> killed=5 survivors=0 exit=0"),
 "census-waiver-boundary-m6-landed-blind": ("held excludes case 7", "LB: defective landed census accepted, exit 1 -> 0"),
 "census-waiver-boundary-m7-drop-waiver-ne": ("waiver_keeps_not_evaluated always held", "none: no fixture zeroes not_evaluated under a waiver; SURVIVES"),
}
C3 = {
 "round71-province-host-claims-m1-accept-any": ("covering_correction drops date+verdict guards", "selftest flipped-verdict and shortcut-all-flipped; external flipped exit 1 -> 0"),
 "round71-province-host-claims-m2-ignore-verdict": ("drops the verdict-equality guard", "selftest flipped-verdict and shortcut-all-flipped; external flipped exit 1 -> 0"),
 "round71-province-host-claims-m3-wrong-tag": ("drops the tag-equality guard", "selftest flipped-verdict/shortcut/wrong-tag; external wrongtag exit 1 -> 0"),
 "round71-province-host-claims-m4-drop-rewritten": ("rewritten = []", "selftest rewritten-marker (REWRITTEN line absent); external rewritten fixture keeps exit 1 via uncovered=14"),
 "round71-province-host-claims-m5-uncovered0": ("uncovered = 0", "selftest base/flipped/shortcut/wrong-tag; external base exit 1 -> 0"),
 "round71-province-host-claims-m6-drop-date": ("drops the correction-date guard", "none: no same-or-earlier-dated correction fixture; SURVIVES"),
}

def diffdet(tool, tag, rec, pristine):
    if tool == "c1":
        diffs = []
        if (rec["ST"]["exit"], rec["ST"]["line"]) != (pristine["ST"]["exit"], pristine["ST"]["line"]):
            diffs.append("ST")
        for k, v in rec["FIX"].items():
            p = pristine["FIX"][k]
            if (v["exit"], v["line"]) != (p["exit"], p["line"]):
                diffs.append(k)
        return diffs
    if tool == "c2":
        diffs = []
        for d in ("ST", "R", "BAD", "HOLE", "LB"):
            r, p = rec[d], pristine[d]
            if d == "ST":
                if (r["exit"], r["line"]) != (p["exit"], p["line"]): diffs.append(d)
            elif r["exit"] != p["exit"] or r["line"] != p["line"]: diffs.append(d)
        return diffs
    diffs = []
    if (rec["ST"]["exit"], rec["ST"]["line"]) != (pristine["ST"]["exit"], pristine["ST"]["line"]): diffs.append("ST")
    for k, v in rec["FIX"].items():
        p = pristine["FIX"][k]
        if (v["exit"], v["line"], tuple(v["rewritten"])) != (p["exit"], p["line"], tuple(p["rewritten"])):
            diffs.append(k)
    return diffs

rows = []
for tool, mat, meta in (("c1", c1, C1), ("c2", c2, C2), ("c3", c3, C3)):
    pr = mat["pristine"]
    for tag, rec in mat.items():
        if tag == "pristine": continue
        change, why = meta[tag]
        diffs = diffdet(tool, tag, rec, pr)
        verdict = "KILLED" if diffs else "SURVIVED"
        rows.append((tool.upper(), tag, change, verdict, ",".join(diffs) or "-", why))
with open(W/"mutants.tsv", "w") as f:
    f.write("tool\tmutant\tchange\tverdict\tchanged_detectors\tkilling_check\n")
    for r in rows: f.write("\t".join(r) + "\n")
print("wrote", W/"mutants.tsv", len(rows), "rows")
for r in rows: print(r[0], r[1], r[3], r[4])
