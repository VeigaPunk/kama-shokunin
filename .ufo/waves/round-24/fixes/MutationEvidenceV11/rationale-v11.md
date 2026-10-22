# MutationEvidenceV11 — round 24 C1 mutation contract, inventory version 11 (final coupled cut)

**Proposal only; no production file is edited by this seat.** Versions 2–10
stay filed (V10 remains the version without the cut below), the lane's
integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched. No operator, no 47-row,
no expectation, no twin-link, no PM08 and no attribution change.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `5498202d9084d417cff30154f57811bd07a27fe39eed137dcff82c411faf3333` | 76461 |
| `promisor-mutants-v11.patch` | `b3e96d0e2ac47dd038c38f4342427341b90f14a0c795a5a12c3cf4718b981995` | 61079 (applies clean at p1 on the integrated file) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged) |
| `selftest-receipt.txt` | — | `selftest cases=42 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV11` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

## 1. The CLI help no longer advertises a frozen experiment

The `--arm` help still read "grid arm to exercise", which invites a reader
to try `--arm frozen` — the arm that runs the grid's **fixed frozen
auditor**, ignores the `--current` mutant and therefore reports a green no
mutant earned. The help now reads:

> **CURRENT arm only**: the sensitivity runner measures the candidate the
> `--current` path names. Any other arm is could-not-evaluate, because the
> frozen arm runs the grid's fixed frozen auditor and ignores the
> candidate.

The behaviour is unchanged from version 9: any other arm is
could-not-evaluate (exit 2), decided before the source is read, the
pristine run and any grid call. Only the advertised contract was wrong;
now it matches the rule.

## 2. The grid's grading explanation is preserved, not discarded

The grid's newer document carries the grading's own messages per row
(`problems`, `amended_problems`, `original_problems`) next to the boolean.
`row_detail()` already lists those keys, and the failed-row details now
carry them **alongside the codes and the observed auditor digest**, so a
receipt says why a row was violated and not only that it was. A field the
grid does not report stays **absent**: no alias, no invented value, and a
row without them keeps its detail unchanged.

The small bounded control: the stub emits one explained row and one plain
row, and the selftest asserts that the explained row's `problems`,
`amended_problems` and `original_problems` reach the failed-row detail and
that the plain row's detail has **no** such key (nothing invented).

## 3. Unchanged from version 10

The current-only arm rule; the provenance block (candidate digest, grid
digest, grid-reported producer digest with the mismatch refusal, the
population and expectation digests and size, the grid's `auditor_sha256`
map, and the observed per-mutant auditor digest alongside the failed and
class rows); the operators, their alternatives and their attribution; the
class taxonomy and aggregates; the harness-fault set (row `traceback`, the
canonical `internal_error` flag, the stderr diagnostics, an invalid row
exit, a malformed verdict); attribution enforced before a credit with the
allowlist not widened; no new admission gate (a valid finite survival
stays a completed run, exit 0); PM08 as a manual review-only note; the
legacy empty-selection guard; the 47 rows and the twin links; N3 as an
intentional envelope with no "declared not broken" metric.

## Not run

No sensitivity sweep and no legacy fixture run (wave 2 is active). The
checks exercised here are the bounded selftest (42 assertions, 0 failed)
and the source compile. No grid version is claimed that was not hashed.
