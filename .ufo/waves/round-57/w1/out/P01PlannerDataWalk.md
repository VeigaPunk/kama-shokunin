# P01 planner data walk

Axes: calibration (C1) and operability (C2), per assignment; this is read-only evidence. No source edits, fixture runs, commits, or installs performed. Tooling rules were read at `/home/vgpnk/.omp/agent/RULES.md`; pacman transactions remain paused.

## C1 — canonical capability-row count

Observed at the initial frozen control (`.ufo/waves/round-57/controls/freeze.txt`): counter baseline reports `mismatches=1 maxN=56 met=False`; detail is the R41 calibration run expecting `42` verifier-spotcheck lesson paths but finding a different stdout. However, `freeze-amendment.txt` explicitly supersedes claim ordering/target: C2 is now the stale count, with actual outside spotcheck count 43. Read amendment as authoritative for current measurement. Relevant counter bytes: `tools/round42-selfdesc-reconcile.py`, `census()` at lines 137–146 counts source rows; `evaluate()` at 149–270, calibration check delegated to `round41-scorecard-reconcile.py` via `load_r41`/`m41.evaluate` (156–159); the stale expected count is emitted as the calibration axis run fact in `SCORECARD.md` line 18 (the `42` in `len(glob.glob('corpus/lessons/*verifier-spotcheck.md'))`), while the head self-description currently describes round 56. The present counter's `maxn` is computed from *all* `## Round N` headings in the entire historical scorecard (167–168), so historical Round 56 is why it reports maxN=56; it is not the canonical capability-list round. Canonical selector `canon()` (120–127) scans lines matching `canonical list as of round N**` and chooses the greatest N; row names/first-working rounds derive from the following table (178–180). Current list is round 49 per `SCORECARD.md:117` and entries 121–131; its first-working rounds are 10,14,16,20,25,30,41,42,43,46,47 (11 rows), not a round-56 value. Thus claims about `maxN=46` from initial freeze do not agree with current code/data semantics; amendment clarifies C2 is a separate round-56 selftest no-op claim and C1 is the stale round-42 calibration count.

Exact frozen output read: `base-c1.out`: `r41=1 ... mismatches=1 maxN=56 met=False`, detail above, `base_c1_exit=1`. Initial `noop-c1.out` reports `mismatches=0 maxN=46 met=True`, exit 0, despite being a no-op. These artifacts predate/are superseded by amendment; do not use their asserted target ordering as current truth.

Likely minimal C1 change per amendment: change the one stale expected numeric literal in the calibration evidence command from 42 to 43 in the current self-description evidence row; leave `maxn` historical-round derivation and canonical heading selection untouched. Acceptance should bind the counter's derived selftest mismatch to zero at the amended baseline, not assert maxN=46. Confirm exact expected value against the amended base/measurement run before integration; no such updated output was inspected here.

## C2 — distinct execution/content binding

Amendment sets C1 to `round56-prereg-check.py` no-op defect (operability), and C2 to the stale self-description count (calibration); original context's labels differ. The frozen claim in amendment: checker accepts matching literal roster without battery executions; predicate is reject no-op while accepting genuine battery roster. Round-56 lesson `corpus/lessons/round-56.md:29` independently records the exact prior defect and references `.ufo/waves/round-56/measured/c2-noop-control.out`. Round-57 `controls/noop-c2.out` records `canonical_table_reads=0`, `self_description_reads=0`, `mismatches=0 maxN=46 met=True`, exit 0—direct falsification of any criterion relying solely on that printed result.

Data dependency for a canonical-row checker should be actual bytes selected by the canonical heading, not an expected count, fixture label, literal roster, or output substring. Existing `canon()` returns both selected heading round and parsed canonical rows. A real checker should read the committed target revision's SCORECARD bytes, select the highest canonical heading and parse its following table (same delimiter/header handling as `table_rows`), then compare row identities and content against independently derived expectations and prove its actual checker/battery path ran. Mutations deleting, adding, renaming, or changing a canonical row need to fail; no-op must fail even if it prints the expected `met=True` summary. Keep C1 count repair independent from C2 execution binding. This is a design implication, not a tested implementation result.

## Exact investigation commands / evidence

- `read` `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round42-selfdesc-reconcile.py:95-270` — parser and counter logic above.
- `read` `/home/vgpnk/Projects/shokunin/kama-shokunin/SCORECARD.md:1-19,115-138` — current authority, canonical capabilities, stale count statement.
- `read` frozen controls `freeze.txt`, `freeze-amendment.txt`, `base-c1.out`, `base-c2-frozen.out`, `noop-c1.out`, `noop-c2.out`; observed outputs quoted above, with frozen recorded exit values as contained in receipts.
- `read` `corpus/lessons/round-56.md` — C2 predecessor and no-op control line 29.

## Separate assigned case

Case 1 independently checked: canonical selection is `canon()`'s greatest numeric `canonical list as of round N**` heading and `table_rows()` consumes the first subsequent pipe-table; historical `## Round N` is a different namespace. This distinction is the material test boundary: a historical-round maximum is not evidence that canonical capability rows were actually read.

Report: .ufo/waves/round-57/w1/out/P01PlannerDataWalk.md