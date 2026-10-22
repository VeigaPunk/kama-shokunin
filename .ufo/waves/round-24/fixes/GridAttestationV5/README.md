# GridAttestationV5 — proposal: delete one dead constant

A **proposal only**. Nothing here is production; the L1 integrates it. V1
(`6d9e31b7…`), V2 (`45e778a8…`), V3 (`437128b8…`) and V4 (`8e0d5c54…`) are
**kept filed**; this directory is the V5 successor.

* proposal source: `promisor-grid.py`, sha256 `d2aca34a4031b332fc1d558083d27aa098768fa3a0623cfb9ae8e7cf83652469`
* `promisor-grid-v5-delta.patch` — the **incremental** V5 delta against the V4 proposal `8e0d5c54…` (sha256 `4e5b138689f7bee274f8c1d96d6e9c2da064501c49feb1f5472376425c280efb`)
* `promisor-grid.patch` — the full delta against the integrated `b034e159…` (sha256 `7b094360cfec55eb03a3f62b714fd0080ea797b6940b134fe39d3fa1c6e8c608`)

## The change

One dead constant is deleted — the whole delta is two removed lines:

```diff
-# the r23 blanket refusal must never be the reason of a current-arm refusal
-METADATA_REFUSAL = ("partial clone (", "promisor pack")
```

`METADATA_REFUSAL` was never referenced (one occurrence in the file: its own
definition). The active metadata-refusal handling is untouched:

* the frozen-history reason class is `REASON_CLASSES["metadata"]` — used for
  the r23 base's own refusals;
* the per-cell `reason_forbidden` rules in the manifest (the current arm's
  "the reason must not be the r23 metadata refusal" pin) are unchanged;
* `check_exit2_form` still forbids the metadata phrasing for a current-arm
  refusal.

Nothing else changes: the manifest (47 cells, `d86b7bea…`), every
expectation, the strong `names_any_of` grader, the strict-14/loose-16
method, the V2 initial-premise guard, the V3 `internal_error` contract, the
V4 behavioural controls, the reachable origins and the `--no-lazy` forensic
probes are all as they were in V4.

## Verification

This is a cleanup, not new validation: **no test was re-run and no suite was
run** (L1 instruction). The single check performed is a compile check of the
proposed source (`py_compile`, ok) and a grep confirming that the constant's
only occurrence in the file was its own definition. The behaviour of the
proposal is therefore identical to V4 by construction — one unreferenced
binding removed.

The knowledge writer may drop the dead anchor.
