# Falsify review: kama round 25 report draft (attempt 2)

**Verdict: defect found.**

The commit hashes, the C1 and C2 counts, the SOURCES row counts and most pointers hold. The draft still has placeholder text, leaves out required conformance items, and omits a non-author critic's harm finding about the C1 claim.

## Scope and method

- Reviewed `.ufo/waves/round-25/report-draft.md` (98 lines). It is unchanged between 46be41c and the current lane tip a46a6181 (`git diff --stat 46be41c a46a6181 -- .ufo/waves/round-25/report-draft.md` is empty).
- Checked against the report contract (`/home/vgpnk/Projects/shokunin/.ufo/prompts/kama-round-25.md` §4, lines 99–129), admission (§2, lines 37–40), campaign addendum (§6, lines 141–350) and §5 (lines 131–140).
- Read committed bytes at a46a6181 (`origin/master` and `master` both point there). Two wave-2 commits, c0a9b02 and a46a6181, landed while I worked. The draft was not changed by them.
- Git commands were read-only: `cat-file`, `show`, `diff`, `log`, `rev-parse`, `merge-base`, `branch --contains`, and `status` with `--no-optional-locks`.
- The C1 and C2 counting commands and the census ran in my own clone's extracted trees under `/fast/scratch/hyaku/kama-r25a2w2/ReviewerReportDraft/`.
- I started no llama-server, touched no port, made no commit, ran no jj command, and installed no tool.

## Blocking: fix before landing

### B1. Placeholder text remains (lines 6, 61, 68, 77, 87–89)

The marker rule (contract §4, lines 121–125) counts placeholder text as a failed round.

- Lines 6 and 68, `LANE_TIP`: use the final master tip after the last landing. At a46a6181, `master` = `origin/master` = `a46a61815f79c558992e3fdea5e01b738442d6a8`. Confirm it is pushed with `git branch -r --contains <tip>`.
- Line 61, `WAVE2_COMMITS`: replace with one row per commit (see M4).
- Line 68: after "(and at LANE_TIP)", paste the C1 counting output and its exit code at that tip. Verified at a46a6181: `registered 28 stale 0 []`, exit 0 (`counts.txt`).
- Line 77, `END_CENSUS`: paste the end-of-round census output and its exit code, and cite its file. No end-of-round file exists yet. The start census is at `.ufo/waves/round-25/before/census-validate.out`.
- Lines 87–89, `TBD`: see N1.

### B2. Claim verdicts and the no-harm statement are missing, and a known harm is not reported (lines 30, 63–71)

- Admission (prompt §2, lines 37–40) requires a verdict for each claim, a statement that no axis is harmed, and "report all verdicts and let the operator rule." The draft gives measurements only.
- Line 30 says "M17 kept on its round-23 line." That hides what the non-author critic found. `.ufo/waves/round-25/a2-build/advice/CriticC1NoHarm.md`:
  - line 1: "two fixable harms, no rejection-grade harm";
  - line 5: "Harm 1: M17 changes identity from killed to surviving";
  - line 13: the round-23 `mutants.json` records M17 as killed by row F13.
- The F13 kill moved to the new M33. The round-23 record is `SCORECARD.md:1166`: "30/31 killed on a named row; survivor M20 defensive-only". The round-25 full run is `final/c1/c1-tip-mutants.json`: `killed` 26, `mutants` 28, `surviving` ["M17-ref-shadow", "M20-log-sha-shape"].
- The instrument docstring (`tests/report-audit/isolation-mutants.py`, lines 30–42 at a46a6181, seven lines added after 1fc41e34) says M17 "keeps its round-23 line, not its round-23 kill" and that M17 "may be unkillable" ([INFERENCE] per the docstring). The report must carry both points.
- The lowest-axis obligation (prompt §2, item 2) is also not named. `SCORECARD.md` lines 1287–1291 at a46a6181 say calibration is at 7, tied with depth and adjacency, and that C1 works calibration.
- Smallest correction:
  - Replace line 30's phrase with: "M17 kept its round-23 element, not its round-23 kill; grid row F13 now kills M33."
  - Add after line 68:
    - "C1 verdict: measured. Stale anchors went from 2 to 0. No-harm: not clean. A non-author critic (CriticC1NoHarm, Harm 1) found that M17's kill was lost; it called the change fixable, and the instrument docstring discloses it. Kills: round 23, 30 of 31 (M20 survived); round 25, 26 of 28 (M17 and M20 survive). The operator rules on the axis fit and on Harm 1."
    - "C2 verdict: measured (14 observed, bound True). No-harm: <state the check you ran, or write 'not checked'>."
    - "Lowest-scoring axis: calibration (7, tied with depth and adjacency at 7). C1 works calibration."

