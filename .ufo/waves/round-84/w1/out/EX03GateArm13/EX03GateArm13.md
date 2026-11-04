# EX03GateArm13 — C1(d)

Axis: operability; guardrail: calibration through honest receipts.

## Deliverable

`pre-report-gate.py` is a byte-complete replacement for `tools/pre-report-gate.py`. Production files were not edited. L1 should install this report at `.ufo/waves/round-84/w1/EX03GateArm13.md`; the seat's exclusive-output restriction keeps its source here.

Arm 13 follows arm 12 and runs only the two round-83 selftests, preserving verbatim the arms 10–12 own-final-summary rule. Missing instruments, nonzero exits, malformed/foreign final summaries and subprocess errors fail closed. Both scripts run even when one fails. No debt-tool or register changes.

Updated current-count docstrings/help and all executable fixture verdict expectations to 13, retaining historical counts. Added green/red arm-13 stubs and missing/foreign-summary cases for each module. Existing stale `PREDICATE` constant (arms=11) intentionally remains outside the requested changes; runtime verdict uses the evaluated arm count, not that constant.

## Exact retained evidence

Scratch clone HEAD: `eb03a64bcd8e2faab0f4f9bcdc55bfc5c1ed2c85`.

- `selftest.out`: full combined output of `python3 tools/pre-report-gate.py --selftest --work /fast/scratch/hyaku/kama-r84/EX03GateArm13/selftest`, exit **0**; terminal `PRE_REPORT_SELFTEST pass=35 fail=0`. Every fixture arm passed, including both missing and foreign-summary cases for arm 13. Four later edits changed only docstring fixture-count descriptions from 11 to 13; no executable changes followed this test.
- `real-gate.out`: full combined output of `python3 tools/pre-report-gate.py --repo . --round 84 --tip master`, exit **1**; terminal `PRE_REPORT round=84 arms=13 failed=4 uncommitted=0`.
- `pre-report-gate.diff`: final `git -C /fast/scratch/hyaku/kama-r84/EX03GateArm13/wt diff -- tools/pre-report-gate.py`, exit **0** (regenerated after the docstring-only edits).
- `commands.json`: exact argv, cwd and exit codes of the three concurrent receipt commands. TMPDIR was `/fast/scratch/hyaku/kama-r84/EX03GateArm13/tmp`; bytecode writing disabled.

### Real failing arms

1. `selfdesc`: calibration closure pointer still names round 82 rather than newest round 83.
2. `newest-closure`: same stale calibration pointer, independently detected.
3. `round-scope`: replacement deliberately remained uncommitted in the clone, so `tools/pre-report-gate.py status= M` is a stray path.
4. `round75-instruments`: debt grading reports `unaccepted=1 bad_rows=10`; first finding is `unknown-event late line 105` for `0d7c7c3e… SCORECARD.md`.

**Arm 13 actually passed**: `PENDING_FALLS_SELFTEST pass=7 fail=0` and `PIN_RECHECK_SELFTEST pass=14 fail=0`. The assignment's prediction that this selftest-only arm would be red before landing is contradicted by the retained run. No live-grading requirement or fabricated red condition was added to force that prediction.

## Command accounting and boundaries

Setup: `mkdir -p <scratch> && git clone --shared <lane> <scratch>/wt && git -C <scratch>/wt rev-parse --show-toplevel && git -C <scratch>/wt rev-parse HEAD`, exit 0; top exactly matched the clone. Output-directory mkdir/copy and scratch replacement copy/tmp mkdir commands each exited 0. Final diff regeneration exited 0. Cleanup `S=/fast/scratch/hyaku/kama-r84/EX03GateArm13; trap 'rm -rf -- "$S"' EXIT` exited 0 and removed scratch after receipt retention.

An initial read-only lane inspection command combined rev-parse/status and directory listing with output trimming; its service completed exit 0, but its stdout was not retained and supplies no evidence here. No lane git mutations, local commits, installs, network requests, background work intentionally requested, or production edits. No LSP tool was mounted; source navigation used anchored reads, not a purported empty LSP result. No unrelated builds, linters or formatters ran.

L1 owns installation and the committed-tree end-to-end gate. Gate selftests do not establish C1's debt/register legs or a green integrated gate.

## Self-evaluation

Accuracy 4/5: exact exits and the unexpected green arm 13 are disclosed; the final four documentation-only edits were not re-tested. Completeness 4/5: complete replacement, required receipts and final diff retained; integrated C1 remains L1-owned. Clarity 4/5: four failures are individually named, but historical documentation is inherently dense. Actionability 4/5: replacement and integration report target are explicit; L1 must still land other slices. Conciseness 4/5: command accounting adds length but preserves auditability. Overall 4.0/5. Highest-impact next action: run the required gate on L1's committed integrated tree. Would the user agree: likely, subject to the explicitly documented arm-13 prediction discrepancy.
