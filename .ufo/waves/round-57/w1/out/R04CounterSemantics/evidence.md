# R04CounterSemantics — round-42 counter attack

Axes: calibration, operability. Read-only; no repo source edits.

## Counterexample / likely mismatch source

`tools/round42-selfdesc-reconcile.py:120-127` scans *all* SCORECARD text for any `canonical list as of round N**` marker. It accepts the marker's subsequent table via `table_rows(lines[i + 1:])`; a new larger N replaces the prior result, but an equal N does not (`N > best`, not `>=`). It does not verify that a marker is the actual canonical heading, that its table belongs to the heading/section, or that it is in the current canonical list rather than a historical/prose occurrence. Thus duplicate equal-number marker citations can cause a preceding historical table to win even when an actual table follows. Counter uses that result as `names` for head capability comparison and retired/saturation checks (`:220-224` and earlier `names` construction); a stale table can report a false mismatch or false clean state.

Strongest simple synthetic counterexample, run against the actual parser function:

```text
python3 -c 'import importlib.util; p="/home/vgpnk/Projects/shokunin/kama-shokunin/tools/round42-selfdesc-reconcile.py"; s=importlib.util.spec_from_file_location("r42",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m); t="**Capabilities - canonical list as of round 57**\n\n| Capability | Evidence | Round |\n|---|---|---|\n| stale-first | x | 1 |\n\n## Round 57\n**Capabilities - canonical list as of round 57**\n\n| Capability | Evidence | Round |\n|---|---|---|\n| actual-later | y | 57 |\n"; print(m.canon(t))'
```

Exact stdout: `(57, [['stale-first', 'x', '1']])`; exit 0. Expected table for the current occurrence would contain `actual-later`. This confirms a parser selection defect, not evidence that the frozen round-57 current SCORECARD contains this exact duplicate. I did not run the round-57 C1 counter against current content.

The real round-42 counter's canonical-selection implementation is `canon()` at `tools/round42-selfdesc-reconcile.py:120-127`; it computes maxN separately from `^## Round (\d+)` headings (`:167-168`). Frozen round-57 base output reports `mismatches=1 maxN=56 met=False` (`.ufo/waves/round-57/controls/base-c1.out:2-4`), but this evidence does not prove that `maxN` mismatch is caused by canonical selection. `maxN` is sourced from round headings, while canonical rows are selected independently; the reported base diagnostic is specifically the r41 calibration command expecting output `42` and got no line `42`.

## Smallest safe correction

Bind canonical-row extraction to a structurally recognized canonical heading/table, scoped to SCORECARD's live canonical section; define deterministic duplicate-heading handling (prefer the actual live/current table or reject ambiguity as unevaluable). Do not use an unrelated marker occurrence as row authority. Keep maxN derivation and canonical-row selection distinct, and report their source/evidence separately. Add regression cases for equal-N duplicate marker (historical before live), greater-N marker in prose, and malformed/missing table.

## Evidence / exits

- Read-only inspection: `read tools/round42-selfdesc-reconcile.py:120-127,149-175,204-224` — parser and consumer logic above.
- Parser counterexample command shown above — stdout exactly as recorded; exit 0.
- Frozen control receipt: `read .ufo/waves/round-57/controls/base-c1.out` — `mismatches=1 maxN=56 met=False`; exit value recorded in file as `base_c1_exit=1`.

No tool installations or repository mutations.