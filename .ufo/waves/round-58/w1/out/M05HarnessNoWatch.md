# M05HarnessNoWatch — round 58 mutation probe

Axes: operability (C1 execution-bound detection); calibration (frozen predicate unchanged).
Mutant: In an isolated scratch copy of `tools/round58-battery-exec-check.py` at build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`, changed `WATCHED = ("run", "assert_mutant_breaks_detection")` to `WATCHED = ("run",)`. This removes observation of the battery's mutation-assert helper while retaining run-frame observation.
Expected detector: frozen C1 checker behavior should reject this mutant because when the battery defines `assert_mutant_breaks_detection`, it must be called and each invocation must issue a subprocess invocation.

Commands and actual outputs (all called from fleet root; scratch at `/fast/scratch/hyaku/kama-r58/M05HarnessNoWatch`):

1. `git -C /home/vgpnk/Projects/shokunin/kama-shokunin show e4891d8a4c9c70e97124980c2ec9aee5762a7f0a:tools/round58-battery-exec-check.py > "$S/check.py"; git -C ... show ...:tools/round56-env-leg-battery.py > "$S/battery.py"; sha256sum "$S/check.py" "$S/battery.py"; python "$S/check.py" --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`
Output: checker SHA-256 `89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5`; battery SHA-256 `69b77a6a64f2667757842c2471ddc256d12ceb5ccca6df0a57b88bbe17ab51c5`; `tip=e4891d8a4c9c70e97124980c2ec9aee5762a7f0a present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True`; exit 0.
2. Mutated checker SHA-256: `537c31b753fe5d02a5d880b4c8a10e13f2e1cf349733f588b9aa6405ed1020b3`. Same checker command output: `tip=e4891d8a4c9c70e97124980c2ec9aee5762a7f0a present=1 roster_match=1 kills=1 controls=2 executed=0 legs=3/3 mutant_assert=0 met=False`; shell reported exit 1 (`set -e` terminated at checker failure).
3. Restored scratch checker from saved original; restored SHA-256 `89ad4e5d5c15c883eacf39126c6d1a0859382c54142976b4ed8539680832eec5`, identical to pre-mutation. Scratch directory removed.

Verdict: **killed**. The baseline passed, and omitting the watched assertion function caused frozen predicate rejection. The probe attacks C1's execution requirement for `assert_mutant_breaks_detection`; no claim or predicate was altered.
