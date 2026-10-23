# VerifyRow09 — correction row 9 hand-verification (C1 calibration)

Seat: `kama-r29-w2-VerifyRow09-3` (w2 reviewer). Item: hand-verify correction row 9
(`SA29:SCORECARD.md:Q:a7e98b1030:0`) WITHOUT running the counter on the lane tree.
All evidence below is hand-derived via read-only git queries; the counter was never executed.

## Verdict

```json
{"sid": "SA29:SCORECARD.md:Q:a7e98b1030:0", "verdict": "confirmed-false", "observed": "q:no-artifact"}
```

## 1. Base statement line (base 2aa46e24, SCORECARD.md:834)

`git --no-replace-objects show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:SCORECARD.md` (lines 832–836):

```
832  .ufo/waves/round-18/live-recovery/receipt-1.json …` — without the pin
833  `baseline=VALID members=3 rejected=0/3` exit 1, with `--tree-sha`
834  `baseline=VALID rejected=3/3` exit 0. The pin binds observed bytes, not an
835  upstream constant, and does not authenticate execution.
```

Line 834 contains exactly one backticked span: `` `baseline=VALID rejected=3/3` ``.
It is 26 characters (within Q's 6–200 bound), contains digits, and contains `=` — so the Q
extractor classifies it (index `k=0`). It starts with backtick, not with any Q_CMD prefix
(python3/python/bash/sh/git/node/./tools///). No other extractor class fires on the line:
no RE_P path, no backticked lane path with digest (RE_HN), no date (RE_T), no
(Measured commit / at/base/tip/…) hex token (RE_CWORD). So the line yields exactly one
statement, the Q one, matching the table's `:0` index.

## 2. Writing revision W

`git blame --line-porcelain 2aa46e24 -L 834,834 -- SCORECARD.md` names
`7229fa95eb122310e9e5334ad799ee3006293ebd` (summary: `round-19: citation provenance,
install-tree pin, r18 defect corrections`, committer time 1792564487).
Re-derived via the counter's own full-file blame (no `-L`), 834th content line:
**7229fa95eb122310e9e5334ad799ee3006293ebd** — identical.

The table cell W = `7229fa95` is the 8-hex prefix of that full hash. (The sid's
`a7e98b1030` is not a commit prefix; it is the statement-line sha, see §4.)

## 3. Q rule applied by hand at W

Rule (count-c1.py docstring, `check()`): a Q statement holds iff the span "occurs verbatim
in at least one blob of the tree at W other than SCORECARD.md, SHONEN.md, LOG.md and
corpus/**". `check()` implements this as

```
git grep -F -q -e <span> W -- . ':(exclude)SCORECARD.md' ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'
```

Hand-ran the exact command at W=7229fa95 with `--no-replace-objects`:
**exit status 1 (no match)** → statement does not hold at W; the observed fail value the
counter prints is `q:no-artifact`.

Cross-check — where the span does live at W: the full-tree `git grep -F` at W finds exactly
one hit, `SCORECARD.md:834` itself, which is excluded by the rule. No committed non-excluded
blob at W contains the span. (The quoted gate output was never committed at round-19; the
span reaches committed lane files only later, e.g. at tip 513eba3 in
`.ufo/waves/round-29/controls/…`/`before/c1-base.json` — consistent with the row's cause
"quoted gate output; no committed file at W holds this text".)

## 4. sid = `SA29:SCORECARD.md:Q:a7e98b1030:0`

The counter builds `sid = f"{fname}:{cls}:{lsha}:{k}"` with `lsha` = first 10 hex of
SHA-256 of the line text. Hand-computed (echo of the exact line bytes):

```
echo '`baseline=VALID rejected=3/3` exit 0. The pin binds observed bytes, not an' | sha256sum
→ a7e98b1030bd5152d6d43fdba990766530d53c263775c8b1c93a7bec2da813bf
prefix (10) = a7e98b1030  ✔
```

with `k=0` (the line's first/only Q span). So `SCORECARD.md:Q:a7e98b1030:0` is exactly the
counter's sid for this statement, and the table's first cell (minus the `SA29:` prefix)
matches it. One correction row in the data commit references this sid (count = 1, no duplicate).

## 5. Correction row last cell = observed value

Data commit 513eba3, SCORECARD.md line 1462 (under `## Round 29 — self-assessment
corrections`, heading line 1443):

```
| SA29:SCORECARD.md:Q:a7e98b1030:0 | SCORECARD.md:834 | Q | `baseline=VALID rejected=3/3` | 7229fa95 | quoted gate output; no committed file at W holds this text | q:no-artifact |
```

Last cell (strip backticks) = `q:no-artifact` = the hand-derived observed value exactly. ✔
The row is the 9th of the 11 appended data rows in the 513eba3 diff, matching "correction
row 9".

## Evidence commands (all read-only, `--no-replace-objects`)

- `git show 2aa46e24:SCORECARD.md | sed -n '832,836p'`
- `git blame --line-porcelain 2aa46e24 -L 834,834 -- SCORECARD.md`
- `git blame --line-porcelain 2aa46e24 -- SCORECARD.md` (full-file, awk-extracted rev #834)
- `git grep -F -q -e 'baseline=VALID rejected=3/3' 7229fa95 -- .` + the four `:(exclude)` pathspecs → rc=1
- `git grep -F -n -e 'baseline=VALID rejected=3/3' 7229fa95` → sole hit SCORECARD.md:834
- `git grep -F -n -e 'baseline=VALID rejected=3/3' 513eba3` → hits at tip (control receipts/before), confirming later commits introduced it
- `git show 513eba3:SCORECARD.md | grep -n 'self-assessment corrections|a7e98b1030'`
- `git show 513eba3 -- SCORECARD.md | grep -n '^+'` (data rows)
- `git show -s --format='%H %ct %s' 7229fa95`

No lane file was modified. The counter was not run (its sha256 `fe11d599…7383` was still
verified against the frozen value).
