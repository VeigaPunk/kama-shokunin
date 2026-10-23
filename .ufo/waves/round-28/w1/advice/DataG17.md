# DataG17 — C1 data seat: cache_prompt, return_tokens, return_progress, stream_options

Lane: kama, round 28, wave 1. Claim: C1 (measured, depth). Assigned port: 48217.
Lane repo read-only; nothing tracked was modified. All outputs under
`.ufo/waves/round-28/w1/out/DataG17/` plus this file.

## Verdict

**0 countable rows from the 4 assigned fields; 4 no-row entries.**
None of the four fields can satisfy C1 at b11755. This is a measured no-change result,
not an unrun cell: every field was probed live on the pinned server.

`rows.json`: `{"rows": [], "no_rows": [stream_options, cache_prompt, return_tokens, return_progress]}`
(each no_row carries its own live status / message / response sha256 / raw body file).

## Source reading (pinned 704366d)

Snapshot `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`
(sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`; my own curl of
`https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp`
at 2026-10-23T08:34:25Z hashes identically).

| field | declaring line | construct | limits / handler |
|---|---|---|---|
| `stream_options` | 26 | `field_nested`, subfield `include_usage` (`field_bool`) at 27 | none |
| `cache_prompt` | 31 | `field_bool("cache_prompt", params.cache_prompt)` | none |
| `return_tokens` | 34 | `field_bool("return_tokens", params.return_tokens)` | none |
| `return_progress` | 37 | `field_bool("return_progress", params.return_progress)` | none |

`field_bool::eval` (line 565) does `val = data.at(n).get<bool>()` inside `handle_with_catch`,
so a non-boolean raises nlohmann `type_error.302` wrapped as
`Field '<name>': [json.exception.type_error.302] type must be boolean, but is <type>` — a 400,
but **not** the `Value must be between A <= value <= B` message C1 requires, and the field has
no bounds to cite. `field_nested::eval` (line 592) only recurses
`if (data.contains(n) && data.at(n).is_object())`; any other JSON type is silently ignored.

`task_params::to_json` in the pinned `server-task.cpp` (lines 25-140) has **no** key for
`cache_prompt`, `return_tokens`, `return_progress`, `stream_options` or `include_usage`
(`grep` over server-task.cpp matches only line 494 `if (include_usage)`, which emits the
OpenAI `usage` chunk in stream mode). So no `effective` row is possible either: the
required `generation_settings[<key>]` does not exist.

## Live evidence (my run, port 48217, pinned binary/pins from the counter)

argv exactly: `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf
--host 127.0.0.1 --port 48217`, under `timeout 900`, setsid'd; killed with
`kill -TERM -- -2575481`; `ss -ltnp` confirms 48217 closed and no server process remains.

Base request `{"prompt": "Once upon a time", "n_predict": 1}` → 200,
sha256 `ac54cfef84a0a695d8af6455958368e47f113b64fceb120db62307ebc406425b` (`resp_base.json`).
Its `generation_settings` has 49 keys; none of the four fields' names appear
(`base_has_field_keys` all false in `probe_summary.json`).

| probe (`set`) | status | message | generation_settings effect |
|---|---|---|---|
| `{"cache_prompt": 1}` | 400 | `Field 'cache_prompt': [json.exception.type_error.302] type must be boolean, but is number` | — |
| `{"cache_prompt": "true"}` | 400 | `... but is string` | — |
| `{"cache_prompt": true}` | 200 | null | identical to base (`{}` diff) |
| `{"cache_prompt": false}` | 200 | null | identical to base; only `timings.cache_n`/`prompt_n` change (0/5 vs 4/1) |
| `{"return_tokens": 1}` | 400 | `Field 'return_tokens': [json.exception.type_error.302] type must be boolean, but is number` | — |
| `{"return_tokens": "true"}` | 400 | `... but is string` | — |
| `{"return_tokens": true}` | 200 | null | identical to base; only response-level `tokens` array changes (`[432]` vs `[]`) |
| `{"return_progress": 1}` | 400 | `Field 'return_progress': [json.exception.type_error.302] type must be boolean, but is number` | — |
| `{"return_progress": "true"}` | 400 | `... but is string` | — |
| `{"return_progress": true}` | 200 | null | identical to base |
| `{"stream_options": 1}` | 200 | null | identical to base (non-object silently ignored) |
| `{"stream_options": "x"}` | 200 | null | identical to base (silently ignored) |
| `{"stream_options": {"include_usage": true}}` | 200 | null | identical to base (indexed for stream chunks only) |
| `{"stream_options": {"include_usage": 1}}` | 400 | `Field 'include_usage': [json.exception.type_error.302] type must be boolean, but is number` | — |

Raw bodies: `resp_*.json` in the same out dir; shas in `probe_summary.json` and `resp`-level
`response_sha256` in `rows.json`. `server.log` copied for pin/startup evidence.

## Structural rule for the round (source-derived, not live-verified beyond the four fields)

`field_bool` stores the sent value verbatim under strict typing, so for any boolean field the
accepted `generation_settings` value equals the value sent — C1 condition (e) (`effective` value
must differ from the value sent) can never hold. Non-boolean input 400s with a type_error, never
with bounds. Therefore **no `field_bool` and no `field_nested` field can ever supply a C1 row**;
`cache_prompt`, `return_tokens`, `return_progress`, `stream_options` (and siblings such as
`verbose`, `timings_per_token`, `stream`, `ignore_eos`, `backend_sampling`, `post_sampling_probs`)
are dead for this claim.

Countable rows can only come from `field_num` entries:
- `set_hard_limits` → `reject`, bounds are exactly the two literals (`n_predict` 45,
  `n_indent` 51, `n_keep` 55, `n_discard` 59, `n_cmpl` 63, `t_max_predict_ms` 75,
  `repeat_last_n` 127, `dry_allowed_length` 150, `dry_penalty_last_n` 154, `adaptive_decay` 172, `min_keep` 184,
  `speculative.n_max` 201, `speculative.n_min` 205, `speculative.p_min` 209,
  `reasoning_budget_tokens` 336; `sse_ping_interval` 41 and `n_cache_reuse` 68 also carry them,
  but `n_cache_reuse` is excluded by the claim — schema line numbers, source only);
- `set_limits` (soft clamp) → `effective`, provided the clamped value is reported under the same
  name in `generation_settings` (`top_k` 90 clamps to [0, INT32_MAX], `top_p` 94 and `min_p` 98
  clamp to [0,1], `xtc_probability` 105 (claim-excluded `xtc_threshold` 109 likewise),
  `temperature` 117 clamps up from negative to 0, `mirostat` 158 clamps to [0,2],
  `adaptive_target` 168 clamps to [-FLT_MAX, 1]; `typical_p` 113 has its limits commented out,
  so it never clamps). This list is a reading of the schema, not live evidence; whoever runs
  those fields must confirm status/message/value.

## Risks / blockers

- No blockers. Nothing in the four fields is countable; a wave that relies on them to reach the
  18-row target must source rows from the numeric fields listed above.
- `stream_options` subfield errors name `include_usage`, which is a different declaring line (27)
  and still not a bounds reject; registering it would also fail the counter's field/line rules.
- No tool installs or updates were performed. No pacman transactions. No subagents.

## Files

Out dir `.ufo/waves/round-28/w1/out/DataG17/`:
`rows.json`, `probe_summary.json`, `base`/`resp_*.json` (14 response bodies), `server.log`.
Scratch (`/fast/scratch/hyaku/kama-r28/w1/DataG17/`): `probe.py`, `gen_rows.py`,
`fetched-schema.cpp` (sha matches the pinned snapshot).
