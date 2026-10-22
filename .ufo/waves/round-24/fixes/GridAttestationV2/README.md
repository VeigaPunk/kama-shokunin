# GridAttestationV2 — proposal: the blobless contract is proved on the clone, and a missing oracle is a could-not-evaluate

A **proposal only**. Nothing here is production; the L1 integrates it. V1
(`fixes/GridAttestation/`, sha256 `6d9e31b7ad2ea8d1cc3770e6ee22d25138de14b92c6b925deb8cdfe365d7159e`)
is **kept filed**; this directory is the V2 successor.

* proposal source: `promisor-grid.py`, sha256 `45e778a856e929cf92ccd10d7fbddfc83224fa4ce3332131ead961c6fee1446b`
* `promisor-grid.patch` — the full delta against the integrated `b034e159…` (520 diff lines)
* `promisor-grid-v2-delta.patch` — the **incremental** V2 delta against the V1 proposal `6d9e31b7…` (143 diff lines), for a surgical composition
* the expectation manifest is **not** touched: 47 cells, byte-identical to the pinned snapshot `d86b7bea…`; the strong `names_any_of` grader, the expectations and the 14-strict/16-loose labelling are unchanged

## What V1 left open (L1 static review)

`blobless_clone()` returned the destination without checking it, and the
contract was asserted only *after* the optional hydration. For a hydrated
cell a clone whose filter was ignored — a complete clone — would still end
with an empty missing set, so the "genuine initial missing" claim was never
proved.

## What V2 changes

1. **The contract is proved on the clone itself, before any hydration.**
   Right after each clone the fetch-free missing set must be non-empty and
   must contain the object the cell is about (the lane's `f` blob, the fleet's
   report blob). Only then, and only if the cell hydrates, is the clone
   hydrated and the final missing set required to be empty. The unhydrated
   cells need no second walk: the initial assertion already covers them.
2. **A negative fixture control.** `blobless_clone(..., filtered=False)` builds
   the deliberate negative — a complete clone that claims to be a blobless
   one. A hydrated builder using it must be refused **before** the hydration
   with a premise failure (exit 2), because the clone was already complete.
   The selftest builds it as an actual fixture and asserts the refusal, and
   it also builds the valid path (a genuine partial clone hydrated into a
   complete one) and asserts that the final missing set is empty.
3. **A missing or unreadable manifest is a could-not-evaluate.**
   `load_manifest()` catches the read `OSError` and raises a separate
   identity: `snapshot_unavailable` — without the bytes no tampering can be
   asserted, so it must never be reported as `snapshot_tampered`. The CLI
   boundary returns **2** with that identity on stderr and runs no arm and no
   auditor. The selftest copies the runner *without* its companion manifest
   and asserts exit 2 with `snapshot_unavailable`.

Unchanged: the origin URL and the reachable origin (the acquisition
tripwire), the `--no-lazy` forensic probes, the manifest byte pin, the
structural table attestation and its negative controls, the 47 manifest bytes,
the strong names grader, the expectations, and the strict/loose labelling of
the amended score.

## Bounded verification (no full suite)

`--selftest` **17/17 ok** — three negative capabilities (dropped case,
weakened names, bad twin), four command-line controls (dropped case,
weakened names, unknown selector, missing manifest), the negative fixture
control (`negative-complete-clone-refused`), the valid path
(`genuine-partial-clone-hydrated`) and the five premise checks.

The blobless family in both arms against the candidate build
`ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`:

| arm | violations | strict amended view | rows |
|---|---|---|---|
| frozen (r23 base) | 0 | 0 / 4 (the r23 metadata refusals) | PG05, PG06, PG28, PG43 exit 2, met |
| current (candidate) | 0 | **4 / 4** | PG05 exit 0, PG06 exit 0, PG28 exit 0, PG43 exit 2 — all met |

`objects_acquired` was empty in every cell of the family. The negative CLI
control was measured directly: a runner copy without its manifest prints
`could-not-evaluate: snapshot_unavailable: the expectation manifest is not
readable: …` and exits **2**, with no arm and no auditor run.

**Not re-run**: the full suite and any candidate sweep beyond the blobless
family and the selftest (L1 instruction).
