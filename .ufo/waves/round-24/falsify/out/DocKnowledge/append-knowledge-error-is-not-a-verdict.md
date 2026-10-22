
## Round24 falsification erratum (2026-10-21, appended)

Measured at the pinned round-24 revision 2e254a1763a9c08aa07fc53081287f506c447d84
against tests/report-audit/repo-state-grid.py, tests/report-audit/promisor-grid.py
and tools/report-landing-audit.py; no sentence above is rewritten, and no
registered expectation, oracle row or immutable ledger cell is edited after the
observation.

- The pinned refusal reason is per grid row, not global. A row that pins no
  reason (F28-shallow-fleet, F29-broken-branch-same-named-tag) credits any
  exit-2 refusal, so an unrelated failure is credited met on those rows; F24's
  pin is the catch-all's own generic `could-not-evaluate: internal: ValueError`
  text, which any internal ValueError satisfies. The earlier claim that the
  catch-all cannot launder an unrelated failure into a met row holds only for
  rows that pin a reason.
- At the pinned revision 2e254a1 F17-errata-revision-correction and
  F24-huge-round-number are `contract` rows (the pinned grid file's kind column
  says so; the label changed in e876b95, before the pinned revision); the
  frozen-auditor-plus-catch-all ablation measures 0 fault rows and 2 contract
  rows met, not one fault row.
- The round-23 lesson's frozen-arm count of 8 is a miscount relative to the
  published/named population: F26 is present in the grid at the named 245a37f6
  snapshot (34b2376 is its ancestor), and the retained round-23 falsify
  artifacts count 9 at that population directly — F01, F02, F16, F18, F19, F20,
  F22, F24, F26 — in `.ufo/waves/round-23/falsify/out/CritAxisScore/grid-both.json`
  and `grid-frozen2.json` (frozen arm), also
  `.ufo/waves/round-23/falsify/advice/CritAxisScore.md:92`. The producer of the
  earlier "8" is unestablished, so this erratum does not claim that no earlier
  count existed; it records that the published population yields 9.
- The legacy F28/F29 rows keep their missing reason pins and stay open; they
  are not credited as content-derived proof of a refusal.
- F24 met through the generic internal text is an error-boundary contract only,
  not domain correctness.
- The registry's mutable consumer cells do not reconcile every row this file
  names (S093 is named above and cited at the round-23 section's source line but
  is not listed in that row's used-by cell), so the reconciliation sentence above
  is qualified by this erratum; the used-by bookkeeping is left to the curator.

source: own measurement at 2e254a1763a9c08aa07fc53081287f506c447d84
(.ufo/waves/round-24/falsify/advice/DocKnowledge.md); tools/report-landing-audit.py,
tests/report-audit/repo-state-grid.py, tests/report-audit/promisor-grid.py
