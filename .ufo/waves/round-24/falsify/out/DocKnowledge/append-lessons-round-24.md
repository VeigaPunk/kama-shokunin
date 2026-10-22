
## Round24 falsification erratum (appended)

Recorded from the round-24 falsify pass against the pinned revision
2e254a1763a9c08aa07fc53081287f506c447d84; no earlier lesson entry, registered
expectation, oracle row or immutable ledger cell is rewritten, and no
post-observation legacy oracle edit is claimed.

- The pinned refusal reason is per grid row, not global. F28-shallow-fleet and
  F29-broken-branch-same-named-tag pin no reason and therefore credit any
  exit-2 refusal, and F24's pin is the catch-all's own generic internal
  ValueError text, which any internal ValueError satisfies. Those legacy
  missing reason pins stay open and are not credited as content-derived proof
  of a refusal.
- At the pinned revision 2e254a1 F17-errata-revision-correction and
  F24-huge-round-number are `contract` rows (the pinned grid file's kind column
  says so; the label changed in e876b95, before the pinned revision); the
  frozen-auditor-plus-catch-all ablation measures 0 fault rows and 2 contract
  rows met, with 0 tracebacks. F24 met through the generic internal text is an
  error-boundary contract only, not domain correctness.
- The round-23 lesson's frozen-arm count of 8 is a miscount relative to the
  published/named population: F26 is present in the grid at the named 245a37f6
  snapshot, and the retained round-23 falsify artifacts count 9 at that
  population directly — F01, F02, F16, F18, F19, F20, F22, F24, F26 — in
  `.ufo/waves/round-23/falsify/out/CritAxisScore/grid-both.json` and
  `grid-frozen2.json` (frozen arm), also
  `.ufo/waves/round-23/falsify/advice/CritAxisScore.md:92`. The producer of
  the earlier "8" is unestablished, so this erratum does not claim that no
  earlier count existed; it records that the published population yields 9.
  The filed round-23 lesson text is unchanged.
- The consumer-reconciliation table above is not universal for every row the
  knowledge entry names: S093 is cited at that entry's round-23 section source
  line and is absent from that row's used-by cell. The used-by bookkeeping is
  left to the curator; this round adds no used-by edit.

source: own measurement at 2e254a1763a9c08aa07fc53081287f506c447d84
(.ufo/waves/round-24/falsify/advice/DocKnowledge.md); tools/report-landing-audit.py,
tests/report-audit/repo-state-grid.py, tests/report-audit/promisor-grid.py
