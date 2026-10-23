# ExecBadArgs — wave-1 advice (round 26 C1 candidate rows, startup channel)

Verdict: 12 confirmed startup signatures for the unknown-flag / invalid-value fault family; all 12 counted by the frozen counter in a scratch `git archive` extract of tip a23c0e0 (`registered 12 counted 12 target 12 met True not-counted []`).

## Fixture pins (verified)
- llama-server: `~/.local/bin/llama-server`, sha256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (build 11755, commit 704366d); `--version` = `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- Model: `~/.cache/kama-shokunin/models/stories260K.gguf`, sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
- Pinned sources: `arg.cpp` sha256 `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`, `llama-context.cpp` sha256 `2a25e556cb0d16725e01ce853fb1b76da91dcb41b803ce1a6bacec89bfb94aa5` (both match count-c1.py pins).

## Confirmed rows (12) — all channel startup, model fixture, occupy_port false
Each reproduced twice on port block 47640-47643 with `timeout 30 <llama-server> -m <fixture> --host 127.0.0.1 --port <p> -t 2 <args>`; every run exited 1 (candidate 12 exited 134/SIGABRT). Each signature: verbatim in pinned source (grep -F), absent from `--help`/`--version` output (grep -F, exact bytes), absent at base 1560e4d8 in SKILL.md+corpus (`git -C <lane> grep -F -q -e '<sig>' 1560e4d8 -- SKILL.md corpus` returned 1 for all 12). Raw logs: `w1-build/out/ExecBadArgs/raw/cand01…cand12-rep{1,2}.log`.

| id | signature (bytes) | trigger args | source row | pinned location (line) | upstream URL (commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad) |
|---|---|---|---|---|---|
| R26-C1-STARTUP-UNKNOWN-FLAG | `error: invalid argument: ` (25) | `--definitely-unknown-flag` | S980 | arg.cpp:830 (`throw std::invalid_argument(string_format("error: invalid argument: %s", arg.c_str()));`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L830 |
| R26-C1-STARTUP-PARALLEL-ZERO | `error: invalid value for n_parallel` (31) | `--parallel 0` | S981 | arg.cpp:2552 (`throw std::invalid_argument("error: invalid value for n_parallel\n");`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L2552 |
| R26-C1-STARTUP-FLASH-ATTN-VALUE | `error: unknown value for --flash-attn: '` (41) | `--flash-attn bogus` | S982 | arg.cpp:1770 (`string_format("error: unknown value for --flash-attn: '%s'\n", value.c_str())`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L1770 |
| R26-C1-STARTUP-REPEAT-PENALTY-ZERO | `error: repeat-penalty must be finite and greater than 0` (57) | `--repeat-penalty 0` | S983 | arg.cpp:2101 (`throw std::runtime_error("error: repeat-penalty must be finite and greater than 0\n");`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L2101 |
| R26-C1-STARTUP-SLEEP-IDLE-ZERO | `invalid value: cannot be 0 or less than -1` (43) | `--sleep-idle-seconds 0` | S984 | arg.cpp:3855 (`throw std::invalid_argument("invalid value: cannot be 0 or less than -1");`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L3855 |
| R26-C1-STARTUP-CACHE-TYPE-K | `Unsupported cache type: ` (23) | `--cache-type-k bogus` | S985 | arg.cpp:322 (`throw std::runtime_error("Unsupported cache type: " + s);`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L322 |
| R26-C1-STARTUP-LOG-COLORS-VALUE | `error: unknown value for --log-colors: '` (41) | `--log-colors bogus` | S986 | arg.cpp:3960 (`string_format("error: unknown value for --log-colors: '%s'\n", value.c_str())`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L3960 |
| R26-C1-STARTUP-REASONING-VALUE | `error: unknown value for --reasoning: '` (39) | `--reasoning bogus` | S987 | arg.cpp:3744 (`string_format("error: unknown value for --reasoning: '%s'\n", value.c_str())`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L3744 |
| R26-C1-STARTUP-PRESENCE-PENALTY-NAN | `error: presence-penalty must be finite` (40) | `--presence-penalty nan` | S988 | arg.cpp:2113 (`throw std::runtime_error("error: presence-penalty must be finite\n");`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L2113 |
| R26-C1-STARTUP-FREQUENCY-PENALTY-INF | `error: frequency-penalty must be finite` (38) | `--frequency-penalty inf` | S989 | arg.cpp:2124 (`throw std::runtime_error("error: frequency-penalty must be finite\n");`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L2124 |
| R26-C1-STARTUP-CHECKPOINT-MIN-STEP-NEG | `checkpoint-min-step must be non-negative` (40) | `--checkpoint-min-step -1` | S990 | arg.cpp:1713 (`throw std::invalid_argument("checkpoint-min-step must be non-negative");`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/arg.cpp#L1713 |
| R26-C1-STARTUP-CTX-SIZE-NEG-ASSERT | `GGML_ASSERT(n_outputs >= 1)` (30) | `--ctx-size -5` (server aborts) | S991 | llama-context.cpp:2624 (`GGML_ASSERT(n_outputs >= 1);` inside `llama_context::graph_reserve`) | https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/src/llama-context.cpp#L2624 |

Source access date for all: 2026-10-23, fresh fetch pinned to commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; the lane snapshot is byte-identical (sha256 above). Quotes above are the located 25-word-max source lines.

## Scratch counter verification (frozen count-c1.py, extract of a23c0e0)
Patch in extract only (registry/error-signatures-r26.json with the 12 rows; SKILL.md `## Round-26 live error signatures` table rows; corpus/SOURCES.md rows S980-S991). Command and output:
```
$ flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out <scratch>/counter-receipt2.json
registered 12 counted 12 target 12 met True not-counted []
_ exit 0; baseline_sha256 7d5e2e9f7e9405c5b609855e19165e073db35fe6cf9a534e1275e65df42e7516; every row `counted: true`, all a-g checks true; observed exits: 11 rows exit 1, ctx-size row exit -6 (SIGABRT).
```
Receipts copied to `w1-build/out/ExecBadArgs/counter-receipt.json` (13-row run) and `counter-receipt2.json` (final 12-row run).

## Rejected candidates (tried, not delivered)
- `--draft 5` → `the argument has been removed. use --spec-draft-n-max or --spec-ngram-mod-n-max`: reproduced (exit 1), verbatim at arg.cpp:4456, absent at base — but clause (f) squash comparison kills it: `--help` wraps the same sentence across lines, so whitespace-stripped help equals whitespace-stripped signature. First counter run showed exactly `f_absent_from_baseline` failure for that row.
- `--repeat-last-n -1` / `--dry-penalty-last-n -1`: source literal is a format string `"error: invalid repeat-last-n = %d\n"` (arg.cpp:2086, 2159); the rendered value `-1` is not verbatim in source, so no clause-(d) signature exists.
- `--kv-overrides`, `--fit-print`, `--color`: not registered in the server build; server prints `error: invalid argument: <flag>` (the unknown-flag fault), not a value-validation message.
- `--ctx-size -5` full line `GGML_ASSERT(n_outputs >= 1) failed`: the ` failed` suffix is added by the macro expansion, not in source; used source-verbatim substring without the suffix.

## Files written (all under the lane)
- `.ufo/waves/round-26/w1-build/out/ExecBadArgs/candidates.json` (12 registry entries)
- `.ufo/waves/round-26/w1-build/out/ExecBadArgs/RUNS.txt` (every command, port, exit code; revision notes)
- `.ufo/waves/round-26/w1-build/out/ExecBadArgs/raw/cand01…cand12-rep{1,2}.log` (24 launch logs), `help.txt`, `version.txt`
- `.ufo/waves/round-26/w1-build/out/ExecBadArgs/counter-receipt.json`, `counter-receipt2.json`
- `.ufo/waves/round-26/w1-build/advice/ExecBadArgs.md` (this report)

## Risks / notes for the L1
- Unknown-flag row signature is the constant prefix `error: invalid argument: `. Under clause (g), if another seat first counts a row whose signature contains this prefix as a substring (e.g. `error: invalid argument: --foo`), this row fails `g_distinct`; if this row counts first, such sibling rows fail. Ordering decides; the counter run above is with this row alone in its family (12/12).
- Row numbers S980-S991 may collide with other seats' SOURCES rows; the integrator must merge and re-run the counter after landing (the counter is the arbiter).
- Candidate 12 is a hard abort (SIGABRT, exit 134) rather than a clean parse error; it is a genuine startup fault with a stable source-verbatim signature, but it writes a core/gdb-style tail to stderr. The 30s window and non-zero exit apply as usual.
- None of the 13 tested signatures occurs in a healthy baseline launch (baseline run of the counter itself passed `f_absent_from_baseline` for all 12 kept rows).
- No tool installed this run; no pacman transaction attempted. No credentials/session material touched. No servers left running: post-run `ss -ltn` showed 47640-47643 clear; `pgrep -af llama-server` shows no processes owned by this seat.

## Revision (coordination with ScribeSkillsRowsStartup)
All 12 registry `args` lists now begin with `-t`, `2` to match the live launches
(the frozen counter's base argv adds only -m/--host/--port). Rebuilt the scratch
extract with the patched registry and reran the counter:
`flock /fast/scratch/hyaku/kama-r26/counter.lock timeout 900 python3 .ufo/waves/round-26/count-c1.py --out counter-receipt3.json`
→ output `registered 12 counted 12 target 12 met True not-counted []`, exit 0
(receipt `counter-receipt3.json` in the out dir).
