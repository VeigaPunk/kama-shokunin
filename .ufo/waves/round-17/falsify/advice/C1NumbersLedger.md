VERDICT: partial — measured C1 run counts agree; historical attribution, axis scores, and one self-test breakdown are not fully represented in the raw artifacts.

# C1 numbers ledger

Attacked C1 calibration-number claims in `corpus/lessons/round-17.md`, `SCORECARD.md` §Round 17, `LOG.md` §round 17, and `SKILL.md` §Round-17. Compared them with `runs/fault-controls-frozen.json`, `runs/fault-controls-current.json`, `runs/mutants-grid.json`, `runs/selftest-tests_probe-verdicts_check.py_--selftest.txt`, and `runs/selftest-.ufo_waves_round-17_c1_mutants.py_--selftest.txt`.

## Findings by severity

### Low — evidence limits, no measured-count contradiction

| Source line(s) | C1 number(s) quoted | Raw evidence and assessment |
|---|---|---|
| `corpus/lessons/round-17.md:18-19`; `SCORECARD.md:656-657`; `LOG.md:996-997` | Round-16 `5/5` grading mutants survived; a sixth (`ignore-verdict`) also survived; baseline pair `55/17` vs `72/0`. | **Agree for the reproduced pair, with historical-provenance limit.** `mutants-grid.json` baseline records frozen `55` passes/`17` failures, current `72`/`0`; under frozen/pair, M1–M5 (five grading-related mutants) and M0 (`ignore-verdict`) all survive. This reproduces the quoted counts in this grid, but the grid is a round-17 artifact and cannot by itself authenticate the cited round-16 run as the original observation. |
| `corpus/lessons/round-17.md:28-30` | F0 plus F1–F8; nine matrix files; probe byte-identical. | **Agree.** Each fault-control JSON has one F0 positive control and eight fault entries (F1–F8), matrix `files: 9`, `tests: 72`; frozen and current records carry the same probe SHA-256. |
| `corpus/lessons/round-17.md:157-159` | Frozen: `5 detected`, `3 accepted`, exit `1`; current: `8 detected`, `0 accepted`, exit `0`. | **Agree.** Frozen JSON has `detected: 5`, `accepted: 3`; its accepted controls are F5, F6, F8. Current JSON has `detected: 8`, `accepted: 0`. Each has eight fault entries; F0 is separate. The raw JSON records per-control `check_exit` values consistent with the stated outcomes (detected faults exit 1; healthy F0 exits 0). |
| `corpus/lessons/round-17.md:161-165` | Frozen/pair `1/8`; frozen/full `7/8`; current/pair `1/10`; current/full `10/10`; only reject-all is killed by pair; frozen/full M8 survives. | **Agree.** `mutants-grid.json` totals are respectively applicable/killed: `8/1`, `8/7`, `10/1`, `10/10`. The pair cells kill only M9 (`reject-all`); the frozen/full cell leaves M8 (`malformed-output-passes`) surviving. Frozen M6/M7 are `site_missing`, explaining the eight applicable mutants; current has ten applicable. |
| `corpus/lessons/round-17.md:175-177` | Nine files, 72 rows; check self-test `72/72 + 5/5`; baseline pair `55/17 → 72/0`. | **Agree for reported totals.** Both fault-control JSONs and the grid say 9 files/72 tests. Check self-test text ends `tests=72 passes=72 failures=0` and `selftest: 5/5 malformed tests rejected (ok)`; the grid independently records `55/17` and `72/0`. The self-test text confirms five rejected cases total, but does not expose the claimed `4 malformed + 1 duplicate-name` breakdown. |
| `SCORECARD.md:680`; `LOG.md:1020-1021` | Fixed detector accepted faults `3 → 0`; full mutants `7/8 → 10/10`; pair mutants `1/8 → 1/10`. | **Agree.** These values match the two fault-control JSON summaries and the four applicable/killed totals in `mutants-grid.json`. |
| `corpus/lessons/round-17.md:5-7`; `SCORECARD.md:661`; `SCORECARD.md:680` | Calibration score `7`, `7 → 7`, delta `0`. | **Not verifiable from the specified raw C1 artifacts.** The run JSON/text contain detector and mutant results, not axis-score calculations. No contradiction is present in the C1 run data, but it cannot substantiate the score. |
| `SKILL.md:561-563,570` | Exit `2` for harness/schema errors; exit `1` for a row failure, including malformed/non-UTF-8 probe output. | **Partially verifiable.** The raw current fault-control JSON demonstrates exit `1` for F1–F8 and exit `0` for F0; the check self-test demonstrates row-level probe exits, including `2`. These selected artifacts do not directly demonstrate the overall gate's harness/schema exit-`2` path, so that contract value is not confirmed by the run summaries. |
| `SKILL.md:570` | Five rejected schema cases: four malformed plus one duplicate-name; nine files; 72 rows. | **Partial.** Five rejections are confirmed by the check self-test output; nine files and 72 tests are confirmed by both fault-control JSONs. The raw self-test output does not distinguish the `4 + 1` case breakdown. |
| `SKILL.md:571-572` | F0 and F1–F8; 72 scratch tests and nine files; mutants M0–M9 (10); `site_missing` not applicable. | **Agree for counts and grid status.** Fault-control JSON has F0 plus eight faults and 9/72 matrix metadata. Grid and mutant self-test enumerate M0–M9 (10); grid totals show frozen `site_missing: 2` (M6/M7) and current `site_missing: 0`. The `0/1/2` entries on these lines describe documented exit-code mappings, not aggregate measured counts; this ledger does not treat them as run totals. |

## Residual risk and verification gaps

- No measured C1 count disagrees with the raw run artifacts.
- Historical round-16 provenance for the `5/5` claim, score `7 → 7`, overall harness/schema exit `2`, and the check self-test's `4 + 1` case composition are not independently established by the specified C1 result files. Marked as evidence limits, not contradictions.
- The C1 mutant self-test JSON reports `selftest: pass` and `exit=0`; the check self-test reports 72/72 matrix rows, 5/5 schema rejections, and `exit=0`. Neither is a substitute for the measured fault-control or mutant-grid totals.

## Commands, scratch, and installs

- Commands run: none. I used read-only file reads; no lane tool, gate, or counting command was run, so there are no command exit codes to report.
- Scratch: none created; nothing to remove.
- Installs/updates: none.
