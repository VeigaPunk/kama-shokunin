# FalsifyRejectAll — do the positive controls refute reject-all and accept near-case names?

Critic: KamaR15.FalsifyRejectAll. Read-only, except for this report. I did not execute any repo code: not
`check.py`, `measure.py`, `measure-before.py`, or the classifier. The counts below come from loading the
12 committed matrix JSONs with plain Python. The mutant predicates are tiny in-memory lambdas over those
literal name lists, so they show how sensitive the matrix is, not how the runner behaves. No installs.

## Axes
- **A1** Reject-all refutation: do the positive controls kill a runner that always rejects?
- **A2** Near-case acceptance: do positives pin that names close to a duplicate are still accepted?
- **A3** Two-sidedness: does the harness require a positive control at all?
- **A4** Duplicate-removed pairing: does each negative have a positive with the same stripped set?

## Inventory (observed)
- 12 matrix files hold 50 tests: 23 with `expected_rejected: false` and 27 with `true`.
- Every file has at least one positive control.
- Positive envelopes: 16 array and 7 object. Every positive has ≥16 distinct stripped names, and its
  distinct count equals its length.
- Candidate guard = frozen guard plus exactly two lines. `diff -u .ufo/waves/round-15/frozen/measure-before.py
  .ufo/waves/round-14/measure.py` shows only `+ if len(declared) != unique:` / `+ problems.append("duplicate case names")`
  at measure.py:358-359. No other normalization is added; identity is still `name.strip()` + `set` (:351-356).

## A1 — PASS: reject-all is refuted
- **Positive grading (`check.py:576-604`)** requires all of:
  - exit 0 and `verdict_exit` 0;
  - `passed == total == len(names)` and `failed == 0`;
  - classifier marker count `== len(names)`;
  - runner `subprocess.Popen` events `== len(names)`.
- `total` is the literal `len(test["names"])` (`:335`), not a number the runner reports about itself.
- A reject-all runner gives exit 1, `passed` 0, marker 0 and Popen 0. It therefore fails every one of the
  23 positives.
- `result_document` is `clean` only if every record passed (`:641`). So a full-matrix run against
  reject-all is `test_failed`.
- Mutants run over the literal names (number of positives that kill each one):

| mutant | positives that kill it |
|---|---|
| always reject | 23 |
| threshold `unique <= 16` | 19 |
| 2-char prefix key | 23 |

- None of the 27 negatives kill these mutants. Positives are the only discriminator here, as intended.
- **The frozen before-run is not reject-all either.** Under `measure-before.py` the positives should also
  measure (exit 0). Only the duplicate negatives should go red. So the before/after contrast cannot be
  explained by blanket failure on either side. [INFERENCE from source: the frozen guard lacks only
  :358-359.]

## A2 — PARTIAL: near-case acceptance is pinned for case, padding and non-ASCII only
Pinned (a mutant that over-normalizes is killed by a positive):

| Near-case | Positive control(s) | Mutant killed |
|---|---|---|
| Case variant `n00` vs `N00` | `ValidBoundaries_16DistinctPlusCaseVariantN00Accepted` (array only, 1 test) | casefold identity |
| Same tab-padding shape as the colliding negative, different stripped value: `\tn16\t` vs negative `\tn09\t` | `TabCollision-tab-wrapped-unique-array` (1 test) | "reject any padded name" |
| Non-ASCII name `名前` | `UnicodeDuplicate_valid_unique_non_ascii_{array,object}_envelope` (2 tests) | "reject non-ASCII" |

Not pinned. These mutants survive with 0 kills, because no positive contains such a pair:
- NFC vs NFD equivalence (`unicodedata.normalize('NFC', …)`);
- NFKC equivalence (for example a fullwidth `ｎ00` vs `n00`);
- internal-whitespace collapse (`''.join(n.split())`, for example `n 01` vs `n01`).

