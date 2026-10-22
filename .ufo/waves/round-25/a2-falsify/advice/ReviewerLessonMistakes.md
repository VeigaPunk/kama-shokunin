# ReviewerLessonMistakes — §Mistakes rows of corpus/lessons/round-25.md (wave 2, falsify)

**Verdict: holds — every row's core factual claim verified by direct re-run or pointer
resolution; 4 minor defects found (one overstated fix surface, two unresolvable/ambiguous
pointers, one muddy captured-by), no evidence defect.** Bytes note: the lesson file moved
during the wave — pinned tip `fa3b62ae` (blob `9d7ec295…`) ≠ master `46be41cf` (harness-only
child) ≠ lane working copy (`c26728b0…`, uncommitted L1 edits: misroot row and axis-misfiled
row are new, chronology/false-timestamp rows rewritten, §C1 result rewritten). My verdicts
cover the working-copy text (the item's live state); where the fa3b62ae bytes differed, I say
so. Per-row evidence: `.ufo/waves/round-25/a2-falsify/out/ReviewerLessonMistakes/verification-log.md`.

## Per-row verdicts

**Row 1 — stale-anchor: HOLDS.** I re-ran the registered C1 command in my own clone:
`registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` (exit 0) at 147f5bdd,
efe58e96 **and 92063cf**; `registered 28 stale 0 []` (exit 0) at 1fc41e34 and fa3b62ae. That
also independently confirms "the M11 literal stopped matching at round-24 commit 92063cf"
(stale 0 at ed1cc3a, stale 2 first appears at 92063cf) and the both-exit-0 red/green claim.
Evidence pointers resolve: `round-24-verifier-spotcheck.md:80-82` and `:151-152` contain the
quoted finding and routed defect 2; `RevengerM11Element.md`, `ScribeMistake.md`,
`ExecC1BaseRun.md` all exist and support their citations. Captured-by "none" is fair for
KQ28–KQ35 (I read them; none requires a re-run) with one caveat below. Two minor defects:
- **(D1, minor) "KQ36 below" does not resolve in this file.** KQ36 lives at
  `corpus/QUALITY.md:203` (landed); round-25.md never mentions where KQ36 is defined, and
  nothing "below" in the lesson defines it. Smallest correction: "KQ36 (`corpus/QUALITY.md`
  round-25 criterion) below" or cite the path.
- **(D2, minor/caveat) captured-by "none" is an interpretation call.** KQ27's admit text
  ("every quoted count … independently enumerated after the artifact changes") arguably
  covers a registered count gone stale after the auditor changed at 92063cf;
  `ScribeMistake.md` Finding 3 argues the narrow reading (report-cardinality scope). The row
  compresses this to "none" without flagging the contest.

**Row 2 — survival hidden by a same-line re-anchor: HOLDS, one overstated fix surface.**
Evidence verified: `final/c1/c1-tip-mutants.json` reads mutants 28, killed 26, pristine
passed, surviving `['M17-ref-shadow','M20-log-sha-shape']`, exit file `exit=0`, M17 grid_exit
0 with no failed rows, M33 killed by F13-ref-named-abbreviation. Both captured-by seats exist
and genuinely capture the finding (`CriticC1NoHarm.md` Harm 1; `MutationM17M33Kill.md`
per-mutant grid results). The instrument docstring
(`tests/report-audit/isolation-mutants.py:33-39`) does say M17 survives and why. **(D3,
minor) The fix cell's "and SKILL registry row now say M17 survives and why" is not met by the
SKILL bytes.** SKILL.md:882-884 says "M17 follows the current local-store spelling. Survival
alone does not establish defensive-only status." and SKILL.md:889 says "M33 is the second
call site of the M17 refusal" — neither states that M17 survives the grid nor why (no caller
reaches the lookup() check since 92063cf; F13's kill moved to M33). A grep of SKILL.md for
`surviv` finds no M17-survival sentence. Smallest correction: either add one sentence to the
SKILL registry row ("M17 is expected to survive: since 92063cf no caller reaches the
lookup() check; F13 kills M33") or narrow the fix cell to the instrument docstring. The
"causal run on ed1cc3a" was not re-run by me (~2 min grid run); it is corroborated by
committed outputs (`RevengerM17Sites` §N2), ReviewerC1Patch's round-23 targeted run, and the
blame/pickaxe history.

**Row 3 — counter accepted a wrong value: HOLDS.** All four specifics resolve in the two
cited files: `MutationC2Counter.md` (pool line `= 12048` accepted for pool 2048;
`nonsense2048`; `build 117550` prefix collision), `CriticC2SizingA2.md` (A03: X1 satisfied by
the fit-probe pool line; A09/A09b: L1 concurrency never checked). Captured-by "the two
wave-1 attack seats" is accurate. Fix demonstrated, and I re-ran it: the amendment-4 counter
prints `registered 14 observed 14 bound True missing []` (exit 0) on the committed receipt,
and on the first committed receipt (5ea4fc4) prints `registered 14 observed 11 bound True
missing ['L1','L2','L3']` (exit 0) — exactly the claimed 11-of-14-because-no-request-times.
Amendment 3's `check_after_change` is present in its bytes;
`a2-build/out/CriticC2SizingA2/counter-attacks-proposed.out` exists.

**Row 4 — misroot: HOLDS (row is NEW in the working copy; absent at fa3b62ae).** Every
pointer resolves: `ReviewerC1Patch.md:94` (disclosure bullet), `out/ReviewerC1Patch/
evidence.md:73` (names `literal-id-checks.py`, `m17-reachability-probe.py`, the `cmp` copy,
the three directories removed at 06:45), `CriticC1Calibration.md:79` (`/tmp/ccal-aud-tip.py`),
`ScribeQualityCriterion.md:50-51` (`/tmp/mutants-red.json`, `/tmp/mutants-green.json`),
`a2-falsify/advice/ScoutMisroot.md` (D4 three unattributed /tmp copies; D5 fleet root clean).
I confirmed independently that neither mis-rooted file remains at the fleet root. Two notes:
- **(D4, minor) the captured-by parenthetical "(it caught the report path, not the artifact
  path)" is muddy.** The mis-rooted files were artifacts, and the disclosure was
  self-initiated by the seat; the wave-1 contract named the artifact out-directory by absolute
  path in the very same sentence as the report-trailer rule (verified in
  `a2-build/dispatch.json`), so no context rule "caught" anything here. Smallest correction:
  credit the seat's own disclosure, e.g. "self-disclosed in its report; the context's only
  relative-path rule governed the report trailer, and nothing caught a relative artifact
  write."
