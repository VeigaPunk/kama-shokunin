# Round-93 `## Dispositions` — candidate (SB01LessonDraft)

The landed lesson (`corpus/lessons/round-93.md` at tip `54b8578f`) has no Dispositions section; it folds the
round-92 closure's R1 into its M3 and leaves R2–R6 unanswered. Round-92's lesson answered its predecessor's R1–R5
in a dedicated section. This is the missing section, drafted from the round-93 record at `54b8578f`. Items that are
not yet measurable are marked so, not claimed.

## Dispositions of the round-92 closure (R1–R6)

- **R1** (`round75-instruments` red; `APPEND_DEBT unaccepted` growing): **carried, not claimed.** The last committed
  gate receipt is round 92's (`.ufo/waves/round-92/measured/gate-final.out`:
  `APPEND_DEBT round=92 … events=97 … unaccepted=18 bad_rows=19`). No round-93 gate receipt exists at this read
  (`grep -rn 'APPEND_DEBT' .ufo/waves/round-93/ --exclude-dir=SB01LessonDraft` is empty), and the lesson's
  `events=100 unaccepted=21` has no committed receipt (lesson M3). This round's probe-bound re-captures
  (`measured/r90-reason-recapture.out` at M1, `r90-reason-recapture-M1b.out` at `b3765799`,
  `r90-reason-cells-recaptured*.jsonl`) replace 24 lines each with identical triples; they are exactly the
  by-design deletion events the carried L0 asks the operator to accept. The register cannot accept rows without that
  ruling; stated, not claimed.
- **R2** (superseding rows for R01/R08 under KQ149, not prose only): **done structurally; C2 not verified.**
  `SKILL.md` @ `ee19acbd` carries `## Listen port and slot-count setters (round 93 revision)` with R16 (port,
  supersedes R01) and R17 (`n_parallel`, supersedes R08); `measured/c2.out` prints
  `decisions=2 decisions_bound=2`. A non-author K2 read then fired on P05–P07 and on R16's router-child clause; the
  L1 recorded the outcome at `54b8578f` (SKILL dated correction, lesson M4/M5, KQ151, "C2 not verified"). R2's
  "every setter named or excluded" is answered in form; the decision wording is not.
- **R3** (the counter must be shown able to fail on the R01/R08 class before it counts): **done for that class.**
  `controls/c2-base.out` (`rows=0 missing=48`, exit 1); `controls/c2-forgeries.out` V1 (the round-92 R01/R08
  decisions with no overriding rows) prints `decisions_bound=0`, exit 1; V9 (a preset left out of R17) prints
  `overriding-set want=4 got=3`. The broader forgery set is weaker than 12/12 — CR02 `14/31` bind, MT02 `16/26`
  mutants survive — and is carried under R4.
- **R4** (`json_array` quadratic path; the C2 counter gaps CR01/MT01): **routed, not claimed.**
  `plans/round-93-claims.md` §"Separability, sources, carried defects" routes it to round 94 ("round 93 takes SC02 F6
  instead"). This round adds its own counter-gap receipts to that carry: `w1/CR02SetterCounter.md` DEFECT-1 (14/31
  forgeries bind; 20/38 with `forgeries2`) and `w1/MT02SetterCounterMutants.md` F1 (16/26 mutants survive, 13 false
  greens). Neither changes the K2 outcome; both widen disclosed limit L1.
- **R5** (report author date precedes the cited tip): **open, not measurable yet.** The round-93 report does not exist
  at this read (`.ufo/reports/round-93/` absent). The closure must run
  `git log --format='%an %H %ad / %cd' -- .ufo/reports/round-93/kama.md` after the final lane push and reject an
  author date earlier than the tip it cites.
- **R6** (RV02 NOTE-1, R03 wording): **carried.** `plans/round-93-claims.md` §"Separability…" carries it; the round-93
  SKILL section adds R16/R17 and does not touch R03. No round-93 receipt addresses it.

## Wave-1 findings — integrated status at `54b8578f`

- **RV01 DEFECT-1** → lesson M5 (landed): the memo key omitted `st_ctime_ns`; the fix landed at `b3765799`, C1 was
  re-measured there (`measured/c1-M1b.out`, 10/10, exit 0), harm is unchanged (`measured/harm-M1b.out`, all arms
  exit 0), and the r90 receipt was re-captured at the new probe (`r90-reason-recapture-M1b.out`, 24 identical
  triples). Remaining gap: the claims' C1 rule text still names a four-field key; disclose the five-field delta.
- **RV02 BLOCKER-1 / CR02 DEFECT-2** → lesson M4 (landed): P05–P07 cells contradict the section's glossary; K2 fired;
  KQ151 added. Remaining gap: M4's `Captured-by: none` should be K2 (fired), per the same commit's message.
- **RV02 DEFECT-2** → SKILL dated correction (landed) but **no lesson row**: R16's router-child clause is defeated by
  `--vision-gemma-*` (8014, argv order). Add the lesson row so "C2 not verified" does not rest on M4 alone.
- **RV02 DEFECT-3** → SKILL correction "Limits" (landed): S596/S598/S599 anchor ranges name narrower lines than the
  P-rows cite. The lesson Gate's re-opened row still says "admitted for the P-rows that cite them" without the
  caveat; point it at the correction.
- **EX01 / EX02** corroborate C1: no base-right/M1-wrong held-out cell; the distinct-copies deadline limit is
  disclosed; the live router oracle agrees at both revisions (`w1/EX01HeldOutRepeat.md`,
  `w1/EX02LiveRouterRepeat.md`).
