#!/usr/bin/env python3
"""R42D07 fleet: run pristine and mutated round-42 counters over the state
matrix, validate reconstructed states against committed receipts, classify
mutants. Read-only on every repo; all writes under the seat."""
import concurrent.futures, hashlib, os, re, subprocess, sys, traceback

SEAT = "/fast/scratch/kama-r42/seats/R42D07"
CLONE = f"{SEAT}/clone"
REPO = f"{SEAT}/fixtures/replay"  # holds lane history + all reconstructed states
OUT = f"{SEAT}/out"
LANE = "/fast/scratch/kama-r42/clone/.ufo/waves/round-42"
BASE = "0b606b03bf0b2a87b791aa537f6c72c941624cf0"
CAND = "c8c92db4bdf1c64357b995e0fe8d2a4f481fe995"
TIP = "3d9bd8d72366e281fab291874524130428ee423d"

revs = {}
for fn in ("replay.rev", "probes.rev"):
    for l in open(f"{SEAT}/{fn}"):
        if "=" in l:
            k, v = l.strip().split("=", 1)
            revs[k] = v
revs.setdefault("BASE", BASE); revs.setdefault("CAND", CAND); revs.setdefault("TIP", TIP)

C2_STATES = ["BASE", "CAND", "TIP", "R-FREEZE", "R-STUB", "R-ALLUNV", "R-SEPC1", "R-SEPC2",
             "P-M01", "P-M02", "P-M03", "P-M13", "P-M05", "P-M11"]
C3_STATES = ["BASE", "CAND", "TIP", "R-FREEZE", "R-ROWSONLY", "R-STAGEDVERBATIM", "R-SEPC3",
             "P-N01", "P-N03", "P-N06", "P-N07", "P-N08", "P-N09", "P-N10", "P-N13",
             "TIP@CAND", "TIP@BN12"]
C2MUT_STATES = ["BASE", "CAND", "TIP", "R-STUB", "R-ALLUNV", "R-SEPC2"]
C2MUT_PROBE = {"M01": ["P-M01"], "M02": ["P-M02"], "M14": ["P-M02"], "M03": ["P-M03"],
               "M13": ["P-M13"], "M05": ["P-M05"], "M11": ["P-M11"]}
C3MUT_STATES = ["BASE", "CAND", "TIP", "R-ROWSONLY", "R-STAGEDVERBATIM", "R-SEPC3"]
C3MUT_PROBE = {"N01": ["P-N01"], "N02": ["TIP@CAND"], "N03": ["P-N03"], "N06": ["P-N06"],
               "N07": ["P-N07"], "N08": ["P-N08"], "N09": ["P-N09"], "N10": ["P-N10"],
               "N12": ["TIP@BN12"], "N13": ["P-N13"]}
C2_NEG = ["BASE", "R-FREEZE", "R-STUB", "R-ALLUNV", "R-SEPC1",
          "P-M01", "P-M02", "P-M03", "P-M13", "P-M05", "P-M11"]
C2_POS = ["CAND", "TIP", "R-SEPC2"]
C3_NEG = ["BASE", "R-FREEZE", "R-ROWSONLY", "R-STAGEDVERBATIM",
          "P-N01", "P-N03", "P-N06", "P-N07", "P-N08", "P-N09", "P-N10", "P-N13",
          "TIP@CAND", "TIP@BN12"]
C3_POS = ["CAND", "TIP", "R-SEPC3"]
RECEIPT = {  # state -> (kind, receipt path relative to LANE)
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

def state_sha(s):
    if s == "TIP@CAND":
        return TIP, CAND
    if s == "TIP@BN12":
        return TIP, revs["B-N12"]
    return revs[s], None

def run_counter(kind, mut, state):
    sha, base_ov = state_sha(state)
    tag = "pristine" if mut == "pristine" else mut
    out = f"{OUT}/{tag}.{state}.{kind}.out"
    exe = f"{CLONE}/tools/round42-digest-audit.py" if kind == "c2" else f"{CLONE}/tools/round42-capacity-audit.py"
    if mut != "pristine":
        exe = f"{SEAT}/mut/{mut}.py"
    cmd = [sys.executable, exe, "--repo", REPO, "--tip", sha]
    cmd += ["--seed", "42"] if kind == "c2" else ["--base", base_ov or BASE]
    cmd += ["--out", out]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=2700, cwd=SEAT)
        rc, err = p.returncode, p.stderr
    except subprocess.TimeoutExpired as e:
        rc, err = "TIMEOUT", (e.stderr or b"").decode() if e.stderr else "timeout"
    with open(out, "a") as f:
        f.write(f"exit={rc}\n")
        if err and str(err).strip():
            f.write(str(err).strip() + "\n")
    return (kind, mut, state, out, rc)