### B3. Round shape and seat record are missing (addendum §6 item 2, lines 203–206)

The addendum requires the round shape, each wave's seat count, role mix and dead seats, any residual call, and the round total. The draft has none of these. Verified values are in `wave-shape.txt`.

- Shape: default two v1 waves, build then falsify.
- Wave 1 (build): 40 seats. Roles: scribe 14, executor 7, scout 5, critic 5, mutation-tester 3, reviewer 2, revenger 2, connector 1, sentinel 1. One batched task call (`a2-build/dispatch-attempts.json`: utc 2026-10-22T09:32:36.711851Z, spawned 40, error null). Policy v1 band 32–64.
- Wave 2 (falsify): 37 seats. Roles: reviewer 22, critic 5, executor 4, mutation-tester 3, sentinel 1, scout 1, connector 1. One batched task call (`a2-falsify/dispatch-attempts.json`: utc 2026-10-22T10:06:02.809049+00:00, spawned 37, error null). Policy v1 band 32–64.
- L2 floor (§3) met inside wave 1: connector 1, executor 7, scribe 14, scout 5, reviewer 2, critic 5. Planner is the L1 by ruling. Neither spec file has a planner role.
- Round total: 77 seats (40 + 37), inside 32–100.
- Attack items from wave 1: state the count. Wave 2 needs at least 32 distinct items. I did not verify this count.
- Residual call: state yes or no. Neither dispatch file shows one.
- Dead seats and refusals: none are recorded, since both attempts show error null. The registries hold spawn records only, with no outcome field. Write "none recorded" and say how you checked.

## Major

### M1. The C2 "before" is measured at the wrong bytes and has no commit (lines 69–70)

- Draft: "`python3 .ufo/waves/round-25/count-c2.py` (amendment-4 bytes): no receipt (counter exit 2…)."
- Evidence (`counts.txt`): at 5388b7cf, the counter's first commit, the default run exits 2 with no count and "cannot read receipt". efe58e96 has no counter file. The bytes at 5388b7cf are amendment-2 bytes, not amendment-4 bytes.
- Smallest correction: "C2 before: at 5388b7cf (the counter's first commit; efe58e96 had no counter): `python3 .ufo/waves/round-25/count-c2.py` exit 2, no count, no receipt. C2 after: at fa3b62ae (counter bytes unchanged since 46fb04bd; receipt 5c95c8f1): `registered 14 observed 14 bound True missing []`, exit 0."
- Optional, and it shows the stricter counter can fail: the first receipt 5ea4fc44 scores `registered 14 observed 11 bound True missing ['L1', 'L2', 'L3']` under the final counter (`counts.txt`).

### M2. The C2 target was widened from 8 to 14 without saying so (lines 16–18)

- `preregistration.json` line 36: `"after_target": "observed 8 (of the 8 cells below)"`.
- `preregistration-amendment-2.json` line 26: `"after_target": "registered 14 observed 14 bound True"`, plus the added cells X1–X3 and L1–L3.
- Amendment 2 is committed at 5388b7cf, before the first receipt (5ea4fc44). The change is legitimate, but the report must say it.
- Fix: add "The preregistered target was observed 8 of 8 cells. Amendment 2 (5388b7cf) widened it to 14 cells before any receipt was committed."

### M3. "Two attack seats found false counts" is inaccurate (line 35)

- Amendment 3 came from one seat, MutationC2Counter (`preregistration-amendment-3.json` line 8).
- Amendment 4 came from two seats, CriticC2SizingA2 and CriticLoadCells (`preregistration-amendment-4.json` lines 8–9).
- Only CriticC2SizingA2 found false counts (15 bad receipts scored 14 of 14). CriticLoadCells found an overlap that was asserted by a label and not recorded.
- Fix: "counter tightened by amendment 3 (c808ba07; wave-1 seat MutationC2Counter) and amendment 4 (46fb04bd; wave-1 seats CriticC2SizingA2 and CriticLoadCells)."

### M4. The Landed changes table is incomplete, and its helper claim is unsupported (lines 49–61)

