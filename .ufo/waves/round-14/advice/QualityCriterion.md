# Round 14 — QualityCriterion (KQ17)

Scope: owned file `corpus/QUALITY.md` only, append-only. No tests, classifier,
selftest, harness, census or network executed. No historical lesson, receipt,
verifier or source file edited.

## Change

`corpus/QUALITY.md`: appended the round-14 section and one row, `| KQ17 | ...`
(line 72), after the intact KQ16 row. Prefix preserved: `git diff --numstat`
reports `11 0 corpus/QUALITY.md`; lines 1–61 are byte-identical (old-file
digest read before the append, `596f87ca…`, matching a pre-append hash of the
first 61 lines). KQ rows matching `^\| KQ\d+` are 16 before and 17 after; the
plain `| KQ17 |` prefix matches the same pattern as KQ1–KQ13/KQ15–KQ16, while
the historical KQ14 `(supersedes ...)` cell is untouched.

No criterion is superseded. KQ13's available/loaded/identity/readiness
separation, KQ14's semantic-human boundary and KQ16's finding-ID/exit
correction remain in force.

## KQ17 obligations written

1. **Outer finding/exit distinct from subfindings and counts.** `finding_id`
   and `verdict_exit` are reported separately from every recorded subfinding
   and aggregate count. A verified-anchor count is not zeroed by a
   higher-precedence could-not-evaluate finding, a count does not change the
   selected exit, and “not admitted as a comparison” is not count 0. The
   selected finding follows the classifier's fixed decision order; `reasons`
   annotates it without upgrading or downgrading the finding or exit. This is
   the prior outside round-13 D2 rule, credited there and marked append-only
   historical clarification, not a round-14 measurement.
2. **Available / loaded / remote separated; readiness unknown.** Tags
   inventory, ps residency and `remote_model`/`remote_host` origin are distinct
   classifications; `readiness` is literally `unknown` and `scope` is
   `offline-captures-not-runtime` for every result including
   `loaded_same_digest`. Exit 0 requires exactly one selected case-sensitive
   tags entry whose `name` or `model` exactly equals the expected string (no
   alias traversal) and one ps entry, nonempty equal string digest and no
   remote marker; that is metadata correspondence only. Classification writes
   nothing beyond stdout; `--selftest` may write only removed temporary
   fixture files.
3. **Fail-closed classification.** No tags match → `unknown` (2); matching
   local tags digest without ps match, or valid empty ps array →
   `available_not_loaded` (1), meaning absent from the supplied ps capture
   only; selected-entry name/model conflict →
   `identity_conflict` (1); otherwise, after the selected identity and
   nonempty-digest checks of `rulings.json` `final_total_order`, a nonempty
   remote marker on the selected entry → `remote_inventory` (1) regardless of
   whether nonempty selected digests differ; differing nonempty tags/ps
   digests → `identity_conflict` (1). Missing/invalid/duplicate/unavailable
   input fails to `unknown`/`invalid_input` (2), and a missing ps input is not
   an empty ps array.
4. **Fixed literal regression cases.** Committed `tests/ollama-evidence/cases.json`
   names each expected `finding_id` and exit; `--selftest` runs the actual
   child CLI and asserts both, reporting expected/observed records and
   passed/failed counts. No import-only assertion; no runtime, acquisition or
   readiness claim.

L1 final-row correction applied: remote classification names the
`final_total_order` in `.ufo/waves/round-14/rulings.json` (selected identity and
nonempty-digest checks precede remote handling; remote precedes unequal
nonempty digests); exact selection is `name` or `model` string equality with no
alias traversal; classification writes nothing beyond stdout while `--selftest`
may write only removed temporary fixture files. No checks were rerun after
these edits.

## Retained evidence (static reads only)

- `corpus/QUALITY.md`: full read before edit; KQ1–KQ16 rows and section
  headers unchanged; post-edit tail re-read.
- `corpus/lessons/round-14.md` §Mistakes after L1's A5/A6 update: current C1
  design mistake `ambiguous design precedence` (initial spec allowed
  remote-inventory and differing-digest overlap; `rulings.json` fixes
  identity-before-remote-before-digest precedence) and `verdict/count
  conflation` (round-13 outside D2; discovery attributed to the non-author
  verifier, no C1, axis or trend credit), plus §Named historical
  clarification recording source-only mismatch count 1 under a verified
  anchor versus outer `manifest_invalid`, exit 2.
- `.ufo/waves/round-14/rulings.json`: input/selection rules used to check
  KQ17's precedence wording (identity conflict before remote handling, remote
  marker before unequal digest, empty markers not remote, absent ps with
  local tag digest `available_not_loaded`).
- `corpus/lessons/round-13-verifier-spotcheck.md` §Routed defects item 2
  (D2, lines 259–267): append a named clarification; do not rewrite the old
  lesson or receipt.
- `.ufo/waves/round-12/acceptance.json` `repoint` record: `mismatches: 1`,
  findings `manifest_invalid` + `source_mismatch`, `exit: 2`,
  `integrity: not_checked`.
- `tools/kama-ollama-evidence.py`: `FINDING_EXIT` map, capture validation,
  selection order (duplicate → invalid_input; name/model conflict →
  identity_conflict; tags remote → remote_inventory; absent ps →
  available_not_loaded; ps conflict/remote/digest → identity_conflict or
  remote_inventory) and `readiness`/`scope` constants.
- `tests/ollama-evidence/cases.json`: 38 cases; expected findings
  `invalid_input` 15, `unknown` 9, `loaded_same_digest` 5,
  `remote_inventory` 4, `identity_conflict` 3, `available_not_loaded` 2.
  Standing case literals, not a promise that the corpus stays at 38.

## Limits

- No execution evidence: the classifier, `--selftest`, measure harness,
  source census and all integration checks were not run by this seat. KQ17 is
  a written quality bar, not a measured round-14 pass.
- Fixture success is lane-authored literal conformance; it does not prove
  vendor semantics, runtime integration, network acquisition, local weights,
  current residency or readiness.
- A fixture count/verdict distribution quoted above is a read-time
  observation; it may change before L1's measured commit.
- Outside review is absent for round 14; the round-13 verifier D2 remains the
  only non-author grounding cited.
- No tool was installed or updated.

## Routing

`KamaR14.AttackDenominator` A5/A6 concerned the L1-owned
`corpus/lessons/round-14.md` draft, which this seat does not own; routed to
`KamaR14`, which updated the lesson (D2 is only the named clarification with
closure left to outside review; the missing executable is a capability gap,
not a prior defect; new `ambiguous design precedence` row for the initial
remote/digest ambiguity now pinned by `rulings.json`). KQ17's motivating cell
was re-grounded to those updated row names in this same append, so no
cross-file citation coupling remains. A7's gloss was applied:
`available_not_loaded` means absent from the supplied ps capture only. D2
carries no C1, axis or trend credit.
