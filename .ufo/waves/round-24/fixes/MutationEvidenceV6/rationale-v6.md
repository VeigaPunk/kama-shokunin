# MutationEvidenceV6 — round 24 C1 mutation contract, inventory version 6

**Proposal only; no production file is edited by this seat.** Versions 2,
3, 4 and 5 stay filed, the lane's integrated runner
(`6e0b9d62db9fe27f6c14c6e16ce239023f699142193adff5291e4374a1bb60a2`) and the
integrated legacy harness
(`bb32ec2146484b74ace787d4d223c4895c68fedf734464485358630bf3c10a2d`) stay
unchanged, and every filed receipt is untouched.

| file | sha256 | bytes |
|---|---|---|
| `promisor-mutants.py` | `24549daa762a8f15b24a7938afc2660adc8399a6b4a53c9faa082c6bdc8f9ed6` | 63596 |
| `promisor-mutants-v6.patch` | `80a3794b46f890777065da90d743ad1db6f40ab2f2ce86dfe30ae9adfd3218ff` | 45741 (applies clean at p1 on the integrated file) |
| `isolation-mutants.py` / `.patch` | `eace4f56e225f33e96676c0fb6c58d657256c9e37cf06130d487155d343e2a00` / `e29abf65637f987c6b0fb70a0513468382e144fa3d5c8755eab6a62c094bb0f4` | 9691 / 899 (unchanged from V4/V5) |
| `inventory-v6.json`, `selftest-receipt.txt` | — | `selftest cases=25 failed=0`, exit 0 |

Scratch: `/fast/scratch/hyaku/kama-r24/MutationEvidenceV6` at base
`2e254a1763a9c08aa07fc53081287f506c447d84`.

---

## 1. The real bug: a crashing stand-in row was credited as a kill

The version-5 `harness_fault` ignored `row.traceback` and any
internal-error marker, so a stand-in row whose auditor crashed earned
`killed: true` — a crash was being read as a violated expectation. In
version 6 a harness fault is **could-not-evaluate** (exit 2, zero kills)
in every one of these cases:

| signal | source | now |
|---|---|---|
| `traceback` | per row | CNE |
| `internal_error` | per row, arm and document (GridOracle's field, confirmed as the canonical name) | CNE |
| `could-not-evaluate: internal:` | the grid's stderr and each row's `stderr_tail` (fallback for a grid version without the boolean) | CNE |
| an invalid row exit | an `exit` outside 0/1/2 | CNE |
| a malformed verdict | exit 0/1 with a `document` field present but `None` | CNE |

The per-row boolean is authoritative; the stderr fallback may not fire
when the auditor's own message is long and its prefix falls outside the
kept tail, which is why the boolean comes first.

## 2. Attribution is enforced before a credit

A violated row whose name falls **outside** the mutant's `expect_rows` is
not a kill: the mutant becomes `could-not-evaluate` (exit 2,
`killed: false`), the out-of-attribution rows are **preserved and
reported** in `unexpected_rows` and in the reason, and the allowlist is
**not widened**. A row that the grid reports but that the mutation did not
predict is a statement about the mutation's model, not a credit.

## 3. Per-mutant classification, read from the row's own fields

Every credited violation is classified from the row's `expected_exit` and
`exit` (the fields the graded rows already carry):

| class | meaning | credit |
|---|---|---|
| `refusal-2` | a normal verdict (expected 0/1) became a refusal (2) | over-refusal signal — **not** an availability credit |
| `actual-verdict` | an unavailable case (expected 2) became a real verdict (0/1) | the **availability** credit |
| `verdict-change` | a normal verdict became another normal verdict | a substantive verdict change, reported separately |
| `diagnostic-only` | the exit is unchanged; only the diagnostics differ | **no** acceptance or availability credit |
| `unclassified` | `expected_exit` or `exit` is missing or outside 0/1/2 | no class credit is guessed |

The classes are reported per mutant (`classes`, `availability_credit`,
`verdict_change`, `diagnostic_only`, `unclassified`). A reason-only
change is never an acceptance or availability credit, and a refusal is
never labelled an availability acceptance. The paired obligations (KQ35)
are read from these **class rows**, not from a raw kill count.

## 4. Negative controls (bounded stub fixtures, no grid run)

`--selftest` now covers 25 assertions, including: a traceback row, an
`internal_error` row, a malformed verdict (exit 0, `document` None), a
violated row outside the attribution (must be preserved, must not be a
kill), a violated row without the comparison fields (must be reported as
`unclassified`, must earn no availability credit), and the pristine abort
(the canary proves no mutant phase ran). The stub rows carry the
canonical shape (`met`, `exit`, `expected_exit`, `document`).

## 5. No new admission gate

A **valid finite survival stays a completed run**: exit 0. Exit 2 is
reserved for could-not-evaluate — a harness fault, an unattributed
violation, an inapplicable mutation, a non-compiling mutant or a failing
pristine run — never for a survivor. The class support data is explicit
in the JSON document, not a gate.

## 6. The legacy empty-selection hazard: corrected attribution

The hazard itself is unchanged and the proposed guard is unchanged (an
empty selection is could-not-evaluate, decided before the source read,
the pristine and any grid call). The **attribution** is corrected: the
short-id behaviour **pre-existed** the round-24 retirement — a selector
like `--only M01` never matched the full ids `M01-replace-objects` — so
the retirement did not cause it. What the retirement did was change the
id set (M14/M22/M27/M29 retired) and expose the staleness of a
hard-coded short id; the compound edit is the id set plus the stale
selector, not a new behaviour.

## 7. Unchanged from version 5

The PM07 canonical recipe and its `expect_rows` (the version-3
restoration), PM08's manual review-only wording and shape, the legacy
empty-selection guard and its file/patch, and every other operator with
its alternatives and its attribution. The 47 grid expectations, the
operator's instructions and the filed receipts are untouched.

**Not run**: no sensitivity sweep and no legacy fixture run (wave 2 is
active). The anchors are checked statically against the latest core
`fixes/StoreLocalPresence/report-landing-audit-v9.py`
(`b9be4f428cd70842320c698794faffaa95571a60fc530df6a84d7d8cade3b26f`):
ten executable mutants, one applicable alternative each, every mutant
compiles, the review-only entry skipped.
