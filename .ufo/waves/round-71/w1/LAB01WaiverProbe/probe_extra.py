#!/usr/bin/env python3
"""Second pass: waiver parsing variants and the C2-relevant discriminators
(s4 refusal-classification, s5t derived total, s10d refusal branch, s6w/s8r
already covered by pass 1)."""
import contextlib
import importlib.util
import io
import sys
from pathlib import Path

CENSUS = Path("/fast/scratch/hyaku/kama-r71/LAB01WaiverProbe/census-probe.py")
spec = importlib.util.spec_from_file_location("census_probe", CENSUS)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

REFUSAL = [("missing dependency",
            "fail-closed refusal: synthetic missing dependency (probe fixture)")]
M_PASS = ("A", "syn-pass", ["bash", "-c", "echo SYN-PASS; exit 0"], "SYN-PASS", [])
M_FAIL = ("A", "syn-fail", ["bash", "-c", "echo SYN-FAIL; exit 1"], "SYN-FAIL", [])
M_REF = ("A", "syn-refusal", ["bash", "-c", "echo 'missing dependency: libxyz'; exit 1"],
         "", REFUSAL)
M_REF_B = ("B", "syn-refusal-b", ["bash", "-c", "echo 'missing dependency: libabc'; exit 1"],
           "", REFUSAL)


def run(members, argv, label):
    mod.MEMBERS = members
    old = sys.argv
    sys.argv = ["census-probe.py"] + argv
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main()
    finally:
        sys.argv = old
    o, e = out.getvalue(), err.getvalue()
    print(f"=== {label} ===")
    print(f"$ python3 census-probe.py {' '.join(argv)}")
    print(o.rstrip())
    if e.strip():
        print(f"[stderr] {e.rstrip()}")
    print(f"[exit] {rc}")
    print()
    return rc, o, e


print("## parsing equivalence: --waive=NAME vs --waive NAME")
run([M_PASS, M_REF], ["--waive=syn-refusal"], "E1 equals-form exact name")
run([M_PASS, M_REF], ["--waive=syn-ref"], "E1b equals-form prefix (must not cover)")
run([M_PASS, M_REF], ["--waive", "syn-refusal", "--waive", "syn-refusal"],
    "E2 duplicate --waive of the same name (waived must be 1, not 2)")
run([M_PASS, M_REF], ["--waive", "syn-refusal", "extra-positional"],
    "E3 extra positional arg is ignored, waiver still parsed")

print("## C2-relevant discriminators")
run([M_PASS, M_REF], [], "D1 refusal classified 'refused'+not_evaluated, fail stays 0 (s4 refusal-as-fail)")
run([M_PASS, M_REF], ["--waive", "syn-refusal"], "D1b same two members, one waiver (s5t total derived)")
run([M_PASS, M_FAIL], ["--waive", "syn-fail"], "D1c same table, failing member waived (s6w)")
run([M_PASS, M_REF, M_REF_B], ["--waive", "syn-refusal"],
    "D2 two not-evaluated members, one waived (partial waiver must still exit 1)")
run([M_PASS, M_REF, M_REF_B], ["--waive", "syn-refusal", "--waive", "syn-refusal-b"],
    "D2b both not-evaluated members waived")

print("## module identity of the copy")
print(f"LANE={mod.LANE}  BUDGET={mod.BUDGET}  len(MEMBERS real table)={len(mod.MEMBERS)}")
