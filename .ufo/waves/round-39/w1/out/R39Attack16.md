# R39Attack16 — mistake evidence and capture criterion

**Seat:** L1Kama39.R39Attack16-2 (mutation-tester variant, read-only evidence inspection)
**Date:** 2026-10-25
**Item:** R39-16 — mistake evidence and capture criterion
**Lane scratch:** /fast/scratch/hyaku/kama-r39 (working-tree evidence; round-39 files untracked in lane git, base 6a4afdfe)
**Source repo:** /home/vgpnk/Projects/shokunin/kama-shokunin (read-only; no round-39 files present at inspection time)
**Axes:** calibration, coverage

## Scope

Inspect the round-39 lesson's `## Mistakes` (the capture criterion and the
evidence pointers it cites) against the committed/working evidence. No source
mutation, no write to lane/source state, no spawn.

## Capture criterion (source of truth)

- Template `{{FLEET_ROOT}}/templates/round-prompt.md` §2b.3: mined mistake must
  carry **class · evidence pointer · captured-by (criterion or rule that should
  have caught it, or `none`) · fix**; "A fix counts only once shown able to fail."
- `kimi-shokunin/skills/shokunin/protocol/CORPUS.md:166-171`: one row per
  mistake; "Prose alone does not record the rejection and its prevention"; "A
  fix is shown able to fail before it counts … commit the observed failure output."

## Findings

### F1 — The `source-schema` row's evidence pointer does not resolve to the described content

The lesson (`validate/corpus/lessons/round-39.md:39`) claims: "first corpus-only
validation mirror `.ufo/waves/round-39/assimilation/validate.out` reported E11
for registry `used-by` paths that live at repository root; the subset mirror
omitted those paths".

Observed working evidence:
- `/fast/scratch/hyaku/kama-r39/.ufo/waves/round-39/assimilation/validate.out`
  (12,453 bytes) contains **zero** E11 lines (`grep -c E11` → 0). It holds 93
  `W04` duplicate-URL warnings plus one terminal `ok` line for
  `validate/corpus/SOURCES.md` — i.e. it is the *successful full-mirror* run,
  not the failed corpus-only run.
- A recursive scan of the whole round-39 wave for the literal `E11` finds no
  output artifact of the described failure; the only hits are historical advice
  documents inside the `validate/` mirror copy (copied source-repo advices), not
  round-39 run outputs.
- The lesson itself (line 27) says the initial incomplete mirror "was discarded,
  not used as evidence." So the red-before E11 output is **not committed and not
  retained** anywhere in the working tree; the pointer names a file whose current
  bytes contradict the row's description.

Impact: the captured-by cell cites the `sources-census.sh` E11 contract (which
exists, including its `E11-dangling-usedby` selftest), but the round did not
"commit the observed failure output" as the protocol requires for a fix that
counts. The mistake narrative is prose-only for its failure witness.

### F2 — The `stale-premise` row is honest but uncaptured by design

Lesson line 40: `captured-by` = "none — package narrative was not cross-checked
against current lane corpus before prose was staged". This matches the protocol's
permitted `none` value and prior-round practice (round-36 mistakes also carry
`none — ...`). The evidence pointer resolves: `corpus/knowledge/consumer-registry.md`
contains the reconciliation-gap section and the two live-measured traps cited.
No failure is claimed for this row beyond disclosure.

### F3 — No fresh fail-capable fix artifact was shipped for either row

Neither row adds a new detector or a committed red-before fixture. F1's row
points to an existing contract (E11) that was not exercised-and-preserved this
round; F2's fix is a process rule with no machine-checkable failure witness.
Under the strict "fix counts only once shown able to fail … commit the observed
failure output" criterion, neither fix is demonstrated from retained bytes.

### F4 — S472/Gate evidence supporting C1 is intact (not falsified)

- Quote resolves at `openai-list.md:17` verbatim; file SHA-256
  `2bbf06bb…793f` matches the lesson; size 1,657 bytes matches (cross-confirmed
  by sibling report R39Attack14).
- C1 no-op control `c1-noop.out`: `admit=0 reject=0 source_rows=203 met=False
  exit=1`; after control `claim-after.out`: `admit=1 rejects=1 sourced_rows=1`,
  registry rows `203 → 204` with the stated counting command.
- Staged/registry collision evidence: `collisions` is empty (0 bytes) and
  `trap-collisions` contains `S471` — consistent with the lesson's guard-trap
  narrative (naive extraction collides on S471; the real intersection is empty).

### F5 — Coverage evidence for C2 is intact (not falsified)

- `claim-after.out`: `round39_pointer=1 entry=1 S472=1`; `c2-noop.out`:
  `coverage_block=0 file_exists=0 cited_new=0 met=False exit=1`.
- README diff adds the round-39 coverage-map row + Frontier disposition; S472
  is present in working `corpus/SOURCES.md` (line 216) and absent at base.

## Verification

- **Killed/survived:** n/a — inspection-only item per assignment ("Inspect
  committed/working evidence only … do not write or spawn"); no mutation probe
  was run.
- **Verdict:** no falsification of C1/C2 controls. One calibration-relevant
  observable gap in the mistake-evidence discipline: the `source-schema` row's
  evidence pointer names `validate.out`, but the retained file is the successful
  run and no E11 failure artifact exists anywhere in the working tree; the
  protocol's "commit the observed failure output" condition is therefore not
  met by retained bytes, and the fix is not demonstrated fail-capable from
  evidence.
- **Caveat:** this is an observation about evidence retention, not a claim that
  the E11 event did not occur; the lesson discloses the discard in prose.
- **Git state:** lane `git status` shows round-39 files untracked
  (`?? .ufo/waves/round-39/`, `?? corpus/knowledge/…r16.md`,
  `?? corpus/lessons/round-39.md`); lane HEAD = base 6a4afdfe. Source repo has
  no round-39 files (read-only). Evidence is working-tree only, consistent with a
  pre-commit round.
