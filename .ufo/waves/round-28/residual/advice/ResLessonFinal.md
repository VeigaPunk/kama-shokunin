# ResLessonFinal — round-28 lesson residual review (READ-ONLY)

Reviewed `corpus/lessons/round-28.md` at `9ce5bd37` (base `4179301f`) against the
committed artifacts. No tools installed (nothing was needed). All git commands
read-only. No counter/server run.

## Verdict
The lesson's Order of events, Measurement numbers, Repairs table, Mistakes row,
Wave records, Claim-verdict paragraph and the mechanical Gate-quote content hold
against the receipts. Findings (all in the Gate "decisions" table and minor
wording):

1. **[Gate row: F28-14/F28-16 labelled seat findings]** The "Meaning-cell
   defects" admit row lists `F28-14` and `F28-16`. The seat that covered each
   ruled the original meaning cell correct — RowReview07 (F28-13/14):
   "**Holds; no correction needed.**"; RowReview08 (F28-15/16): "both rows
   HOLD. No false, unsupported or over-general statement found". No other
   wave-2 report flags these rows (grep over w2/advice for F28-14/F28-16:
   only RecountFreshClone/RowReview07/08 mentions, none a defect). The two
   meaning cells were nevertheless rewritten to add "(field-omitted value…);
   the declaration has no limits, so this is a generic float32 conversion" —
   an L1 harmonization with the section's A1-disclosure prose, not a
   seat-reported defect. Corrected text: put F28-14/16 under a separate
   "prose harmonized to the generic-conversion disclosure (no seat finding)"
   action, and cite the actual defect-flagging seats for the other 16 ids
   (RowReview04: 07,08; RowReview06: 11; RowReview09: 17; RowReview10: 19,20;
   RowReview11: 21,22; RowReview13: 25; RowReview17: 33,34; plus
   CriticDepthAxisPostData for 03,04,05,09,20,25,27,33 and
   ScoutSkillContradictions for 19,27).
2. **[Gate row: seat list incomplete/inexact]** The same row's parenthetical
   names only RowReview04/06/09/10/11/13/17 + CriticDepthAxisPostData +
   ReviewSkillSectionIntro + ScoutSkillContradictions. Wave-2 had 17
   RowReview seats; the uncited RowReview01/02/03/05/08/14/15/16 covered the
   remaining rows (and each held its rows) — the parenthetical should say
   "RowReview01-17 (defect rows in 04/06/09/10/11/13/17)…".
3. **[Minor wording] "Pre-freeze control call"** (lesson line 32): the A0
   freeze commit `d8bf1804` is 08:14:03Z; the control call was granted at
   08:14:33Z and dispatched 08:14:5xZ (`.ufo/waves/round-28/controls/HOLDS.md`),
   i.e. after the A0 freeze. The "pre-freeze" label is the preregistration's
   own usage (kill_rule / `pre_data_amendment_A1`) meaning "before the final
   (A1) counter freeze"; suggest "Post-A0-freeze, pre-A1 control call".
4. **[Minor wording] lesson lines 5-6** "Every seat report is under
   `.ufo/waves/round-28/` (controls/, controls-A1/, w1/advice/, w1/out/)" —
   the parenthetical omits `w2/advice/` and `w2/out/` where the wave-2
   reports (incl. the cited CriticA1Legitimacy) live. Complete the list.
5. **[Terminology] "Wave 1 (… 08:31-08:34Z)"** (line 38) is the dispatch
   window; seat scoring ran past it (DataG01 counter-primitive check at
   08:35:54Z, DataG15 at 08:36:53Z). Fine as a dispatch time but should say
   "dispatched 08:31-08:34Z".
6. **[Unverified claim] "validated v1"** (lines 115, 120): `w1/validate.err`
   and `w2/validate.err` are empty and neither spec carries a schema marker;
   the validation step is asserted, not evidenced. State the validator
   command/exit, or drop the phrase.

## What holds (checked against artifacts)

- **Order of events / times.** `git log` (cI): d8bf1804 08:14:03Z;
  5ebe7b1b 08:26:53Z; 75b78bb4 08:38:16Z; fb10d9da 08:53:48Z; e49b4cf7
  08:55:40Z; 9ce5bd37 09:17:31Z. A1 "written about 08:37:23Z, committed
  08:38:16Z" matches CriticA1Legitimacy (first write 08:37:23.720Z, commit
  08:38:16Z); DataG01's four row drafts scored with A0 primitives at
  08:35:54Z (critic: 08:35:53.929Z/08:35:54.037Z); data landed after A1;
  "before any data row was committed, but NOT before data was scored" holds.
- **Preregistration** (`.ufo/waves/round-28/preregistration.json`): target
  `counted >= 18`; `counter_sha256_A0` e6a706bb…0540c; `counter_sha256` (A1)
  a38faefe…49a5; pilot 2/2 (n_cache_reuse, xtc_threshold); A1 text "before
  the counter scored any data row" present (line 41) and the lesson's
  correction of it is faithful; counter bytes unchanged between 75b78bb4 and
  9ce5bd37 (proved sha256 at e49b4cf7/9ce5bd37/worktree).
- **Measurement.** base `before/c1-base.out` 0/0 met False; `final/c1-e49b4cf7.out`
  and `final/c1-9ce5bd37.out` registered 34 counted 26 met True with exactly the
  eight ids F28-11/14/16/17/21/22/25/26; `final/c1-A0-e49b4cf7.out` and
  `final/c1-A0-9ce5bd37.out` 34/34. Registry has 34 rows F28-01..F28-34; the
  eight not-counted fields are the six float32-saturation + seed + n_probs
  (matches RecountFreshClone note; all 8 rows carry `e:generic-conversion`).
