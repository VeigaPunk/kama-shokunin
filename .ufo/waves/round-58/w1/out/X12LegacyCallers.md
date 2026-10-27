# X12LegacyCallers — every pointer to `tools/round56-prereg-check.py`

Rev under test: build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a` (base `2f53614e`, freeze `dcd69473`). Reads were
`git -C <lane> show/grep <rev>:<path>`; writes lived in `/fast/scratch/hyaku/kama-r58/X12LegacyCallers` (removed) and here.

## Census
`git grep -n round56-prereg-check e4891d8 -- ':!.ufo'` → 9 lines in 7 files (`receipts/live-refs.txt`); `.ufo` history
holds 135 more. The working tree (which moved to `SCORECARD.md`+`corpus/SOURCES.md` edits while I worked) carries the
identical 9-line set — no historical row was repointed (`receipts/forward-pointers.txt`).
**Executable callers: none.** `git grep -n 'prereg-check\.py' e4891d8 -- tools tests` returns only the new checker's
docstring line, and the battery C1 grades never names it (`git show e4891d8:tools/round56-env-leg-battery.py |
grep -n prereg-check` → no match, exit 1; its legs are `round54-replay-code-audit.py`, `round56-replay-code-audit.py`,
`round56-env-leg-test.py`). C1's genuine arm is independent of the legacy path.

## Per-surface verdict — repoint? what breaks?
| surface | repoint? | breakage if repointed or removed |
|---|---|---|
| `LOG.md:2458` | **No** — round-57 narrative, append-only ledger | append-only audit grades the LOG preamble; editing falsifies the record |
| `SCORECARD.md:3128` (round-56 C2 row) | **No** — records its instrument and frozen SHA `c7b0d787…` | would claim round 56 ran a tool that did not exist then; this row is the C2 stale-leg object |
| `SCORECARD.md:3155` (round-57 C1 row) | **No** — the round-58 row is the citation site | misstates which instrument produced `noop-c1.out` |
| `corpus/SOURCES.md:269` (S516 `used-by`) | **Not in place** — SOURCES-CONTRACT-v1 rule 2 is append-only | in-place edit violates rule 2; a new row is the legal route |
| `lessons/round-56.md:8`, `round-57.md:7`, `round-57.md:26` | **No** — frozen lesson records | rewrites what those lessons state they did |
| `lessons/round-57-verifier-spotcheck.md:20` | **No** — names the revision `83c1c4a5…` it measured | the receipt stops describing its own run |
| `tools/round58-battery-exec-check.py:4` | already correct (cites it as *replaced predecessor*) | none |
| `.ufo/waves/round-56…57/**` (135 files) | **No** — committed receipts | rewriting receipts is out of bounds |

Forward pointers already exist and are right: `corpus/SOURCES.md:270` (S517, `used-by`
`tools/round58-battery-exec-check.py`) and `SCORECARD.md:3198`, which measures via
`--checker-blob <rev>:tools/round58-battery-exec-check.py` and names the legacy tool only as base narrative.
**Recommendation:** leave the file and every historical row untouched — this lane keeps frozen counters in place.

## Does replacing or deleting the path break anything? (measured in a fixture clone)
Fixture `$D` = `git archive e4891d8` + own commits `9a662963` (unchanged) → `aab4c5e4` (legacy path overwritten with the
new checker bytes) → `ccb63372` (legacy path deleted) — `receipts/mutate-verdicts.txt`.
- `tools/round58-battery-exec-check.py --repo $D --tip {aab4c5e4,ccb63372}` → `met=True`, **exit 0** in both; likewise
  `tools/round58-c1-counter.py --repo $D --tip {…} --checker …/round58-battery-exec-check.py` →
  `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, **exit 0** in both.
- Base arm is blob-bound, not worktree-bound: `--repo <lane> --tip e4891d8 --checker-blob
  2f53614e:tools/round56-prereg-check.py` → `genuine=1/1 benign=1/3 noop_rejected=1/11 errors=0 met=False`, **exit 1**
  (the frozen before-line), independent of the working tree (`receipts/base-arm-and-hash.txt`).
- **Breaks if re-run after replacement**: `.ufo/waves/round-57/OutsideDefectAudit/38/receipts/checks.sh:19` hashes the
  live path; its recorded `dee6f922…` is exactly the tip blob, while the overwritten bytes hash to `89ad4e5d…`. Sibling
  `receipts/fixtures.sh:10-11` pins the old arm by revision but reads `HEAD:tools/round56-prereg-check.py` for the new
  arm — after a replacement that arm silently becomes round 58's.
- **Not coupled**: `R57Item05CounterSelftest/bin/selftest.py:12` names it only in a docstring; its instrument is its own
  shape-compatible copy `bin/ref-c1-execbind.py` (line 4).
- **Blind**: `tools/round54-cited-path-check.py` yields byte-identical tallies with the file present and absent
  (`cited=715 unresolved=14 disclosed=14 undisclosed=0 bad=1`, `receipts/cited-path-*.txt`), because both SCORECARD
  mentions sit in command spans and the parser drops spans containing spaces (`BAD_CHARS = set(" <>$=()|'\"")`, lines
  165/244/282/334). `citation-provenance.py` → `required=17 verified=17 missing=0 mismatch=0`, exit 0;
  `registry/required-citations.json` has no row for this path → no digest pin.

## Limits / risks (reported, not repaired)
- **L1 (timing, not a defect):** the freeze's "sourced on S517" does not resolve at the measured tip (`git grep -n S517
  e4891d8` matches only `controls/freeze.txt:4`); the row landed in the working tree afterwards (`SOURCES.md:270`).
- **L2 (stale self-description):** `tools/round56-prereg-check.py:2` still reads "Round-56 C2 calibration counter" with
  no frozen-for-round-57 / superseded marker, although round 57 used it as the C1 instrument — a production edit, L1's call.
- **L3 (pre-existing red, unrelated):** the cited-path counter already exits 1 at the tip on `bad ledger line 46`
  (`round-53-verifier-spotcheck.md` replacement not cited); not caused by this path, flagged to avoid mis-attribution.
- No tools installed or upgraded; pacman untouched.
