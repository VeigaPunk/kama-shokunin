#!/usr/bin/env python3
"""R42D07 summarize: classify counter mutants from the persisted out/ receipts.
Run after fleet.py's run phase; overwrites artifacts/matrix.tsv and
artifacts/classification.tsv with correctly parsed results."""
import os, re, sys

SEAT = "/fast/scratch/kama-r42/seats/R42D07"
OUT = f"{SEAT}/out"
LANE = "/fast/scratch/kama-r42/clone/.ufo/waves/round-42"

C2_STATES = ["BASE", "CAND", "TIP", "R-FREEZE", "R-STUB", "R-ALLUNV", "R-SEPC1", "R-SEPC2",
             "P-M01", "P-M02", "P-M03", "P-M13", "P-M05", "P-M11"]
C3_STATES = ["BASE", "CAND", "TIP", "R-FREEZE", "R-ROWSONLY", "R-STAGEDVERBATIM", "R-SEPC3",
             "P-N01", "P-N03", "P-N06", "P-N07", "P-N08", "P-N09", "P-N10", "P-N13",
             "TIP@CAND", "TIP@BN12"]
C2MUT_STATES = ["BASE", "CAND", "TIP", "R-STUB", "R-ALLUNV", "R-SEPC2"]
C2MUT_PROBE = {"M01": ["P-M01"], "M02": ["P-M02"], "M14": ["P-M02"], "M03": ["P-M03"],
               "M13": ["P-M13"], "M05": ["P-M05"], "M11": ["P-M11"], "M10": ["P-M10"]}
C3MUT_STATES = ["BASE", "CAND", "TIP", "R-ROWSONLY", "R-STAGEDVERBATIM", "R-SEPC3"]
C3MUT_PROBE = {"N01": ["P-N01"], "N02": ["TIP@CAND"], "N03": ["P-N03"], "N06": ["P-N06"],
               "N07": ["P-N07"], "N08": ["P-N08"], "N09": ["P-N09"], "N10": ["P-N10"],
               "N12": ["TIP@BN12"], "N13": ["P-N13"]}
C2_NEG = ["BASE", "R-FREEZE", "R-STUB", "R-ALLUNV", "R-SEPC1"]
C3_NEG = ["BASE", "R-FREEZE", "R-ROWSONLY", "R-STAGEDVERBATIM"]
RECEIPT = {
    ("BASE", "c2"): "controls/base.c2.out", ("BASE", "c3"): "controls/base.c3.out",
    ("CAND", "c2"): "c2/candidate.out", ("CAND", "c3"): "c3/candidate.out",
    ("R-FREEZE", "c2"): "controls/freeze.c2.out", ("R-FREEZE", "c3"): "controls/freeze.c3.out",
    ("R-STUB", "c2"): "controls/junk-c2-stub.c2.out",
    ("R-ALLUNV", "c2"): "controls/junk-c2-allunverifiable.c2.out",
    ("R-SEPC1", "c2"): "controls/sep-c1-only.c2.out",
    ("R-SEPC2", "c2"): "controls/sep-c2-only.c2.out",
    ("R-ROWSONLY", "c3"): "controls/junk-c3-rowsonly.c3.out",
    ("R-STAGEDVERBATIM", "c3"): "controls/junk-c3-stagedverbatim.c3.out",
    ("R-SEPC3", "c3"): "controls/sep-c3-only.c3.out",
}

def norm_receipt(text):
    lines = [l for l in text.split("\n") if not l.startswith("tip=")]
    return re.sub(r"\['r41[^]]*\]", "[X]", "\n".join(lines))

def parse_out(path):
    met, legs, rest, rc = None, "", [], None
    for l in open(path):
        l = l.rstrip("\n")
        if l.startswith("exit="):
            rc = l[5:]
            continue
        m = re.search(r"met=(True|False)", l)
        if m and "=" in l.split(" met=")[0]:
            met = m.group(1)
            legs = l.split(" met=")[0]
        elif not l.startswith("tip="):
            rest.append(l)
    return met, legs, "\n".join(rest), rc