def norm_receipt(text):
    lines = [l for l in text.split("\n") if not l.startswith("tip=")]
    t = "\n".join(lines)
    return re.sub(r"\['r41[^]]*\]", "[X]", t)

def parse_out(path):
    met, legs, rest = None, "", []
    for l in open(path):
        l = l.rstrip("\n")
        m = re.search(r"met=(True|False)", l)
        if m and "=" in l.split(" met=")[0]:
            met = m.group(1)
            legs = l.split(" met=")[0]
        elif not l.startswith("tip=") and not l.startswith("exit="):
            rest.append(l)
    return met, legs, "\n".join(rest)

def main():
    os.makedirs(OUT, exist_ok=True)
    jobs = []
    for s in C2_STATES:
        jobs.append(("c2", "pristine", s))
    for s in C3_STATES:
        jobs.append(("c3", "pristine", s))
    muts = [l.split("\t")[0] for l in open(f"{SEAT}/artifacts/mutants.tsv").read().split("\n")[1:] if l]
    for m in muts:
        kind = "c2" if m.startswith("M") else "c3"
        for s in (C2MUT_STATES if kind == "c2" else C3MUT_STATES):
            jobs.append((kind, m, s))
        for s in (C2MUT_PROBE if kind == "c2" else C3MUT_PROBE).get(m, []):
            jobs.append((kind, m, s))
    print(f"{len(jobs)} jobs", flush=True)
    results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as ex:
        futs = [ex.submit(run_counter, k, m, s) for k, m, s in jobs]
        for i, fu in enumerate(concurrent.futures.as_completed(futs)):
            kind, mut, state, out, rc = fu.result()
            results[(kind, mut, state)] = (out, rc)
            if (i + 1) % 20 == 0:
                print(f"  {i+1}/{len(jobs)} done", flush=True)

    # validation of reconstructed states against committed receipts
    valid, invalid = {}, []
    for (state, kind), rel in RECEIPT.items():
        out, rc = results[(kind, "pristine", state)]
        got = norm_receipt(open(out).read())
        want = norm_receipt(open(os.path.join(LANE, rel)).read())
        okk = got == want
        valid[(state, kind)] = okk
        (print if okk else print)(f"validate {state}.{kind}: {'OK' if okk else 'MISMATCH vs ' + rel}",
                                  flush=True)
        if not okk:
            invalid.append((state, kind, rel))
    # pristine claim-tip acceptance
    for kind in ("c2", "c3"):
        out, rc = results[(kind, "pristine", "TIP")]
        met, _, _ = parse_out(out)
        print(f"pristine {kind} at claim tip: met={met} exit={rc}", flush=True)

    # matrix + classification
    mrows, crows = ["mut\tkind\tstate\tmet\tlegs"], ["mut\tkind\tclaim\tbaseaccept\texposed\t"
                                                    "positivebroken\tprobeaccept\tmet_invisible"]
    for m in muts:
        kind = "c2" if m.startswith("M") else "c3"
        met = {}
        legs = {}
        for s in (C2_STATES + C2MUT_PROBE.get(m, [])) if kind == "c2" else \
                 (C3_STATES + C3MUT_PROBE.get(m, [])):
            if (kind, m, s) not in results:
                continue
            out, rc = results[(kind, m, s)]
            mm, ll, _ = parse_out(out)
            met[s] = mm
            legs[s] = ll
        claim = "OK" if met.get("CAND") == "True" and met.get("TIP") == "True" else "BROKEN"
        baseacc = met.get("BASE") == "True"
        neg = C2_NEG if kind == "c2" else C3_NEG
        pos = "R-SEPC2" if kind == "c2" else "R-SEPC3"
        committed_neg = [s for s in neg if not s.startswith("P-") and s not in ("TIP@CAND", "TIP@BN12")]
        exposed = [s for s in committed_neg if met.get(s) == "True" and valid.get((s, kind), True)]
        probeaccept = [s for s in (C2MUT_PROBE.get(m, []) if kind == "c2" else C3MUT_PROBE.get(m, []))
                       if met.get(s) == "True"]
        posbroken = met.get(pos) == "False"
        invisible = claim == "OK" and not baseacc and not exposed and not posbroken
        mrows.append(f"{m}\t{kind}\t{';'.join('%s=%s' % (s, met.get(s, '-')) for s in sorted(met))}")
        crows.append(f"{m}\t{kind}\t{claim}\t{baseacc}\t{exposed or '-'}\t{posbroken}\t{probeaccept or '-'}\t{invisible}")
    open(f"{SEAT}/artifacts/matrix.tsv", "w").write("\n".join(mrows) + "\n")
    open(f"{SEAT}/artifacts/classification.tsv", "w").write("\n".join(crows) + "\n")
    print("\n".join(crows[1:]), flush=True)
    print("FLEET-DONE", flush=True)
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:
        traceback.print_exc()
        sys.exit(3)
