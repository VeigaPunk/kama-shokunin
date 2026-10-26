# K1Hist — C1 independent recount (append-only-audit v2)

**Verdict: agreement — the independent recount (built from the frozen v2 definitions and git primitives only) matches the lane's `append-only-audit.py` v2 output exactly on all 85 contracted files and all 5 events; no disagreements, no defects found.**

## Method (no tool/counter code read)

Independent implementation written from the frozen counter's published definition (tools/round47-append-audit-v2-check.py docstring, `v2 definitions` block; the only code text I read is that docstring region):
- commits: `git rev-list --parents --topo-order --reverse 3a09a1d93dcc16799cf6c4b48786e6440af134c4` → 303 commits; diff of each commit vs its first parent (root vs empty tree).
- contract: blob `3a09a1d...:registry/append-only-contract.tsv` (header `path\trule\tdeclared_at\tnote`); patterns expanded with `fnmatch.fnmatchcase` over `git ls-tree -r --name-only` at tip → **85 files** (sorted, de-duplicated).
- deleted: `git diff --numstat --no-renames <p> <c> -- <file>` per (commit, file); events = deleted ≥ 20. Content multiset D taken from `git diff --unified=0 --no-color --no-ext-diff --no-renames` parsing hunk sections (lines starting with `-` inside a hunk, byte-exact; a final non-empty segment after the last `\n` counts as a line).
- held(x) = Σ_v min(D[v], max(0, M_x[v] − K[v])), K = M_parent − D; window = event commit and every later commit in the rev-list up to tip; status = restored/unrestored/partial.

Independent check performed inside the recount: for every event, `sum(D) == numstat deletions` (hunk sum vs numstat); any mismatch aborts with an error.

## Evidence

### 1. Official tool run (comparison target)
```
$ python3 /home/vgpnk/Projects/shokunin/kama-shokunin/tools/append-only-audit.py \
    --repo $S/lane --to 3a09a1d93dcc16799cf6c4b48786e6440af134c4 --json
exit=1   # stderr empty; expected (partial events exist)
```
Output: schema `append-only-audit/v2`, 85 files, 303 commits, 5 events.

### 2. Independent recount run
```
$ python3 recount_c1.py $S/lane 3a09a1d93dcc16799cf6c4b48786e6440af134c4 registry/append-only-contract.tsv
run_exit=0
```
Output: schema `append-only-audit/v2`, 85 files, 303 commits, 5 events.

### 3. Comparison (recount.json vs tool.json)
```
files equal: True                  (85 = 85, identical sorted lists)
event key sets equal: True         (same 5 (commit, file) pairs)
field disagreements: 0             (deleted, restored_max, restored_best, restored_by, status — all equal)
```

### 4. Events (identical in both)
| commit | file | deleted | restored_max | restored_best | restored_by | status |
|---|---|---:|---:|---|---|---|
| dd9f5dc6c0e63d038bdd070094d7f38290eeee1b | SCORECARD.md | 31 | 24 | dd9f5dc6… | — | partial |
| 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c | LOG.md | 2292 | 2292 | 82b5e9d33a19734a1f33985acabe7021593e9199 | 82b5e9d3… | restored |
| 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c | SCORECARD.md | 2421 | 2420 | 82b5e9d3… | — | partial |
| 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c | corpus/QUALITY.md | 375 | 375 | 82b5e9d3… | 82b5e9d3… | restored |
| 0718b6abbda6afa6b0ce586f46739fbb92c7cf9c | corpus/README.md | 663 | 663 | 82b5e9d3… | 82b5e9d3… | restored |

### 5. Numberstat cross-check (hunk sums vs numstat), all events
```
dd9f5dc6 SCORECARD.md   hunk_sum=31   minus_lines=31   numstat_del=31
0718b6ab LOG.md          hunk_sum=2292 minus_lines=2290  numstat_del=2292
0718b6ab SCORECARD.md    hunk_sum=2421 minus_lines=2417  numstat_del=2421
0718b6ab corpus/QUALITY.md hunk_sum=375  minus_lines=375   numstat_del=375
0718b6ab corpus/README.md   hunk_sum=663  minus_lines=663   numstat_del=663
```
A naive `-`-line count undercounts LOG.md by 2 and SCORECARD.md by 4 because deleted *content* lines begin with `---` (e.g. LOG.md diff lines 2112 `---tip <full-commit>` reads …` and 2121 `---rev <full-commit>` reads …`, in `git diff --unified=0 --no-color --no-ext-diff --no-renames 0718b6ab^ 0718b6ab -- LOG.md`). These are exactly the round-46 D1 gap numbers (2290 vs 2292, 2417 vs 2421); the v2 hunk-header counting correctly keeps them, and the recount's `sum(D) == numstat` assertion passes on all events.

## Findings
None — zero disagreements between the independent recount and the audit tool. No defect to propose.

## Artifacts
- Script: `recount_c1.py` (independent recount, committed to out dir).
- `recount.json` — independent recount output.
- `tool.json` — official audit tool output (exit 1) copied from scratch.
