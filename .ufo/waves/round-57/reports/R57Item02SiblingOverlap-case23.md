# R57Item02SiblingOverlap — distinct case 23: independent counter test on mutated fixtures

Seat: `R57Item02SiblingOverlap` (connector, leaf; no subagent). Lane HEAD measured: `7b74e2f2515a6f598918488fa5144658ff29925f`. Lane advanced to `8a7f1976` during the run; the counter and round-56 checker bytes are unchanged between those tips (`git diff --stat 7b74e2f2 HEAD -- tools/round42-selfdesc-reconcile.py tools/round41-scorecard-reconcile.py tools/round56-prereg-check.py` prints nothing; only `SCORECARD.md` differs).

Method: the lane was cloned read-only into scratch (`git clone --no-hardlinks <lane>`), checked out at `7b74e2f2`, and each variant was a scratch clone with one edit committed. Before every fixture commit, `git -C <fixture> rev-parse --show-toplevel` was asserted equal to the fixture path. The round-42 counter was run as `TMPDIR=<scratch>/tmp python3 <fixture>/tools/round42-selfdesc-reconcile.py --repo <fixture> --tip HEAD` (no `--out`, so no repo write). Exit codes are the counter's own.

## Results (exact summary lines)

| variant | tip | edit (round-49 canonical block only, or none) | exit | summary line |
|---|---|---|---|---|
| base | `7b74e2f2` | none | 0 | `r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=56 met=True` |
| v1-omit49 | `355a9eb9` | `## ` heading line "canonical list as of round 49" deleted; its 11 rows left orphaned | 0 | same counts, `mismatches=0 maxN=56 met=True` |
| v1c-omit49-block | `397fddbe` | whole round-49 block deleted (heading, prose, header, separator, 11 rows; 17 lines) | 0 | same counts, `mismatches=0 maxN=56 met=True` |
| v2-badpath | `e5793fcc` | row `live-receipt-replay`, description cell: `kama-llamacpp-live/v5` → `corpus/knowledge/no-such-file-r57.md` | 0 | `mismatches=0 maxN=56 met=True` |
| v2-deadpointer | `68cd737c` | row `live-receipt-replay`, evidence cell: `.ufo/waves/round-48/c2/live/receipt-1.json` → `.ufo/waves/round-48/c2/live/receipt-missing.json` (a dead path) | 0 | `mismatches=0 maxN=56 met=True` |
| v3-wrongbind | `2fc7c0c1` | row `live-receipt-replay`, evidence cell: `tools/kama-live-replay.py` → `tools/pin-watch.py` (existing, unrelated) | 0 | `mismatches=0 maxN=56 met=True` |
| frozen base | `b89bdab2` | (lane tree at freeze base) | 1 | `r41=1 ... mismatches=1 maxN=56 met=False` + `detail: r41 calibration run ... no stdout line == '42' (exit 0)` |

Stored receipts: `.ufo/waves/round-57/w1/out/R57Item02SiblingOverlap/` (`*.round42.out`, `*.round42.err`, `fixtures.tsv`, `prereg-*.out`).

Limits of this test: fixtures are constructed from the lane's own text; the counter is the only instrument run on them, and the round-56 checker was run only on the lane tips. Mutations are single edits; this shows the counter's blind spots, not that every canonical-row defect escapes.

## What the results show

- The round-42 counter cannot distinguish a canonical round-49 table from its round-48 fallback. `canon()` takes the highest `canonical list as of round N` heading; round 48's 11 names equal round 49's, so `caps` passes after the round-49 block is removed (v1c).
- Canonical evidence pointers are not checked for existence (v2-deadpointer passes). The counter's `receipts` leg reads only sections whose headings name rounds 40 and 41; the `province` leg checks only that `tools/`/`registry/` tokens appear in `PROVINCE.md`, not that they exist or run.
- The counter never executes canonical rows: the 11 round-49 rows contain zero run facts and zero SHA-256 digests (the executed-fact machinery `run_fact`/`RUN_RE` is applied only to `## Axes` rows). v3-wrongbind shows a row can be rebound to an unrelated existing tool.

## Cleanup

Scratch fixture clones were removed after receipts were copied to the wave path, per the seat rules. The exact construction commands are reproducible from the table above and from the repo at `7b74e2f2`. No file in the lane was written; `git status --short -- tools SCORECARD.md LOG.md corpus` printed nothing for the lane.
