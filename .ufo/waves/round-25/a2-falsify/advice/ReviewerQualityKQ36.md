# KQ36 review — ReviewerQualityKQ36 (kama round 25, attempt 2, wave 2 falsify)

Verdict: **defect found** — KQ36's substance verifies end-to-end (every cited
able-to-fail fact reproduced, including at the true landed tip), but the row
as written is violated by the lane's own honest landing practice
(self-referential "landed tip"), and its cited motivating lesson contains one
false attribution (SKILL registry row does not say M17 survives). Wording
corrections below; no production edits made by this seat.

Item: `corpus/QUALITY.md` KQ36 at `fa3b62ae6475d111eb466d79af616aeebb08bbb9`
(row text at QUALITY.md:203; append-only verified: `git diff --numstat
147f5bdd fa3b62ae -- corpus/QUALITY.md` → `6 0`; still unchanged at HEAD
`46be41cf`, empty diff). Full command/exit log:
`.ufo/waves/round-25/a2-falsify/out/ReviewerQualityKQ36/verification.md`.

## Findings by severity

### F1 (medium) — "at the round's landed tip" is self-referential and was not met literally by the round's own landed evidence

- QUALITY.md:203 admits only a re-run "at the round's landed tip" and its
  reject column names "the re-run uses a revision other than the landed tip".
  The round's C1 tip-run evidence is recorded at 1fc41e34, while the round's
  landed tip is fa3b62ae, which adds the evidence itself plus a 7-line
  instrument docstring note (`git diff 1fc41e3 fa3b62ae --
  tests/report-audit/isolation-mutants.py` → 7 insertions, 0 deletions,
  docstring only). A run's own record can only be committed after the run, so
  the literally-latest landing commit always postdates every recorded run —
  the criterion, at its birth commit, outlaws the only achievable practice
  (same bootstrap as KQ28's pre-commit draft audit).
- Measured, the gap is immaterial here: my counter run at fa3b62ae prints
  `registered 28 stale 0 []` (exit 0), and my full-instrument run at
  fa3b62ae is byte-identical to the committed
  `.ufo/waves/round-25/final/c1/c1-tip-mutants.json` (both sha256
  `75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1`).
  SCORECARD.md:1256 discloses the measured commit ("instrument unchanged
  since, except its docstring"), so the lane's practice is honest — the row
  is imprecise, not the round fraudulent.
- Suggested wording (append as a qualification paragraph under the Round 25
  section, KQ18-clarification style): "「the round's landed tip」 means a
  commit the report names, whose bytes of both the measured source and the
  instrument are identical to the round's final landing commit; any later
  in-round change to either file is disclosed with its effect on the pasted
  output." Reject column correspondingly: "…uses a revision whose measured-
  source or instrument bytes differ from the landed tip without disclosure."

### F2 (medium) — the cited lesson claims a SKILL.md statement that does not exist

- `lessons/round-25.md` §Mistakes row 2 (fix cell) says: "the instrument
  docstring and SKILL registry row now say M17 survives and why". KQ36 cites
  "§Mistakes rows 1-2" as its motivating lesson.
- The instrument docstring does say it (fa3b62a diff: "F13 now kills M33 and
  M17 survives the grid (full run at 1fc41e34: 28 mutants, 26 killed,
  survivors M17 and M20)"). But SKILL.md has no such statement: a whole-file
  grep finds M17 only at line 883 (superseded round-24 paragraph: "M17
  follows the current local-store spelling") and line 889 (registry row:
  "M11 and M17 re-anchored; M33 is the second call site of the M17 refusal
  … unchanged isolation elements remain explicit") — neither says M17
  survives.
- KQ36's own reject condition ("a re-anchored mutant's change from killed to
  surviving is not reported") does not fire — the survival is reported in the
  docstring, the lesson, SCORECARD:1264-1266 and the JSON. The defect is the
  lesson's false attribution to SKILL.
- Smallest correction (L1): append to the SKILL.md:889 pinned-values cell:
  "; M17 survives the grid since 92063cf (no current row reaches the
  lookup() refusal; F13 now kills M33)" — or, if SKILL.md must not move, an
  append-only erratum in the lesson correcting the attribution.

### F3 (low) — the could-not-evaluate parenthetical is instrument-specific but reads definitional

- "(its unique-match guard fails, exit 2)" accurately describes
  `tests/report-audit/isolation-mutants.py:204-210` (`source.count(old) != 1`
  → `return 2`), but other registered counting commands cannot-evaluate
  differently (e.g. `report-landing-audit.py` exit classes, count-c2.py's
  unreadable-receipt exit 2 being coincidental). A reader could conclude only
  exit-2 unique-guard failures make a value "unverified at that tip".
- Suggested wording: "(for the registered isolation instrument, its
  unique-match guard fails: exit 2; otherwise the command's documented
  could-not-evaluate exit)".

### F4 (low) — trigger misses changes to the registered command's own bytes

- The trigger fires when "a round … changes a source measured by a registered
  counting command". Round 25 changed the registered command's own file twice
  (1fc41e3 re-anchor, fa3b62a docstring), after which SCORECARD.md:1166's
  historical counts measure a superseded instrument — no KQ36 obligation
  covers that case (KQ27's revision-tying partially does). The re-run happened
  anyway as the claim itself, so no landed harm.
- Suggested trigger extension: "…changes a source measured by a registered
  counting command, or the command's own committed bytes…".

### F5 (low) — "names, per mutant" scope ambiguity

- "A re-anchor names, per mutant, whether its last recorded kill still holds"
  reads as all mutants. The landed record names continuity explicitly only
  for the affected trio (M11 kill holds via F20; M17's kill lost and moved to
  M33; M20 unchanged survivor — docstring, lesson, SCORECARD,
  `final/c1/c1-tip-mutants.json`, ExecC1TipReplicate.md), with current
  per-mutant kill rows from which the rest is derivable but not stated
  against the round-23 ledger (SCORECARD.md:1166).
- Suggested wording: "for every mutant whose literal the re-anchor changed".

## Checked and holding (no finding)

- **Precise and enforceable core.** The registered command reproduces
  deterministically from committed bytes: mine at efe58e96 →
  `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`
  exit 0; at 1fc41e34 and at fa3b62ae → `registered 28 stale 0 []` exit 0.
  Stale reporting, "value … unverified at that tip", and every reject clause
  map 1:1 onto the mined defect (round-24 spotcheck :80-82; auditor changed
  by 92063cf with no re-run — `git log 147f5bdd..fa3b62ae --
  tools/report-landing-audit.py` is empty: round 25 itself changed no
  measured source, so the trigger correctly does not fire backwards onto the
  repair round).
- **Able-to-fail evidence resolves and holds.** All four cited facts hold:
  counter before/after values (reproduced); full instrument exit 2 at
  efe58e96 after ten mutants (reproduced: exit 2, 349 s wall vs their 349.20 s,
  stderr byte-equal `could-not-evaluate: M11-listing-surrogates: pattern
  matches 0 times`); exit 0 at the tip commit named per row with survivors
  M17/M20 (reproduced byte-identically, and additionally at the true landed
  tip fa3b62ae); evidence files exist and say what the row quotes
  (ExecC1BaseRun.md; final/c1/ with `.exit` 0, empty `.err`, JSON
  `"killed": 26, "mutants": 28, "pristine": "passed"`, M33 killed by
  F13-ref-named-abbreviation). 1fc41e34 is an ancestor of fa3b62ae
  (`merge-base --is-ancestor`, exit 0).
- **Not universal beyond what it enforces.** Scoped to registered counting
  commands (SCORECARD-cited — SCORECARD.md:1166 registers the isolation
  instrument — or claim-registered, e.g. amendment-4's count-c2.py); bounded
  per round; no host-wide mutation-score policy.
- **Consistent with KQ27-KQ35.** KQ27 (counts tied to measured revision;
  KQ36 adds the tip re-run and staleness semantics), KQ25 (an error stays
  visible, non-passing; no zero-defect laundering), KQ20 (per-mutant kill
  credit), KQ24 (documented non-zero terminal code — SKILL.md:889 verdict map
  "2 fail-fast could-not-evaluate"), KQ28 (complementary draft-time audit vs
  tip-time count; no conflict found), KQ34 (counts name the measured
  revision; the M17/M33 split preserves single-element mutants), KQ35/KQ22/
  KQ29-KQ33 (no interaction). No supersedes clause needed; the row supersedes
  nothing and lands append-only.
- **Same drift shape is clean for C2.** count-c2.py and the receipt bytes are
  identical between 5c95c8f1 and fa3b62ae (empty diff, exit 0).

## Residual risk and verification gaps

- I did not re-run the full instrument at the second base revision 147f5bdd
  (ExecC1BaseRun recorded it twice there with identical results; my efe58e96
  run matches their efe58e96 record exactly).
- "After ten mutants" rests on ExecC1BaseRun's `--only` ordering experiments
  plus matching wall times (349 s), not on my own run-order trace.
- Lane HEAD moved to 46be41cf (3 commits after fa3b62ae) during this wave;
  QUALITY.md is unchanged, but other files' current state is outside this
  item.
- My instrument runs execute the lane grid in temp fixture repositories only;
  no network, no registered consumer probed, no llama-server child started,
  ports untouched.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/out/ReviewerQualityKQ36/verification.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-falsify/advice/ReviewerQualityKQ36.md` (this report)
- Scratch (heavy outputs, clone, extracted revision trees):
  `/fast/scratch/hyaku/kama-r25a2w2/ReviewerQualityKQ36/`

No tools installed (none needed). No lane production files touched; no
commits, no jj commands.
