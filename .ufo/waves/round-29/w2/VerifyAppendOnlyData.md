# VerifyAppendOnlyData — round 29 w2 (kama, C1)

Seat: `kama-r29-w2-VerifyAppendOnlyData`
Slice: data-commit append-only shape of `513eba3b` vs base `2aa46e24`.
Repo: `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch master). All checks are
commit-vs-commit; the dirty working tree does not affect them.

## Verdict: VERIFIED — append-only claim holds for the correction surface; one scope clarification on the "9 files" check (see F1).

## Commands run and outputs

### 1. Endpoints and range contents
```
git cat-file -t 2aa46e24…  → commit
git cat-file -t 513eba3b…  → commit
git log --format='%H %s' 2aa46e24..513eba3b
  513eba3b round-29: C1 data (11 appended self-assessment correction rows); routed repair 6 echo-recheck exit-2 receipt; mined-mistake fix in prereg-time-check (space/tilde time forms) with receipts
  35b90184 round-29: pre-freeze control call receipts (14 seats; no control meets C1; counter unchanged) before any correction row
  827d1365 round-29: C1 freeze (calibration): counter, preregistration, base receipt, census start; before any seat
```
The range `2aa46e24..513eba3b` spans **three** commits: freeze, controls, data.

### 2. `git diff --stat 2aa46e24..513eba3b` (the literal assigned command)
```
171 files changed, 15830 insertions(+), 3 deletions(-)
```
Top entries are `.ufo/waves/round-29/before/*` and `.ufo/waves/round-29/controls/Ctl*/…`
(full listing: artifact of `git diff --stat`, 171 rows; `git diff --name-status` = **169 A, 2 M**;
the only modified files are `SCORECARD.md` and `tools/prereg-time-check.py`).

### 3. Pure-append check on SCORECARD.md over the range
```
git diff 2aa46e24..513eba3b -- SCORECARD.md | grep -c '^-[^-]'   →  0
```
(grep exits 1 on count 0 — expected.) SCORECARD.md receives **zero** deletions across
the entire range.

### 4. SHONEN.md / LOG.md untouched in range
```
git diff --quiet 2aa46e24..513eba3b -- SHONEN.md  → exit 0
git diff --quiet 2aa46e24..513eba3b -- LOG.md     → exit 0
```
Both files byte-identical between base and data tip.

### 5. The "exactly 9 files" clause — where it actually lands
The range stat lists **171 files, not 9**, because the range includes the freeze and
controls artifact trees. The 9-file figure is exact for the **data commit itself**:
```
git show --stat --format= 513eba3b
 .ufo/waves/round-29/mined/orig-75b78bb4.out        |  5
 .ufo/waves/round-29/mined/orig-selftest.out        | 46
 .ufo/waves/round-29/mined/patched-75b78bb4.out     |  5
 .ufo/waves/round-29/mined/patched-d8bf1804.out     |  5
 .ufo/waves/round-29/mined/patched-selftest.out     | 56
 .ufo/waves/round-29/repairs/echo-exit2/existing.json| 1
 .ufo/waves/round-29/repairs/echo-exit2/receipt.txt  | 11
 SCORECARD.md                                       | 23
 tools/prereg-time-check.py                         | 13
 9 files changed, 162 insertions(+), 3 deletions(-)
```
These 9 files cover all three clauses of the commit message: SCORECARD.md correction
rows, the echo-exit2 repair receipt, and the prereg-time-check fix plus its mined/*.out
receipts. Nothing else is touched.

### 6. SCORECARD.md addition is a tail append with exactly 11 data rows
```
git show 513eba3b -- SCORECARD.md | grep '@@'   →  @@ -1439,3 +1439,26 @@
git show 513eba3b:SCORECARD.md | wc -l          →  1464
git show 513eba3b -- SCORECARD.md | grep -c '| SA29:'  →  11
```
Single hunk at end-of-file (old file ends at 1441 w/ context; new file 1464): 23 added
lines = section heading, prose, table header+separator, and **exactly 11 `| SA29:…`
correction rows — one per false statement**. Zero `-` lines in the file's diff.

### 7. All 3 range deletions are inside tools/prereg-time-check.py
```
git diff --numstat 2aa46e24..513eba3b | awk '$2>0'  →  10  3  tools/prereg-time-check.py
```
Deleted lines are the old `TIME_RE` regex and strict-`T`-only parse lines, replaced by
the space/tilde-tolerant forms — the disclosed "mined-mistake fix". The C1 correction
surface (SCORECARD.md/SHONEN.md/LOG.md) is 100% append-only.

## Findings

- **F1 (clarification, not a defect):** the instruction "the stat lists exactly the 9
  files the commit message names" is true of `git show --stat 513eba3b`, not of the
  assigned range stat, which correctly lists 171 files because freeze (`827d136`) and
  controls (`35b90184`) sit inside `2aa46e24..513eba3b`. If the L1 expects the range
  stat to show 9, that expectation is malformed; the underlying claim (data commit
  touches exactly the 9 files its message describes) is **verified**.
- **F2 (disclosed non-append, verified):** the data commit is not purely additive —
  `tools/prereg-time-check.py` has 10+/3− (the mined-mistake fix, named in the commit
  message with receipts under `.ufo/waves/round-29/mined/`). This does not violate the
  C1 claim, which scopes "appended exactly one correction row per false statement" to
  the self-assessment files; SCORECARD.md is pure tail-append and SHONEN.md/LOG.md are
  untouched.
- **F3 (context, not a defect of this commit):** working tree carries uncommitted
  ` M LOG.md`, ` M SCORECARD.md`, ` M SHONEN.md`, ` M tools/prereg-time-check.py` and
  untracked `.ufo/waves/round-29/{final,mined,w1,w2}` paths — the attempt-1 leftovers
  named in the wave brief, under verification elsewhere.

## Residual risk / gaps
- Row-content correctness (each row's statement/W/cause) is out of this slice's scope;
  only count (11) and placement (tail append) are verified here.
- Whether the post-freeze prereg-time-check.py edit affects preregistration integrity
  is a separate check; the commit discloses it and adds before/after receipts.

## Tools installed
None — stock `git`/`grep`/`awk`/`wc`/`mkdir` only.
