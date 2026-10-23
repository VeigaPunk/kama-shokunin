# ConfirmM04 — SCORECARD.md:Q:4f8083e30a:0

## Verdict: `confirmed-false`

The counter's observed value `q:no-artifact` is correct under the frozen class-Q rule; the
base statement was false at the revision that wrote it. Independently established without
running or trusting the counter (rule applied by hand from the frozen docstring; the counter
script was read only to quote its regexes, never executed).

## Statement and W

- Line 211 of SCORECARD.md at base 2aa46e24 (sha256 of the line = `4f8083e30a…`, matching the
  sid; exactly one Q token on the line, index 0 — the other backticked span starts with
  `bash`, a command, so it is not a Q token).
- Token: `` `rows=50 resolved=48 terminal=2 unresolved=0` ``.
- W = `40660352d4a9eb00a5d6195f0f064f5c64618143` ("round-10: post-review fixes",
  2026-10-19), named by `git blame -L 211,211 --line-porcelain 2aa46e24 -- SCORECARD.md`;
  agrees with the W recorded in the base receipt.

## Hand-applied class-Q rule

Rule (docstring): the span must occur verbatim in at least one blob of the tree at W other
than SCORECARD.md, SHONEN.md, LOG.md and corpus/**.

- `git grep -F` at W with exactly those exclusions: **no match** (exit 1) → the statement
  does not hold at W → `q:no-artifact` is the correct observed value.
- Without exclusions, the W tree contains the span in exactly two blobs: SCORECARD.md:211
  (the statement itself) and corpus/lessons/round-10.md:148 (excluded surface).

## Intended referent and cause

The quote is the stdout of `bash .ufo/round-10/audit/validate-new-pointers.sh` (round-10
new-pointer validator). The measurement was real and internally consistent at W:

- The script exists at W and prints exactly this format (`printf 'rows=%s resolved=%s
  terminal=%s unresolved=%s\n' …`).
- The committed ledger `.ufo/round-10/audit/stale-anchors.tsv` at W has exactly 50 data rows
  and exactly two terminal entries — A17 (`none — dead surface`) and A51 (`UNDECIDABLE …`) —
  matching `rows=50 terminal=2` and the line's parenthetical.
- The run record was committed at W in `corpus/lessons/round-10.md:148` (fenced block with
  the two `terminal` rows and the totals line) and is quoted in the fleet report
  `/home/vgpnk/Projects/shokunin/.ufo/reports/round-10/kama.md:120` ("Output at `4066035`"),
  which is outside the lane tree.

So the falsity is an evidence-surface failure, not an invented measurement: the only
W-committed lane copy of the output lives under `corpus/**`, which class Q excludes by
design (committed evidence outside corpus). No allowed blob carried the span until
round-11 advice files at `3285cdf` (2026-10-20).

The tip correction row (HEAD SCORECARD.md:1457) records observed value `q:no-artifact` for
this sid, matching the receipt. One wording nit, not a defect: its cause cell says "no
committed file at W holds this text", while `corpus/lessons/round-10.md:148` at W does hold
it — the row is valid because the last cell is what the counter checks.

## Files

- `verdict.json` — machine-readable verdict, commands with exact outputs, referent, cause.
- `REPORT.md` — this file.
- Advice copy: `.ufo/waves/round-29/w1/advice/ConfirmM04.md`.

No tools were installed (none needed). No writes outside the two bound paths. No git/jj
writes; no processes left running; no llama-server started.