This is **not a defect in the committed candidate**. The diff shows none of these normalizations. It
bounds how far the claim reaches: the matrix pins "stripped, case-sensitive, non-ASCII-preserving
identity". It does not pin Unicode-normalization or internal-whitespace non-equivalence. Receipts must
not say that positive controls prove "only exact stripped duplicates are rejected" in general.

## A3 — CONDITIONAL GAP: a positive control is present only by literal content, not enforced
- `load_matrix` fails closed on an empty matrix (`check.py:224-225`). It has no check that at least one
  `expected_rejected: false` test exists.
- `--only` narrows to any single id (`:725-730`).
- Counterexample (derived from code, not run): `check.py --only AppendDuplicate_first_name_appended_array_envelope
  --runner <always-reject runner>`.
  - That runner returns exit 1, verdict 1, an `error` containing `duplicate case names`, `passed` 0,
    `failed == total`, `tool_present` true, null exits, marker 0 and audit 0.
  - The rejected branch (`:528-575`) passes, so the result is `clean`/0.
- The same happens if a future edit deletes every positive from the JSONs.
- Prior advice raised the same concern: `build/advice/AttackConstant.md:47` asked for "at least one literal
  `expected_rejected: false` control"; `FindingExit.md:46` covers `--only` anchoring. It was not
  implemented in `check.py`.
- Today the full matrix contains 23 positives, so this is not a current false pass.

## A4 — MINOR: three negatives have no exact duplicate-removed positive
- `DistantDuplicate.Object16FirstRepeatedAtEnd` uses the `m00…` set. `ValidBoundaries_…ExactDuplicate{Last,First}Rejected`
  use the `vd…` and `ve…` sets. No positive in any file has the same stripped set.
- The other 24 negatives each have an exact duplicate-removed positive.
- This does not hurt discrimination:
  - names never reach the child (`measure.py:220` uses an index-named dir; `:230-235` argv has no name);
  - the guard depends on names only through strip and set cardinality.
- One wording nit: `build/advice/ValidBoundaries.md:18` says the 16-unique accepted fixtures "serve as
  the duplicate-removed counterparts". They use `vb…` names, not `vd…`/`ve…`, so they are equivalent
  only up to cardinality, not literally.

## Impacted axes
- Calibration (C1): A1 holds. A2 and A3 limit what the receipt may claim.
- Operability: no effect on the guard. The committed predicate is minimal and does not over-normalize.

## Smallest safe correction (no new feature)
1. **Admission rule, no code change.** L1 admits the green only from a full-matrix run (`only: null`) in
   which ≥1 `expected_rejected: false` record passed with marker == Popen == `len(names)`. Never admit
   from an `--only` run or a matrix that has no positives.
2. **Claim bound, in the receipt or R2 text.** Positive controls defeat reject-all, threshold off-by-one,
   case-folding, padded-name rejection and non-ASCII rejection. They do not pin NFC/NFKC or
   internal-whitespace non-equivalence.
3. **Optional, owned by L1/GuardHarness, not required for this round.** A one-line `load_matrix`
   post-check that fails closed when the selected tests contain no `expected_rejected: false` entry.
   Either this or rule 1 closes A3.

## Evidence anchors
- `tests/ollama-corpus-guard/check.py`: 192-211, 224-226, 335, 528-604, 641, 725-730.
- `.ufo/waves/round-14/measure.py`: 350-364, 377-380, 220, 230-235.
- `.ufo/waves/round-15/frozen/measure-before.py` vs current: the two-line diff above.
- `tests/ollama-corpus-guard/{ValidBoundaries,TabCollision,UnicodeDuplicate}.json`: the near-case positives.
- `SCORECARD.md:495-497`: the "positive controls defeat a vacuous reject-all implementation" claim
  (supported by A1, with the A2/A3 bounds).

Report: .ufo/waves/round-15/falsify/advice/FalsifyRejectAll.md