- **Counted cells byte-unchanged** between e49b4cf7 and 9ce5bd37: programmatic
  diff of SKILL.md rows shows the id/field/value/outcome/source cells identical
  for all 34 rows; only the 18 meaning cells (F28-03/04/05/07/08/09/11/14/
  16/17/19/20/21/22/25/27/33/34) and intro/no-row prose changed. Registry and
  corpus/SOURCES.md are identical between those commits.
- **Gate quotes (mechanical).** All 34 rows S140-S173: quote == pinned snapshot
  lines L,L+1 whitespace-joined cut to the stated word count (≤25 words);
  field declared on line L (`new field_`); URL `#L` anchor matches; accessed
  times all in 08:32:44Z-08:34:35Z; seat fetch hashes equal the pinned snapshot
  sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
  (verified on DataG01/03/06/09/10 copies). `quote-check.out` matches its
  script: seat 34/8 not-verbatim, gate 34/0; script exits 1 iff a gate quote
  fails.
- **Controls.** HOLDS.md matches the lesson: evidential do-nothing 0, junk
  0/30, label-keyed 12/41, source-blind 14/38, duplicate-field 0/26 (receipt
  JSON re-checked); holds CtlNoReader/ObjectStore/AllFalse (cyber refusals),
  CtlEcho/SourceMisuse (auto model switch); receipt counts: CtlEcho 1/21,
  CtlSourceMisuse 2/12. A1 controls: CtlA1Conversion 20/52 A0 vs 0/52 A1;
  CtlA1Rescore source-blind 14→9, label-keyed 12→7, max 9; CtlA1BlindPlus
  11/38 (single-shot policy). No control meets 18; counter/target unchanged.
- **Wave records.** w1 spawn-result: first send refused 08:30:41Z for all 32
  (`Background job limit reached (100)`); resend chunks 12/12/8 at 08:31:50Z,
  08:32:50Z, 08:33:50Z, all refused=[]; spec roles 21 executor/4 scribe/3
  reviewer/2 scout/1 connector/1 critic = 32. w2 spawn-result: one call
  08:57:46Z started=32 refused=[]; spec roles 28 reviewer/2 critic/1 executor/
  1 scout = 32; 32 advice files per wave; dead seats none.
- **Repairs** rows 1-7: ExecCountC2Fix outputs match (`registered 14 observed
  14 bound True missing []` before/after; forged cells 14/14/True → 14/11/
  False [K2,K4,L1]; forged raw re-bound 14/14/True → 14/13/False [K3]);
  ExecEchoRecheck 6/6 exit 0 twice, existing `--out` refused exit 2 with
  sentinel byte-unchanged, mutated baseline `drift req1-plain` exit 1;
  ExecGateRegistryCheck base-4179301 exit 1 `unregistered …round-25/count-c2.py,
  …round-27/count-c1.py; registered 2 unregistered 2`; QUALITY.md round-28
  KQ37 items 1-4 verified (S139 wording, clause-(d) correction, boundary scope
  `boundary-leg.receipt.json:10-14` — string-length ≥4, exact case-sensitive,
  E26-14 named, F3 leg requirement); round-27 residual spawn at 07:23:39.921107Z
  (spawn-result.txt:10); `r27-8057282c-stat.out` shows 8057282c added 4 files
  incl. census-final.out and sources-append-only-final.out.
- **Mistakes row** line cites check out (SCORECARD.md:1197-1239 round-24
  calibration; 1252-1304 round-25 calibration/coverage; 1312-1339 round-26
  shortcut control refused before data then 12/12 after data; 1365-1370
  round-27 C1 0/15 miss, no data seat); gate-registry base proof; quote-check
  proof; pilot 2/2.
- **Claim verdict** vs CriticA1Legitimacy: the adopted wording matches the
  critic's recommended wording (post-data-informed A1, DataG01 08:35:54Z,
  written ~08:37:23Z committed 08:38:16Z, min_p -0.25→-1.5 reprobe, 20/52
  A0 vs 0/52 A1, A1 only removes rows, met unchanged). ExecShortcutPostData
  20/20 met True under A1 from declared limits, no server run by writer,
  clause (c) text-only (counter accepted nominal accessed timestamps); the
  lesson's "recorded as a limit, not a source-blind control" and "source-blind
  controls reached 14 (A0) and 11 (A1)" match CtlSourceBlind (A0 14/38) and
  CtlA1BlindPlus (A1 11/38).
- **SCORECARD round-28 row** states depth 7 → 7 with the same reasoning.
- **Instrument-registry corrections** landed in SKILL.md (C1 exit map now
  includes exit 1 malformed-JSON/uncaught path; echo-recheck write scope now
  includes `<out>.server.log` sidecar) — matching the admitted findings of
  ReviewInstrumentRegistry; Gate-registry occurrence-only limitation is stated
  in the registry row and Mistakes row.

## Residual risk / verification gaps
- DataG05/DataG07 "accessed (UTC)" cells in the Gate table could not be
  independently re-derived: their seat reports record the fetch ("re-fetched
  by curl now: same sha"; "my own fetch at 704366d matches the pin") but not a
  timestamp, and no fetched copy survives for those seats; the times
  (08:33:18Z/08:34:04Z) are plausible but unverifiable from committed
  artifacts.
- "Validated v1" for both wave specs (finding 6) is the only asserted
  operational step with no committed evidence.
- ExecCountC2Fix triple-forgery boundary and echo-recheck baseline-integrity
  ceiling are disclosed in the seat reports as limits; the lesson does not
  overstate them.
