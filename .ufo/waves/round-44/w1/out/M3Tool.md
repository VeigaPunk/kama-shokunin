# M3Tool — mutation test of tools/release-recheck.py (round-44, lane kama)

Verdict: the built-in selftest kills only 4 of 18 single-point mutants (14 survive), yet every measured survivor materially corrupts the C1 draft on the real population (up to 82 of 91 rows), so these are coverage gaps, not equivalent mutants; 15 proposed cases in `selftest-additions.py` kill all 14 survivors and pass pristine (15/15, exit 0); the pristine draft reproduces the frozen `.ufo/waves/round-44/c1/draft-ledger.tsv` byte-identically (diff empty, exit 0).

## Method

- Frozen helper bytes confirmed before any mutation: `sha256sum tools/release-recheck.py` = `50e77fa1a3d9d1d4407c3fbdc9e0b67aeceaf0a92389638f0c471d44991ba157`, equal to `counter_sha256`… `helper` sha in `.ufo/waves/round-44/preregistration.json` (C1 `helper` field). All work on a scratch copy `/fast/scratch/hyaku/kama-r44/M3Tool/pristine.py`; the lane file was never opened for write.
- Baseline: `python3 pristine.py selftest` → 5/5 PASS, `selftest pass=5 fail=0`, exit 0.
- 18 mutants, one behavior-bearing point each, each applied as an exact-once string replacement (asserted `count==1`) to a separate scratch copy: `relocate()` ×3 (nearest-offset choice :142, 80-line span window :139, stripped comparison :133), `clusters()` ×4 (adjacent-merge `+1` :116, split-at-80 bound :116, widen `<20` :121, widen bound direction), `cited()` ×9 (one per pattern/substitution, lines 77–95), `draft_row()` ×2 (verdict choices :178 and :185).
- Detector: `python3 mutants/<name>.py selftest` with `TMPDIR=$S`; killed = exit != 0 or any `FAIL` line; a baseline failure would have been inconclusive (baseline was clean, so not applicable).
- Full per-mutant record: `mutants.tsv` beside this report; raw JSON `mutation-results.json`.

## Results — 4 killed, 14 survived

Killed by the built-in selftest: `C1a-no-adjacent-merge` (FAIL range: pin=5,6,7 rel=7,8,9), `C2b-widen-200` (FAIL moved-holds: pin=10-16 rel=12-18), `BR1-no-bare-range` (FAIL range: TODO), `V2-holds-as-reworded` (FAIL moved-holds: verdict=holds-reworded). All other 14 mutants run the 5 cases green.

Population impact of four survivors (draft on the 91-row population, diff vs pristine draft, changed-row count):

| mutant | rows changed | example |
|---|---|---|
| R3-raw-compare | 82 | S035 holds→TODO |
| R2-window-8 | 17 | S042 release `5171-5174,-` TODO (partial) |
| V1-unchanged-as-holds | 4 | S106 unchanged-file→holds (counter-invalid verdict for changed=0) |
| C2a-no-widen | 1 | S047 pin `26-27,575-576`→`26,575` |

Every survivor therefore changes what the C1 counter would read — none is equivalent; the selftest simply does not reach them.

### Notable findings

1. **Note column is never asserted** (`cmd_selftest`, frozen lines 205–209 check only verdict/pin/rel). `LI1-no-linesN` survives because `line 10` falls back to weak `{10}` → same ranges, only the note (`pin range picked from the first WEAK number`) differs. The additions kill it via a two-cite anchor where weak-min picks the wrong line (`see line 10 and line 30` → pristine `10,30`).
2. **Kept ISO dates emit no line number on any file shorter than the year** (`D1-keep-dates`): `re.finditer` consumes `2026-10` as a bare-range match that the `0 < a <= b` condition then rejects, and scanning resumes past it; weak numbers are dash-blocked on both sides. A plain date anchor cannot kill this mutant — the killer needs a year-sized L-cite (`L0999-10-26` on a 1000-line file). `date-in-anchor` is kept as a documentation/regression case that passes on both pristine and the mutant.
3. **"lines 5-7" is single-covered, not double-covered**: the bare-range mutant is caught only because `lines? (\d{1,5})` has `(?![\w.\-])` — the trailing `-` blocks it, so disabling the bare-range pattern leaves nothing. Accidental, not by design.
4. **Verdict-string mutants**: `unchanged-file`→`holds` survives because no fixture case has `changed=0` (c.cpp is absent at pin, not unchanged). One unchanged-file case kills it.

## Proposed selftest additions (verified)

`selftest-additions.py` (beside this report) rebuilds the selftest fixture plus 8 extra files (d–l.cpp, incl. a 1000-line file) and 15 cases; runnable standalone: `python3 selftest-additions.py tools/release-recheck.py` (tool path argv[1]).

- Pristine: 15/15 PASS, exit 0 (`additions pass=15 fail=0`).
- Each of the 14 survivors: exit 1, killed by its target case (per-mutant `killed_by` in `additions-vs-mutants.json`); R2/C1b/H1/BV1/LI1 are each killed by ≥2 cases.

## Population check (pristine)

`python3 pristine.py draft --sources corpus/SOURCES.md --upstream /fast/scratch/hyaku/kama-r44/shared/llama.cpp --release-name b11889 --release-commit d854d98bae598388ecea1ed84396587e5edc326d` → exit 0, 92 lines, `diff` vs `.ufo/waves/round-44/c1/draft-ledger.tsv` **empty** (byte-identical). Receipt: `population-draft-receipt.tsv`.

## Defect / drift finding (not fixed in place, per freeze)

Mid-wave the lane working tree's `tools/release-recheck.py` drifted from the frozen helper: `sha256` now `70476496aa85e1085a9ae8ef3c59c63abe08a8409f948b81f3cdd2fa6c3c34ce`, `git status --porcelain` → ` M tools/release-recheck.py` at commit 77d1bbf5. The diff vs frozen bytes touches only error paths — `git()` (`raise SystemExit` → stderr print + `sys.exit(2)`) and `cmd_draft` input validation (sources readable; upstream holds the release commit) — none of relocate/clusters/cited/draft_row verdict logic, so all verdicts above stand for the frozen helper named by the preregistration. Flagging for the L1: the working tree is ahead of the frozen hash the preregistration pins.

## Commands (evidence)

- `sha256sum tools/release-recheck.py` → `50e77fa1…` (matches preregistration helper sha)
- `python3 pristine.py selftest` → `selftest pass=5 fail=0`, exit 0
- 18 × `python3 mutants/<name>.py selftest` → verdicts in `mutants.tsv`
- `python3 pristine.py draft … > population-draft.tsv` → exit 0; `diff population-draft.tsv .ufo/waves/round-44/c1/draft-ledger.tsv` → empty
- `python3 selftest-additions.py pristine.py` → exit 0; × 14 survivors → exit 1 each
- `sha256sum tools/release-recheck.py` (after) → `70476496…` (external drift, see above)

No tools installed (none needed). Restoration evidence: all mutants and the pristine copy lived in `/fast/scratch/hyaku/kama-r44/M3Tool/` (removed below); the lane tool was never written by this seat — the only byte change to it is the L1's working-tree edit documented above. Scratch removed: `rm -rf /fast/scratch/hyaku/kama-r44/M3Tool`.
