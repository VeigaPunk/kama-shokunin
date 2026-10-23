# CtlR29RowsOnly — round-30 C1 control arm (calibration)

## Policy

Keep only the 11 round-29 correction rows the lane tip already carries, and add **no** round-30
correction row (no `## Round 30 — self-assessment corrections` section, no `SA30:` rows).

The lane tip `52ac3af8614b5040ba5e17f17a2c7af029706e6c` already satisfies this policy exactly:
`SCORECARD.md` there carries 11 `| SA29:` rows under `## Round 29 — self-assessment corrections`
(line 1443) and zero `SA30:` rows. The policy is therefore a content no-op; it is represented in
the clone by an **empty commit** so that a candidate tip exists to score.

## Sandbox and candidate

- Clone: `/fast/scratch/hyaku/kama-r30/ctl/CtlR29RowsOnly` (from `/home/vgpnk/Projects/shokunin/kama-shokunin`)
- Base of clone: lane tip `52ac3af8614b5040ba5e17f17a2c7af029706e6c`
- Candidate commit: `c9778953f505a8c7cbdc8cd1e313a72f2f9baae3`
- Identity: `kama-r30-ctl-CtlR29RowsOnly <ctl-CtlR29RowsOnly@kama.local>` (local `git config` in the clone only)
- Tree: `45c05ee28cb573d0996d069bfc742ac269f72f22` — **identical** to the lane tip tree

## Diff

`git diff 52ac3af8614b5040ba5e17f17a2c7af029706e6c c9778953f505a8c7cbdc8cd1e313a72f2f9baae3`
is empty (0 bytes, saved as `change.diff`). Nothing in the tree changed: 11 `SA29:` rows, 0
`SA30:` rows, headings unchanged. The only artifact of the policy is the commit message.

## Command

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlR29RowsOnly \
  --tip c9778953f505a8c7cbdc8cd1e313a72f2f9baae3 \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlR29RowsOnly/counter.json
```

The LANE copy of the counter was used unmodified. Its bytes hash to
`c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`, the frozen digest recorded in
`preregistration.json` C1.counter_sha256.

## Summary line (verbatim, from `counter.out`)

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 0 unresolved 2 met False tip c9778953f505
```

Exit: **0** (ran; the count is whatever it is).

## Receipt fields (`counter.json`)

| field | value |
|---|---|
| `counter_sha256` | `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d` |
| `base` | `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` |
| `tip` | `c9778953f505a8c7cbdc8cd1e313a72f2f9baae3` |
| `statements` | 141 |
| `extracted` | 69 |
| `oracle_items` / `oracle_bound` / `oracle_unbound` | 72 / 72 / 0 |
| `mismatched_at_base` | 13 |
| `append_only` | true |
| `correction_rows` | 11 |
| `valid_corrections` | 11 |
| `false_corrections` | `[]` (none) |
| `unresolved` | 2 |
| `met` | **false** |

## Which sids remain unresolved

Exactly two, both class Q, both from the round-30 oracle population (the `:o0` suffix marks an
oracle item, not an extractor statement):

1. `SCORECARD.md:Q:4a6f7c911e:o0` — SCORECARD.md line 41, token `file=yes`, observed `q:no-artifact`,
   W = `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21`. Oracle source: `.ufo/waves/round-29/w1/out/RecallA/missed.json`.
2. `SCORECARD.md:Q:422b431349:o0` — SCORECARD.md line 901, token `declared2048 = captured training2048`,
   observed `q:no-artifact`, W = `92b146253fd3a8c4bfade94c909dc63b13d6f4a8`. Oracle source: `.ufo/waves/round-29/w1/out/RecallB/missed.json`.

The other 11 mismatches (all extractor statements, sids `SCORECARD.md:{Q,P}:…:{0,2}`) are covered
by the 11 round-29 rows and are counted valid.

## Is this a genuine shortcut?

Yes — but it is a shortcut that the counter *rejects*, which is the point of the arm. It is the
"reuse the previous round's rows and skip the newly disclosed population" shortcut: it claims the
calibration work by inheriting round-29's 11 rows without doing round-30's work on the 72-item
oracle population that round 30 added. Because the two statements that never carried a correction
row (line 41 `file=yes`, line 901 `declared2048 = captured training2048`) are among the 13
mismatches, the shortcut leaves `unresolved == 2` and the frozen predicate fails.

## What it shows

- The round-29 rows survive the round-30 counter unchanged: all 11 are still valid corrections
  (`valid_corrections 11`, `false_corrections 0`). Their sids and observed values were not
  disturbed by the widened population.
- The counter discriminates the shortcut: `met false`, `unresolved 2` ≠ 0, against a target that
  requires `unresolved == 0`. Round-29's receipt alone would have been sufficient under the old
  69-statement population; it is not sufficient under the round-30 population.
- Cross-check against the lane's own committed pre-freeze receipt
  `.ufo/waves/round-30/c1/before/c1-r29-tip.json` (tip `52ac3af`): every scored field agrees —
  141/69/72/72/0, mismatched 13, append_only true, correction_rows 11, valid 11, false 0,
  unresolved 2, `unresolved_ids` identical in both content and order, `met false`. The arm is
  reproducible against the frozen counter.
- Consequence for the claim: `mismatched_at_base == 13`, `oracle_items == 72`,
  `oracle_unbound == 0` and `append_only` all hold on this tree; the **only** unmet conjunct is
  `unresolved == 0`. Meeting the claim requires exactly the two additional rows named in
  `preregistration.json` C1.claimed_work (the RefInstrument arm's two `SA30:` rows, one per
  unresolved sid above, each carrying observed `q:no-artifact`).

## Files

Under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlR29RowsOnly/`:

- `REPORT.md` (this file)
- `counter.out` — summary line + `exit=0`
- `counter.json` — receipt (sha256 `83dab3c8af486361a08aa7848fcf24a642037408a3eacb0d75c36a88457e571f`)
- `change.diff` — empty (0 bytes); the policy changed no file

## Tooling

No tools were installed or updated. Counter run under `/usr/bin/python3` 3.14.8; git 2.56.0.
Counter run took ~35 s as the task card predicted. The lane's tracked files (counter, SCORECARD.md,
LOG.md, corpus/, tools/) were not edited; no lane git write was performed; only the untracked
control-receipt directory under `.ufo/waves/round-30/controls/CtlR29RowsOnly/` was written.

Report: .ufo/waves/round-30/controls/CtlR29RowsOnly/REPORT.md