- The fix cell's "the L1 misroot sweep before the report checks the fleet root" is
  prospective and not yet verifiable at review time. Input for that sweep: ScoutMisroot D2
  found two pre-existing fleet-root strays (`write`, `scripts/hyaku/__pycache__/
  append-closure.cpython-314.pyc`) **with intent-to-add index entries** — the sweep must clear
  index entries (`git restore --staged`), not only files. "The falsify-wave context repeats
  the absolute-path rule for artifacts" is verified verbatim in `a2-falsify/dispatch.json`.

**Row 5 — chronology: HOLDS.** Verified from commit times: first receipt 5ea4fc4 at
09:37:28Z, amendment 3 c808ba0 at 09:38:45Z (after it, by 77 s ≈ "a minute later"); amendment
4 46fb04b at 09:42:31Z, receipt re-run 5c95c8f at 09:42:57Z (before it); 5ea4fc4 stays on
master's linear history. The working-copy captured-by is accurate: amendment 3's
`order_disclosure` is in its committed bytes; CriticC2SizingA2's verdict recommended
"committed before any receipt"; ReviewerAmendment2 (I2) independently confirms the ordering.
The failure demonstration is the committed ordering itself; the fix is the verified
46fb04b-before-5c95c8f ordering. At fa3b62ae this row read "the author, on reading
CriticC2SizingA2" — the working-copy wording is more precise; both are supportable.

**Row 6 — false timestamp repeated: HOLDS as amended.** At fa3b62ae the row covered only
amendment 2 (09:30Z > commit 09:28:44Z) and missed that amendment 3 repeated the class
(09:40Z > commit 09:38:45Z). The working copy adds it, cites `CriticC2SizingA2` (§5) **and**
`ReviewerAmendment2` (M1 amendment-3 stamp, M2 amendment-2 stamp), and names both errata
homes (amendment 4 `errata_to_amendment_2`; `errata-attempt-2.json`). All verified: both
stamp-vs-commit pairs from `git log`; both errata present in the named files; amendment 1's
"false timestamp" correction (the "same class" reference) present; amendment 4's `written_utc`
names only the observed `date -u` output and defers to the commit time. The fa3b62ae version
of this row was incomplete; the working copy fixes it — flagging so the intermediate state is
on record.

**Row 7 — axis misfiled (new, working copy only): SUPPORT VERIFIED; fix admittedly not
demonstrable this round.** I ran the counter myself at the three named revisions:
`registered 31 stale 0 []` at e876b95, `registered 27 stale 0 []` at ed1cc3a, stale 2 first
at 92063cf — the row's factual core ("the SCORECARD and SKILL statements were true when
written … stale from 92063cf") is confirmed independently of CriticC1AxisFit. Both cited
advice files exist and argue the point. **(D5, minor) the prompt pointer resolves only from
the fleet root**: `.ufo/prompts/kama-round-25.md:347-348` does not exist under the lane root
(verified: not found); the file is `/home/vgpnk/Projects/shokunin/.ufo/prompts/
kama-round-25.md`, and lines 347-348 do contain "A calibration claim must count mismatches
between the lane's self-assessment (SCORECARD/SHONEN) and observed repo state." Given this
round's own misroot row, add a fleet-root qualifier. The row honestly declares "Not yet shown
able to fail: no later round has applied it" — so, unlike rows 1-3, its fix has no red/green
demonstration; that is a stated limitation, not a hidden one.

## Residual risk

- The M17-reachability "why" rests on git 2.56.0 behaviour plus caller reading (three seats);
  older-git behaviour remains [INFERENCE] territory — unchanged from the seats' own scoping.
- The L1 misroot sweep has not run yet (prospective); fleet-root index entries (ScoutMisroot
  D2) are the part most likely to be missed.
- Row 1's "captured-by none" vs KQ27 remains a judgment call the closure may read more
  broadly than ScribeMistake did.
- The lesson bytes are still moving (uncommitted edits at review time); rows added or edited
  after my read are not covered by this report.

## Verification gaps (not run, with corroboration)

- Full instrument `--json` run (~16 min): not re-run; corroborated by the committed
  `final/c1/c1-tip-mutants.json` (exit 0) plus ReviewerC1Patch's independent full run (exit 0,
  wall 983.9 s, same survivors) and ExecC1TipReplicate.md.
- Row 2's causal ed1cc3a grid run: not re-run; corroborated by committed outputs and history.
- Amendment-3's synthetic negatives: not regenerated; the stricter counter's behaviour was
  verified directly instead (see verification log A2).

No tool installed or upgraded. No llama-server child started, no port touched. No jj
command; lane git read-only; git checkouts confined to my clone
`/fast/scratch/hyaku/kama-r25a2w2/ReviewerLessonMistakes/clone`.

Report: .ufo/waves/round-25/a2-falsify/advice/ReviewerLessonMistakes.md
