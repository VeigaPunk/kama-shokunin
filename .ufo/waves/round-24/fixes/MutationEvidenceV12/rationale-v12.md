# MutationEvidenceV12 — round 24 C1 mutation contract, inventory version 12

**Proposal only; no production file is edited by this seat.** Versions 2–11
stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched. No operator, no 47-row, no
expectation, no twin-link, no PM08, no attribution and no ordinary-survival
change.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `c7d1782310ce2e0e3c7ac10af0aeb3d2568d9f74d41dc240acec7c0548c2fb64` | 78717 |
| `promisor-mutants-v12.patch` | `ca51dea6e22c9cf2c83461fa14ce3acf271b8bcaccf166dc5879bba1c9186284` | 63969 (applies clean at p1 on the integrated file) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged) |
| `selftest-receipt.txt` | — | `selftest cases=43 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV12` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

## 1. The vacuous green: a run with no graded cell

Selecting only an **open/ungraded** cell (the grid's `PG40`) produced a
valid pristine with **zero graded oracle cells**: every mutant could then
be reported as a survivor without any comparison, and the run exited 0.
That is the same class of defect as the frozen-arm false green — a green
that no measurement earned.

Version 12 makes the precondition of the experiment explicit:

* after a **valid pristine**, the run requires **at least one graded row**
  before it may report "pristine passed" and before the mutant loop
  starts. An empty graded set is **could-not-evaluate (exit 2)**, with
  zero kills and **no mutant run at all**;
* likewise, a **mutant** run that yields no graded row cannot be a valid
  survivor: it is reported as could-not-evaluate, not as "survived".

Nothing is made graded: the open cell stays open and ungraded, and the
ordinary survival path (graded rows present, no violation) is unchanged.

The bounded control: the stub reports an **open-only** row (kind `open`,
ungraded) and the selftest asserts that the runner aborts with exit 2
after **exactly one grid invocation** (the pristine) and that the reason
names the missing graded row.

## 2. This is a precondition, not a feature

There is no new manual mode, no telemetry framework and no new admission
gate: the rule is the experiment's own precondition — a sensitivity run
without a graded cell has nothing to compare. Exit 2 remains
could-not-evaluate; an ordinary survival still completes with exit 0;
PM08 stays unexecuted and uncredited.

## 3. Unchanged from version 11

The current-only arm rule and its help text; the provenance block (the
candidate digest, the grid digest, the grid-reported producer digest with
its mismatch refusal, the population and expectation digests and size, the
grid's `auditor_sha256` map, and the observed per-mutant auditor digest
alongside the failed and class rows); the operators, their alternatives
and their attribution; the class taxonomy and aggregates; the harness-fault
set (row `traceback`, the canonical `internal_error` flag, the stderr
diagnostics, an invalid row exit, a malformed verdict); attribution
enforced before a credit with the allowlist not widened; the grading
explanation preserved where the grid reports it and absent where it does
not; the legacy empty-selection guard; the 47 rows and the twin links; N3
as an intentional envelope with no "declared not broken" metric.

## Not run

No sensitivity sweep and no legacy fixture run (wave 2 is active). The
checks exercised here are the bounded selftest (43 assertions, 0 failed)
and the source compile. No grid version is claimed that was not hashed.
