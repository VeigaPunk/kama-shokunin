# w2 / MutateRowKill — C1 correction-row mutation probe

Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`,
branch master, unchanged). Claim: C1 (calibration), the 11 committed correction rows.
Item: delete row 5, then alter its last cell by one character, then duplicate it.
Scratch clone: `/tmp/mrk-c1` (fresh `git clone --no-hardlinks` of the lane, detached at
`513eba3b`). Counter under test: lane `.ufo/waves/round-29/count-c1.py`,
sha256 `fe11d599d064f5749c829394fc813f43921de2f9903e41c7217e3daa4b647383`
(identical in clone). Python 3.14.8. No tools installed; no pacman; no delegation.

Target row (SCORECARD.md line 1458 at tip, 5th `SA29:` row):

```
| SA29:SCORECARD.md:P:312b3e69b1:0 | SCORECARD.md:740 | P | `round-17-verifier-spotcheck.md:217–221` | c6dc46fa | bare file name; the lane file is corpus/lessons/round-17-verifier-spotcheck.md | p:absent |
```

## Baseline (pristine bytes)

Command: `cd /tmp/mrk-c1 && python3 .ufo/waves/round-29/count-c1.py --repo /tmp/mrk-c1 --tip refs/heads/master --out .../base-restored.json`

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
exit=0
```

Pristine SCORECARD.md: content sha256 `a46bcc744032bbab69738e654c657f58ee45c2ee55c8ee84f800251ab922f7b9`,
git blob OID `b805c8929aad048bd6b6dc8708e12de66f75d150`. Baseline passes, so a mutant failure is
attributable to the mutation.

Method note: the clone's checked-out commit was detached, so `refs/heads/master` stayed at
`513eba3b`. The first (unguarded) run after mutant A therefore measured the pristine tip; that
receipt was deleted and every mutant was re-run with `--tip HEAD`. All numbers below are from
the `--tip HEAD` runs (mutant commits are direct children of `513eba3b`).

## Mutants

| # | change | mutant commit | SCORECARD blob OID | SCORECARD content sha256 | receipt |
|---|---|---|---|---|---|
| A | row 5 deleted (1 deletion) | `33651e6c79e3934f07a370bedaf4d3285a323c5e` | `feefb49d364fed8cd2fc925d781f98cadf5b3b19` | `54d87b6d3e2df1e6a549f6d0c4307210a6c233a960cd77a8fac8c8b83231421e` | `mutant-a-missing-row.json` |
| B | row 5 last cell `p:absent` → `p:absfnt` (1 char) | `f79a1620af10f2a737b6f1584a3b9371c6fbe87f` | `0be3dc7e43305db458e51fc52549a0a33b8ea4d0` | `91e725be624fa56d0d063f4b258d9d6a2f3983fd36fa475dea221a6192613892` | `mutant-b-wrong-observed.json` |
| C | row 5 duplicated on identical bytes (1 insertion) | `59d9afb3039f6ec3983de4cdc6583e2e750aeb01` | `7f934055888886b6ed6216cf0cf433282f46686b` | `f1ee492cce48e2868bdc0c9bd80c81055b8679a2c1bb9179a711f0a42d013cba` | `mutant-c-duplicate-row.json` |

### A — deleted row 5

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 10 false_corrections 0 unresolved 1 met False tip 33651e6c79e3
```

Verdict **KILLED**. Matches the item's prediction exactly: the statement loses its only valid
row, `unresolved_ids` = `SCORECARD.md:P:312b3e69b1:0`, `valid_corrections 10`, `met False`,
exit 0.

### B — row 5 last cell one character wrong

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 10 false_corrections 1 unresolved 2 met False tip f79a1620af10
```

Verdict **KILLED**, with a numeric divergence from the prediction. Receipt detail:
`false_corrections [{sid: SCORECARD.md:P:312b3e69b1:0, observed: p:absfnt, why: wrong-observed}]`,
`unresolved_ids [SCORECARD.md:P:312b3e69b1:0]`, `unresolved 2`.

The item predicted `false_corrections 1 and unresolved 1`; actual is `1 and 2`. The counter is
self-consistent with its frozen docstring: the statement no longer has a valid correction row
(so it is counted once as uncovered) *and* the row is a false correction (counted again, since
"each false correction is itself counted as unresolved"). The prediction omitted the
uncovered-statement term. Not a counter defect; the mutant is rejected either way.