- Three round-25 commits after fa3b62ae are missing from the table: 46be41c (report draft, falsify spec, late wave-1 advice), c0a9b02 (falsify-wave corrections in progress) and a46a6181 (falsify-wave errata, entry fixes and advice). Add one row per commit with its subject. All three are ancestors of `origin/master` (`hash-ancestry.txt`).
- Line 49 says "all pushed through `jj-lane.sh`." For the nine commits from efe58e96 to 46be41c, the author is `kama-shokunin <kama@shokunin.local>`, which is the helper's identity, and all are on `origin/master`. The helper's `landed <hash>` lines are not in the repo. Either cite them, or write "pushed; ancestor of origin/master (verified)."

### M5. "S060 used-by gains …" gives no old and new text (line 79)

- Contract §4 requires rows touched as old→new.
- Verified in `corpus/SOURCES.md` at fa3b62ae, row S060, used-by column:
  - old: `corpus/knowledge/gguf-declared-identity.md, corpus/lessons/round-20.md`
  - new: `corpus/knowledge/gguf-declared-identity.md, corpus/lessons/round-20.md, corpus/knowledge/context-capacity.md`
- It is the only existing row that changed, and no status or recheck cell changed.
- Fix: write the old and new values as above.

### M6. Row counts are not in the cited census file (lines 76 and 78)

- `before/census-validate.out` shows W04 warnings and `exit=0`, but no row count.
- The counts come from census mode (`sources-census.txt`):
  - efe58e96: rows 105; tier A 100, B 2, C 3; mined 86, queued 8, rejected 11.
  - fa3b62ae: rows 113; tier A 108, B 2, C 3; mined 94, queued 8, rejected 11.
- Fix: paste the census-mode `file rows`, `tier` and `status` lines for the start and end. Keep `validate` for the exit code.

### M7. Round-24 routed defects and inherited state are not addressed (contract §5 item 5; addendum §5 and "Earlier attempts", lines 162–165)

- The round-24 spot-check (`corpus/lessons/round-24-verifier-spotcheck.md`) lists five routed defects. The draft covers only defect 2 and the locator erratum. Give one line for each:
  - 1: no round-24 file edited;
  - 2: repaired by C1;
  - 3: locator erratum, in the lesson;
  - 4: native-role and scope qualifications kept;
  - 5: H2 stays open (see M9).
- The watchdog shows attempt 1 ended as `lane-dead-no-report kama round=25` (`.ufo/watchdog.log`, 2026-10-22T05:31:20-03:00). The addendum requires naming which inherited outputs were reused after re-checking and which were discarded. The draft only says the attempt-1 wave was committed as a record.

### M8. The misroot sweep is required and not recorded (addendum §6 item 3, lines 257–262)

- The draft has no sweep line. My read-only sweep (`fleet-status-sweep.txt`: `git --no-optional-locks … status --porcelain`, rc 0, 17 entries) shows:
  - driver state (`.ufo/state/*.report-baseline`, `.ufo/watchdog.log`);
  - an operator goal file;
  - a hyaku bytecode file;
  - a staged root file named `write`, whose content is `agent://U100N079H334f935b` and which names no lane or round.
- None is clearly from kama round 25. I did not touch any of them.
- Fix: add "Misroot sweep at <time>: `git -C /home/vgpnk/Projects/shokunin status --porcelain` rc <n>, <count> entries. Kama round-25 misroots: <none, or each listed and copied with cmp>. Unattributed root file `write` (names no lane or round) left in place." Re-run at landing.

### M9. The open L0 question is not noted (contract §5, lines 138–140)

- `/home/vgpnk/Projects/shokunin/.ufo/l0-questions.md` has "kama | round-24 | R23-H2 remains open: may the report-landing audit require Git >=2.45 …". `preregistration.json` lists it under `open_l0`.
- Fix: "Open L0 question: R23-H2 (Git 2.45 or later as a prerequisite) remains open. Routed around this round; no answer recorded."

### M10. The tool-install line is missing (addendum §6 item 6, lines 325–326)

- `LOG.md` line 1678 at a46a6181: "Tool installs: none by the author; no seat reported an install."
- Fix: add "Tool installs: none (LOG.md §Round 25)."

### M11. The dispatch time has no evidence (line 4)

- "dispatched 2026-10-22T09:19:49Z" has no pointer.
- The only record I found is `.ufo/watchdog.log`: "2026-10-22T06:19:51-03:00 launch kama round=25 … attempt=2". That is 09:19:51Z.
- Fix: cite that line and use 09:19:51Z, or cite whichever record holds 09:19:49Z.

