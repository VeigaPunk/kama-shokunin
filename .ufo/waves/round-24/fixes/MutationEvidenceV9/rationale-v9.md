# MutationEvidenceV9 — round 24 C1 mutation contract, inventory version 9

**Proposal only; no production file is edited by this seat.** Versions 2–8
stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched. No primary-47, expectation,
twin-link, PM08 or operator-recipe change; no full sweep.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `2ee2bea2b43024c97fb8b0bf657cbc052519a34eace9b23063b55dd03f432114` | 71798 |
| `promisor-mutants-v9.patch` | `c9b44c15d720b48d4078fd858475bf35739cd66804b4aaedcc5a0161b6cdd46e` | 55533 (applies clean at p1 on the integrated file) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged) |
| `selftest-receipt.txt` | — | `selftest cases=40 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV9` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

## N1 — a false green on the frozen arm is closed

`--arm frozen` makes the grid run its **fixed frozen auditor** and ignore
the `--current` mutant, yet the runner reported "pristine passed" and the
mutants as survivors: a green that no mutant earned. The sensitivity
runner measures the **current arm only**.

* Any other arm (`frozen`, `both`, anything else) is **could-not-evaluate
  (exit 2)**, decided **before** the source is read, before the pristine
  run and before any grid call. There is no compatibility mapping that
  fakes an experiment.
* `--arm current` stays explicitly valid.
* The bounded control: the selftest runs `--arm frozen`, `--arm both` and
  `--arm currentish` against the stub grid and asserts exit 2, **zero grid
  invocations** (the canary log stays empty) and a reason that names the
  current-arm restriction.

## N8 — the inputs now identify what was measured

The document carries a `provenance` block with byte identities, not
pathnames:

| field | source |
|---|---|
| `candidate_auditor_sha256` | the sha256 of the candidate file's bytes (read once, reused) |
| `grid_sha256` | the sha256 of the grid producer's bytes (read once, reused) |
| `population_sha256` | the grid document's own field (the pristine run) |
| `expectations_sha256` | the grid document's own field (the pristine run) |
| `population_size` | the grid document's own field |
| `grid_auditor_sha256` | the grid document's `auditor_sha256` map, i.e. the digest of the auditor each arm actually used |

Each mutant entry additionally carries the **observed per-mutant auditor
digest** (the digest the grid reported for that run), and the failed-row
details carry it alongside the class rows. Nothing is invented: a field the
grid does not report stays absent, and the selftest cross-checks that the
grid's current-arm digest equals the digest of the candidate file the
runner passed. The stub grid was made honest for the canonical output
shape: it computes the same fields from the bytes it actually uses.

## Unchanged from version 8

The operators, their alternatives and their attribution; the class
taxonomy (`refusal-2`, `actual-verdict`, `verdict-change`,
`same-verdict-exit`, `diagnostic-only`, `unclassified`) and the aggregates;
the harness-fault set (row `traceback`, the canonical `internal_error`
flag, the stderr diagnostics, an invalid row exit, a malformed verdict);
attribution enforced before a credit, with the out-of-attribution rows
preserved and the allowlist not widened; no new admission gate (a valid
finite survival stays a completed run, exit 0); PM08 as a manual
review-only note; the legacy empty-selection guard; the 47 rows and the
twin links.

**N3 stays an intentional envelope:** the expectation lists are the
mutant's attribution, not a promise that every listed row breaks, and the
runner emits no "declared not broken" metric — unexecuted, allowed and
target rows are not conflated.

## Not run

No sensitivity sweep and no legacy fixture run (wave 2 is active). The
checks exercised here are the bounded selftest (40 assertions, 0 failed)
and the source compile.
