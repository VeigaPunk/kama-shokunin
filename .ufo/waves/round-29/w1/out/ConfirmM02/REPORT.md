# ConfirmM02 — sid SCORECARD.md:Q:f4c42debcc:2

**Verdict: `confirmed-false`** (the base statement was false at the revision that wrote it; the counter's `q:no-artifact` observation is correct).

## Statement

- File SCORECARD.md line 20 at base 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d, class Q, token `` `RESULT pass=24 fail=0` ``.
- Writing revision W = ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 (confirmed by `git blame -L 20,20 --line-porcelain 2aa46e24 -- SCORECARD.md`, which names ea72c3e… for line 20).
- Full line at base: `| **freshness** (worked round 2) | **6 → 7** | `snapshot` writes dated `kama-probe/v2` JSON and diffs tracked `registry/history/latest.tsv` into append-only `DELTA.md`; live re-census run: `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2` — the 16 transitions are the honest record of 8 consumer files deleted from the box plus MODEL_OK→DEAD on the dead ports; stable re-run `transitions=0`; `tools/test-snapshot.sh` md5 `860f26ac05938cdfc1a8816eff1570b4` → `RESULT pass=24 fail=0` | round 3 |`

## Q rule applied by hand (frozen docstring, count-c1.py)

A Q span (6–200 chars, digit + "=" or space+{met,registered,counted,stale,observed,verified,RESULT}, not starting python3/python/bash/sh/git/node/./tools///) must occur **verbatim in at least one blob of the tree at W other than SCORECARD.md, SHONEN.md, LOG.md and corpus/**. Fail = `q:no-artifact`.

## Independent verification (no use of the counter)

1. `git grep -F -e "RESULT pass=24 fail=0" W -- .` — span occurs at W only in **LOG.md** (lines 142, 215, 242), **SCORECARD.md** (the statement line itself), **SHONEN.md**, **corpus/knowledge/snapshot-history.md**, **corpus/lessons/round-2.md**. All are excluded classes.
2. `git grep -F -l -e "RESULT pass=24 fail=0" W -- . ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'` — no file listed (exit 1).
3. Same with `-q` — exit 1, i.e. the counter's `q:no-artifact` branch triggers.

⇒ The span is absent from every non-excluded committed blob at W ⇒ the statement does not hold at W.

## Where the quoted output actually came from

- `tools/test-snapshot.sh` exists at W and its md5 is exactly `860f26ac05938cdfc1a8816eff1570b4` (matches the claim's H field).
- The result line itself was recorded in **LOG.md §§round 1–2** (W lines 142, 215, 242) and copied into corpus knowledge/lesson files — all excluded by the Q rule by design.
- The fleet report `/home/vgpnk/Projects/shokunin/.ufo/reports/round-2/kama.md:14` (read-only, round-4 and round-10 reports too) records the same `RESULT pass=24 fail=0`, but reports are not committed lane-tree blobs at W.

So the underlying fact is real (the script does emit that line), but the Q class requires a committed, non-excluded artifact at W, and none exists. The statement is false per the frozen rule.

## Commands

Full command list with exact outputs (trimmed ≤ 40 lines each) is in `verdict.json`.

## Cause (one sentence, for the correction row)

> Quoted output RESULT pass=24 fail=0 exists only in LOG.md/corpus at W, which class Q excludes.
