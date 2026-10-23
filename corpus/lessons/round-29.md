# kama — round 29 lesson (2026-10-23, attempt 1)

Author: kama L1 round 29 (KamaR29). Base `2aa46e24`. One measured claim (C1, calibration),
the routed repairs from `corpus/lessons/round-28-verifier-spotcheck.md:220-247`, and the frontier
step. Seat reports: `.ufo/waves/round-29/controls/` (pre-freeze control call) and
`.ufo/waves/round-29/w1/` (wave 1: `advice/`, `out/`).

## Claims

**C1 (measured, calibration).** Surface: SCORECARD.md and SHONEN.md self-assessment statements.
The lane gains a check of six statement classes (P pointer, H digest, N line count, C commit,
T time, Q quoted output) against the repo at the commit that wrote each line (`git blame
--line-porcelain`, S174), and SCORECARD.md gains an appended section `## Round 29 —
self-assessment corrections` that records the observed value for each base statement the check
finds false. Why this shape: rounds 26-28 were depth claims on live server measurement and were
rejected; the round prompt asks for a different claim shape, and calibration (7) is the lowest
assigned axis (`../shokunin.conf:52`).

Order of events (all lane commits by `jj-lane.sh`):
1. `827d1365` (10:55:45Z) freeze: counter (sha256 `fe11d599…7383`), preregistration, base receipt
   `before/c1-base.out`: `statements 69 mismatched_at_base 11 … unresolved 11 met False`, census
   start. Before the freeze the L1 ran four pilots of the extractor on the base and fixed extractor
   faults found by reading matched lines (preregistration `pilot_history_before_freeze`): no seat
   had run. This is pre-freeze design work informed by base data; it is disclosed, not hidden.
2. Control call, 14 seats (dispatched 10:58Z), committed `35b90184` before any correction row:
   no control meets the target (`controls/SUMMARY.md`). Closest shortcuts: text-only prediction
   (CtlSourceBounds) 9 valid, 7 false, unresolved 9; base-tree check (CtlBaseTree) 6 valid, 4
   false, unresolved 9. The reference policy RefPaste (the claimed work) meets by design.
3. Wave 1 (32 seats) dispatched 12:02:5xZ after a 37-seat send waited the full seat-gate window
   (11:00-11:59Z, `timeout … live=63 pending=33`) and was re-sized to 32 items.
4. `513eba3b` (12:02:54Z): 11 correction rows (data) appended by the L1. Measured from a fresh
   clone of the lane remote: `statements 69 mismatched_at_base 11 append_only True
   valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a`
   (`final/c1-513eba3b.out`).

Falsification in wave 1:
- ConfirmM01-M11 checked each of the 11 statements by hand without running the counter: all 11
  `confirmed-false` under the class rule, each with the intended referent
  (`w1/out/ConfirmM*/verdict.json`).
- CriticAxisFit (`w1/out/CriticAxisFit/critique.md`): the strongest objection is that the class
  rules flag evidence that does not resolve, not judgments that were wrong. Lines 740 and 1375
  cite real lane files without their directory, and the judgments they support were true at W. The
  seven Q failures show the output was not retained verbatim outside the self-report files; they do
  not show the reported values were false. The critic does not count RefPaste as a skipped-work
  control (it performs the declared work), but holds that `unresolved 0` records completed
  acknowledgements, not proven overreach. **The author accepts this reading.** C1 moves the
  self-assessment's evidence record (11 statements whose stated evidence did not resolve at
  writing now say so); it does not show the lane's past judgments were wrong.
- CriticPredicateIdentity (`w1/out/CriticPredicateIdentity/findings.md`): the predicate is not
  literally one sentence in three places. preregistration.json C1.predicate is two sentences that
  incorporate the counter docstring's class rules; the receipt carries the label and target fields
  but not the sentence. The operative target fields agree. This is a conformance defect against the
  round contract's "same sentence" rule, disclosed here and in the report.
