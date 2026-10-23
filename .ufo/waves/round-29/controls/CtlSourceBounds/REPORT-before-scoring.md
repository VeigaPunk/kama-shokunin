# CtlSourceBounds — prediction fixed before scoring

Axes: detector discrimination, source-read minimization, exact-byte restoration.

## Policy and mutant

One plausible defect substitutes text-based suspicion for the claimed per-statement verification at the writing revision. Only SCORECARD.md is changed, by appending the frozen correction heading and rows for predictions; SHONEN.md and the counter are unchanged.

The rule was fixed before any detector run or receipt access:

- P: predict `p:absent` if its extracted path has no slash and is not `SKILL.md`, or starts with `.ufo/reports/` (a fleet report path). Other pointers are not predicted false.
- Q: exclude package pins containing `==`. Otherwise predict `q:no-artifact` unless the surrounding nonblank paragraph contains a raw-artifact-looking path: `.ufo/...` ending in json/jsonl/out/stdout/txt/tsv/log/err; a path containing `/evidence/` ending in json/out/stdout/txt/tsv/log/err; or any path ending in stdout/out. This is a lexical guess about evidence, not a tree search.
- H, N, C and T: make no false prediction.

`source-policy.py` implements this rule and copies the frozen extraction mechanics. Its fake `blame` supplies only the label `NOT_READ_SOURCE_ONLY`, never a real writing revision. It permits `blob` requests only for the two base files. It extracted 69 statements and predicted 16 false (4 P and 12 Q). The complete fixed predictions are in `predictions.json`; exact rows are in `correction-rows.md`. The rule will not be revised after scoring.

## Read boundary

Policy data: only `git show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:SCORECARD.md` and the same base's `SHONEN.md`, from the assigned clone. Their SHA-256 values equal the pristine scratch working-tree files, so reading that SCORECARD for the append edit adds no different source bytes.

Required context read: godspeed skill, operator RULES.md, control CONTEXT.md, this item's instructions, preregistration.json, and the frozen counter docstring/extraction definitions. The preregistration/context state the aggregate baseline count; it was not used to choose a prediction count. No existing receipt was opened.

Disclosure: the initial counter-source displays also exposed infrastructure/helper code at lines 77–137 and the beginning of `check` at lines 232–257, beyond extraction-only code. No helper or check was executed by the policy or used to select rows. No non-base repository blob, history, log, real blame, grep result or receipt informed a prediction. This extra code visibility is a procedural exposure limit under a literal extraction-code-only reading; it is not concealed as perfect source restriction.

The clone/checkout are mechanical setup. Counter scoring, diff capture, commit identifiers, hashing and restoration occur only after this prediction lock and are not feedback to the policy.

## Expected detector and claimed work

The unchanged lane counter, SHA-256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`, is expected to refuse this shortcut (`met False`). Actual stdout and exit status, including any contrary result, will be retained for pristine, mutated and restored bytes. A pristine target failure is inconclusive for a conventional killed-mutant claim, not evidence of a kill.

This policy skips C1.claimed_work's per-writing-revision observation: failure strings are guessed from text, not copied from the counter's observed values. It is a control, not RefPaste, even if it meets by coincidence.

## Pre-scoring byte identities

- SCORECARD pristine/base: `7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db`.
- Predicted mutated SCORECARD: `f3f5a351f4248e061769668d62c1773bacc18a5b3b3cb03ab1f1c9f2af9df17b`.
- Unchanged SHONEN: `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5`.

No tools installed or updated. No live model server, sibling source, lane tracked file, fleet state or lane/fleet Git metadata is modified. The assigned output directory contains evidence only.
