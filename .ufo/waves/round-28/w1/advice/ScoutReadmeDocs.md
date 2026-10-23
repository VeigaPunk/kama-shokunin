# ScoutReadmeDocs

Doc/code check only. No llama-server was started. No packages installed.

Compared `tools/server/README.md` at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (`/fast/scratch/hyaku/kama-r28/llama.cpp`) with the pinned `server-schema.cpp` snapshot. Full table, quotes, and both line numbers: `.ufo/waves/round-28/w1/out/ScoutReadmeDocs/readme-vs-schema.md`.

## What the code does

`set_limits` clamps (`server-schema.cpp` 538-539). `set_hard_limits` rejects with `Value must be between A <= value <= B` (`server-schema.h` 52-62, `server-schema.cpp` 540-543). The README never says clamp and never says 400 for these fields.

Live calls: 8 clamp, 14 reject. Three more (`speculative.n_max` 201, `speculative.n_min` 205, `speculative.p_min` 209) sit in `#if 0` (198-227) and are not request fields. `typical_p` line 113 is a commented `set_limits`, not a call. `n_probs`, `top_n_sigma`, dynatemp, the penalty floats, `dry_base`, mirostat tau/eta, and `seed` have no limit call.

## Disagreements (README vs the call)

- `temperature` schema 117 clamps to `[0, +inf]`. README 588 says a negative temperature is still the sampling temperature. Anthropic README 1646 says "0-1 (default: 1.0)"; the converter copies the value through and does not inject 1.0 (`server-chat.cpp` 593-595), so values above 1 are kept.
- `xtc_threshold` schema 109 clamps to `[0, 1]`; desc and POST 570 say above 0.5 disables XTC. CLI 133 says "1.0 = disabled".
- `adaptive_target` schema 168 clamps only the top at 1.0 and accepts negatives down to `-FLT_MAX`. CLI 144 says "valid range 0.0 to 1.0". No POST option.
- `t_max_predict_ms` schema 75 rejects below -1. POST 592 says default `0`, disabled. The stored default is `-1` (`server-task.h` 69). The timer runs only when the value is positive (`server-context.cpp` 2085), so 0 and -1 both disable it, but 0 is not the default.
- `reasoning_budget_tokens` schema 336-337: hard `[-1, INT32_MAX]`, desc "(-1 = disabled)". CLI 238 (`--reasoning-budget`, not the request name) says "-1 for unrestricted". `common.h` 292 matches the schema desc. `sampling.cpp` 315 skips the sampler when the value is negative unless `grammar_lazy` or `reasoning_control`, and line 321 then passes `INT_MAX`. README states only "unrestricted". No POST option.

## Silent, not contradictory

Sentinels that match the schema desc, with no reject/clamp words: `sse_ping_interval` (-1), `n_keep` (-1), `repeat_last_n` (0), `dry_penalty_last_n` (0), `n_cache_reuse` (0), `top_k` / `top_p` / `min_p` / `xtc_probability` on the CLI rows only. `mirostat` names 0, 1, 2, which is the clamp interval, and does not say other values are clamped rather than rejected.

`adaptive_decay` is the only exact numeric match: CLI 145 "0.0 to 0.99" equals schema 172 `set_hard_limits(0.0f, 0.99f)`. README does not say that out-of-range is a 400. No POST option.

`n_discard` (schema 59, hard `[0, INT32_MAX]`, desc "0 = half context") has no option prose. It appears only as `"n_discard": 0` in examples at README 885, 1028, 1093.

`n_cmpl` schema 63 is hard `[1, params_base.n_parallel]`. POST 539 gives no default and no cap. `common.h` 462 initializes `n_parallel` to 1; `server.cpp` 169-172 rewrites a negative value to 4 at startup. README CLI 177 only says `--parallel` default -1 means auto.

## Confidence and gaps

High on the line numbers that were read from those two files and from `server-schema.h`, `server-task.h`, `server.cpp`, `server-chat.cpp`, `common.h`, `arg.cpp`, and `sampling.cpp` at the same checkout. This seat did not POST to llama-server, so it does not say what `generation_settings` stores after a clamp. OpenAI's own docs, only linked from README 1320 and 1351, were not fetched.