- RecallA/RecallB: the extractor misses 72 checkable statements of the six classes (32 in
  SCORECARD lines 1-720, 40 in 721-1441, none in SHONEN); 70 hold at W and 2 do not (line 41 Q
  `file=yes`, line 901 Q `declared2048 = captured training2048`). These are not counted; recall is
  a disclosed limit. ConfirmM07 also found SCORECARD line 824 says "selftest 5 cases" while the
  tool at W prints 12 cases: a prose mismatch outside the six classes.
- ScoutHeldRules (`w1/out/ScoutHeldRules/held-rules.md`): no lane tool already checks these
  statements at their writing revision; the four nearest tools' self-tests exit 0.
- ConnectorSiblings (`w1/out/ConnectorSiblings/overlap.md`): no sibling province owns
  writing-revision statement checks; tsukuroi's and kaidoku's self-assessment checkers are
  different claims on their own lanes. No contested scope.

## Repairs (round-28 spot-check routed items, not claims)

| # | Item | Disposition | Evidence |
|---|---|---|---|
| 1 | depth counter design | criterion KQ38 appended to QUALITY.md (no depth claim this round) | `corpus/QUALITY.md` §Criterion added — round 29: measured depth…; draft `w1/out/ScribeDepthCriterion/` |
| 2 | A1 time | corrected by appended record below; frozen bytes untouched | `w1/out/ScribeA1TimeCorrection/evidence.txt`; `git log -1 --format=%cI 75b78bb4` = `2026-10-23T05:38:16-03:00` |
| 3 | timing evidence outside the repo | raw transcript excerpts committed with source and excerpt sha256 | `w1/out/ExecTimingTranscript/provenance.json`, `excerpt-DataG01-2.jsonl` (tool call 08:35:53.929Z, result 08:35:54.037Z), `excerpt-DataG15-2.jsonl` (08:36:53.343Z / .398Z) |
| 4 | gate-registry-check | see §Repair 4 below | `w1/out/ExecGateRegistryV2/` |
| 5 | instrument registry kinds | see §Repair 5 below | `w1/out/ScribeInstrumentRegistry/` |
| 6 | echo-recheck exit-2 receipt | committed: `echo-recheck cannot-evaluate --out exists: …` `exit=2`, sentinel sha256 unchanged, no llama-server before or after | `.ufo/waves/round-29/repairs/echo-exit2/receipt.txt` (`513eba3b`) |
| 7 | lesson Gate preamble 4 vs 8 | corrected by appended record below | `.ufo/waves/round-28/final/quote-check.out` |
| 8 | report wording | the round-29 report states that the round-28 A1 counter was also met by a post-data declared-bounds projection (20/20) | report §Work performed |
| 9 | SHONEN box 2 wording | SHONEN.md line 8 corrected (box stays `[~]`) | `w1/out/ScribeShonenBox2/evidence.md`; `.ufo/waves/round-17/runs/controls-frozen.json` |

**Round-28 A1 amendment-time correction (append-only; drafted by ScribeA1TimeCorrection).** The
frozen `.ufo/waves/round-28/preregistration.json` `pre_data_amendment_A1` text says "Written
2026-10-23 ~08:45Z"; that time is wrong. The authoring record logs the A1 edit call at
08:37:23.720Z and its result at 08:37:23.732Z, and commit `75b78bb4` is dated 08:38:16Z. This
correction leaves the frozen bytes untouched. It does not imply A1 preceded all data evaluation:
DataG01 ran A0-counter functions at 08:35:54Z, before the edit (`w1/out/ExecTimingTranscript/`).

**Round-28 Gate quote-count correction (append-only).** The `## Gate` preamble of
`corpus/lessons/round-28.md` says "Four seat-supplied quotes were not verbatim". That counts only
the four paraphrase cases (lora, xtc_probability, temperature, logit_bias).
`.ufo/waves/round-28/final/quote-check.out` reports `seat quotes 34 not-verbatim 8; gate quotes 34
not-verbatim 0`: the other four (preserved_tokens, ignore_eos, stop, samplers) were joined with
"...". Eight of 34 seat quotes were not verbatim; all 34 Gate quotes passed.

## Gate

New SOURCES rows S174-S177, each opened this round by the wave-1 scribe named (fetched page saved
with sha256 in its out dir) and checked against the installed Git 2.56.0 manual where available.

