#!/usr/bin/env python3
"""Build fixture SCORECARD.md variants from the freeze bytes (scratch only; repo untouched)."""
import os
import subprocess

REPO = "/home/vgpnk/Projects/shokunin/kama-shokunin"
FREEZE = "c07e1f909414aafb2d8de5605a81fd3bd4e3550e"
S = "/fast/scratch/hyaku/kama-r86/RV01ClaimsReview/fixtures"
os.makedirs(S, exist_ok=True)
base = subprocess.run(["git", "-C", REPO, "show", f"{FREEZE}:SCORECARD.md"],
                      capture_output=True, text=True, check=True).stdout
lines = base.split("\n")
assert lines[5].startswith("**Current authority (round 85):**"), lines[5][:60]
assert lines[17].startswith("| calibration | **7** | round-83 final"), lines[17][:60]


def head(rev, round_tok="85", cmd_round="85", receipt="gate.out"):
    return (
        "**Current authority (round 86):** assigned axes are operability + calibration (`shokunin.conf`); "
        "Latest measured round: 85. Terminal gate measured at `" + rev + "`: "
        f"`python3 tools/pre-report-gate.py --repo . --round {cmd_round} --tip master` printed "
        f"`PRE_REPORT round={round_tok} arms=13 failed=1 uncommitted=0`, exit1; receipt "
        f"`.ufo/waves/round-85/measured/after/{receipt}`."
    )


ROW_OLD = lines[17]
ROW_NEW = ROW_OLD.replace(
    "latest outside closure `corpus/lessons/round-84-verifier-spotcheck.md` (round84 rejected-honest-stop; round83 rejected-harmed)",
    "latest outside closure `corpus/lessons/round-85-verifier-spotcheck.md` (round85 rejected-honest-stop; round84 rejected-honest-stop)",
)
assert ROW_NEW != ROW_OLD
ROW_NEW_TESTF = ROW_NEW.replace(
    "test -f corpus/lessons/round-84-verifier-spotcheck.md", "test -f corpus/lessons/round-85-verifier-spotcheck.md")
assert ROW_NEW_TESTF != ROW_NEW


def write(name, head_line, row_line):
    ls = list(lines)
    ls[5] = head_line
    ls[17] = row_line
    with open(os.path.join(S, name), "w", encoding="utf-8") as f:
        f.write("\n".join(ls))
    print("wrote", name)


R_MEASURED = "948dec784a9736b4a36d6a10d303fbee054b19c6"   # round-85 measured revision (no receipt there)
R_DELIVERED = "6abaf0a8d11a76b141f37a9e9f6144b797af0b24"  # receipt committed here
R_BASE = "3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d"      # receipt present, ancestor of freeze
R_ROUND84 = "b53cd336e0cb204cf71246e95fdf7494babeafa4"   # round-84 measured revision, no round-85 receipt

write("f1-head-R-measured-rev.md", head(R_MEASURED), ROW_OLD)
write("f2-head-R-delivered.md", head(R_DELIVERED), ROW_OLD)
write("f3-head-R-base.md", head(R_BASE), ROW_OLD)
write("f4-head-R-round84-only-token-swap.md", head(R_ROUND84), ROW_OLD)
write("f5-row-only-repaired.md", lines[5], ROW_NEW)
write("f6-row-repaired-testf-stale.md", head(R_DELIVERED), ROW_NEW)
write("f7-row-and-testf-repaired.md", head(R_DELIVERED), ROW_NEW_TESTF)
write("f8-head-R-freeze-self.md", head(FREEZE), ROW_NEW_TESTF)
