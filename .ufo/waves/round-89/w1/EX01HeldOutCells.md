# EX01HeldOutCells — round-89 wave 1 (C1 held-out cells, operability)

## Scope

Held-out live cells for C1 on lane-owned b12177 router children (sha256
`ba272ee3…b362b0`), model stories260K (`270cba1b…`), free loopback ports, children in their own
session and killed by process group; no request touched 127.0.0.1:1234. For every cell I recorded
the router status BEFORE grading, then the frozen base probe B (`56174a1f`, sha256
`99dd1ab8…`), the measured probe M (`4f9eacf7`, sha256 `a4f496bb…`), both run from a cwd other
than the router's, then the frozen oracle (real `POST /v1/chat/completions`, max_tokens 2; 200 ->
MODEL_OK, 400 `model is not loaded` / 500 `failed to load` -> MODEL_UNLOADED, anything else -> no
verdict). Classes: HARM = base agreed with the oracle and M did not; FIX = M agrees and base did
not; LIMIT = both disagree; AGREE = both agree; INDETERMINATE = no oracle verdict.
Nothing tracked in the lane was edited; no tool install/upgrade was needed (no pacman, no uv).

## Commands and outputs (exit codes)

- `git -C <lane> show 56174a1f:tools/kama-probe.sh > probe-base.sh`; `git show 4f9eacf7:… > probe-M.sh`;
  `sha256sum` -> base `99dd1ab8d41bb682bb24d4747b85d1f86fb84c145c6531cd2f0201d738d54be5`,
  M `a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf`. exit 0.
- `python3 cells.py --probe-base probe-base.sh --probe-M probe-M.sh --work /fast/scratch/…/cells-work
  --out .ufo/waves/round-89/w1/out/EX01HeldOutCells` (TMPDIR=scratch) -> **exit 0**; full stdout in
  `cells.out` (receipt line numbers below), per-cell JSON incl. full `status.args` in `cells.json`,
  router logs in `logs/`. `python3 -m py_compile cells.py` exit 0.
- Probe `check` exit codes: base rc=0 on every cell; M rc=0 on its MODEL_OK rows and rc=2 on each
  MODEL_UNLOADED row (probe drift exit; `cells.json` `base.rc`/`M.rc`).

## Findings

| cell | status before | B | M | oracle | class | receipt |
|---|---|---|---|---|---|---|
| 01 last byte cut | unloaded | MODEL_OK | MODEL_UNLOADED invalid | 500 failed to load | FIX | cells.out:3 |
| 02 directory at path | unloaded | MODEL_OK | MODEL_UNLOADED invalid | 500 failed to load | FIX | cells.out:4 |
| 03 FIFO at path | unloaded | MODEL_OK | MODEL_UNLOADED invalid | POST hangs (no verdict) | INDETERMINATE | cells.out:5 |
| 03b FIFO + writer | unloaded | MODEL_OK | MODEL_UNLOADED invalid | 500 failed to load | FIX | cells.out:6 |
| 04 chmod 000 valid | unloaded | MODEL_OK | MODEL_OK autoload | 500 failed to load | LIMIT | cells.out:7 |
| 05 missing mmproj | unloaded | MODEL_OK | MODEL_UNLOADED missing | 500 failed to load | FIX | cells.out:8 |
| 06 version field = 2 | unloaded | MODEL_OK | MODEL_OK autoload | **200**, status_after loaded | AGREE | cells.out:9 |
| 07 version = 0x03000000 | unloaded | MODEL_OK | MODEL_UNLOADED invalid | 500 failed to load | FIX | cells.out:10 |
| 08 split shard 2 missing | unloaded | MODEL_OK | MODEL_OK autoload | 500 failed to load | LIMIT | cells.out:11 |
| 09a symlink -> valid | unloaded | MODEL_OK | MODEL_OK autoload | **200**, loaded | AGREE | cells.out:12 |
| 09b dangling symlink | unloaded | MODEL_OK | MODEL_UNLOADED missing | 500 failed to load | FIX | cells.out:13 |
| 10a relative path present | unloaded | MODEL_OK | MODEL_OK autoload | **200**, loaded | AGREE | cells.out:14 |
| 10b relative path absent | unloaded | MODEL_OK | MODEL_OK autoload | 500 failed to load | LIMIT | cells.out:15 |
| 03a FIFO present at startup | — | — | — | router never binds | (runtime) | cells.out:2 |

