# ExecVerbosityControl — C2: does `-v` change what is served?

Verdict: `-v` changes no served value on the lane fixture; it only adds log lines.
The KV-pool info block (`llama_context: n_ctx = <pool>`) first prints at `-lv 4`
(trace); the string `llama_context: n_ctx` appears earlier at `-lv 2` only as a
warning line, not as the pool value.

## Method

Fixture: `~/.local/bin/llama-server` version `0.7.0-dev (build 11755, commit
704366d76)`, model `~/.cache/kama-shokunin/models/stories260K.gguf` sha256
`270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches the
registered fixture). All servers on `127.0.0.1`, ports 47460-47469, launch form
`llama-server -m <model> --host 127.0.0.1 --port <port> --no-webui --offline
[-v] <cell args>`, one child at a time, killed, port confirmed closed before the
next run. Readiness polled via `/health` 200. Bodies fetched with Python
`urllib` (HTTP 200 for every fetch), saved raw, then compared field-by-field.

Run script: `/fast/scratch/hyaku/kama-r25a2/ExecVerbosityControl/runner.py`
(exit 0; all 6 cell runs and 10 verbosity runs finished, every run recorded
`ready=True`, `port_closed_after=True`, `exit_code=0`).

## Cell diffs: `-v` vs plain

For each cell (K1 `-c 0`, K6 `-c 1000 -np 3 --no-kv-unified`, X1
`-np 4 --no-kv-unified`) one plain run and one `-v` run; ports K1 47461/47462,
K6 47463/47464, X1 47465/47466.

| cell | /props | /slots | /v1/models |
|---|---|---|---|
| K1 | only `media_marker` differs | byte-identical JSON | only `data[0].created` differs (1 s) |
| K6 | only `media_marker` differs | byte-identical JSON | only `data[0].created` differs (1 s) |
| X1 | only `media_marker` differs | byte-identical JSON | only `data[0].created` differs (1 s) |

Served values identical across plain and `-v`:

- K1: props `default_generation_settings.n_ctx` 2048, `total_slots` 4, slots
  n_ctx `[2048, 2048, 2048, 2048]`, models meta `n_ctx_train` 2048, `n_ctx`
  2048.
- K6: n_ctx 512, total_slots 3, slots n_ctx `[512, 512, 512]`, meta
  n_ctx_train 2048, n_ctx 512.
- X1: n_ctx 2048, total_slots 4, slots n_ctx `[2048, 2048, 2048, 2048]`,
  meta n_ctx_train 2048, n_ctx 2048.

The two differing fields are volatile, not flag-dependent: `media_marker`
differs between two plain runs too (K1 on ports 47467 and 47468, both without
`-v`: markers `<__media_nktk07rlwoLZJdWG5HrvhhrhavyNtU32__>` and
`<__media_kBXQllRjvbRYdYnOR01jrbfVdofz5EED>` differ; both runs `exit_code=0`,
port closed). `created` is a unix timestamp that increments with each launch
(1792661606->1792661607 etc. across sequential runs). Both are the "timestamps
and ids that vary" this seat was told to ignore.

Log evidence (same config, `-v` adds the context block before the same
`load_model:` line):
- K1: `load_model: initializing, n_slots = 4, n_ctx_slot = 2048, kv_unified =
  'true'` present in both logs; `-v` log additionally prints
  `llama_context: n_ctx = 2048` and `n_ctx_seq = 2048`.
- K6: `n_slots = 3, n_ctx_slot = 512, kv_unified = 'false'` in both; `-v`
  log additionally prints `llama_context: n_ctx = 1536`, `n_ctx_seq = 512`.
- X1: `n_slots = 4, n_ctx_slot = 2048, kv_unified = 'false'` in both; `-v`
  log additionally prints `llama_context: n_ctx = 8192`, `n_ctx_seq = 2048`.

## Lowest verbosity that prints `llama_context: n_ctx`

Sweep on K6 args (`-c 1000 -np 3 --no-kv-unified`), port 47460, one run per
level, `-lv 1..9` and `-v`.

| -lv N | matches of `llama_context: n_ctx` | what prints |
|---|---|---|
| 1 | 0 | nothing |
| 2 | 1 | WARNING (line 4): `llama_context: n_ctx is not divisible by n_seq_max - rounding down to 1536` |
| 3 | 1 | same WARNING; info block absent (line 9) |
| 4 | 4 | WARNING + INFO block: `llama_context: n_ctx = 1536`, `n_ctx_seq = 512` (lines 117-131) |
| 5-9 | 8 | WARNING + INFO block printed twice (lines 282-296 and 818-832 at lv5; `-v` lines 284/285 and 820/821) |
| -v | 8 | same as lv5-9 |

- Lowest `-lv N` printing any line containing `llama_context: n_ctx`: **2**
  (warning about rounding, not the pool value).
- Lowest `-lv N` printing the KV-pool value block `llama_context: n_ctx = 1536`
  (and `n_ctx_seq`): **4** (trace). At the default `-lv 3` (info) it is
  absent; `-v` prints it too (same block as lv >= 5).
- This confirms the amendment-2 note ("at `-lv 3` it is absent") and adds the
  exact threshold: trace, `-lv 4`.

## Files written

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecVerbosityControl/body-diff-summary.json` — per-cell endpoint equality, diff fields, run records, sweep results with line numbers.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-25/a2-build/out/ExecVerbosityControl/endpoint-bodies/` — 18 raw bodies (K1/K6/X1 x plain/v x /props /slots /v1/models).
- This advice report.
- Scratch (not artifacts): `/fast/scratch/hyaku/kama-r25a2/ExecVerbosityControl/` runner.py, runs.json, sweep.json, all server logs.

## Notes and risks

- `sweep-v.log` and lv5-9 logs show the info block twice per run; lv4 shows it
  once. Cause not established from these logs [INFERENCE: debug-level logging
  emits a second context block for a per-slot/second allocation path]; irrelevant
  to the threshold finding.
- At sweep end and cell runs, all my ports (47460-47469) were confirmed closed
  (`ss -ltn` no match) and no child of this seat remained. One llama-server on
  port 47428 (outside my range, args `-v -c 0`) was present during this run; it
  belongs to another seat and was not touched.
- No tools installed or upgraded (curl, jq, python3 already present); no
  pacman transaction attempted.
