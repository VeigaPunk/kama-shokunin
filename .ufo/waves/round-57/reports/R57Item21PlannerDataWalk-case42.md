# R57Item21PlannerDataWalk — distinct case 42

Axes under examination: calibration and operability, as assigned. Read-only data walk; no lane source edits, no shared-file writes, no commits or installs. Tool authorization was read first (`/home/vgpnk/.omp/agent/RULES.md`); no package transactions performed.

## Observed facts

- Frozen round-57 base receipt `.ufo/waves/round-57/controls/base-c1.out` at tip `b89bdab2cc114735ec5d331c6c610134258f7864` gives `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`, exit 1. The sole detail says the calibration run `python3 -c "import glob;print(len(glob.glob('corpus/lessons/*verifier-spotcheck.md')))"` did not produce expected `42` (the command exited 0).
- Exact current canonical heading selected by `canon()` is `**Capabilities — canonical list as of round 49**` in `SCORECARD.md` (line 2844 at working read); there is no canonical round-56 heading. `canon()` in `tools/round42-selfdesc-reconcile.py:120-127` scans matching headings, selects the greatest round number, and parses subsequent table rows. The distinct `maxN` is computed from every `## Round N` heading in the whole SCORECARD at lines 167-168; `maxN=56` is consistent with the historical Round 56 section and is not a canonical-table round.
- Round-56 SCORECARD says the calibration row includes the 42-spotcheck count, and cites the round-55 admitted closure (`SCORECARD.md:3132`). The non-author closure `corpus/lessons/round-56-verifier-spotcheck.md:7-14` describes the committed round-56 report and its claims; §Routed defects lines 41-46 includes inherited report audit and other items. At the round-57 frozen tip, there are 43 `corpus/lessons/*verifier-spotcheck.md` files (independently counted by the current R41 check; its expected 42 is the sole mismatch). Thus stale expected count 42 should become 43, not a change to `maxN`.
- Exact executed reproduction: copied the frozen tip's `tools/round42-selfdesc-reconcile.py` and `tools/round41-scorecard-reconcile.py` blobs into private scratch, then ran `PYTHONDONTWRITEBYTECODE=1 python3 <scratch>/round42-selfdesc-reconcile.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip b89bdab2cc114735ec5d331c6c610134258f7864`. Output was `tip=b89bdab2cc114735ec5d331c6c610134258f7864` then `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`, detail `r41 calibration run ... no stdout line == '42' (exit 0)`, `CASE42_EXIT=1`.
- My initial execution using only the round-42 counter failed before measurement: `FileNotFoundError` for adjacent `round41-scorecard-reconcile.py` in scratch, exit 1. I then copied the dependency blob and reran successfully as above. No empty/cold server issue.
- Round-56 closure evidence: `corpus/lessons/round-56-verifier-spotcheck.md:14` explicitly records the no-op matching ROSTER fixture passing (`met=True`, exit 0), and lines 41-46 route strengthening execution-binding gates. The round-57 amendment `.ufo/waves/round-57/controls/freeze-amendment.txt` makes the stale-count calibration claim distinct from that operability no-op claim; do not conflate them. Round-57 `controls/noop-c2.out` is the separate no-op counter evidence, not a round-56 closure receipt.

## Inference and limits

Inference: minimum calibration repair is to replace the stale literal expectation `42` in the calibration evidence row/run fact with the observed outside closure count 43, preserving the canonical heading/table and historical `maxN` derivation. The actual line location should be confirmed against the target revision before editing. This report did not edit or rerun a modified counter, so it does not establish a green after-state.

The original round-57 prompt's C1/C2 order conflicts with the pre-data `freeze-amendment.txt`; amendment expressly supersedes claim ordering and is authoritative for these findings. No independent judgment of claim admissibility or axis movement is made.

## Commands and exits

1. `git -C <lane> cat-file -p b89bdab2...:tools/round42-selfdesc-reconcile.py > <scratch>/round42-selfdesc-reconcile.py` — exit 0.
2. `git -C <lane> cat-file -p b89bdab2...:tools/round41-scorecard-reconcile.py > <scratch>/round41-scorecard-reconcile.py` — exit 0.
3. `PYTHONDONTWRITEBYTECODE=1 python3 <scratch>/round42-selfdesc-reconcile.py --repo <lane> --tip b89bdab2...` — summary above; exit 1.
4. `grep -nE '^\*\*Capabilities — canonical list as of round'` on frozen SCORECARD showed headings 16,17,34,41,42,43,46,47,48,49; highest is round 49.

Report artifact: `.ufo/waves/round-57/reports/R57Item21PlannerDataWalk-case42.md`.
