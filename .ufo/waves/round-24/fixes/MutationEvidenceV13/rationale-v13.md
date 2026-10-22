# MutationEvidenceV13 — round 24 C1 mutation contract, inventory version 13

**Proposal only; no production file is edited by this seat.** Versions 2–12
stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched. No operator, no 47-row, no
expectation, no twin-link, no PM08, no attribution and no classifier change;
no broader binding validation, no telemetry, no sensitivity sweep.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `3dae9345743910e475a8d506a76f0bf1771f2c44becda72d7a2706c9e766d45f` | 80492 |
| `promisor-mutants-v13.patch` | `810f1862fe66e2f497ed617333b87fffa4483f4f3213fb0a640e880cb92b24b2` | 65777 (applies clean at p1 on the integrated file) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged) |
| `selftest-receipt.txt` | — | `selftest cases=45 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV13` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

## 1. The producer-digest refusal belongs to the pristine validation

The grid-reported producer-digest check (the grid's `grid_sha256` against
the digest the runner hashes from the grid file) sat **after** the mutant
loop, so a pristine whose grid producer could not be identified still had
all the mutants run on it before the refusal. Version 13 moves the
**existing** check — same condition, same result — into the pristine
validation, **before** the loop: an unidentified pristine is refused and
no experiment runs on it.

The bounded control: the stub reports a wrong producer digest in the
pristine, and the selftest asserts the runner refuses with exit 2 after
**exactly one grid invocation** (the pristine) and a reason that names the
digest.

## 2. Every observed run stays identifiable

The observed per-mutant auditor digest was recorded only on the
killed/survived path, so a mutant that ended in could-not-evaluate (a
harness fault, a grid exit 2, a producer-digest mismatch, an
out-of-attribution violation) lost the digest of the run that was actually
observed. Version 13 records it **as soon as the grid reports it**, so
every observed run is identifiable even when nothing is credited. A digest
the grid does not report stays **absent**: nothing is invented.

The bounded control: the stub reports a correct digest in the pristine and
a wrong one in the mutant runs; the selftest asserts that the
could-not-evaluate entry **keeps the observed auditor digest**.

## 3. Unchanged from version 12

The current-only arm rule and its help text; the graded-row precondition
(a valid pristine with no graded row is could-not-evaluate, and a mutant
run with no graded row cannot be a valid survivor); the provenance block
(candidate digest, grid digest, grid-reported producer digest, population
and expectation digests and size, the grid's `auditor_sha256` map, and the
observed per-mutant auditor digest alongside the failed and class rows);
the operators, their alternatives and their attribution; the class
taxonomy and aggregates; the harness-fault set (row `traceback`, the
canonical `internal_error` flag, the stderr diagnostics, an invalid row
exit, a malformed verdict); attribution enforced before a credit with the
allowlist not widened; the grading explanation preserved where the grid
reports it and absent where it does not; the legacy empty-selection guard;
the 47 rows and the twin links; N3 as an intentional envelope with no
"declared not broken" metric.

## Not run

No sensitivity sweep and no legacy fixture run (wave 2 is active). The
checks exercised here are the bounded selftest (45 assertions, 0 failed)
and the source compile. No grid version is claimed that was not hashed.
