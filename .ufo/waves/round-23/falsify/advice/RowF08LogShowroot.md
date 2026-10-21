# Row F08-log-showroot-cutoff — independent rebuild

Seat: CloseKama22.RowF08LogShowroot-2. Clone:
`/tmp/kama-r23w2/CloseKama22.RowF08LogShowroot-2`, `git rev-parse HEAD` =
`245a37f69628c2c6bb29bbf17897d8fb5946c857`. git 2.56.0. Auditors used:
frozen object `4fe9339f8fc3a4a4a479d9c938a850da12f1124d` (content sha256
`09ecd63bdc3a5be5264e6d2966602a32e52ca0678dc89de99959318245ab3b3f`) and
current `tools/report-landing-audit.py` (blob `f10d811eafcc5bc853abdf75c4a05ec2374cd579`,
sha256 `f228f17420134a4a4fb6d1f93b943f78647e7e60882f767e6cb7cba11d6928a7`).
Grid sha256 `72c1e53083a33da9d5beb065c2483f3c1456c1489b6cca26f2842453f74836da`.

## Verdict

**PARTIALLY.**

1. The F08 fault premise is **real and observed**: repo-local `log.showRoot=false`
   hides the fleet root commit's add from `git log --diff-filter=A`, the frozen
   arm flips to `landed-omitted` (exit 1), and the current arm stays clean (exit 0).
2. The expected outcome (`exit 0`, no defect kinds) is **correct**, not merely
   what current does: the fleet commit that first added the report is the root
   commit (author time 2000), the lane's second commit (3500) is therefore
   `post_report`, and both publishes carry byte-identical report content, so a
   3500-authored commit cannot be expected in bytes authored at 2000.
3. A **near variant of the same first-add channel is still wrong in current**:
   the first add made by a *merge commit* is invisible to
   `--diff-filter=A` (git does not diff merges without `-m`/`--diff-filter`
   merge variants). With F08's drop/re-add shape this flips current to a false
   `landed-omitted` (exit 1); with the merge as the only add it returns
   `exit 2 "has no fleet commit"` for a report that `git show HEAD:<path>`
   reads. Both arms fail identically, so this is not a frozen→current
   regression and it is inside the docstring's disclaimer "other
   repository-local channels are not claimed" (tools/report-landing-audit.py:54);
   it is nevertheless absent from the wave's declared open list and is a real
   residual for the same cutoff primitive.

## 1. Premise (frozen) — observed

Builder `f_show_root` at tests/report-audit/repo-state-grid.py:304-316, row at
:549. Hand rebuild (fresh /tmp repos, `GIT_CONFIG_GLOBAL=/dev/null`,
`GIT_CONFIG_NOSYSTEM=1`, identity set per command, no grid import):
lane commits `round-1: work` @1000 (cited) and `round-1: after report` @3500 by
`kama-shokunin`; fleet root commit @2000 adds `.ufo/reports/round-1/kama.md`
citing the @1000 commit; `git rm` @3000; re-add identical bytes @4000;
`git config log.showRoot false`.

- `git log --diff-filter=A --format=%at -- .ufo/reports/round-1/kama.md`
  → `'4000'` (root add hidden).
- same with `-c log.showRoot=true` → `'4000\n2000'`.
- frozen auditor: **exit 1**, cutoff 4000, required 2, post_report 0,
  defect `landed-omitted` token `365ea9639b75954b6bca63c9f1309b55d0b0e20f`
  (the @3500 lane commit), stderr empty, no traceback.
- current auditor: **exit 0**, cutoff 2000, required 1, post_report 1,
  defects `[]`, stderr empty.

In-clone grid run:
`python3 tests/report-audit/repo-state-grid.py --case F08-log-showroot-cutoff --arm both --json`
→ frozen `exit=1 kinds=["landed-omitted"] met=false`; current `exit=0 kinds=[] met=true`.
This reproduces the L1's 1-fault/1-control result for this row. Note the
builder's `require` (:314-315) only proves the config hides the add; it does not
prove frozen flips. Here the flip is real because re-add @4000 > lane @3500.

## 2. Is `exit 0` the correct expectation?