- NOTE (no harm): no HARM cell — base never agreed with the oracle on a cell M missed. Counts
  `CELLS cells=13 AGREE=3 FIX=6 INDETERMINATE=1 LIMIT=3` (cells.out:30). The six FIX cells show M's
  header checks matching the router's own 500 for a 1-byte truncation, a directory, an mmproj-missing
  preset, a byte-swapped version, and a dangling symlink; the FIFO class gets the same verdict once
  a writer lets the loader reach its own failure (03b).
- NOTE: AGREE on the three loadable variants — b12177 loads a version-2 header (patched in place)
  and a symlinked model, and a preset `model = rel.gguf` relative to the router cwd; M leaves all
  three MODEL_OK, so no false red on loadable models (cells.out:9,12,14; `cells.json` status_after
  `loaded`).
- NOTE (LIMIT, frozen undecidable rule): chmod-000 valid file — M returns MODEL_OK
  `router-unloaded-autoload` (open raises EACCES -> file_state `-`) while a real completion gets 500
  (cells.out:7). Same false-green class as the U cells, but the frozen rule explicitly keeps an
  unreadable file undecided; not a regression, worth remembering when the rule is revisited.
- NOTE (LIMIT): split-model first shard with siblings deleted — the first shard parses as `ok`, so M
  leaves MODEL_OK; the router answers 500 (cells.out:11). `llama-gguf-split --split
  --split-max-tensors 4` wrote 12 shards, only `out-00001-of-00012.gguf` kept. A split-count check
  (S584 split metadata) would close it but is outside the frozen rule.
- NOTE (LIMIT, deliberate): relative `model =` path absent in the router cwd — M leaves MODEL_OK
  (relative paths are undecidable by rule), oracle 500 (cells.out:15).
- NOTE/DEFECT in b12177, not in the probe: (a) a preset model path that is a FIFO present at startup
  blocks router startup — no listener bound in 8 s, `wchan=wait_for_partner`, `State: S (sleeping)`
  (cells.out:2; `logs/03a-fifo-at-startup.router.log`); (b) a bare FIFO completion hangs: my 12 s
  POST timed out, entry stuck `status_after=loading`, the router logged
  `request cancelled while waiting for model name=cell`, and the model instance had to be killed
  (cells.out:5; `logs/03-fifo-at-path.router.log`). The probe itself never blocked: t_M
  0.11–0.12 s on both FIFO cells (vs 0.13–0.26 s elsewhere), so "must not hang the probe" holds.
- NOTE: `status.args` for the symlink cell keeps the symlink path (`…/link.gguf`, not the target),
  and preset entries expose the model path exactly as written; `status.args[0]` is the absolute
  b12177 binary in every cell, so M's local-router gate is satisfied.
- NOTE: 03b's writer thread was still pending at POST time and joined during load (`writer_pending
  true`, `writer_joined false` before the POST, fd closed after), i.e. the 500 came from the loader,
  not from an open timeout.

## Deliverables

- `.ufo/waves/round-89/w1/out/EX01HeldOutCells/cells.py` — driver (imports helpers from
  `tools/round89-unloadable-cells.py`; no hardcoded `/tmp`; `--work` scratch).
- `.ufo/waves/round-89/w1/out/EX01HeldOutCells/cells.out` — full run receipt, exit 0.
- `.ufo/waves/round-89/w1/out/EX01HeldOutCells/cells.json` — status before/after, `status.args`,
  probe verdicts/reasons/rc/elapsed, oracle code+message, class, FIFO startup record.
- `.ufo/waves/round-89/w1/out/EX01HeldOutCells/logs/` — 14 router logs (13 cells + startup check).
- Scratch `/fast/scratch/hyaku/kama-r89/EX01HeldOutCells` removed after receipts were copied; no
  llama-server child left running (pgrep by scratch path empty).

VERDICT: holds — no held-out harm; 6 FIX vs the router's own answers, 3 AGREE on loadable models, 3 frozen-rule LIMITs, 1 INDETERMINATE caused by a b12177 FIFO-load hang (probe itself answered in 0.12 s).
