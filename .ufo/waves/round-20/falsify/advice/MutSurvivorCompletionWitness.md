VERDICT: confirm - The existing partial-completion regression detects the false kill caused by removing the completion-count equality.

Scope: one private scratch mutant; axes were detector sensitivity, isolation, and exact restoration. No lane/evidence/registry/production edits, Git operations, services, installs, or delegated probes.
Target: `.ufo/waves/round-18/c2/survivors.py:931-959`, specifically line 959 in `selftest_enumeration_matches`.
Mutant: replace `return int(match.group(1)) + failed_cases == int(match.group(2))` with `return True`; retain summary-presence and baseline-total checks.
Expected detector: existing `selftest_pure` regression at `survivors.py:1813-1824`, especially `(b/c) one-of-42 summary with one target FAIL is incomplete`.
The bounded scratch detector calls the unchanged `selftest_pure(check)` (49 checks), collects failures, and also calls `selftest_arm` on the synthetic records below. Exit 1 means a regression failed or partial/complete outcomes differ from inconclusive/killed; otherwise exit 0.

Injected records (not external selftest executions): clean baseline exit=0, stdout=`42/42 selftest cases passed\n`; partial exit=1, stdout=`FAIL: edit after a blank line\n1/42 selftest cases passed\n`; positive control exit=1, stdout=`FAIL: edit after a blank line\n41/42 selftest cases passed\n`. All have spawn_error=None and timed_out=False. Partial enumerates only 1 pass + 1 FAIL, not 42 cases.
Scratch mirrored the survivor source and its five frozen-file dependencies so source-derived paths resolve privately. The full machinery selftest and full 15-cell census were not invoked.

Exact command, identical in pristine/mutated/restored phases (cwd `/tmp/kama-r20-MutSurvivorCompletionWitness`):
```sh
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/kama-r20-MutSurvivorCompletionWitness timeout 20s python3 /tmp/kama-r20-MutSurvivorCompletionWitness/detector.py /tmp/kama-r20-MutSurvivorCompletionWitness/lane/.ufo/waves/round-18/c2/survivors.py
```
Detector SHA256 in all phases: `a6bab6d893742b3feca0797429cceaa4fc0047fdc7dc94c98f11b3fb27158a8f`.

Pristine: actual exit 0; stderr empty; exact stdout:
```json
{"completion_regressions": [{"detail": "", "name": "(b/c) completed 42-case target failure kills", "passed": true}, {"detail": "", "name": "(b/c) early-abort same target literal is inconclusive", "passed": true}, {"detail": "", "name": "(b/c) one-of-42 summary with one target FAIL is incomplete", "passed": true}], "injected_observations": {"complete_target_failure": ["killed", "targeted selftest assertion failed: edit after a blank line"], "partial_target_failure": ["inconclusive", "selftest did not enumerate the baseline case set"]}, "pure_checks": 49, "pure_failed": [], "scope": "pure-classifiers-only"}
```
Mutated: actual exit 1; stderr empty; exact stdout:
```json
{"completion_regressions": [{"detail": "", "name": "(b/c) completed 42-case target failure kills", "passed": true}, {"detail": "", "name": "(b/c) early-abort same target literal is inconclusive", "passed": true}, {"detail": "", "name": "(b/c) one-of-42 summary with one target FAIL is incomplete", "passed": false}], "injected_observations": {"complete_target_failure": ["killed", "targeted selftest assertion failed: edit after a blank line"], "partial_target_failure": ["killed", "targeted selftest assertion failed: edit after a blank line"]}, "pure_checks": 49, "pure_failed": [{"detail": "", "name": "(b/c) one-of-42 summary with one target FAIL is incomplete", "passed": false}], "scope": "pure-classifiers-only"}
```
Restored: actual exit 0; stdout and stderr byte-for-byte equal to pristine. Positive complete-target control remains `killed` in all three phases; no-summary early-abort regression remains passing even under this count-only mutant.
Mutation outcome: **killed**, not baseline-inconclusive: pristine/restored pass all 49 checks, mutant fails exactly the existing partial-count regression and demonstrably misclassifies partial output as `killed`.

Restoration evidence (SHA256):
- Source before/during/after, scratch pristine, pristine backup, scratch restored: `c4c29c5a1d5d8a3981bfff58934d59c03cbb8f76f1dcf540edd8556ec4813890`.
- Scratch mutated: `47fad96bf638a1a4bcf921776ee9ba921a02eb2955158320abf52b7566b582a9`.
- Exact restored-scratch versus pristine-backup byte comparison: True; source hash unchanged: True.
Cleanup command: `rm -rf -- /tmp/kama-r20-MutSurvivorCompletionWitness && test ! -e /tmp/kama-r20-MutSurvivorCompletionWitness && printf '%s\n' 'SCRATCH_REMOVED=1'`; actual exit 0, stdout `SCRATCH_REMOVED=1`.
No tool installations or updates.