| S### | URL | accessed (UTC) | located quote (≤ 25 words) | opened by |
|---|---|---|---|---|
| S174 | https://git-scm.com/docs/git-blame | 2026-10-23T12:02:48Z | "last modified the line" (§DESCRIPTION) … "commit information for each line, not just the first time a commit is referenced" (§--line-porcelain) | ScribeSrcGitBlame |
| S175 | https://git-scm.com/docs/git-merge-base | 2026-10-23T12:03:03Z | "and exit with status 0 if true, or with status 1 if not." (§OPTIONS `--is-ancestor`) | ScribeSrcMergeBase |
| S176 | https://git-scm.com/docs/git-grep ; https://git-scm.com/docs/gitglossary | 2026-10-23T12:02:41Z / 12:02:57Z | "Instead of searching tracked files in the working tree, search blobs in the given trees." ; "If it matches, the path is ignored." | ScribeSrcGitGrep |
| S177 | https://git-scm.com/docs/pretty-formats | 2026-10-23T12:02:47Z | "committer date, UNIX timestamp" (PRETTY FORMATS, placeholder `%ct`) | ScribeSrcPrettyFormats |

Status changes: S174-S177 new rows, status `mined`, used-by
`corpus/knowledge/self-assessment-at-writing.md, .ufo/waves/round-29/count-c1.py`. S177's scribe
drafted `queued` with used-by `—` (the entry was not yet landed when it checked); the L1 set
`queued → mined` and `— → the entry` on integration. No existing row changed.

Decisions on seat findings:

| Finding (seat) | Decision | Reason |
|---|---|---|
| Amend the counter or predicate after the axis-fit objection (CriticAxisFit implies a semantic class rule) | **reject** | kill rule: the predicate is frozen; the objection is accepted as the reading of what C1 shows, not as a rule change |
| Count the 72 recall misses or the line-824 "5 cases" prose mismatch (RecallA/B, ConfirmM07) | **reject** | not in the frozen universe; disclosed as limits |
| Treat RefPaste as a control meeting the counter | **reject** | it performs the declared claimed work (CriticAxisFit agrees); the axis question is answered by the reading above, not by calling it a shortcut |
| L1 cause cells "no committed file at W holds this text" (ConfirmM02, M04) | **admit** | the span existed at W in LOG.md or a lesson (excluded files); corrected by an appended note in the SCORECARD round-29 section |
| SHONEN box 2 corrected wording (ScribeShonenBox2) | **admit** | verified against `controls-frozen.json` and the round-17 falsify advice |
| Predicate not one literal sentence (CriticPredicateIdentity) | **admit** as a disclosed conformance defect | no rule change |

## Mistakes

| class | evidence pointer | captured-by | fix |
|---|---|---|---|
| The lane's own false-timestamp falsifier missed the round-28 A1 misdate (round 28). `tools/prereg-time-check.py` read only `YYYY-MM-DDTHH:MM[:SS]Z`; the A1 text wrote `2026-10-23 ~08:45Z`. | `.ufo/waves/round-29/mined/orig-75b78bb4.out` (`no ISO-8601 UTC timestamps found … exit=0` at 75b78bb4) | the tool's own self-test, which had no non-`T` form; caught by the round-28 closure | the tool now also reads `YYYY-MM-DD HH:MMZ` and `YYYY-MM-DD ~HH:MMZ`. Shown able to fail: patched run at 75b78bb4 flags line 41 `2026-10-23 ~08:45Z (later than commit by 404s)`, exit 1 (`mined/patched-75b78bb4.out`); d8bf1804 passes (`mined/patched-d8bf1804.out`); self-test 14 PASS exit 0 (`mined/patched-selftest-v2.out`); MutateTimeCheck's 3 surviving mutants (plain-space form removed, seconds truncated) are killed by the added 7-second case (`mined/survivor-recheck.out`) |
| The L1's own correction cause cells overstated (this round). Several cells said "no committed file at W holds this text" although the span sat at W in LOG.md or a lesson, which the Q rule excludes. | `w1/out/ConfirmM02/verdict.json`, `ConfirmM04/verdict.json` | ConfirmM seats (non-author hand checks) | appended note in SCORECARD §Round 29; the counted last cells are unaffected |