def main():
    R = {}  # (kind, tag, state) -> (met, legs, rest, rc)
    for fn in os.listdir(OUT):
        m = re.match(r"(.+)\.(.+)\.(c2|c3)\.out$", fn)
        if m:
            tag, state, kind = m.groups()
            R[(kind, tag, state)] = parse_out(os.path.join(OUT, fn))
    # validation
    print("== reconstruction validation (pristine vs committed receipts)")
    valid = {}
    for (state, kind), rel in RECEIPT.items():
        key = (kind, "pristine", state)
        if key not in R:
            print(f"  {state}.{kind}: NO PRISTINE RUN")
            valid[(state, kind)] = False
            continue
        met, legs, rest, rc = R[key]
        want = norm_receipt(open(os.path.join(LANE, rel)).read())
        got = norm_receipt(open(os.path.join(OUT, f"pristine.{state}.{kind}.out")).read())
        okk = got == want
        valid[(state, kind)] = okk
        print(f"  {state}.{kind}: {'OK' if okk else 'MISMATCH vs ' + rel}")
    for kind in ("c2", "c3"):
        key = (kind, "pristine", "TIP")
        if key in R:
            print(f"  pristine {kind} at claim tip: met={R[key][0]} exit={R[key][3]}")
    # pristine baseline at probe states (must be met=False for the probe to be valid)
    print("== probe baselines (pristine must read met=False)")
    probe_ok = {}
    for (kind, tag, state), (met, legs, rest, rc) in sorted(R.items()):
        if tag == "pristine" and state.startswith(("P-", "TIP@")):
            probe_ok[(kind, state)] = met == "False"
            print(f"  {kind} {state}: met={met} exit={rc} {'OK' if met == 'False' else 'PROBE INVALID'}")

    muts = sorted({t for (k, t, s) in R if t != "pristine"})
    mrows = ["mut\tkind\tstate-results (met / legs-diff)"]
    crows = ["mut\tkind\tclaim\tbaseaccept\texposed_by_committed_control\tpositivebroken\t"
             "probeaccepts\tmet_invisible_on_committed_suite"]
    for m in muts:
        kind = "c2" if m.startswith("M") else "c3"
        states = (C2MUT_STATES + C2MUT_PROBE.get(m, [])) if kind == "c2" else \
                 (C3MUT_STATES + C3MUT_PROBE.get(m, []))
        met, legs = {}, {}
        for s in states:
            key = (kind, m, s)
            if key in R:
                met[s], legs[s] = R[key][0], R[key][1]
        claim = ("OK" if met.get("CAND") == "True" and met.get("TIP") == "True"
                 else "INCONCLUSIVE" if met.get("CAND") is None or met.get("TIP") is None
                 else "BROKEN")
        baseacc = met.get("BASE") == "True"
        exposed = [s for s in C2_NEG if kind == "c2" and met.get(s) == "True" and valid.get((s, kind), True)] + \
                  [s for s in C3_NEG if kind == "c3" and met.get(s) == "True" and valid.get((s, kind), True)]
        pos = "R-SEPC2" if kind == "c2" else "R-SEPC3"
        posbroken = met.get(pos) == "False"
        probes = (C2MUT_PROBE.get(m, []) if kind == "c2" else C3MUT_PROBE.get(m, []))
        probeacc = [s for s in probes if met.get(s) == "True" and probe_ok.get((kind, s), False)]
        invisible = claim == "OK" and not baseacc and not exposed and not posbroken
        # leg-level diffs vs pristine at the same state
        diffs = []
        for s in states:
            pk = (kind, "pristine", s)
            if s in legs and pk in R and R[pk][1] and legs[s] and R[pk][1] != legs[s]:
                a = dict(kv.split("=") for kv in R[pk][1].split())
                b = dict(kv.split("=") for kv in legs[s].split())
                dl = [f"{k}:{a.get(k)}->{b.get(k)}" for k in sorted(set(a) | set(b))
                      if a.get(k) != b.get(k)]
                diffs.append(f"{s}[{','.join(dl)}]")
        mrows.append(f"{m}\t{kind}\t" + "; ".join(
            f"{s}={met.get(s, '-')}" + (f" ({d})" if (d := next((x for x in diffs if x.startswith(s + '[')), None)) else "")
            for s in states))
        crows.append(f"{m}\t{kind}\t{claim}\t{baseacc}\t{exposed or '-'}\t{posbroken}\t"
                     f"{probeacc or '-'}\t{invisible}")
    open(f"{SEAT}/artifacts/matrix.tsv", "w").write("\n".join(mrows) + "\n")
    open(f"{SEAT}/artifacts/classification.tsv", "w").write("\n".join(crows) + "\n")
    print("\n== classification")
    print("\n".join(crows[1:]))
    inv = [r.split("\t") for r in crows[1:] if r.split("\t")[7] == "True"]
    print(f"\n== DELIVERABLE: met-invisible survivors (no committed control kills): "
          f"{[r[0] for r in inv]}")
    print("FLEET-SUMMARY-DONE")
    return 0

if __name__ == "__main__":
    sys.exit(main())
