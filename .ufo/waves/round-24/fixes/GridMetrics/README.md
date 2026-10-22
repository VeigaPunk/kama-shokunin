# GridMetrics — proposal: per-arm amended-view metrics and a drop premise assertion

A **proposal only**. Nothing here is production; the L1 integrates it.

* base: lane commit `2e254a1` (the integrated grid `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`,
  the manifest `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` — **unchanged**)
* proposal source: `promisor-grid.py`, sha256 `bc2b03dbf90e669b0324c28c59900bb6f739435c0ad1e0ec932c70493b8d125e`
* patch against the integrated file: `promisor-grid.patch` (76 lines, 4 hunks)
* the expectation manifest is **not** touched: 47 cells, the strong
  `names_any_of` grader is untouched, no expectation was relaxed.

## What is wrong today (source diagnosis, no rerun needed)

`doc["arms"][<arm>]["amended_view_met"]` counted only the rows whose
`met_amended_frozen` is true, and `amended_view_unmet` listed only the
frozen-arm rows. In the **current** arm `met_amended_frozen` is `None` for
every row, so the current arm always reported `amended_view_met = 0` and an
empty unmet list, while the per-row `met` values and the arm's `violations`
were correct. The summary was therefore misleading in the arm that matters.

Second, `withdrawn_original_failures` listed every current-arm row whose
*original* view was unmet, which mixes two different things: rows whose
expectation the amendment changed (genuinely withdrawn) and rows whose
original and amended views agree (an ordinary failure, mislabelled as a
withdrawal).

Third, the removal premise was not asserted. `build()` dropped the requested
object and recorded it, but nothing checked that the object really is absent
from the store afterwards; the premise check walked only the selected root
(`refs/heads/master`), so an unselected branch's missing blob was never
asserted.

## The proposal

1. **Per-arm amended-view metrics.** The amended view is now scored with the
   key that belongs to the arm: `met_amended_frozen` for the frozen arm (the
   historical baseline) and `met_amended` for the current arm (the live view).
   The summary adds `amended_view_measured_on` so the reader always knows
   which arm a number belongs to.
2. **Withdrawn versus failed.** `original_view_unmet` now lists *every*
   current-arm row whose original view is unmet; `withdrawn_original_failures`
   is restricted to the rows whose original and amended expectations differ
   (the rows the amendment actually changed) and the manifest's
   `amendment_changed_cases` names them. A row whose original and amended
   views agree is no longer labelled a withdrawal.
3. **A removal must really hold.** After each requested drop the builder
   probes the target repository with lazy fetching disabled and refuses to
   continue if the object is still available: a store that could serve the
   object again is a premise failure (exit 2), never a silently different
   fixture. This covers the unselected-branch blob, whose absence the
   selected-root walk never asserted.
4. **The `--keep` probe rule is documented** in the module docstring:
   fixtures deliberately keep a blobless clone's local origin **reachable**
   (a lazy fetch would succeed against it and acquire objects, which the
   per-run before/after object inventory reports as `objects_acquired`), a
   manual probe with `--keep` must keep the origin in place and must run git
   with `--no-lazy-fetch`, and **the origin must not be disabled or deleted to
   hide a flag regression** — that would hide the very regression the
   acquisition tripwire exists to catch.

## Bounded verification (no full suite)

`--selftest` 11/11. The changed family — the 20 cells that request a
removal (PG13–PG21, PG31–PG37, PG43–PG46) — was run in both arms against
the candidate build `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`:

| arm | violations | amended view | original view unmet | withdrawn | leaks / tracebacks / timeouts |
|---|---|---|---|---|---|
| frozen (r23 base) | 0 | 8 / 20, measured on the frozen arm | — | — | 0 / 0 / 0 |
| current (candidate) | 0 | **20 / 20, measured on the current arm** | PG34 | PG34 (an amendment-changed row) | 0 / 0 / 0 |

The twelve frozen-arm unmet cells are the r23 metadata refusals (the
historical baseline), not failures. The new drop assertion held on every
removal cell; no premise failure was raised.

**Not re-run**: the full suite (L1 instruction) and any candidate sweep beyond
the 20-cell family.
