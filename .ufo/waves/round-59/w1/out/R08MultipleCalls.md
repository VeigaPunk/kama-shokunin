# R08MultipleCalls — round 59

Axes: operability; calibration (assigned 7, lowest).

## Finding

**The C1 checker is coded to reject a second subprocess call in any named run frame, even if the original call/result remains.** In `tools/round59-battery-outcome-check.py`, the child harness appends every `subprocess.run` invocation to the active frame's `calls` list (`fake_run`, lines 59–76; frame setup at 106–117). The checker then requires `len(calls) == 1` and that sole argv contain both `--counter` and `--expect` (lines 187–192). Thus an added call in `run` produces a two-element list and `calls_ok=False`; the baseline/fault pass predicates require every leg's `calls_ok` (`193–198`). Keeping the original run result does not satisfy the one-call invariant.

This is source-level evidence, not a measured mutation result: no custom extra-call fixture was executed, and the frozen C1 counter's enumerated controls do not include this mutation (`tools/round59-c1-counter.py`, `NEW_NOOPS` at lines 11–13 and fixture selection at 77–85). No claim that a counter run passed or rejected a concrete mutation is made. The measured C1 command was not run for this seat. No LSP device/status was available in the provided tool inventory; evidence is direct source reading, not semantic LSP proof.

## Commands / verification

No counter or fixture command run; no exit status or output to report. No tools installed or updated.
