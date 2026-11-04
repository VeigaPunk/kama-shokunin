#!/usr/bin/env python3
"""LAB01WaiverProbe: drive a byte-identical copy of tools/round65-host-census.py
by importing it and swapping in a synthetic MEMBERS table. The copy's main()
is not patched: only the module global MEMBERS is reassigned, exactly the input
the real tool would read from a real census.

Every arm prints the exact argv, the captured stdout/stderr and the exit code.
"""
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

RESULTS = []


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
    print(f"{o.rstrip()}")
    if e.strip():
        print(f"[stderr] {e.rstrip()}")
    print(f"[exit] {rc}")
    print()
    RESULTS.append(dict(label=label, argv=argv, stdout=o, stderr=e, exit=rc))
    return rc, o, e


print("### H1 — a waiver on an evaluated FAILING member")
run([M_PASS, M_FAIL], ["--waive", "syn-fail"], "H1a waiver on evaluated fail")
run([M_PASS], ["--waive", "syn-pass"], "H1b waiver on evaluated pass (control substrate)")

print("### H2 — waiver matched by prefix or glob")
run([M_PASS, M_REF], ["--waive", "syn-ref"], "H2a prefix 'syn-ref' vs member 'syn-refusal'")
run([M_PASS, M_REF], ["--waive", "syn-ref*"], "H2b glob 'syn-ref*' vs member 'syn-refusal'")
run([M_PASS, M_REF], ["--waive", "*"], "H2c glob '*' vs member 'syn-refusal'")

print("### H3 — waived not-evaluated member still counted, waived=1 printed")
rc3, o3, e3 = run([M_PASS, M_REF], ["--waive", "syn-refusal"],
                  "H3 exact-name waiver on not-evaluated member")

print("### H4 — two invocations in one process")
# 4a: identical argv twice: outputs must be byte-identical and both exits equal.
mod.MEMBERS = [M_PASS, M_REF]
argv = ["--waive", "syn-refusal"]
captures = []
for _ in range(2):
    old = sys.argv
    sys.argv = ["census-probe.py"] + argv
    out, err = io.StringIO(), io.StringIO()
    try:
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            rc = mod.main()
    finally:
        sys.argv = old
    captures.append((rc, out.getvalue(), err.getvalue()))
print("=== H4a same argv twice in one process ===")
print(f"$ python3 -c 'import census_probe as m; m.main(); m.main()'  # argv {argv}")
print(f"call1 exit={captures[0][0]} call2 exit={captures[1][0]} "
      f"stdout_identical={captures[0][1] == captures[1][1]} "
      f"stderr_identical={captures[0][2] == captures[1][2]}")
print(f"call1 stdout:\n{captures[0][1].rstrip()}")
print(f"call2 stdout:\n{captures[1][1].rstrip()}")
print()

# 4b: a state-leak check: waiver run first, then a no-waiver run in the same
# process. If any verdict state were cached, call 2 would inherit waiver/exit 0.
rc_a, o_a, e_a = run([M_PASS, M_REF], ["--waive", "syn-refusal"], "H4b call 1 (waiver)")
rc_b, o_b, e_b = run([M_PASS, M_REF], [], "H4c call 2 (no waiver, same process)")

print("### machine summary")
for r in RESULTS:
    verdict = next((ln for ln in r["stdout"].splitlines()
                    if ln.startswith("HOST_CENSUS")), "")
    print(f"{r['label']!r}: exit={r['exit']} {verdict}"
          + (f" | stderr={r['stderr'].strip()!r}" if r["stderr"].strip() else ""))
print(f"H4a identical-repeat: exit1={captures[0][0]} exit2={captures[1][0]} "
      f"same_stdout={captures[0][1] == captures[1][1]}")
print(f"H4b/H4c same-process leak check: call1_exit={rc_a} call2_exit={rc_b} "
      f"call2_has_waived_token={'waived=' in o_b}")