### M12. The planner bullet has no evidence pointer and misdescribes the second walk (lines 43–45)

- The bullet cites "pilot.md" and "amendment 2 honesty note 3" without paths.
- The walk in `preregistration-amendment-2.json` honesty_notes[2] is titled "L1 planning walk at 09:26Z" (K6 arguments, port 47311, killed). The draft calls it "an L1 verbosity walk."
- Fix: "Planner seat: the L1 holds the canonical planner seat (2026-10-19 ruling). Its planning walks: `.ufo/waves/round-25/pilot.md` (about 08:22 UTC, before the preregistration) and `.ufo/waves/round-25/preregistration-amendment-2.json` honesty_notes[2] (09:26Z, port 47311, killed). No planner seat was dispatched."

### M13. The "mined mistake" wording claims more than was shown (lines 82–83)

- The lesson (`corpus/lessons/round-25.md` line 48) shows the instrument can fail: it prints `stale 2` at efe58e96 and `stale 0` at 1fc41e34. It does not show that criterion KQ36 would have failed.
- The round-24 base shows that: the same command prints `registered 27 stale 2 [...]` at 147f5bdd and at 92063cf, both exit 0 (`counts.txt`).
- Fix: "Fix KQ36 (re-run registered counts at the landed tip) shown able to fail: at the round-24 base 147f5bdd the registered command prints `registered 27 stale 2`, exit 0."

## Minor

### N1. Trend verdicts are placeholders, and the committed SCORECARD uses a value that is not allowed (lines 87–89)

- Allowed values (contract §4): improved, harmed, unchanged, unprovable-but-better.
- `SCORECARD.md` lines 1306–1308 at a46a6181 say "quality unchanged-to-improved." That is not an allowed value.
- Choose one value per dimension and cite evidence. The M17 change (B2) is evidence against a clean quality verdict.

### N2. The SHONEN pointers do not match the box text (lines 93–96; `SHONEN.md` lines 5–12)

- Line 94: the box says "executed and logged in LOG.md." Add the LOG.md §Round 25 C2 bullet.
- Line 96: the box says "PROVINCE.md still accurate." The draft cites the knowledge entry, which does not show that. Use `PROVINCE.md` §Write boundary (line 45) and state it is unchanged this round (`git diff --stat efe58e96 fa3b62ae -- PROVINCE.md` is empty).
- Lines 93 and 95: keep each box's own pointers (`SKILL.md` §Decision table, line 125; §Checklist, line 193; `corpus/knowledge/snapshot-history.md` §Run it), then add the round-25 pointers after them.
- Keep every line at [~]. None has a named non-author verifier.

### N3. The C1 counting command is referenced, not pasted (lines 65–66)

- Contract §4 says "each with the counting command." Paste `preregistration.json` line 16 verbatim.

### N4. The C1 full run has no commit recorded (line 31)

- `final/c1/` holds `c1-tip-mutants.exit` (`exit=0`), the JSON and a `.time` file (real 16m25.987s), but no commit.
- The instrument at a46a6181 differs from 1fc41e34 only by the docstring (`git diff --stat 1fc41e34 a46a6181 -- tests/report-audit/isolation-mutants.py`: seven insertions). Either record the commit in that folder, or re-run at the landed tip.

### N5. The C1 "before" has no full run (lines 65–68)

- The full instrument stops on reaching M11 at efe58e96 and 147f5bdd (`errata-attempt-2.json` line 12). So "26 of 28 killed" is a first full observation, not a before-and-after change. Say so.
- Also say that M20 survived at round 23 too (`SCORECARD.md:1166`).

### N6. Wrong commit for the errata (lines 25–26)

- `errata-attempt-2.json` was committed at fa3b62ae, not 5388b7cf (verified with `git show --name-only`).
- Fix: "(5388b7cf; errata in fa3b62ae)."

### N7. The final report location (contract §4)

- The final report goes to `/home/vgpnk/Projects/shokunin/.ufo/reports/round-25/kama.md`. That file does not exist yet. The draft is the lane copy only.

## Checked and held

