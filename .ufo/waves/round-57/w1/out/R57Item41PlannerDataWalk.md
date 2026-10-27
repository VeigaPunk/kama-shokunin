# R57Item41PlannerDataWalk — assigned data walk

Axes: calibration + operability. Read-only; no source edits, fixture runs, VCS mutations, or installations. Authorization rules read at `/home/vgpnk/.omp/agent/RULES.md`; no tooling install.

## Findings

### Frozen round-42 counter expected value and source

The round-57 amendment explicitly identifies C2 as the `tools/round42-selfdesc-reconcile.py` stale calibration count: base says expected `42`, while the actual committed outside verifier-spotcheck count is `43`; it requires changing only that stale self-description count and requiring `mismatches=0` (`.ufo/waves/round-57/controls/freeze-amendment.txt`, complete line 1). This is the amendment to ordering only; it says it does not replace base/control evidence.

The counter's module contract states `r41` imports the round-41 head-table counter unchanged, and that round-41 calibration run must have stdout line `'42'` (docstring lines 20–22 and current SCORECARD calibration evidence). The frozen C1 receipt `.ufo/waves/round-57/controls/base-c1.out` reports `r41=1 ... mismatches=1 maxN=56 met=False`; its detail is exactly the r41 calibration command expecting `42`, with no stdout line equal to `42`, and `base_c1_exit=1`. It is not a `maxN` failure: that detail names only the imported r41 calibration run.

### Actual `maxN` derivation is distinct

`tools/round42-selfdesc-reconcile.py:evaluate` (lines 167–168) computes `rounds` from every SCORECARD line matching `^## Round (\d+)` and sets `maxn = max(rounds)`. This is a historical `## Round N` heading scan over the SCORECARD text. It does not derive from canonical capability-row count. `canon()` (120–127) separately scans any line containing `canonical list as of round N**`, takes the greatest N, and parses subsequent table rows; `evaluate` separately uses that result for canonical `names` (178–180). Therefore `maxN=56` in frozen output records the largest historical round heading, not the expected spotcheck count and not the canonical heading/table selection. The base's reported `56` does not establish that canonical rows are read correctly.

### Canonical heading and row evidence

At the measured tree, `SCORECARD.md:115–129` labels `## Capabilities` as a mirror of the round-49 canonical list and says the counters resolve the highest-numbered canonical heading below. `SCORECARD.md:121–129` displays the capability mirror, but canonical data is in the round-49 section later in the file; `canon()`'s actual selection criterion is the bold phrase `Capabilities - canonical list as of round N` (counter lines 120–127), not `## Round N` (167–168). Current displayed canonical capabilities have first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47, but these are not the outside-closure count.

The current calibration row in `SCORECARD.md:18` states the external verifier-spotcheck glob count as `43`, says the value is re-derived at the measured tip, and names the round-56 spotcheck as latest outside closure. `corpus/lessons/round-56.md:31` records the CENSUS boundary: 43 spotcheck files are consistent with the end tree; its mistake 29 records the no-op roster counter false green as exit 0. On the exact frozen-counter contract, expected count 42 is stale and tree-described current count is 43. I did not execute the counter or independently enumerate files; this is a source/evidence walk, not a fresh measured run.

### Round-56 closure evidence / boundary

`corpus/lessons/round-56.md:8,20,29` says C2 roster fidelity was frozen, the separate non-author post-integration spot-check was pending at report time, and a no-op with matching literal roster returned `met=True` (exit 0) without executing battery entries; the lesson explicitly says C2 is not admitted and the frozen predicate is not changed after data. `.ufo/waves/round-56/measured/final-c2.out` records `present=1 roster_match=1 kills=1 controls=2 met=True`, `exit=0`. Round56's own measured C1 outputs (`measured/base-c1.out`, `measured/build-c1.out`) concern LD_AUDIT and are unrelated to the round42 counter's stale spotcheck count.

The round-56 SCORECARD review `.ufo/waves/round-56/w1/out/V03ScorecardDrift.md:75–88` captured the earlier state at frozen tip `efc6b3ec`: round42 counter `maxN=55`, `mismatches=1`, with the same r41 expected-42 calibration command failing. That is historical round-56 evidence, not current round-57 `maxN=56`; it demonstrates the distinction between the historical-heading maximum changing from 55 to 56 and the independent calibration count mismatch.

## Commands / exits

Read-only evidence commands were the `read` calls on the exact paths/ranges cited above. No shell or fixture command was run, hence no new command exit codes are claimed. Exact prior outputs/exits are quoted with their receipt paths; no inference is presented as a fresh run.

## Separate assigned case 62

Case 62: checked independently against frozen counter source and current SCORECARD: `maxN` is max historical `## Round N` (56 in the round-57 frozen receipt); canonical heading/table selection is a separate parser path; the stale 42→43 target concerns the imported r41 glob-count run. Round-56 closure explicitly documents no-op C2 false green; no source code or counter was executed here.

Report: .ufo/waves/round-57/w1/out/R57Item41PlannerDataWalk.md
