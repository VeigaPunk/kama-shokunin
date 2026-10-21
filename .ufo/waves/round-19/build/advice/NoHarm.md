VERDICT: confirm - the sixth pin is inert without its flag, accepts all 11 committed receipts at their own recorded install-tree digest, and every legacy replay reproduces its recorded exit and output; the caveats below are pre-existing or process notes, not defects of the pin.

# NoHarm advice: six-pin compatibility (round 19, build)

Scope: `tests/llamacpp-live/check-receipt.py` six-pin addition against committed `live/` (r16, r17, r18) and `live-recovery/` (r18) receipts, plus legacy replays. Work copy `/tmp/kama-r19-NoHarm`; receipts, matrix and reproduce script in its `out/`. Lane not written.

## Identity (executed)
- Lane HEAD is `8bf99ca`, not the stated `1b85a24`. `git diff --stat 1b85a24 8bf99ca`: one doc file (+153), so gate and receipts are unchanged from `1b85a24`.
- The lane gate moved during the run: `tests/llamacpp-live/check-receipt.py` mtime 03:33:16 added two selftest mutations (`tree-sha-absent-expect`, `tree-sha-malformed-expect`). Snapshots tested: lane `10912f24...` (this verdict), copy `afc9e79b...`, HEAD `1dfcf23e...` (pre-pin).
- All 11 committed receipts have blobs equal to HEAD. Each has 51 install_tree entries and recorded `install_tree_sha256` `6c216313...5a2c`, which recomputes equal.

## Evidence (all commands executed; exits observed)
1. Sixth pin with the receipt's own digest, plus the four legacy pins: exit 0 on all 11, lane and copy. Wrong nibble, all-zero, or uppercase digest: exit 1. HEAD given the flag: exit 2 (argparse). `out/matrix.json`.
2. Inert without the flag: 1026 mutated receipts (key delete/null, digest tamper, consistent member swap, and others), HEAD vs lane: identical exit and stdout after masking `0x...`. The 22 raw differences were a `<object object at 0x...>` repr that both checkers print. `out/fuzz-summary.json`, `out/normalized-diff-summary.json`.
3. Pin isolation: the tree-pin message appears iff the mutated recorded digest differs from the pinned value, 1026/1026. The 33 mutants newly rejected are exactly deleted/nulled digest and consistent swap in each of the 11 receipts.
4. Legacy replays, run with lane receipt paths and the argv shape of `.ufo/waves/round-18/runs/run.py:69-78`: 11/11 exits and stdout/stderr SHA256 equal `commands.json`, wrong-probe-pin exit 1. `round-16/live/replay-captured-503.py`: exit 0, output byte-equal to the recorded `.txt`. The legacy runner passes only four pins, so I also ran four pins plus the receipt's own tree digest: exit 0 on all 11.
5. Selftests, all exit 0: HEAD (72 mutations), lane (76), frozen (39), `controls.py --selftest` (70 cases, 0 failures). The frozen pre-v3 checker rejects the six v3 receipts on schema; `run.py` applies it only to v1/v2, so this is expected and not a regression.
6. Current-host live gate (the `live-gate-i` analogue): r18 live-recovery 1-3 exit 0. r18 `live/` 1-3 exit 1 on one problem, `tool.sha256 dc036d7d... != 83eac5c0...`. The tree pin passes.

`out/reproduce.sh` covers item 1 (pins, zero and flag checks), HEAD and lane selftests, and the round-16 replay: exit 0, log in `out/reproduce.log`. Items 2-4 and the frozen selftest are in `out/matrix.json`, `out/fuzz-summary.json` and `out/normalized-diff-summary.json`; the controls selftest is in `out/controls-selftest.stdout`.

## Findings (none blocks the claim)
- [Medium, provenance] r18 `live/` is not bound to the current producer. Tool `dc036d7d` matches commit `c6dc46f`; current `83eac5c0` matches `0c75c61`. The `live/` receipts validate under their own pins only. Treat `live-recovery/` as the current-tool evidence set.
- [Medium, process] `run.py` refuses a dirty tree except `runs/` (not `run.py`) and `live-recovery/`. Simulated on the copy's `git status --porcelain`: 11 lane lines are dirty (`check-receipt.py`, `run.py`, SCORECARD, two corpus files, and untracked round-19 and registry/tools paths); a 12th, my copy's `out/`, is absent from the lane. The runner would exit 2 until these are committed. Commit the gate first so `measured_commit` names the bytes that ran.
- [Low, pre-existing in HEAD] The `MISSING = object()` sentinel repr leaks into INVALID text (22/1026 mutants), so stdout for malformed receipts is non-deterministic. Suggest rendering `<missing>`. Not changed; lane is read-only.
- [Info, trust model] A pin equal to a receipt's own digest proves compatibility, not authenticity. Authenticity needs a host-computed pin, as `run.py` does via the producer's `install_tree()` at gate time. The sixth pin binds only the combined digest; members are bound only through it.
- [Info, fail-closed] `install_tree()` hashes every depth-1 regular file in the install directory (`tools/kama-llamacpp-live.py:178-202`). Any new regular file there changes the digest and rejects every pinned receipt. Count is 51 now.

## Not run
`install-tree-grid.py`, `run.py`, the live harness, and the full `controls.py` run. These are L1-owned measurements, and no llama-server was launched. Installs or updates: none.
