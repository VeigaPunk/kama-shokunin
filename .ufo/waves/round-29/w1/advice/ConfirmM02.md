# Advice — ConfirmM02 (round 29 wave 1, C1 first falsifier)

**sid `SCORECARD.md:Q:f4c42debcc:2` → `confirmed-false`** (counter's `q:no-artifact` is correct).

## Findings (by severity)

1. **False at W (confirmed).** Line SCORECARD.md:20 at base 2aa46e24, W = ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21 (blame-confirmed). Span `` `RESULT pass=24 fail=0` `` occurs at W only in LOG.md (142/215/242), SHONEN.md, corpus/knowledge/snapshot-history.md, corpus/lessons/round-2.md, and the SCORECARD.md line itself. With `:(exclude)` applied exactly as the counter does, `git grep -F` finds nothing (exit 1) ⇒ `q:no-artifact` correct.
2. **The referent is real but unrecorded outside the excluded set.** `tools/test-snapshot.sh` at W has md5 `860f26ac05938cdfc1a8816eff1570b4` (matches the statement's H field); the RESULT line comes from LOG.md §§round 1–2 (excluded) and from fleet reports (`round-2/kama.md:14`, `round-4/kama.md:32`, `round-10/kama.md:21,47`), which are not committed lane blobs at W.
3. **No counter defect found.** The Q rule was applied by hand and matches the counter's check; the verdict is the statement being false at W, not a counter false-positive.

## Suggested correction row content

- sid: `SCORECARD.md:Q:f4c42debcc:2` — observed `q:no-artifact`
- cause (≤25 words): "Quoted output RESULT pass=24 fail=0 exists only in LOG.md/corpus at W, which class Q excludes."

## Notes

- Verification was read-only git on the lane checkout (blame, grep, show, ls-tree); no write was made to the lane repo; no installs; no scratch used.
- Evidence files: `w1/out/ConfirmM02/verdict.json`, `w1/out/ConfirmM02/REPORT.md`.
