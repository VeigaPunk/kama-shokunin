# VerifyRow02 — hand verification of correction row `SA29:SCORECARD.md:Q:f4c42debcc:2`

Seat: kama-r29-w2-VerifyRow02 (leaf, no subagents). Date: 2026-10-23.
Compliance: count-c1.py was never executed on the lane tree (or anywhere); all commands were read-only git
object reads (`show`, `blame`, `grep`, `rev-parse`, `log`) plus `wc`/`sha256sum`. No lane file, index, or jj
state touched. Scratch: `/tmp/kama-r29-w2-VerifyRow02` (created, unused — no clone needed). No tools installed
(none needed). Note on method: artifacts are prose markdown and git objects — no LSP server applies to these
files; git-object evidence is the appropriate and used method (text grep used only as a fallback over committed
blobs, never presented as semantic proof beyond the counter's own git-grep semantics).

## Verdict

**confirmed-false** — hand-derived observed value: `q:no-artifact` (exactly the correction row's last cell).

## Evidence, step by step

Repo: `/home/vgpnk/Projects/shokunin/kama-shokunin`. Base `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d`,
data commit `513eba3ba51a142c9936553e3a85918345eb5c4c`, frozen counter read at
`.ufo/waves/round-29/count-c1.py` (docstring Q rule + `check()` Q branch: `git grep -F -q` for the span at W
with `:(exclude)SCORECARD.md`, `:(exclude)SHONEN.md`, `:(exclude)LOG.md`, `:(exclude)corpus`;
fail string `q:no-artifact`).

1. **Base statement located.** `git show 2aa46e24…:SCORECARD.md` line 20 is the freshness row ending
   `… md5 `860f26ac05938cdfc1a8816eff1570b4` → `RESULT pass=24 fail=0` | round 3 |`.
   `lsha = sha256(line-20-bytes)[:10] = f4c42debcc` (computed via `sed -n 20p | tr -d '\n' | sha256sum`).
2. **sid index matches.** Enumerating line 20's backticked spans per the counter regex
   (6–200 chars, ≥1 digit, and `=` or space+{met,registered,counted,stale,observed,verified,RESULT},
   not starting with python3/python/bash/"sh "/git/node/./tools// /):
   Q#0 `snapshot=20261014T124232Z prev=20260929T043044Z rows=3 model_ok=0 drift=3 transitions=16 exit=2`;
   Q#1 `transitions=0`; Q#2 `RESULT pass=24 fail=0` (21 chars, has digits and `=`, starts "RESULT").
   The sid's trailing `:2` selects Q#2 — the token named in the correction row. Consistently, sibling row
   `SA29:SCORECARD.md:Q:f4c42debcc:0` carries the Q#0 token.
3. **Writing revision W.** `git blame -L 20,20 --line-porcelain 2aa46e24… -- SCORECARD.md` →
   `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21` (committer time 1791981983 = 2026-10-14 09:46:23 −0300,
   "round-3: re-census — derived --ufo-src, registry cut to live rows, corpus errata").
   Row's W cell `ea72c3ea` matches this prefix.
4. **Class Q rule applied by hand at W.** Counter-equivalent:
   `git --no-replace-objects grep -F -q -e 'RESULT pass=24 fail=0' ea72c3eae4ec… -- . ':(exclude)SCORECARD.md'
   ':(exclude)SHONEN.md' ':(exclude)LOG.md' ':(exclude)corpus'` → **rc=1** (no artifact).
   Unfiltered grep at W shows the span only in excluded paths: LOG.md:142,215,242; SCORECARD.md:11 (W's copy
   of the same row); SHONEN.md:12; corpus/knowledge/snapshot-history.md:66; corpus/lessons/round-2.md:49.
   ⇒ statement does not hold at W; observed = `q:no-artifact`.
   Cause-column cross-check ("a later commit does [hold it]"): first commit in `ea72c3ea..513eba3b` where a
   non-excluded path gains the span is `e246c40` (round-5, 2026-10-15 02:13:31 −0300), e.g.
   `.ufo/reports/round-5/kama.md:90` at base — after W (1791981983). Accurate.
5. **Correction row matches the observed value.** Data-commit SCORECARD.md line 1455, under heading
   `## Round 29 — self-assessment corrections` (line 1443), exactly one row for this sid (no duplicate):
   `| SA29:SCORECARD.md:Q:f4c42debcc:2 | SCORECARD.md:20 | Q | `RESULT pass=24 fail=0` | ea72c3ea |
   test-snapshot result quoted; at W no committed file held it (a later commit does) | q:no-artifact |`
   Last cell `q:no-artifact` (no backticks to strip) equals the counter's Q-fail string exactly.

## Residual risk / gaps

- `blame --line-porcelain` content-follow semantics: I used `-L 20,20` on the base blob, the same invocation
  shape the counter uses (full-file blame at BASE, `filename SCORECARD.md` header present, no rename boundary
  crossed for line 20). W agrees with the row; no gap.
- The Q check searches committed blobs at W only; I reproduced it with the same git invocation and excludes.
  Working-tree state is irrelevant to both.
- Append-only prefix property and the other 10 rows: out of this seat's scope, not checked.
