# FinalPM10 — PM10-ignore-opaque-nonleaf-missing (bounded mutation probe)

**VERDICT: KILLED (bounded sample).** The exact registered operator is killed by the pinned current-arm grid on both declared attribution rows: assigned primary PG47-opaque-tree-with-unresolved-fabricated-token and the one second declared discriminator PG46-opaque-tree-hides-cited-blob. Changed substantive verdict (2 -> 1), not a names/reason-only difference; no violated row outside the attribution envelope.

**Setup / identity (all observed).** `git clone --no-hardlinks` into `/fast/scratch/hyaku/kama-r24/postfix/FinalPM10/clone`, detached at `92063cfc60e217fa7e2098c568578119b16a1b95`. Hashed in clone, unmodified: auditor `tools/report-landing-audit.py` `b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`; mutator `tests/report-audit/promisor-mutants.py` `971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200`; grid `tests/report-audit/promisor-grid.py` `30483830e0461898bd9b710603e755b08cf58e2a2a215a747098ebbe0383f270`; 47-cell manifest `promisor-grid-expectations.json` `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (unchanged before and after; never edited).

**Operator.** Taken verbatim from the pinned mutator's `MUTANTS` entry (exactly 1 registered id, exactly 1 alternative: `insert` of `PM10_INSERT` at anchor `if __name__ == "__main__":`); anchor occurrences in the pinned auditor = 1 (unique applicability), mutant compiles = True, applied alternative index 0; no re-anchoring, no retargeting, no hand-written variant; the mutant diff is exactly the 12-line PM10 insert.

**Detector.** The pinned mutator's own `run_grid()` -> `python3 tests/report-audit/promisor-grid.py --arm current --current <tool> --json --case PG47-... --case PG46-...`. The mutator's default/main path was NOT invoked (no 47-cell pristine run, no selftest, no historical suite); each run had its own existing unique TMPDIR under this seat's scratch.

**Decisive observations — pristine tool** (grid exit 0): PG47 exit 2 (expected 2, met=True), PG46 exit 2 (expected 2, met=True); PG47 stderr = `round 1: unknown: unavailable required object: 0123456789abcdef0123456789abcdef01234567 could be hidden behind the missing tree or commit 2a675c1af91c97c51f5101d6cff10bb797458ab6` — a content-derived refusal (exit 2, no JSON verdict).

**Decisive observations — mutant tool** `d647f0871f6c63ab1c7edc1b58807f20281f3abd1f186bd04f67ca4f7e9b2fcb` (grid exit 1): PG47 exit 1, PG46 exit 1; stderr empty; stdout carries a JSON verdict with defect `unresolved-full-hash` token `0123456789abcdef0123456789abcdef01234567` (ordinary failed finding). Row class `actual-verdict` (2 -> 1) for both rows; graded problems (amended = graded view, current arm) `["exit 1 != 2"]`, also present in the original view of both rows; `met_amended=0/2`, `amended_view_unmet=[PG46…, PG47…]`.

**Attribution.** Violated rows = exactly PM10's `expect_rows` {PG46, PG47}; unexpected rows = none. Both cases carry `twin: null`, so no twin was compared and no twin violation is claimed.

**Hygiene (both tools).** `internal_error` False, traceback False, timed_out False, leaked False, `objects_acquired` empty (lane+fleet); grid-reported `grid_sha256`, `expectations_sha256`, `population_sha256` (612b0a74f3eebaa9…) identical across the pristine and mutant runs; grid `auditor_sha256.current` matched each tool's bytes (b9be4f42… pristine / d647f087… mutant); pristine copy byte-identical to the pinned auditor. Baseline green, so the comparison is valid.

**Residuals / scope.** A 2-cell bounded sample of 47: evidence that the opaque-non-leaf rule is load-bearing for PG46/PG47 only; not a statement about the other 45 cells, not global equivalence. PM10's clause "a known-present blob that merely fails commit peeling keeps its wrong-type finding either way" (PG38/PG39 neighbourhood) was not exercised — outside the 2-cell budget, unclassified, not credited. The original unknown clause stays WITHDRAWN/NOT-ACHIEVED; amended rows passing do not retroactively pass it. Gitfloor H2 untouched; no score promotion or self-admission.

**Artifacts.** Raw evidence under `.ufo/waves/round-24/postfix/out/FinalPM10/` (pm10-probe.json, grid-pristine.json, grid-mutant.json, driver.py, work/report-landing-audit.pristine.py, work/report-landing-audit.PM10.py); scratch `/fast/scratch/hyaku/kama-r24/postfix/FinalPM10/`. No tools installed or upgraded.

Report: .ufo/waves/round-24/postfix/advice/FinalPM10.md
