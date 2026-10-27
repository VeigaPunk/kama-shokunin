# R10CliContract — Round 58 CLI compatibility

## Finding — observable summary line changed

The new checker accepts `--repo`, `--tip`, and optional `--out`, and I exercised all three; invalid tip still exits 2 with `could-not-evaluate: invalid tip`. On the genuine build tip, both old and new checkers exit 0. However, the old summary line is:

`present=1 roster_match=1 kills=1 controls=2 met=True`

while the new line is:

`present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True`

Thus the CLI flags and exit classes are compatible, but the promised unchanged summary-line shape is not. A consumer matching the complete legacy summary will fail to parse the new line. This is an actionable compatibility break if downstream consumers use exact/anchored output parsing; no such live caller was verified.

## Caller inventory

A committed-tree literal search at `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a` found lane references naming the old checker in `SCORECARD.md`, `LOG.md`, `corpus/SOURCES.md`, `corpus/lessons/round-56.md`, `corpus/lessons/round-57.md`, `corpus/lessons/round-57-verifier-spotcheck.md`, historical wave reports/receipts under `.ufo/waves/round-56/` and `.ufo/waves/round-57/`, and the new checker's own replacement docstring. These references mostly document historical evidence or command examples, not demonstrated automated downstream invocations. `SCORECARD.md` Round 57 command is a concrete human-run example; no script caller was established by the literal inventory.

## Verification evidence

Command: `python3` invocation of each checker with `--repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a`, then again with `--out /fast/scratch/hyaku/kama-r58/R10CliContract/out`: both returned exit 0. Old stdout: `tip=...\npresent=1 roster_match=1 kills=1 controls=2 met=True\n`; new stdout includes added `executed=1 legs=3/3 mutant_assert=1` fields. Invalid-tip invocation for each returned exit 2 and stdout `could-not-evaluate: invalid tip\n`. No exit-1 CLI case was run. Literal caller inventory command searched tracked committed blobs for `round56-prereg-check.py`; results summarized above. No live LSP device was available, so caller inventory is textual evidence only, not semantic proof.