Yes. The auditor's own contract (tools/report-landing-audit.py:22-25) defines
`landed-omitted` by "the author time of the fleet commit that
**first added** the report"; :28-30 adds "Author time is used ... Lane commits
authored after the report are `post_report` and not required." The first add is
the root commit: `log.showRoot` is a display setting (git-config(1):
"If true, the initial commit will be shown as a big creation event. This is
equivalent to a diff against an empty tree." —
https://git-scm.com/docs/git-config#Documentation/git-config.txt-logshowRoot),
while the commit's tree genuinely adds the path relative to the empty tree.
Its author time is 2000; the @3500 commit is later and is correctly
`post_report`. Both publishes in the fixture are the same `report([lc])` bytes
(grid :308 and :312), so the @4000 re-add changes neither content nor the
first-add; the bytes authored at 2000 cannot be expected to cite a 3500 commit.
Exit 0/no kinds is therefore the contract's answer independent of current.
Resetting the cutoff at a re-add would demand a citation the unchanged bytes
cannot contain; refusing a transient report removal would make ordinary fleet
recovery fatal.

## 3. Near variant current still gets wrong (same cutoff primitive)

`git log --diff-filter=A` never emits a diff for a merge commit unless a
`--diff-merges` variant is given (git-log(1): "unless one of `--diff-merges`
variants (including short `-m`, `-c`, `--cc`, and `--dd` options) is explicitly
given, merge commits will not show a diff" — https://git-scm.com/docs/git-log).
So a merge commit that is itself the first add of the report is invisible to
`report_cutoff` (tools/report-landing-audit.py:203-206) in both arms.
Reproduced with hand-built merge commits (`git commit-tree`, parents: mainline
without the report, side branch without it; merge tree adds the report,
author/committer @2500):

- **N1, merge add only** (`/tmp/f08-N1`): A-log `''`;
  `-m --first-parent` A-log `'2500'`; `git show HEAD:<path>` returns 77 bytes.
  Both arms: **exit 2**, stderr
  `could-not-evaluate: round 1: .ufo/reports/round-1/kama.md has no fleet commit`.
  That statement is false: the report is committed and readable. Per the
  documented rule the correct result is clean: cutoff 2500, lane @1000 cited,
  lane @3500 post_report → exit 0.
- **N2, F08's exact shape but hidden by a merge** (`/tmp/f08-N2`): merge adds
  @2500, `rm` @3000, identical re-add @4000. A-log `'4000'`;
  `-m --first-parent` A-log `'4000\n2500'`. Both arms: **exit 1**, cutoff 4000,
  required 2, kinds `['landed-omitted']` — a false defect, since the true
  first add is @2500 and @3500 is post_report (correct exit 0). Current's
  `-c log.showRoot=true` pin (:95) does not cover this producer.
- Control M1 (ordinary merge of a side branch whose commit adds the report):
  A-log `'2000'`, both arms exit 0 — the gap needs the merge commit itself to
  introduce the path (evil merge / add during merge resolution), which is
  narrow but is ordinary reachable repository state, not config.
- Remediation shape (not applied): `git log -m --first-parent --diff-filter=A`
  yields `'2500'` for N1 and `'4000\n2500'` for N2, restoring the true first add
  (`out[-1]` then 2500).
- Other probes that did **not** reproduce a current error: a report renamed
  into place (`git mv drafts/kama.md <rel>`) is reported as `A` at the rename
  commit by the pathspec-limited log (both arms exit 0, cutoff 2500, with and
  without `diff.renames`); a lane name containing pathspec metacharacters
  (`kama[1]`) plus a literal `kama[1].md` report also resolved correctly
  (current exit 0).

## Not verified

- Only the F08 row was run from the grid; the other 25 fault rows, the 8
  controls, the full 26/26 + 8/8 numbers, `isolation-mutants.py`, the selftest
  50/50, and the rounds 10-22 ledger no-harm claim were not re-run.
- git < 2.45 behavior was not exercised.
- N1/N2 correctness is derived from the documented cutoff rule; no independent
  reference implementation was written.
- Whether the L1 already knows the merge-add producer (it is not in the
  declared open list as relayed); no real fleet repository with such a history
  was examined — the evidence is hand-built fixtures.
- Timing/`union` semantics, alternates (O01), gitfile redirect (O02),
  ambiguity overwrite, second Landed section, errata correction resolution were
  not touched.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-23/falsify/advice/RowF08LogShowroot.md`
  (this report; the only lane-tree file written).
- Scratch only, outside the lane: clone
  `/tmp/kama-r23w2/CloseKama22.RowF08LogShowroot-2`, frozen copy
  `/tmp/frozen-r23-f08.py`, fixtures `/tmp/f08-hand`, `/tmp/f08-rename`,
  `/tmp/f08-rename-{true,false}`, `/tmp/f08-N1`, `/tmp/f08-N2`, `/tmp/f08-glob`.
- No installs or upgrades. No lane tracked file, index, jj state, or other
  checkout was modified.