- Hashes: all 11 round-25 commits resolve as commits (`cat-file -t` rc 0). The chain efe58e96 → 5388b7cf → 1fc41e34 → 5ea4fc44 → c808ba07 → 46fb04bd → 5c95c8f1 → fa3b62ae → 46be41c → c0a9b02 → a46a6181 is linear (`merge-base --is-ancestor` rc 0 for each step). `origin/master` = `master` = a46a6181 (`hash-ancestry.txt`).
- C1 counting command (`preregistration.json` C1.command), rc 0 throughout:
  - efe58e96 and 5388b7cf: `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`;
  - 1fc41e34, fa3b62ae, 46be41c and a46a6181: `registered 28 stale 0 []`.
- C1 full run (`final/c1`): `exit=0`, pristine passed, 28 mutants, 26 killed, survivors M17 and M20. The four retired IDs (M14, M22, M27, M29) predate round 25; the RETIRED list is unchanged from 147f5bdd through a46a6181.
- C2 counting command: `registered 14 observed 14 bound True missing []`, rc 0, at fa3b62ae and a46a6181. The counter bytes are unchanged since 46fb04bd. Receipt 5c95c8f1 runs 09:42:42.438Z to 09:42:50.502Z with exit_code 0 and all ports closed.
- The knowledge entry header. At 46be41c it cited the first receipt's window (09:36:51–09:36:59Z). At a46a6181 line 2 cites the final window (09:42:42Z–09:42:50Z). That is resolved at the tip. Recheck at landing.
- SOURCES: rows 105 → 113; tier A +8 (S106–S113, all tier A, opened 2026-10-22, recheck on-release); mined 86 → 94; `validate` rc 0 at efe58e96 and fa3b62ae.
- Required sections are present in the required order: Work performed (line 8), Landed changes (47), Before → after (63), Sources & frontier (73), Trend verdicts (85), SHONEN (91). The Stale-lane line (98) is present.
- Pointers resolved at a46a6181:
  - SKILL.md lines 188–190 (premise text);
  - SKILL.md §Round-25 decision rows (line 677);
  - corpus/README.md "## Frontier advanced — round 25 (K05 declared versus served context)";
  - corpus/knowledge/context-capacity.md §Related lane evidence (line 233);
  - corpus/lessons/round-25.md §Mistakes row 1 (line 48);
  - tests/report-audit/isolation-mutants.py; tools/kama-context-capacity.py;
  - final/context-capacity-receipt.json; before/census-validate.out (exit=0).
- Registry count repaired: SKILL.md line 889 says "28 retained literals since round 25"; line 1007 keeps the round-24 count of 27 as history. The stale count the critic cited (Harm 2) is fixed.
- The planner ruling is followed: neither spec file has a planner role.
- PM08 wording: SKILL.md line 1050, "PM08 stays filed/manual/unexecuted/uncredited."
- Attempt 1 stood down at 08:30Z for the job limit, as the draft says (`.ufo/watchdog.log`).

## Residual risk and verification gaps

- The lane is still moving. Wave-2 advice and outputs are untracked. A committed copy of a receipt under `out/RerunC2Counter/` is deleted in the working tree. Re-check every pointer at the landing commit, not at a46a6181.
- I did not re-run the 16-minute C1 instrument. I used the saved JSON and exit file.
- I did not run the capacity tool, because it starts llama-server and this seat must not. C2 was checked on the committed receipt through the counter only.
- I did not reopen the S106–S113 sources. The wave-2 reopen seats cover them.
- I did not verify the wave-1 count of distinct attack items (32 needed).
- Commit identity was checked on the nine commits from efe58e96 to 46be41c, not on c0a9b02 or a46a6181.
- The fleet-root sweep is a snapshot. Driver-owned files change between checks.

## Files written

- `.ufo/waves/round-25/a2-falsify/out/ReviewerReportDraft/numbered-draft.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReviewerReportDraft/hash-ancestry.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReviewerReportDraft/counts.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReviewerReportDraft/sources-census.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReviewerReportDraft/wave-shape.txt`
- `.ufo/waves/round-25/a2-falsify/out/ReviewerReportDraft/fleet-status-sweep.txt`
- `.ufo/waves/round-25/a2-falsify/advice/ReviewerReportDraft.md` (this report)
- Scratch outside the lane: `/fast/scratch/hyaku/kama-r25a2w2/ReviewerReportDraft/` (own clone, extracted trees, receipt copies `receipt-5ea4fc44.json` and `receipt-5c95c8f1.json`).

Tools installed: none. I used git, the Python standard library and bash only.

Report: .ufo/waves/round-25/a2-falsify/advice/ReviewerReportDraft.md
