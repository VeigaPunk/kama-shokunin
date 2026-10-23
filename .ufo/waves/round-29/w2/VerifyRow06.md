# VerifyRow06 — hand-verification of correction row 6 (sid `SA29:SCORECARD.md:Q:0ccd533544:0`)

Verdict JSON: `{"sid": "SA29:SCORECARD.md:Q:0ccd533544:0", "verdict": "confirmed-false", "observed": "q:no-artifact"}`

All checks performed by hand on committed objects only (`git --no-replace-objects`, no counter run
on the lane tree). Repo: `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch master, tip
`513eba3ba51a142c9936553e3a85918345eb5c4c`).

## The correction row (tip SCORECARD.md)

Row 6 = line 1459 of `HEAD:SCORECARD.md`, under `## Round 29 — self-assessment corrections`
(heading at line 1443). It is the unique row for this sid (grep count = 1):

```
| SA29:SCORECARD.md:Q:0ccd533544:0 | SCORECARD.md:823 | Q | `required=3 found=0 verified=0 missing=3` | 7229fa95 | quoted citation-provenance before-run; no committed file at W holds this text | q:no-artifact |
```

Last cell (the counter-observed value per `corrections()` in count-c1.py: `cols[-1]`):
**`q:no-artifact`**.

## Step 1 — base statement line

`git show 2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d:SCORECARD.md`, line 823 (inside the
round-19 C1 "sourced" cell):

```
before `required=3 found=0 verified=0 missing=3` exit 1; after
```

The row's `statement token` cell `` `required=3 found=0 verified=0 missing=3` `` occurs verbatim
on this line inside backticks — extraction target located exactly where the row claims.

sid well-formedness (sid = `<file>:<class>:<line-sha256[:10]>:<index>` per `extract()`):
- sha256 of the line text (newline-stripped) = `0ccd533544244c84a6aa67d78f710822f1585edfbfc9b525803f84a3535c5d3f`
  → 10-char prefix `0ccd533544` ✔ matches sid field.
- index `:0` ✔ — the line's only qualifying Q span is that one backticked span (Q scan `kq=0`;
  the second half of the sentence, `` `required=3 found=3 ...` `` on line 824, is the *next* line's
  statement and a separate row). Span qualifies: 39 chars (6–200), contains digits, contains
  `=`, does not start with a command prefix.

## Step 2 — writing revision W

`git blame --line-porcelain 2aa46e24… -- SCORECARD.md`, line 823:

```
7229fa95eb122310e9e5334ad799ee3006293ebd 823 823
summary round-19: citation provenance, install-tree pin, r18 defect corrections
committer-time 1792564487  (2026-10-21 03:34:47 -03:00)
```

W = `7229fa95eb122310e9e5334ad799ee3006293ebd`, prefix `7229fa95` = the row's `W` cell ✔.
W is a strict ancestor of BASE (`git merge-base --is-ancestor` → true).

Note on the assignment wording "confirm W's prefix matches the sid": the sid field is the
*line-hash* prefix (`0ccd533544`), not W's commit prefix — confirmed by reading `extract()` in
`.ufo/waves/round-29/count-c1.py` (`sid = f"{fname}:{cls}:{lsha}:{k}"` where `lsha` is the
sha256 of the line text). W's prefix `7229fa95` correctly appears in the row's dedicated `W`
column, and the sid's `0ccd533544` is verified as the line hash. No defect; terminology caveat
only.

## Step 3 — Q rule applied by hand at W

Q rule (count-c1.py docstring + `check()`): the backticked span must occur verbatim in at least
one blob of the tree at W, excluding SCORECARD.md, SHONEN.md, LOG.md, corpus/**; else the
statement is false with observed `q:no-artifact`.

Counter-equivalent hand check:

```
$ git --no-replace-objects grep -F -q -e 'required=3 found=0 verified=0 missing=3' \
    7229fa95eb122310e9e5334ad799ee3006293ebd -- . ':(exclude)SCORECARD.md' \
    ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'
exit 1            # zero hits → check fails → observed "q:no-artifact"
```

Cross-checks:
- Unrestricted at W: the span occurs ONLY in `W:SCORECARD.md:823` (the claim itself) — the
  exclusion of SCORECARD.md removes the sole occurrence.
- At BASE the span exists in several round-19/20 `.ufo/waves/.../build/` files — all committed
  *after* W, so they do not help it at W (row's cause text is accurate).
- Hand-derived observed value = **`q:no-artifact`**.

## Step 4 — row's last cell vs observed

Row last cell `q:no-artifact` == hand-derived `q:no-artifact` ✔ — the correction row carries the
exact string the counter would print, matching the `valid_corrections` criterion
(`obs != mism[sid]` → false-row if mismatched).

## Findings

- **None.** Row 6 is a confirmed-false Q statement, validly corrected. sid decomposition, line
  location, blame-derived W, excluded-artifact scan at W, and last-cell observed value all check
  out independently of the counter.
- Caveat (no defect): the sid's hex field is the statement *line hash*, not W's commit hash; the
  row's W column carries `7229fa95` correctly.

## Verification gaps

- Zero-hit at W established by `git grep -F` on the committed tree (byte-exact substring over all
  blobs minus the four exclusions) — the same operation the counter performs; not a proxy.
- I did not re-verify the other 10 rows, append-only, or the counter's sha256 (out of scope for
  this item; covered by sibling seats).
