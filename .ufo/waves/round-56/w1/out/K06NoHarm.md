# K06NoHarm — Round 56 scope and axis evidence

## Axes reviewed
- **Operability:** whether the targeted environment gate catches `LD_AUDIT` without disturbing the replay counter's unrelated behavior.
- **Calibration:** whether the preregistered battery roster is tied to committed bytes and the specified red/green controls.

## Counterexample / evidence
- Freeze commit `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` is additive-only: 10 paths, 2634 insertions, no deletions. Added paths are round-56 tools, preregistration, source snapshots, controls, and two `SOURCES.md` rows. No route/config path appears in its changed-path stat; no existing production file is replaced.
- `sha256sum tools/round56-replay-code-audit.py tools/round56-prereg-check.py` returned respectively `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` and `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`, matching frozen digests.
- Baseline-to-freeze counter change is a new file; its relevant intentional delta is `BAD_ENV = ("LD_PRELOAD", "DYLD_INSERT_LIBRARIES", "LD_AUDIT")` and updated round/base/source documentation. The prior counter remains available as `tools/round54-replay-code-audit.py`; battery labels it `base-old-counter`, consistent with the prior frozen counter lineage.
- Recorded receipts show C1 base `ld_audit=missed ... exit=0`, new counter `ld_audit=detected ... problems=['env: server environment carries LD_AUDIT'] ... exit=0`, and one-line mutant `ld_audit=missed ... exit=0`. They also show glibc's expected refusal of `/usr/lib/libexpat.so.1` as an audit interface (`undefined symbol: la_version`), while the test still finds the variable in the live child's environment. This appropriately limits the claim to variable-name detection, not successful code injection.
- Recorded C2 controls show base `present=0 roster_match=0 kills=0 controls=0 met=False`, exit 1, and freeze `present=1 roster_match=1 kills=1 controls=2 met=True`, exit 0. The checker reads committed preregistration and battery blobs at the requested tip and compares the literal roster; this matches the frozen, narrow calibration predicate.
- `corpus/SOURCES.md` adds S512 as mined/accepted for the specific LD_AUDIT fact and S513 as rejected for overlap, without changing existing rows. No tool was installed or updated.

## Assessment / smallest safe correction
No scope expansion, route/config mutation, or harmed-axis defect is evidenced in the inspected freeze and receipts; no correction is warranted. Calibration is deliberately roster fidelity only, not validation of mutant quality beyond the frozen C1 control, as the preregistration states. Preserve that limitation in any downstream claim; do not broaden either predicate post-freeze.
