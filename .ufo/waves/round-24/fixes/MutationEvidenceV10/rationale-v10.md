# MutationEvidenceV10 — round 24 C1 mutation contract, inventory version 10

**Proposal only; no production file is edited by this seat.** Versions 2–9
stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched. No primary-47, expectation,
twin-link, PM08 or operator-recipe change; no full sweep.

Version 10 is a **strict superset of version 9** with two small additions
that follow the grid's own V6 contract (grid proposal sha256
`d8ff2c473a28249433cc52dd42c67252a5af1c54b59c4d3aeee3c243e3cf654f`, proposal
only). Version 9 remains valid if the L1 prefers fewer changes.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `c00af3513944a6c1ec29c9a987347d92220d55f741d484e229962d0f1e490c19` | 73767 |
| `promisor-mutants-v10.patch` | `84de3c880e5c283f82ed657f4ef6d58d8f10c5aa8cf2933ba1af892295079bf2` | 57792 (applies clean at p1 on the integrated file) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged) |
| `selftest-receipt.txt` | — | `selftest cases=41 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV10` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

## 1. The grid's own producer digest is compared, not trusted blindly

The grid's V6 document adds one key — `doc["grid_sha256"]`, the producer's
own source digest. It is a new key, not a rename, so a grid that does not
carry it simply leaves the field absent on my side.

The runner now:

* records the grid's reported digest in the provenance block
  (`grid_reported_sha256`) next to the digest it computed itself from the
  grid file's bytes (`grid_sha256`);
* **refuses** the run (could-not-evaluate, exit 2, zero kills) when the
  grid reports a digest that differs from the file the runner hashed —
  that means what was measured is not identified, so nothing is credited;
* applies the same check to every mutant run, so a grid that changed
  between the pristine and a mutant run is caught.

The bounded control: the stub grid reports a wrong producer digest in one
mode, and the selftest asserts the runner refuses (exit 2) with a reason
that names the digest.

## 2. The grading explanation travels with the failed rows

The grid's V6 rows carry the grade messages (`problems`,
`amended_problems`, `original_problems`) next to the boolean. The runner
carries those fields into the failed-row details, so a receipt says *why*
a row was violated and not only that it was. No grading rule changes and no
field is required: a grid that does not carry them leaves the detail
unchanged.

## 3. Unchanged from version 9

The current-only arm rule (any other arm is could-not-evaluate before the
source, the pristine and any grid call); the provenance block (candidate
digest, grid digest, population and expectation digests and size, the
grid's `auditor_sha256` map, and the observed per-mutant auditor digest
alongside the failed and class rows); the operators, their alternatives and
their attribution; the class taxonomy and aggregates; the harness-fault
set (row `traceback`, the canonical `internal_error` flag, the stderr
diagnostics, an invalid row exit, a malformed verdict); attribution
enforced before a credit with the out-of-attribution rows preserved and
the allowlist not widened; no new admission gate (a valid finite survival
stays a completed run, exit 0); PM08 as a manual review-only note; the
legacy empty-selection guard; the 47 rows and the twin links; N3 as an
intentional envelope with no "declared not broken" metric.

## Not run

No sensitivity sweep and no legacy fixture run (wave 2 is active). The
checks exercised here are the bounded selftest (41 assertions, 0 failed)
and the source compile. The grid version measured against is named by
hash, not by path.
