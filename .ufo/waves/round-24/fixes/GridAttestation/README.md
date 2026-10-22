# GridAttestation — proposal: attestation of the pinned oracle (GridMetrics + attestation)

A **proposal only**. Nothing here is production; the L1 integrates it.

* base: lane commit `2e254a1` — the integrated grid `b034e1596746d312989b7894c0757b67859df19a476a01ccd95076424135cefa`,
  the manifest `d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1` (**unchanged**)
* proposal source: `promisor-grid.py`, sha256 `98fe76368c122fcc4bd66e10c1495bd2670dc37c90268a45f4e55900ef0989e5`
* patch against the integrated file: `promisor-grid.patch` (395 diff lines)
* it **includes** the four GridMetrics fixes (`bc2b03dbf90e669b0324c28c59900bb6f739435c0ad1e0ec932c70493b8d125e`,
  filed separately and left in place) and adds the attestation work below
* the expectation manifest is **not** touched: 47 cells, byte-identical to the
  pinned snapshot; the strong `names_any_of` grader is untouched; no
  expectation is relaxed and nothing is fitted to a population

## Why (GateGridSelftest, fresh falsification)

The selftest contained the tautology `population(table) == population(table)`
and therefore attested nothing: a dropped case, a weakened `names_any_of` list
or a bad twin link all passed. The blobless premise facts were only *recorded*,
never *asserted*, so a clone whose filter was ignored, or a hydration that
happened silently, would have produced a different fixture under the same
cell name.

## What the proposal adds

1. **A literal byte pin on the expectation manifest.**
   `MANIFEST_SHA256 = d86b7bea9c49c3d2fcd026a3a1ffb502871d15a2c8db624eba9745e664f14cd1`
   is checked **before** the selftest and before any arm run. Any byte change
   is refused with `could-not-evaluate: snapshot_tampered: …` and exit 2. The
   pin covers the dropped case, the weakened names list and any rewritten
   expectation alike; the table's bytes are never changed by this proposal.
2. **A real negative capability replaces the tautology.** `validate_table()`
   attests the table structurally: unique and well-formed case ids, the
   pinned case and open-row counts, resolvable builders, twin links that point
   at real cases, known reason classes, known defect kinds, known token
   placeholders, and a content refusal that carries a `names_any_of` pin.
   The selftest now proves the *rejection* capability: a dropped case, a
   weakened names list and a dangling twin link must each be reported.
3. **Bounded command-line controls.** The selftest copies the runner and the
   manifest into a scratch directory and tampers with the copy: a copy with a
   dropped case and a copy with a weakened names list must both exit 2 with
   `snapshot_tampered`, and an unknown `--case` selector must be refused
   (exit 2) instead of ignored — also with `--selftest`.
4. **The blobless fixture contract is asserted, not just recorded.** After a
   genuine blobless clone the missing set is computed with lazy fetching
   disabled and must be **non-empty** (a filter that was ignored is a premise
   failure, exit 2); a hydrated clone must end with an **empty** missing set (a
   silent hydration is a premise failure); an unhydrated clone must still miss
   the object the cell is about — the lane's `f` blob for PG28, the fleet's
   report blob for PG43.
5. **The reachable origin stays reachable.** Nothing removes, disables or
   repoints the blobless clone's local origin: it is the acquisition
   tripwire. A lazy fetch would succeed against it and acquire objects, which
   the per-run before/after inventory reports as `objects_acquired`; the
   forensic probes keep using `--no-lazy-fetch`, and the fresh isolated state
   of every fixture is preserved. This proposal adds no generic copy
   framework and no whole-closure production gate — only the fixture
   contract and the attestation.

## Bounded verification (no full suite)

`--selftest` 14/14 ok, including the three negative capabilities and the
three command-line controls. The blobless family was run in both arms against
the candidate build `ea51bc35b71ac09f4c233e21a16be49af555e1333004a0fe166234de79edd220`:

| arm | violations | amended view | rows |
|---|---|---|---|
| frozen (r23 base) | 0 | 0 / 4 (the r23 metadata refusals) | PG05, PG06, PG28, PG43 all exit 2 and met |
| current (candidate) | 0 | **4 / 4** | PG05 exit 0, PG06 exit 0, PG28 exit 0, PG43 exit 2 — all met |

The new blobless contract held on every cell of the family: no premise
failure was raised, so the filter really omitted the promised objects, the
hydrated clones really are complete, and the unhydrated ones really miss the
object their cell is about.

## Correction to the amended comparison (ConnMetrics + CaseLaneTree)

The amended-view score was **not comparable between the arms**: the frozen arm
was scored with `form_check=False` and without the names pin, the current arm
with the strict rules. The two numbers (a loose 16 and the current arm's
score) were therefore not the same measurement.

The proposal now grades the live **amended** comparison with **identical
rules in both arms** — same exit, same defect set, same reason class, same
strong `names_any_of` pin, same no-verdict rule, same acquisition rule. The
exit-2 form check is arm-independent and the caller decides:

| score | rules | meaning |
|---|---|---|
| `met_frozen` (frozen column) | `form_check=False` | the historical reproduction: the r23 metadata refusal still counts as met, so the 47/47 history is intact |
| `met_amended_frozen` | `form_check=True`, the case's names and forbidden list | the strict, comparable baseline |
| `met_amended` (current arm) | `form_check=True`, the case's names and forbidden list | the live score |
| `met_amended_frozen_loose` | `form_check=False`, no names | the **former** exit/reason-only score, kept under its own label and never conflated with the strict one |

Measured on the frozen arm (historical only, no candidate): the strict
baseline is **14 / 47** and the loose score is **16**; the two cells that
differ are **PG16-missing-lane-tree-plain** and
**PG20-missing-fleet-tree-plain** — the r23 base names the required path
rather than the tree object id, which the strict names pin rejects. The
frozen column still reproduces **47 / 47** with 0 violations.

The old loose 16 is filed, not rewritten. The strict number is the one the
final measurement should report; a "before" target that is red is not a
could-not-evaluate, and the CLI exit contract is unchanged (frozen history and
current live violations drive exit 1; only harness faults drive exit 2).

**Not re-run**: the candidate sweep (L1 instruction) beyond the blobless
family and the selftest.
