# RVW01ClaimC1 — advisory C1 attack

Axes: operability + calibration; judged calibration, frozen 7, saturation 8, nudge inactive. No admission/verdict.

## Findings

1. **High — closure-only selftest blind to non-closure counter erasure.** Scratch mutation `c = dict.fromkeys(c, 0)` before aggregation leaves all five arms green (`pass=5 fail=0`, exit 0), despite erasing nine actual non-closure mismatches. The committed census still registers 22 members including this selftest; registration plus five arms is not sufficient enforcement of the no-weakened-check kill rule. This mutant does NOT pass the full base counter: closure_ptr=0, mismatches=1, exit 1.
2. **High — frozen base red reproduced exactly.** At committed base 6035e952c2521999e192d6f236331f265ac98392: r41=2 banner=1 planned=1 retired=1 province=4 closure_ptr=0, all other family counters zero, mismatches=10 maxN=69 met=False, exit 1. Original selftest: ok has mismatches=9, four plants have 10; pass=4 fail=1, exit 1. Only ok fails its assertion.
3. **Blunt fake green is caught by the full target.** Replacing aggregation with `mism = 0` returns met=True / exit 0 without any record/harness repair, but keeps closure_ptr=0 and maxN=69; selftest pass=1 fail=4 / exit 1. The original frozen bytes on the untouched base remain red. Do not confuse mutant output with original-counter output.

## Evidence

All files below are relative to the lane:

- `.ufo/waves/round-70/w1/out/RVW01ClaimC1/attack.md`
- `.ufo/waves/round-70/w1/out/RVW01ClaimC1/report.md`
- `.ufo/waves/round-70/w1/out/RVW01ClaimC1/evidence.txt`
- `.ufo/waves/round-70/w1/out/RVW01ClaimC1/reproduce.py`

Exact commands, stdout/stderr, exit codes, byte hashes, per-fact breakdown and closure requirements are retained there. No production patch or mutant should be landed from this seat. L1 must land genuine standing-record and Git-dependent run-fact repairs, preserve all checks, and measure the actual landing SHA with independent negative controls.

Residual risk: no actual landing diff/tip or full census was reviewed; no endpoint/runtime claim exercised. LSP device unavailable, so inspection used text fallback. No tracked lane files edited; no tool installs; scratch removed by EXIT trap.
