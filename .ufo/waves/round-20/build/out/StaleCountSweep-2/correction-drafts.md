# Draft appended corrections (append-only; drafted, NOT applied to the lane)

Measured values (source: `.ufo/waves/round-19/evidence/c1-counting.txt`, measured_commit `028235e6`; re-run at lane pin `37bd4c5` in a scratch clone): four-row registry, before-tokens `required=4 found=0 verified=0 missing=4 mismatch=0 off_ref=0` exit 1; after `required=4 found=4 verified=4 missing=0 mismatch=0 off_ref=0` exit 0; `--selftest` `selftest: ok (15 cases)` exit 0.

## SCORECARD.md (append at end of file)

**Round-19 C1 count correction (appended, stale-count sweep).** The round-19 C1 counts above (`required=3 found=0 verified=0 missing=3`, `required=3 found=3 verified=3 missing=0 mismatch=0`, `selftest 5 cases`) and the erratum's "three registry-row digests" were written against the three-row registry. At the measured commit `028235e6` (lane pin `37bd4c5`) the registry has four rows (`s055-commands`, `gate-live-1`, `c2-official-stdout`, `gate-live-checkpoint`). Counting command `python3 tools/citation-provenance.py`: before the tokens `required=4 found=0 verified=0 missing=4 mismatch=0`, exit 1; after `required=4 found=4 verified=4 missing=0 mismatch=0`, exit 0. `--selftest`: `selftest: ok (15 cases)`, exit 0. Read "three registry-row digests" as four and "selftest 5 cases" as 15. Source: `.ufo/waves/round-19/evidence/c1-counting.txt`.

## LOG.md (append at end of file)

**Round-19 C1 count correction (appended, stale-count sweep).** The round-19 entry (`missing=3 exit 1 → missing=0 verified=3 exit 0; selftest 15 cases`) and the round-19 erratum ("binds three registry-row digests") predate the fourth registry row (`028235e6`). At `028235e6` (lane pin `37bd4c5`): before the tokens `required=4 found=0 verified=0 missing=4 mismatch=0`, exit 1; after `required=4 found=4 verified=4 missing=0 mismatch=0`, exit 0; selftest 15 cases, exit 0. The selftest count (15) is correct; the registry-row count is four, so the before/after reads `missing=4 → missing=0 verified=4`. Source: `.ufo/waves/round-19/evidence/c1-counting.txt`.

## corpus/lessons/round-19.md (append at end of file)

**Round-19 C1 count correction (appended, stale-count sweep).** Line 12 ("before the tokens: `missing=3`, exit 1"), the M1 row ("before/after `missing=3` → `missing=0`") and the C1 scope-correction sentence ("the digests and ancestry of the three registry rows") were written against the three-row registry. At the measured commit `028235e6` (lane pin `37bd4c5`) the registry has four rows: before the tokens `required=4 found=0 verified=0 missing=4 mismatch=0`, exit 1; after `required=4 found=4 verified=4 missing=0 mismatch=0`, exit 0; `--selftest` 15 cases, exit 0. Read "three registry rows" as four and the before-state as `missing=4`. Source: `.ufo/waves/round-19/evidence/c1-counting.txt`.

## corpus/lessons/round-18.md

No draft. The round-18 erratum (lines 386-424 at `37bd4c5`) contains no stale C1 count; its cite-token list (lines 418-424) names four tokens, which matches the four-row registry.
