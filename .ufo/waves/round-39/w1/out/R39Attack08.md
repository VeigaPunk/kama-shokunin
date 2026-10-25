# R39-08 — admit+reject and flips: observable findings

Scope: round-39 C1 calibration (admit/reject Gate entries) and C2 coverage claims, per the
frozen preregistration. Evidence inspected read-only in the lane scratch working copy
`/fast/scratch/hyaku/kama-r39` (canonical round-39 evidence) and the L1 source repo
`/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only).

## Findings (severity order)

### 1. MEDIUM — The tip's reject count is stated inconsistently across the round's own evidence, and the recorded counting command undercounts the Gate
- Lesson Gate `/fast/scratch/hyaku/kama-r39/corpus/lessons/round-39.md` records exactly
  **one Admit** (S472 amendment, line 19) and **two Rejects**, each with a Flip clause:
  - line 21 `Reject staged runtime-health-surface-matrix-amendment-2026-10-24-r16.md … Flip: a later round selects the health-route/process theme …`
  - line 23 `Also reject hosted-health-route-configuration.md … Flip: province boundary changes or an in-scope local platform surface is demonstrated.`
- Root working-tree `SCORECARD.md:72` records tip `admit=1 rejects=1 sourced_rows=1`, and
  its counting command is `grep -c '^Reject staged'` — which matches **only** the line-21
  reject; the line-23 `Also reject` is invisible to it.
- The validation mirror `…/assimilation/validate/SCORECARD.md:2040` records the same
  evidence tip as `admit=1 reject=2 sourced_rows=1`, with the broader `grep -c '^Reject'`
  (matches both rejects). The lesson file is byte-identical in both copies (diff: none).
- `LOG.md:9` says "one … selected-theme rejection; additional out-of-theme hosted-health
  material is also refused"; `…/validate/LOG.md:2198` says "one sourced assimilation
  admission and two rejects".
- Impact: C1's counter requires only "at least one package-theme reject with reason and
  flip" (preregistration.json), so the second reject does **not** falsify C1 — but the
  round's own tip summaries disagree (1 vs 2 rejects) for identical content, and the
  documented measurement command cannot observe the second reject entry it nonetheless
  describes in the lesson.

### 2. LOW — The evidence is uncommitted: the L1 source repo carries no round-39 content at its current head
- The lane scratch `.git` HEAD is exactly base `6a4afdfe48b0b54239d127761d21a5cf21b5b0ea`
  (round-36 commit); every round-39 artifact (lesson, amendment, S472 row, README pointer,
  assimilation receipts) is an uncommitted working-tree change on top of that base.
- `/home/vgpnk/Projects/shokunin/kama-shokunin` HEAD is `873c5d77` (2026-10-24); its tree
  contains **zero** round-39 paths (git ls-tree grep: none), its wave dir ends at
  round-37, and the base commit is not resolvable in that repo (git rev-parse fails).
- So "tip" evidence exists only in working-tree form in the lane scratch copy; the claim
  base-vs-tip contrast cannot currently be reproduced from committed bytes in the L1 repo.

## Findings consistent with the claims (no falsification)

- **Admit is real and grounded:** lesson line 19 admits the amendment, limited to the
  `created` distinction; S472 row exists (`corpus/SOURCES.md`, `^| S472 |` count = 1),
  amendment file exists (`corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md`),
  README round-39 pointer exists (`corpus/README.md` `| 39 |` count = 1).
- **Located quote resolves at line 17:** `openai-list.md` line 17 reads `The Unix timestamp
  (in seconds) when the model was created.` (matches the lesson's quote and the S472 row);
  the file is 1,657 bytes; the HTML fetch is 609,612 bytes — both match the lesson's stated
  sizes. The S472 quote is therefore grounded exactly as claimed.
- **Flip clauses are present and phrased as conditions:** both rejects carry a Flip: clause;
  no flip is used to re-admit anything this round.
- **Base controls are genuinely false:** `c1-noop.out` = `C1_NOOP admit=0 reject=0
  source_rows=203 met=False exit=1`; `c2-noop.out` = `C2_NOOP coverage_block=0 file_exists=0
  cited_new=0 met=False exit=1`; preregistration.json and preregistration-frozen.json are
  byte-identical.
- **Second reject's province citation holds:** PROVINCE.md:40–53 refuse remote web surfaces
  (kake) and README.md:64 names remote endpoint health as kake/kumitate territory, so the
  `hosted-health-route-configuration.md` rejection reason is consistent.

## Residual risk / verification gaps
- I did not execute the claimed counting commands (`grep -c …`, `sources-census.sh`); counts
  above are direct read observations of the files the commands target. The census 203→204
  transition is asserted in `claim-after.out` and the round-39 lesson; I did not re-run the
  census script.
- The source row's "absent at base" leg is verified for the scratch repo's base commit
  (`git show 6a4afdfe:corpus/SOURCES.md` → 0 S472 rows; base tree has no round-39 lesson);
  it is not verifiable in the L1 repo where the base commit is unresolvable.
- Non-author spot-check remains pending (lesson line 33), as the round itself records.

## Verdict
No falsification of C1 or C2 found within the inspected evidence: the admit and both rejects
(with flips) are recorded, S472 is grounded at Markdown line 17, and the base no-op controls
are false. The observable defect is calibration-reporting inconsistency around the second
reject (scorecard/LOG labels 1 vs 2; documented grep pattern undercounts the Gate), plus the
uncommitted status of all round-39 evidence at the base commit in the lane scratch, with no
round-39 content in the read-only L1 repo.
