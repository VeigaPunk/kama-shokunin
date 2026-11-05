#!/usr/bin/env python3
"""SB01 C2 probe: classify() on self-consistent lies. Run from a `git archive <rev>` copy:
    python3 probe_c2.py <copy-of-tip>
Expected at bafae7af: both forged greens -> verdict=escaped (red at grade); lying fail_lines -> killed by summary-cardinality."""
import importlib.util
import pathlib
import sys

root = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
spec = importlib.util.spec_from_file_location("r86mo", root / "tools" / "round86-mutant-owners.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

cases = {
    "consistent-forged-green (dropped arm, arms=34 hardcoded)": (
        "APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0\n"
        "APPEND_DEBT_SELFTEST pass=34 fail=0 arms=34\n", "", 0, "arm-count"),
    "dropped arm, EXPECTED lowered to 33 (self-consistent)": (
        "APPEND_DEBT_SELFTEST_ARMS arms=33 expected=33 fail_lines=0\n"
        "APPEND_DEBT_SELFTEST pass=33 fail=0 arms=33\n", "", 0, "arm-count"),
    "owned FAIL with ARMS fail_lines=0 lie": (
        "APPEND_DEBT_SELFTEST_ARMS arms=34 expected=34 fail_lines=0\n"
        "APPEND_DEBT_SELFTEST_FAIL note-deletion-equals-subject exit=1 want=0\n"
        "APPEND_DEBT_SELFTEST pass=33 fail=1 arms=34\n", "", 1, "note-deletion-equals-subject"),
}
for name, (out, err, rc, owner) in cases.items():
    verdict, label, detail = M.classify(out, err, rc, owner)
    print(f"{name}: verdict={verdict} label={label} detail={detail}")
src = (root / "tools" / "round86-mutant-owners.py").read_text()
print("DECLARED_POPULATION used in grade() only via pristine arms:",
      "population" in src and "arms_value" in src)
