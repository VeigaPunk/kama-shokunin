# Round 29 attempt 2 — wave w2 integration record (2026-10-23, L1 KamaR29)

Wave: one v2 wave `round-29-w2`, 64 seats, policy `/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json`
(band 64–128; attack 42/64 = 65.6%: reviewer 29, critic 6, mutation-tester 7; executor 6, scout 10,
scribe 2, connector 1, sentinel 1, revenger 1, simplifier 1). Dispatched by the orchestrator (Main) as
one batched task call per the operator's mid-flight directive; L1 session dispatched zero seats.
Grant: `granted lane=kama wave=round-29-w2 seats=64 live=21 pending=65 cap=256`. First send: 20 live,
44 queued behind the host per-session job limit; all 64 dispatched inline by Main as seats settled.

## Seat verdict tally (64/64 returned; none dead; no refusals after queuing)

- Counter/receipts: RerunCounter PASS (+D1/D2/D3/D4 findings below); RerunCounterBase PASS (base receipt
  byte-identical); VerifyReceiptsCommitted AUTHENTIC ×2 (byte-identical incl. env -i); CounterDeterminism
  probes pass (limits disclosed); MutateBaseTip freeze-tip fail-closed + mutant M1 killed; VerifyFrozenBytes
  VERIFIED (counter/prereg/base receipt blobs identical across 827d1365/35b90184/513eba3b).
- Correction rows: VerifyRow01..11 all confirmed-false by non-counter hand derivation (11/11); VerifyRefPaste
  PASS (11/11 observed values byte-exact, sid sets equal, append-only strict prefix); BlameAudit 11/11 W
  match (sid hash = sha256(line)[:10] — w2 item text misdescribed it).
- Controls: RerunCtlSourceBounds 9/7/9 reproduced; RerunCtlBaseTree 6/4/9 reproduced; VerifyControlsSummary
  14/14 recomputed (two LOW findings → SUMMARY erratum appended).
- Mutants: MutateRowKill 3/3; MutateAppend 2/2; MutateFrozenHead 2/2 (one unexercised code-read edge
  disclosed); item-text arithmetic predictions wrong in two items — counter self-consistent under the
  frozen contract.
- Narrative/repairs: VerifyA1Time PARTIAL (A1 sub-second record added at integration); VerifyGateQuote
  CONFIRMED; VerifyTimingTranscripts PASS (10/10); VerifyEchoReceipt clean; VerifyShonenBox2 no numerical
  mismatch (arm clause added); VerifyShonenGates PASS; VerifyKQ38 criterion captures rule (LOW tightened);
  VerifyKQ39 PASS (CtlBaseTree drift clause reproduced); VerifyScorecardNarrative V1-V10 pass (tip-suffix
  cell fix applied); VerifyLesson PASS (timestamp/mutant-count fixes applied); VerifyKnowledgeEntry MEDIUM
  self-resolves on commit (H description tightened); VerifyLogEntries gates re-verified (citations fixed);
  VerifyAppendOnlyData VERIFIED; VerifyBaseMapping PASS (6/6); VerifyQualityDiff VERIFIED; VerifySourcesDiff
  PASS; VerifyCensusStart holds (end census receipt landed); CensusRun counts PASS, D1 same-commit landing
  honored.
- Scope/siblings: ConnectorOverlap partial prior art (kaidoku class-T tool — note appended to lesson);
  MisrootSweep no kama misroots; SentinelScope HIGH/MEDIUM spec-text defects disclosed (steered mid-flight;
  one pre-steer /fast/scratch residue disclosed); RevengerPrereg timeline CLEAN (F1 prospective citation
  disclosed); SimplifierLeftovers checklist adopted (__pycache__ discarded); FrontierReadme
  no_advance_no_core_move (README rows added); SrcS174 verbatim FAIL → fixed pre-landing; SrcS175 clean;
  SrcS176 semantic hold, fragments partial → teaches/anchor tightened pre-landing; SrcS177 HOLD-high;
  ScribeGateLog transitions integrated into the lesson; ScribeReportDraft skeleton used; CriticClaimShape /
  CriticAxisFit / CriticPredicateIdentity / CriticNoHarm / CriticStagnation / CriticReportContract all
  advisory — disclosed defects and limits carried into SCORECARD/LOG/lesson/report.

## Material findings applied at integration (pre-landing)

- D1 (RerunCounter): the four P-token cells in the correction table re-quoted verbatim would plant 4 new
  false P statements at the next extraction base. Fix: middle-cell prose rewrite (`MISSION.md:29` →
  `MISSION.md` line 29, and the three siblings). Byte-prefix property preserved (rows live after base EOF);
  dress rehearsal: r29 receipt at the simulated tip unchanged (69/11/append True/11 valid/0 false/0
  unresolved/met True); next-base simulation drops to the 11 historical falses only (97 statements, zero
  new planted).
- D2 (RerunCounter): the attempt-1 SHONEN line-8 rewrite formed a new backticked class-Q span false at its
  writing revision. Fix: "accepted-bad = 6" → "accepted-bad is 6" (removes the `=` trigger; verified no
  qualifying span remains on the line).
- D3 (RerunCounter): three dangling relative citations in SCORECARD/LOG made lane-absolute.
- VerifyA1Time: A1 sub-second authoring record (08:37:23.720Z/.732Z) added to SCORECARD + LOG.
- SrcS174/SrcS176: located-quote/teaches cells replaced with seat-verified verbatim page text.
- VerifyMistakeFix: selftest count corrected to 13 cases + aggregate (receipt-counted); 513eba3b receipt
  added showing the tool correctly still flags the frozen round-28 preregistration (exit 1, by design);
  tool docstring/help updated to the three accepted time forms; tool-vs-counter regex direction difference
  disclosed in the lesson.
- VerifyLesson/VerifyFrozenBytes: lesson prose timestamps aligned to git metadata (freeze 10:55:43Z,
  controls 11:11:28Z, w1 dispatch 12:02:03.361941Z, data 12:02:52Z); "3 surviving mutants" → 2.
- VerifyControlsSummary: SUMMARY.md erratum appended (verdict receipts vs DIAGNOSTIC copies).
- CensusRun D2/D3/D4: lesson Gate used-by migrations recorded with retain/drop decision; end census
  receipt landed at `.ufo/waves/round-29/final/census-end.out`; README index row + frontier disposition added.

## Disclosed, not fixed

Counter recall 69 of ≥141 checkable statements; predicate two-sentence conformance defect (frozen);
counter reads tip bytes not authorship; blame.ignoreRevsFile env sensitivity (fail-closed); exit code
signals execution not verdict; in_lane() absolute-pointer skip; scanner `###` edge unexercised;
ctl receipt diagnostic-copy naming; W04 duplicate-url warning class (83 rows, pre-existing pattern);
/fasta scratch residue ptc-selftest-ywq_7og0 (seat-admitted, harmless).
