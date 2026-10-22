# MutationEvidenceV14 — round 24 C1 mutation contract, inventory version 14

**Proposal only; no production file is edited by this seat.** Versions 2–13
stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched. No backend, no schema
framework, no operator, no 47-row, no expectation and no twin-link change;
no full sensitivity sweep.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `971c3ecbc1af05d4e6806ed06e8d3c7499ff55caf09e7bbc2c5ae2992204f200` | 84320 |
| `promisor-mutants-v14.patch` | `cf21f1f27530ae450b1728c0e3a7d9d8545665d420d665bf4668dd04461786d3` | 69681 (applies clean at p1 on the integrated file) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged) |
| `selftest-receipt.txt` | — | `selftest cases=47 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV14` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

## 1. The exit-only pristine gap is closed

The pristine check consulted only the grid's **exit code**: a grid that
returned rc 0 while a graded row was unmet (or its twin constraint
failed) was accepted as a pristine, so the run continued on a "pass" the
grid's own rows contradicted.

Version 14 requires the pristine to satisfy the grid's contract in full:
**rc 0 AND no violated graded row**. Otherwise the run is
could-not-evaluate (exit 2) **before any mutant runs**.

## 2. The mirror contradiction is not a kill

The same rule, symmetric, applies to a mutant run: **rc 0 with a violated
graded row** is a contradictory grid protocol (the grid says the run
passed and names a violated row), so it is **could-not-evaluate with zero
kills** — the receiver may not launder a contradiction into a pristine or
into a kill. This is the mirror of the rule that already existed for
"rc 1 without an identifiable violated row".

The resulting protocol matrix (unchanged where it already held):

| run | rc | violated graded rows | outcome |
|---|---|---|---|
| pristine | 0 | none | pristine passes |
| pristine | 0 | some | could-not-evaluate (exit 2), no mutant runs |
| pristine | 1 | some or none | could-not-evaluate (exit 2) |
| mutant | 0 | none | survivor (a completed run, exit 0) |
| mutant | 0 | some | could-not-evaluate, zero kills |
| mutant | 1 | some | kill, attributed to the mutant's rows |
| mutant | 1 | none | could-not-evaluate (the contradiction's other side) |

A real grid never contradicts itself; the point is that the receiver
cannot read a contradiction as a pass.

## 3. The two bounded controls

* **pristine rc 0 + a violated row**: the stub's pristine contradicts the
  grid, and the selftest asserts the runner refuses with exit 2 after
  **exactly one grid invocation** (the pristine) and a reason that names
  the violated graded row;
* **mutant rc 0 + a violated row**: the pristine is sound and a mutant
  run contradicts the grid; the selftest asserts the run exits 2, that
  **no kill is credited**, and that the could-not-evaluate entry records
  the contradictory row.

## 4. Unchanged from version 13

The current-only arm rule and its help text; the graded-row precondition;
the pristine producer-digest refusal (before the loop); the early
recording of the observed per-mutant auditor digest; the provenance block;
the operators, their alternatives and their attribution; the class
taxonomy and aggregates; the harness-fault set; attribution enforced
before a credit with the allowlist not widened; the grading explanation
preserved where reported and absent where not; the legacy empty-selection
guard; the 47 rows and the twin links; N3 as an intentional envelope with
no "declared not broken" metric; PM08 unexecuted and uncredited.

## Not run

No sensitivity sweep and no legacy fixture run (wave 2 is active). The
checks exercised here are the bounded selftest (47 assertions, 0 failed)
and the source compile. No grid version is claimed that was not hashed.
