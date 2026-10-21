# Retrospective roster, not original dispatch

`.ufo/waves/round-18/residual/assignments.json` first landed in round 19,
commit `7229fa95eb122310e9e5334ad799ee3006293ebd`, not with the round-18
residual advice. This sidecar labels it retrospectively in round 20.
Its SHA256 is `8d3a9aee251e700319f93210de7bdd945730fdb3d83fc17e5f109451ef389226`.

The seven listed verdicts match the committed advice: Privacy/Health/ImplPin/
CounterC2 confirm; CounterC1/Claims/Corpus partial (4/3). The asserted roles
(6 reviewer, 1 critic) and single-call shape cannot be independently recovered
from those reports, which do not record roles or original spawn handles.
The JSON is not an original taskCall, spawn result, or completeness proof.

This supersedes the "Dispatch record" wording in the round-19 appended
round-18 lesson erratum and LOG. The original JSON bytes remain unchanged.
Evidence: round-20 `build/advice/AssignmentsLabel.md`; `git log -- <path>`;
`git show 1b85a24:<path>` is absent, `git show 7229fa95:<path>` exists.
