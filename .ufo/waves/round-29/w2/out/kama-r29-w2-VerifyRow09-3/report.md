# VerifyRow09 report — correction row 9 hand-verification

Seat: `kama-r29-w2-VerifyRow09-3`. Item: VerifyRow09 (C1 calibration; the 11 committed
correction rows → row 9, sid `SA29:SCORECARD.md:Q:a7e98b1030:0`). The counter
(`.ufo/waves/round-29/count-c1.py`, sha256 `fe11d599…7383` ✔ verified) was NOT run; every
step was reproduced by hand with read-only git.

## Verdict

```json
{"sid": "SA29:SCORECARD.md:Q:a7e98b1030:0", "verdict": "confirmed-false", "observed": "q:no-artifact"}
```

## Steps

1. **Base statement** — base `2aa46e24:SCORECARD.md` line 834:
   `` `baseline=VALID rejected=3/3` exit 0. The pin binds observed bytes, not an ``.
   Exactly one backticked span, 26 chars, contains digit + `=` → Q class, `k=0`; no other
   class fires on the line (no P path, H/N digest, T date, C hex token).
2. **W** — `git blame --line-porcelain` at base: line 834 written by
   `7229fa95eb122310e9e5334ad799ee3006293ebd` (round-19 citation-provenance commit),
   re-confirmed by the counter's full-file blame (834th content line). Table W cell
   `7229fa95` = 8-hex prefix of that hash. ✔
3. **Q rule by hand at W** — docstring rule: span must occur verbatim in a blob of W's
   tree other than SCORECARD.md/SHONEN.md/LOG.md/corpus/**. Exact `git grep -F -q`
   command from `check()` ran at W with the four exclude pathspecs: **rc=1 (no match)**.
   Full-tree grep at W finds the span only in `SCORECARD.md:834` itself (excluded). The
   statement is therefore FALSE at W; observed value = `q:no-artifact`.
4. **Observed value match** — tip 513eba3 SCORECARD.md line 1462 correction row:
   last cell `q:no-artifact` = hand-derived observed value exactly. Row is the 9th of 11
   data rows; sid matches (`a7e98b1030` = first 10 hex of sha256 of the line bytes, verified
   independently); exactly one row names this sid (no duplicate).

## Finding

No defect. The correction row is accurate: statement confirmed false at W, observed value
exact. No lane file was modified; no counter execution; no tools installed (nothing new
needed — only git/printf/sha256sum, already present).

## Residual risk

- This seat verified only row 9; the other 10 rows and the receipt-level claims are other
  seats' slices.
- The verification is against committed objects with `--no-replace-objects`, matching the
  counter; the lane's working tree was not consulted (and need not be).
