# CtlDoNothing — do-nothing control (round 29, kama lane, C1 calibration)

## Policy

Do nothing. No policy code, no file edits, no commit. The clone is checked out at the
freeze commit and scored in place:

- Clone: `env -u GIT_DIR -u GIT_WORK_TREE -u GIT_INDEX_FILE git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /fast/scratch/hyaku/kama-r29/ctl/CtlDoNothing/repo`
- `git checkout -q -B ctl 827d136546b85059a984b34970f5b493d9a71290` in that clone
- Step 2 skipped per the item file ("Commit nothing new … skip step 2"): no commit was
  created, no tracked file in the clone was modified. `git rev-parse ctl` =
  `827d136546b85059a984b34970f5b493d9a71290`, identical to the freeze commit.
- `git status --porcelain` in the clone: empty (clean tree).

The scored tip is therefore the freeze commit itself — a tip whose SCORECARD.md still
carries all 11 false base statements and no "## Round 29 — self-assessment corrections"
section at all. This is the degenerate control: the counter must refuse it.

## What the policy read

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CONTEXT.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/items/CtlDoNothing.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/preregistration.json` (C1 block:
  base, target, `claimed_work`, `before` receipt line, planned controls list)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` docstring
  (lines 1–63) — the frozen predicate, the six statement classes, the correction-row rule,
  the append-only rule, and the usage line
- `/home/vgpnk/.omp/agent/RULES.md` (operator tooling directive)
- The clone's own committed objects at `ctl` — read only by the counter, which reads
  committed objects only (`git --no-replace-objects`), never the working tree.

## What the policy did NOT read

- No blob of the lane tree was opened by hand: no SCORECARD.md/SHONEN.md content beyond
  the base bytes the counter itself examines, no statement line, no statement id, no
  observed value, no writing revision `W` beyond what the counter prints.
- No correction row was written, read, or inspected; no "## Round 29 — self-assessment
  corrections" heading was created anywhere.
- No file in the lane repo / fleet repo was read as data for a policy; the lane repo was
  only used as a clone source. Nothing in the lane repo was modified, and no git/jj
  write was performed in the lane repo or the fleet repo.
- The counter was NOT modified: `sha256sum` of
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/count-c1.py` =
  `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383` (matches the frozen
  preregistration hash), verified before the run.

## Counter line (verbatim from `counter.out`)

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 0 false_corrections 0 unresolved 11 met False tip 827d136546b8
exit=0
```

Receipt fields (`receipt.json`): `statements 69`, `mismatched_at_base 11`, `append_only true`,
`valid_corrections 0`, `false_corrections 0`, `correction_rows 0`, `unresolved 11`,
`met false`, `tip 827d136546b85059a984b34970f5b493d9a71290`, `base 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`,
`by_class {C:27, H:2, N:2, P:10, Q:25, T:3}`.

## `met` value

`met = false`.

The target is `mismatched_at_base >= 1 and unresolved == 0`. The do-nothing control
satisfies the first half (mismatched_at_base = 11, identical to the frozen base receipt)
and fails the second half (unresolved = 11, since no correction row exists for any of the
11 false statements). The counter therefore **refuses** the do-nothing policy, which is
the correct behaviour for this control: the instrument is not satisfied by inaction.

Note on the tip: the counter's base receipt was taken at tip `2aa46e2481d2`; this control
is scored at the freeze commit `827d136546b8` as instructed by the item ("use `--tip ctl`
at the freeze commit as is"). The freeze commit only adds the round-29 counter /
preregistration / base receipt, so SCORECARD.md is byte-identical to base at the tip
(`append_only true`) and the statement set and mismatch count are unchanged
(69 / 11, same by-class breakdown). The control result is therefore the same as the base
line `statements 69 mismatched_at_base 11 append_only True valid_corrections 0
false_corrections 0 unresolved 11 met False tip 2aa46e2481d2`.

## Does the policy skip the claimed work?

**Yes — entirely.** `preregistration.json` C1.claimed_work requires: "For each base
statement the frozen check finds false at its writing revision, append one row to
SCORECARD.md under the heading '## Round 29 — self-assessment corrections' that names the
statement id and states the check's observed value."

The do-nothing policy performs none of it:
- appended correction rows: 0 (required: 11, one per false base statement);
- rows naming a statement id (`SA29:<sid>`): 0;
- rows stating the observed value the counter prints (`p:absent`, `q:no-artifact`, …): 0;
- the "## Round 29 — self-assessment corrections" heading was never created.

`valid_corrections 0` / `false_corrections 0` / `unresolved 11` is the honest measurement of
that omission. The control does not even attempt to game the instrument: it neither
suppresses the mismatch (`append_only` still true, all 11 false statements still visible)
nor fabricates rows. Its value to the round is as the null arm: it pins the counter's
failure mode when the claimed work is absent — `unresolved` stays at the full base count
of 11 and `met` is false.

## Risk / limits

- The counter reads committed objects only, so the do-nothing policy's "no working-tree
  edits" is equivalent to "no committed edits" here; there is no uncommitted-state
  confound in this arm.
- No installs were performed in this seat (no tool was needed); nothing to record under
  the operator tooling directive.
- `change.diff` is empty (0 bytes) by construction — that is the correct artefact for a
  do-nothing policy, and it is under the 1 MiB bound.
- Not applicable to this control: any risk that the counter's own extractor has a defect.
  This arm carries no extractor fault of its own.

## Files

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDoNothing/REPORT.md`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDoNothing/receipt.json`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDoNothing/counter.out`
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/controls/CtlDoNothing/change.diff` (empty, 0 bytes)
