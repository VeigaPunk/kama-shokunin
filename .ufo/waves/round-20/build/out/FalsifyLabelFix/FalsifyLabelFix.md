VERDICT: confirm - three round-19 labels say "falsify-wave" (lesson-19:51, lesson-19:79, SCORECARD:844) but name build-wave seats; the falsify wave never spawned.

# FalsifyLabelFix — round-19 wave-label audit

Audited lane tip `37bd4c5bd456a2f8a54d3312c28495c321715856` via `git show` / `git grep` (read-only; lane untouched).

## Facts (executed)
- Falsify wave never spawned: `.ufo/waves/round-19/falsify/refused-attempt-1.json` = `"seats": 66, "refused": 66, "spawned": 0` (job cap 100 reached).
- Committed `falsify/` has no reports and no `validation.json`; `advice/` holds only `swarm-registry.json`.
- `build/dispatch.json` (sha256 `de806ed8…cddcead`, same at worktree and lane tip): 64 spawn members; line 421 "BUILD wave of 64 seats".
- Target seats are build spawn members and absent from `falsify/dispatch.json`: CritC1Inflation (critic), CritAxisHarm (critic), TreeCap (scout), TameshiConventions (connector), C2BaselineInvalid (reviewer).
- Other seats cited by the mislabeled sections, also build-only: DraftScorecard (scribe), CitationNegatives (scout), MutTokRegex (mutation-tester), MutationChecker and GridSelftest (executor), RevisionDriftScan (scout).

## Every mislabeled line (`git grep -n -i falsify` over SCORECARD.md, LOG.md, corpus/lessons/round-19.md)
Wrong label:
- `corpus/lessons/round-19.md:51` "Falsify-wave and residual findings". Bullets 53 (TreeCap), 58 (CritAxisHarm), 62 (DraftScorecard/CitationNegatives), 65 (MutTokRegex/MutationChecker), 68 (GridSelftest) are build seats.
- `corpus/lessons/round-19.md:79` "C1 scope correction (falsify-wave refutation accepted)". The refutation at line 81 is by build critic CritC1Inflation.
- `SCORECARD.md:844` "Round-19 C1 erratum (falsify-wave refutation accepted)". Same refutation, same error.

Misattributed without the word "falsify":
- `LOG.md:1158-1161` "Falsify wave validated at 66 seats; dispatch refused ... Wave-1 findings integrated". The refusal clause is correct. "validated" has no committed artifact, and `falsify/spec.json:2` says "FALSIFY wave of 64 seats" while it holds 66 items. "Wave-1 findings" can only mean build-wave findings [INFERENCE: intent; artifacts show no falsify output].

Correct, no change: `LOG.md:1170-1171` "a fresh critic refuted" (build critic). Already flagged by the verifier at `corpus/lessons/round-19-verifier-spotcheck.md:188-189`. Rounds 15-18 hits (LOG 75, 914-982, 1030-1112; SCORECARD 640, 710-759) are correct as written. Note round-18 also reports 66 (LOG.md:1112), a coincidence with round-19's refused 66.

## Draft appended corrections (NOT applied; append-only)
A. `corpus/lessons/round-19.md`, append at end:
```
## Correction (round 20, appended): wave label
Lines 51 and 79 say "falsify-wave". No falsify wave ran in round 19:
`falsify/refused-attempt-1.json` records seats 66, refused 66, spawned 0. The
findings in the section above come from the BUILD wave (`build/dispatch.json`,
64 spawn members): TreeCap, RevisionDriftScan, CitationNegatives (scout);
CritAxisHarm, CritC1Inflation (critic); DraftScorecard (scribe); MutTokRegex
(mutation-tester); MutationChecker, GridSelftest (executor); TameshiConventions
(connector); C2BaselineInvalid (reviewer). Read "falsify-wave" as "build-wave".
The original headings are retained as written.
```
B. `SCORECARD.md`, append at end:
```
### Round-19 label correction (appended, round 20)
The "falsify-wave refutation accepted" label in the Round-19 C1 erratum is wrong.
The refutation came from build-wave critic CritC1Inflation
(`.ufo/waves/round-19/build/dispatch.json`). The falsify wave was refused and
spawned nothing (`.ufo/waves/round-19/falsify/refused-attempt-1.json`). C1 score 7 -> 7 is unaffected.
```
C. `LOG.md`, append under "round 19 erratum":
```
- Correction (round 20, appended): the round-19 falsify wave never spawned
  (refused 66/66). "Wave-1 findings integrated" means build-wave findings only.
  No committed falsify/validation.json exists, so "validated at 66 seats" is unevidenced.
  falsify/spec.json context says 64 seats; it holds 66 items.
```

## Commands run (exits observed; all read-only)
1. `cat build/dispatch.json`; `ls -la falsify/`; `cat falsify/refused-attempt-1.json` — 0
2. `git grep -n -i falsify <tip> -- SCORECARD.md LOG.md corpus/lessons/round-19.md` — 0; lane-wide `git grep -n -i falsify <tip> -- .` — 0
3. `git show <tip>:{corpus/lessons/round-19.md,SCORECARD.md,LOG.md} | cat -n` (ranges above) — 0
4. python3 role/membership extraction on both dispatch files — 0 (build 64 spawn; falsify 66 spawn)
5. `grep -c` on the five target names: build 2 each, falsify 0 each (exit 1 = zero matches)
6. `sha256sum` worktree vs `git show | sha256sum` on build dispatch — both `de806ed8…`, 0
7. `git ls-tree -r --name-only <tip> -- .ufo/waves/round-19/falsify` + validation grep — 0; grep exit 1 (none)
8. `grep -n -o` "BUILD wave of 64 seats" (build, line 421) and "FALSIFY wave of 64 seats" (spec, line 2) — 0; spec items = 66 — 0
9. `mkdir -p` advice and out dirs — 0; `git status` on corpus/SCORECARD/LOG — clean, 0

No installs or updates. No scratch created.
