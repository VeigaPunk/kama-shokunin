VERDICT: confirm - the drafted round-21 LOG entry's numbers all trace to the recorded exits/stdout in runs/b76727f3, and 27 of 28 recorded commands re-run read-only at the measured commit reproduce those exits (26/27 stdout digests identical, the one difference being ephemeral ports); LOG.md was not edited; the lane working tree carries an uncommitted tool edit that no measurement covers.

# Scribe report — round 21 LOG entry (ScribeLog)

Attacked target: the claim set of the round-21 official measurement at `b76727f31e522763ce24e43d6ec86d21b507a11f` (C1 report-landing detector, C2 install-links pin, frontier census), as it would be written into `LOG.md`.

## Behavior
- Draft entry: `.ufo/waves/round-21/falsify/out/ScribeLog/LOG-round-21-entry.md` (round-20 entry format; bullets, measured numbers, limits).
- Re-execution table: `.ufo/waves/round-21/falsify/out/ScribeLog/rerun-check.tsv`.
- Scratch `/tmp/kama-r21-ScribeLog` (clone at b76727f + rerun outputs) removed after writing.

## Commands executed (exit observed)
- `git clone` of the lane to scratch, `git checkout b76727f…`: exit 0; `git status --porcelain` empty.
- Recorded commands re-run from the clean clone with the recipe's argv (`/usr/bin/python3`, Python 3.14.8): 27 executed, all exits equal declared exits (c1-absent-at-base 128; c1-audit-raw 1; c1-audit-ledger 0; c1-audit-selftest 0; c2-grid-frozen 1; c2-grid-both 1; c2-grid-current 0; c2-grid-selftest 0; c2-gate-selftest 0; c2-producer-selftest 0; c2-live-gate-pinned 0; c2-live-gate-wrong-links-pin 1; c2-legacy-receipt-1/2/3 0; c2-legacy-receipt-1-required 1; nh-* all 0; fr-sources-validate 0; fr-sources-census 0).
- Stdout SHA-256 identical to `commands.json` for 26/27; `c2-producer-selftest` differs only in listener ports (`::1:45229` vs `::1:35371`).
- Not re-run: `c2-live-receipt` (launches llama-server; forbidden). Its receipt was checked from the official `runs/b76727f3/live-receipt.json` via the pinned gate (exit 0) and wrong-pin gate (exit 1), both re-run.
- `commands.json`: 28 entries, `as_expected` true for all, `timed_out` false for all; 28 `.exit` files match.
- Lane checkout inspected read-only: `git status --porcelain`, `git diff --stat`, `git log`, `git rev-parse --short HEAD` (`a661714`).
- No tools installed or upgraded. Used preinstalled `jq`; no pacman, no uv, no network.

## Findings for the L1 (integration)
1. Measured tool state is the `b76727f` tree, not `a29bb84`: `git diff --stat a29bb84 b76727f -- tools tests registry` shows 5 files changed (700+/381−) after the draft commit. The LOG must cite `b76727f` for the detector's numbers. `4e75d9e`→`b76727f` changes only `.ufo/waves/round-21/build/` (5 files), so the recipe ran against the tools as they stand at `b76727f`.
2. Frontier W04 duplicate-URL warnings grew from six (round 20) to eight: S031, S043, S056, S060, S064, S065, S067, S071. S067 and S071 are new this round. `sources-validate` exit 0 still (warnings only). The lesson's Gate table does not mention this; the LOG should.
3. The ledger's "corrected 9" is bookkeeping (errata rows = defects). The LOG draft says so explicitly; a reader counting "9→0" would misread.
4. The round-21 fleet report is not in the measured recipe: the recipe runs `--rounds 10-20` only; no `--report 21=` run. The lesson's M2 cites `--report 21=` as the intended check. The LOG must not claim the round-21 report passed the audit.
5. The lesson's "9/9 hand-confirmed by build seats, 0 FP/FN" is build-seat evidence; the scribe did not re-derive those hand counts [INFERENCE: not re-derived].
6. Round-21 Landed list (for the LOG's Landed bullet): `a29bb84`, `1471344`, `4e75d9e`, `b76727f` (all by kama-shokunin, 2026-10-21, `git log 7a6bc911..b76727f`). Confirm the round-21 Landed list includes all four; the round-20 closure's "Landed omitted four commits" is the failure mode C1 polices.
7. Lane tip moved after measurement: `a661714` (round-21: official measurement at b76727f3, the commit under attack) adds only `runs/b76727f3/` (86 files) on top of `b76727f`; tools/tests/registry are identical between `b76727f` and `a661714` (`git diff --stat b76727f a661714`).
8. UNCOMMITTED lane drift (blocking for any claim beyond `b76727f`): the lane working tree at scribe time had an uncommitted edit to `tools/report-landing-audit.py` (`git diff --stat`: 15 insertions, 1 deletion) that reads the committed fleet report via `git show HEAD:` and adds a selftest case `committed-report-bytes-not-worktree`. No measured stream covers that edit. The LOG must cite the 32/32 selftest and 9-defect raw run at `b76727f` only; the edit must be committed and re-measured, or reverted, before it is claimed. Also uncommitted in the lane: `SCORECARD.md`; untracked `.ufo/waves/round-21/build/{completion-summary,verdict-count}.json` and `.ufo/waves/round-21/wave-accounting.py`. The scribe did not touch any of them.

## Out of scope / not done
- `LOG.md`, `corpus/SOURCES.md`, the lesson, `registry/`, the lane checkout and the fleet repo were not modified (read-only).
- No live server, no model download, no subagent dispatch.
- Build-seat hand recounts (C1 9/9) and the lesson's source-quote table were not re-executed.

## Artifact paths
- `.ufo/waves/round-21/falsify/out/ScribeLog/LOG-round-21-entry.md`
- `.ufo/waves/round-21/falsify/out/ScribeLog/rerun-check.tsv`
- `.ufo/waves/round-21/falsify/advice/ScribeLog.md` (this report)