### C — row 5 duplicated under the heading

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 10 false_corrections 1 unresolved 2 met False tip 59d9afb3039f
```

Verdict **KILLED**, again stricter than predicted. Receipt detail:
`false_corrections [{sid: SCORECARD.md:P:312b3e69b1:0, observed: p:absent, why: duplicate}]`,
`unresolved_ids [SCORECARD.md:P:312b3e69b1:0]`, `valid_corrections 10`, `unresolved 2`.

The item predicted `false_corrections 1 unresolved 1`; actual is `false_corrections 1
unresolved 2`. Cause, read from `corrections()`/`main()` in the frozen counter: the loop adds
the first row to `valid`, the second row's sid is already in `seen` so it becomes a false row,
and then `valid -= {r["sid"] for r in false_rows}` removes the sid outright. So a duplicate
invalidates the original identical row too: `valid_corrections` drops 11 → 10 and the sid is
counted once as uncovered plus once as a false correction. This is stricter than the
docstring's literal reading ("does not carry exactly one valid correction row for it" — the
first row is itself valid, which would give unresolved 1). Behavior is deterministic and the
mutant is still rejected; the docstring phrase vs the `valid -=` line is flagged for the L1 as
a wording/edge-case mismatch, not corrected here.

## Restoration evidence

After each mutant the clone was reset with `git reset -q --hard 513eba3ba51a142c9936553e3a85918345eb5c4c`,
then `sha256sum SCORECARD.md` and `git status --porcelain | wc -l` were read:

| stage | HEAD | SCORECARD content sha256 | git status |
|---|---|---|---|
| clone creation | `513eba3b` | `a46bcc74…922f7b9` | clean |
| after A | 33651e6c → reset | `54d87b6d…` → `a46bcc74…922f7b9` | 0 |
| after B | f79a1620 → reset | `91e725be…` → `a46bcc74…922f7b9` | 0 |
| after C | 59d9afb3 → reset | `f1ee492c…` → `a46bcc74…922f7b9` | 0 |
| final | `513eba3b` | `a46bcc74…922f7b9` | 0 |

Restored-bytes baseline re-run (`--out base-restored.json`):

```
statements 69 mismatched_at_base 11 append_only True valid_corrections 11 false_corrections 0 unresolved 0 met True tip 513eba3ba51a
exit=0
```

Byte-identical to the pre-mutation baseline; `met True` restored.

## Scope observations (code inspection, no extra mutant run)

- `corrections()` reads only the tip SCORECARD.md text. Nothing binds a correction row to a
  commit, author, or append event; my synthetic commits (author `mutant
  <mutant@example.invalid>`) were consumed as data and the counter still evaluated normally.
  The receipt therefore certifies *tip content*, while C1's history claim ("lane commit
  `513eba3b` appended exactly one correction row per false statement") rests on evidence
  outside this counter.
- `append_only` was True in all three mutants because the edits stayed inside the appended
  region; the base-prefix check is exercised (10:55:45Z base bytes through line 1441 are
  still a prefix of every mutant blob).
- `mismatched_at_base` stayed 11 in every run, confirming the mutation did not perturb the
  base-statement extraction (blame at `2aa46e2` is independent of tip).

## Files produced

Under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/MutateRowKill/`:

```
f3c7a43907d44a4780593e4a12d07b71950e7fd32debb27f144c7dc0069dd504  base-restored.json
f7eb9f892ee4dda48ac50d4fb7298025eec6063fc6c244cebf628f097623e654  mutant-a-missing-row.json
2187a2de97cf9aaa3645fae94bf1e3268ac90cf99c419f575dbbdf92a5226e7f  mutant-b-wrong-observed.json
c7ab93bc8baecc859c70b0e0e626030b6fc2b37576f61040d388066df1f9277b  mutant-c-duplicate-row.json
```

Lane bounds: nothing in the lane was written except this directory and the trailer copy
`w2/MutateRowKill.md`; lane HEAD is still `513eba3b`, counter sha256 still `fe11d599…7383`,
`git status --porcelain` still lists the same 13 attempt-1 entries (6 modified, 7 untracked
paths). Scratch clone confined to `/tmp/mrk-c1`; no pacman, no installs, no delegation.
