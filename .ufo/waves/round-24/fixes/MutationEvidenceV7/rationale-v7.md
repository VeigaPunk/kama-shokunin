# MutationEvidenceV7 — round 24 C1 mutation contract, inventory version 7

**Proposal only; no production file is edited by this seat.** Versions 2–6
stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `7ba30cccca3aa8f976dee7f20ccbfe7e4b533b65a4ceb1c5bf0e01530eaf4447` | 66708 |
| `promisor-mutants-v7.patch` | `69fe153ccc0d5e90fb68b0e96c63e88d30c1dec1b1578e8e9b04be217e7c7c6b` | 48907 (applies clean at p1) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged) |
| `inventory-v7.json`, `selftest-receipt.txt` | — | `selftest cases=34 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV7` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

## 1. The bug the L1 found, and the taxonomy that replaces it

The version-6 `classify_row` tested the **normal/normal branch before the
equality branch**, so a violated row whose exit was unchanged (0 → 0 or
1 → 1) was labelled `verdict-change`. An exit pair alone never shows
that the whole verdict changed: the same exit can hide a different
document.

Version 7 compares the exits first:

| expected → actual | class | credit |
|---|---|---|
| 0 → 0, 1 → 1 | `same-verdict-exit` | the same exit; the detail may differ — no substantive exit change, no availability claim |
| 0 ↔ 1 | `verdict-change` | the pass/fail of the verdict changed |
| 0/1 → 2 | `refusal-2` | an over-refusal signal, **not** an availability credit |
| 2 → 0/1 | `actual-verdict` | the **availability** credit |
| 2 → 2 | `diagnostic-only` | the refusal stayed a refusal |
| missing or outside 0/1/2 | `unclassified` | no class credit is guessed |

## 2. Aggregates

`diagnostic_only` is true **only** when every class is `diagnostic-only`; a
`same-verdict-exit` or `unclassified` row keeps the aggregate false and
its named rows are preserved separately (`same_verdict_exit`,
`unclassified`). `availability_credit` is true for an `actual-verdict`
class, `verdict_change` for `refusal-2` or `verdict-change`. The unused
`credit = availability` local is gone. The main agent's final statistics
are derived from the observed classes.

## 3. Behaviour control (bounded, no grid run)

The selftest now walks **all nine exit pairs** (0/1/2 × 0/1/2) through a
stand-in row and asserts the class of each; the existing missing-metadata
control stays. Total: 34 assertions, 0 failed.

## 4. Unchanged from version 6

The harness-fault set (a row `traceback`, the `internal_error` flag, the
`could-not-evaluate: internal:` stderr fallback, an invalid row exit, a
malformed verdict); attribution enforced before a credit, with the
out-of-attribution rows preserved and the allowlist not widened; **no new
admission gate** — a valid finite survival stays a completed run (exit 0);
PM07's canonical recipe and its `expect_rows`; PM08's manual review-only
wording and shape; the legacy empty-selection guard and its file/patch;
every other operator with its alternatives and attribution.

**Not run**: no sensitivity sweep and no legacy fixture run (wave 2 is
active). The anchors are checked statically against the latest core
`fixes/StoreLocalPresence/report-landing-audit-v9.py`
(`b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`):
ten executable mutants, one applicable alternative each, every mutant
compiles, the review-only entry skipped.
