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

## Actual detector output

All three runs used the same unchanged lane counter and a 300-second timeout. Each completed with exit 0; no detector repair, policy revision, server launch or second mutant was attempted.

Pristine, `ctl` at `827d136546b85059a984b34970f5b493d9a71290`:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
exit=0
```

Mutated, `ctl` at `af96283389ded62899b386fdc988bd3ddcbca9e2`:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 9 false_corrections 7 unresolved 9 met False tip af96283389de
exit=0
```

Restored, `restored` at `6df2824e7e43a74809aed51570171ed308818367`:

```text
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 6df2824e7e43
exit=0
```

`met` is **false** for the assigned control. The counter refuses these fixed text guesses: 9 valid rows, 7 false corrections and 2 base mismatches left without valid rows produce unresolved 9. The control skips the claimed revision-based observation. This is not a killed-mutant claim: conventional mutation verdict **inconclusive**, because the pristine target already fails (`met False`). No source-only success or coverage claim is inferred from this one policy, and the disclosed extra code visibility remains a procedural limit.

## Restoration and prediction-lock evidence

The exact appended 21 lines were removed, then committed on a separate `restored` branch so `ctl` retains the scored policy. The working tree is left at the restored commit. SCORECARD SHA-256 goes:

```text
before:   7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db
mutated:  f3f5a351f4248e061769668d62c1773bacc18a5b3b3cb03ab1f1c9f2af9df17b
restored: 7af59cc0226f05b534c2f628345a53b8d9866bef2245c0092bb3758b4752d1db
```

SHONEN SHA-256 stayed `1ff9e2f363baedc09ae913c2036d79b53dcd270c851419ef33b8dc337a6d3fb5`. The complete frozen and restored Git trees both identify as `efe74520595f60b69e33b79b378348fe69a31043`; the mutant tree is `410fb6f8d771558caa812dde93711e15cfb9e065`. The counter SHA-256 before and after every run is the frozen `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`.

The runner copied this report's pre-result bytes to `REPORT-before-scoring.md` before its first invocation. All three status records have the same pre-result report hash `80f9e0d9be8494b6292e494215a05b0de7c3d70444e9846f3044d1bfd2b1d86a`, prediction hash `f1a477ff43b8feb25935a0aab9d195e3030927d4824dc2b6d1601519bdaee22e` and source-policy hash `9e51c98a4b5f917cdfdb53e0bf498a7f584b04f16f1adf95e67dd9007c351631`. Thus the baseline output was not used to adjust predictions.

## Evidence files

All paths below are within `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlSourceBounds/`:

- `REPORT.md`, `REPORT-before-scoring.md`: policy, exposure disclosure, prediction lock and results.
- `counter.out`, `receipt.json`: canonical assigned-policy output and receipt.
- `pristine-counter.out`, `pristine-receipt.json`, `restored-counter.out`, `restored-receipt.json`: same detector on control bytes.
- `pristine-status.json`, `mutated-status.json`, `restored-status.json`, `restoration.json`: commands, exit statuses and byte/tree identities.
- `change.diff` (1748 bytes), `commit.json`: committed policy change, frozen and mutant commit identifiers.
- `source-policy.py`, `source-statements.json`, `source-hashes.json`, `predictions.json`, `policy-hashes.json`, `correction-rows.md`: reproducible source-only prediction and exact proposed rows.
- `score-probe.py`: bounded invocation/evidence capture, not a modified detector.
