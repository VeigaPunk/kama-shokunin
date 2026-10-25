# R39-28 — wave role mix and report evidence

Agent: L1Kama39.R39Attack28 (simplifier; axes calibration/coverage; milestone r39 claim falsification)

## Findings

- `w1/spec.json` declares `maxLanes: 33`, axes `calibration` and `coverage`, and report directory `.ufo/waves/round-39/w1/out`.
- The checked-in-in-scratch dispatch lists 33 assignments across 10 roles: connector 1, critic 5, executor 6, mutation-tester 4, revenger 1, reviewer 5, scout 5, scribe 4, sentinel 1, simplifier 1. Thus it has role diversity, but is execution/review heavy: executor+reviewer+mutation-tester are 15/33 (45.5%). This count describes dispatch configuration, not proof that every assigned role executed independently.
- At inspection, the scratch report directory contained 9 `R39Attack*.md` reports (including this agent's assignment was not yet present). The dispatch has 33 assignments; therefore reports then present were 9/33, and the report set was incomplete. The scratch Git status showed `.ufo/waves/round-39/w1/` untracked, so these were working evidence, not committed artifacts.
- The dispatch embeds one common framing and same two judged axes for the assignments; role labels alone do not establish independence. Report artifacts are the relevant evidence for actual findings. Existing R39Attack20 report explicitly limits the calibration result to the frozen finite predicate and flags a coverage overclaim risk; this is one report, not a wave-level synthesis.
- Frozen preregistration records C1 `7 -> 7` and C2 `9 -> 9` and specifies predicates (assimilation/preregistration-frozen.json:6-20). The wave role/report census does not itself evaluate either predicate and cannot validate either score. In particular, a partial report set cannot be treated as complete coverage of declared attacks.

## Conclusion

Observable workflow evidence shows a broad role mix but incomplete report capture at inspection time. This weakens the evidentiary claim of completed independent wave coverage, but does not falsify or confirm the frozen numeric scores. No checks or tools were run/installed; observations were read-only except for writing this requested report.