VERDICT: confirm - all 40 four-pin replays of the five round-16/17 receipts exit 0; the 20 lane-path runs are byte-identical (sha256) to the committed round-18 records and the 20 snapshot-path runs match after path normalisation, on all four gates; the new tree pin is inert when absent. Two hazards are reported below (evidence clobber in the lane working tree; legacy tool pins do not match the current tool). Neither is a C2 regression.

# C2Legacy advice (round 19)

Axes: operability (legacy compatibility of `--expect-install-tree-sha256`); calibration (what a four-pin replay can and cannot prove).

Scope: round-16/17 receipts checked with their own four recorded pins (model, server, probe, tool), no tree pin, gate-level on stored evidence. Lane access was read-only; every run used `/tmp/kama-r19-C2Legacy` (copy). No llama-server started (`pgrep -x llama-server` exit 1). No installs.

## Result

`/usr/bin/python3 out/replay.py` → exit 0, `all_expectations_met=True` (`out/legacy-replay.txt`, `out/legacy-replay.json`).

- Four-pin replay, 5 receipts × 4 gates × 2 paths = 40 runs, all exit 0 (round-18 committed `legacy-frozen-i` / `legacy-current-i`: exit 0).
- Lane-path argv (the exact round-18 argv): stdout and stderr sha256 equal the committed record, 20/20.
- Snapshot-path runs: stdout equal after normalising the path prefix, 20/20.
- Wrong-probe control (`receipt-frozen-probe.json`, current probe pin): exit 1 on 4/4 gates, equal to committed `legacy-wrong-probe-pin` (exit 1, same stdout hash).
- Tree pin on legacy receipts (EXTRA rows): own digest → exit 0 on 5/5 for each of wt and lane-HEAD; `0`×64 → exit 1 on 5/5 each. Frozen gate rejects the flag with exit 2 (argparse), as expected for the pre-pin baseline.
- Selftests: r18 0; wt 0 (74 mutations); lane-HEAD 0 (76 mutations); frozen 0 (informational).
- Edge cases (`/usr/bin/python3 out/edge-cases.py` → exit 0, both gates): empty pin → 1; uppercase pin → 1; tree pin alone → 0; null tree digest without pin → 0; null digest with pin → 1.

Gates: frozen `ad680179…` (blob 886670df); r18 = committed blob 75ed7edb (eb78788b = 1b85a24 = 8bf99ca); wt = round-19 snapshot `afc9e79b…` (blob 06ab8d61); lane-HEAD = committed 7229fa9 `10912f24…` (blob fe53e789).

## C2 delta

- Against blob 75ed7edb: 30 changed lines, all additive (flag, `expect_tree=None` parameter, `if expect_tree is not None:` block, hex-format entry, selftest cases). With the flag absent no new branch runs (`out/gate-eb78788b-vs-worktree.diff`).
- The lane moved during this session: HEAD 8bf99ca → 7229fa9. The committed gate differs from my snapshot only by two added selftest mutations; `validate()` is identical (`out/lane-now-vs-snapshot.diff`, 15 lines). Both gates were replayed.

## Findings

1. HAZARD, act before any commit: evidence clobber in the lane working tree. `.ufo/waves/round-18/runs/commands.json` in the lane working tree has been overwritten by a partial run and is still changing: 10 records at 03:36:24 (sha b0e6c8e1…), 11 records at 03:37:49 (sha 50e70962…), measured_commit 7229fa95, names only selftests and c1-measure, zero `legacy-*` records. The committed `7229fa9` file has 32 records including all 11 legacy records (sha b8dadf30…), which is this replay's reference. `run.py` sets `records=[]` per process and rewrites `commands.json` after every command (`run.py:6,29` at 7229fa9), so any partial invocation clobbers the file. Do not commit the working-tree version; restore it from HEAD. I did not write to the lane.
2. MEDIUM, what the replay can prove: each pin is that receipt's own recorded digest (the same construction as `run.py:74-75`), so exit 0 proves gate consistency and output identity, not provenance. Independent on-disk anchors (`legacy-replay.txt`, 24/35 equal): model, server, libllama-server-impl and probe match for all five receipts; the probe of `receipt-frozen-probe.json` matches `.ufo/waves/round-16/frozen/kama-probe-before.sh`. The tool pin matches for none of them: recorded `b8c5e8d4…` (round 16) and `0efd1723…` (round 17) against on-disk `tools/kama-llamacpp-live.py` `83eac5c0…`. `git log` shows that tool last changed in `0c75c61` (round 18), and `0efd1723…` equals the round-18 frozen copy. So the legacy receipts were produced by earlier tool versions; no report may say they came from the current tool. The gate never reads the tool file, so this does not affect the C2 verdict.
3. INFO: the frozen baseline does not accept the new flag (exit 2). Tree-pinned replays must use the current gate.

## Gaps

- Live llama-server not exercised; this is a gate-level replay of stored receipts.
- Round-16 tool digest `b8c5e8d4…` was not searched for in git history; no claim is made about its origin.

## Commands and exits (cwd `/tmp/kama-r19-C2Legacy`)

- `cp -a /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/kama-r19-C2Legacy` → 0
- `cmp` lane vs copy, 12 files at session start → 0 each
- `sha256sum -c SHA256SUMS` (round-18 frozen manifest) → 0 (10 OK)
- `git -C <lane> --no-optional-locks show|rev-parse …` (read-only) → 0
- `diff -u` frozen vs snapshot gate → 1 (expected; this is the whole r18 repair, not the C2 delta)
- `git diff eb78788b -- tests/llamacpp-live/check-receipt.py` → 0, 90 lines of output (the C2 delta)
- `/usr/bin/python3 out/replay.py` → 0; `/usr/bin/python3 out/edge-cases.py` → 0
- `pgrep -x llama-server` → 1 (none, before and after)

Receipts under `/tmp/kama-r19-C2Legacy/out`: `replay.py` (sha256 5b2f8d8c…), `legacy-replay.json` (d869b7af…), `legacy-replay.txt` (be1ab4cd…), `edge-cases.py` (4658d8c8…), `edge-cases.json` (2a0f1e04…), `committed-commands-7229fa9.json`, `committed-run.py`, `gates/*.py`, and the diffs above.

Installs: none. Lane writes: this report file only.
