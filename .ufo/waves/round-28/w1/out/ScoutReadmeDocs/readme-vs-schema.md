# README vs server-schema limits (704366d76)

Sources, both at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`:

- README: `/fast/scratch/hyaku/kama-r28/llama.cpp/tools/server/README.md` (`git rev-parse HEAD` equals that commit).
- Schema: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp` (same text as the tree's `tools/server/server-schema.cpp`).

Enforcement, not the README: `field_num::set_limits` stores inclusive bounds and **clamps** (`server-schema.cpp` 538-539: `val = std::max(min, std::min(max, ...))`). `set_hard_limits` sets the same bounds and `is_hard_limit = true` (`server-schema.h` 52-62), then **throws** `Value must be between A <= value <= B, but got ...` (`server-schema.cpp` 540-543). `handle_with_catch` (518-522) prefixes that text with the field name. The README never uses the word clamp, and it never says an out-of-range request field returns 400.

`INT32_MAX` below is the C constant on the call (2147483647). Float calls are marked `f`.

Commented-out and therefore **not** a limit: `typical_p` line 113 (`// ->set_limits(0.0f, 1.0f)`). README still documents it (POST 548, CLI 134) with default `1.0` / `1.0 = disabled` and no range. Numeric fields with neither call (`top_n_sigma`, `dynatemp_range`, `dynatemp_exponent`, `repeat_penalty`, `frequency_penalty`, `presence_penalty`, `dry_multiplier`, `dry_base`, `mirostat_tau`, `mirostat_eta`, `seed`, `n_probs`) are out of this table. `dry_base` rewrites values below 1.0 in its own handler (schema 143-146); that is not `set_limits`.

## Table

| field | enforce | schema lines | bounds | README lines | flag |
| --- | --- | --- | --- | --- | --- |
| sse_ping_interval | reject | decl 40, call 41 | -1 .. INT32_MAX | POST 606; CLI 221 | sentinel agrees; silent on reject |
| n_predict | reject | decl 44, call 45, aliases 46-47 | -1 .. INT32_MAX | POST 532; CLI 51; alias default Anth 1642 | silent on reject |
| n_indent | reject | decl 50, call 51 | 0 .. INT32_MAX | POST 534 | silent |
| n_keep | reject | decl 54, call 55 | -1 .. INT32_MAX | POST 536-537; CLI 54 | sentinel agrees; silent on reject |
| n_discard | reject | decl 58, call 59 | 0 .. INT32_MAX | samples only 885, 1028, 1093 | silent (no option prose) |
| n_cmpl | reject | decl 62, call 63 | 1 .. params_base.n_parallel | POST 539; `--parallel` CLI 177 | silent on floor and on slot cap |
| n_cache_reuse | reject | decl 67, call 68 | 0 .. INT32_MAX | POST 541; CLI 224 | silent on reject |
| t_max_predict_ms | reject | decl 74, call 75 | -1 .. int64 max | POST 592 | disagree on default |
| top_k | clamp | decl 89, call 90 | 0 .. INT32_MAX | POST 526; CLI 128; Anth 1650 | silent on clamp |
| top_p | clamp | decl 93, call 94 | 0 .. 1 f | POST 528; CLI 129; Anth 1648 | silent on clamp; Anth default differs |
| min_p | clamp | decl 97, call 98 | 0 .. 1 f | POST 530; CLI 130 | silent on clamp |
| xtc_probability | clamp | decl 104, call 105 | 0 .. 1 f | POST 568; CLI 132 | silent on clamp |
| xtc_threshold | clamp | decl 108, call 109 | 0 .. 1 f | POST 570; CLI 133 | disagree (CLI disable point) |
| temperature | clamp | decl 116, call 117 | 0 .. +inf f | POST 520; CLI 127; n_probs note 588; Anth 1646 | disagree |
| mirostat | clamp | decl 157, call 158 | 0 .. 2 | POST 572; CLI 148 | interval named; silent on clamp |
| adaptive_target | clamp | decl 167, call 168 | -FLT_MAX .. 1 f | CLI 144 only | disagree (valid range vs clamp) |
| adaptive_decay | reject | decl 171, call 172 | 0 .. 0.99 f | CLI 145 only | range agrees; silent on reject |
| repeat_last_n | reject | decl 126, call 127 | 0 .. INT32_MAX | POST 552; CLI 135 | sentinel agrees; silent on reject |
| dry_allowed_length | reject | decl 149, call 150 | 0 .. INT32_MAX | POST 562; CLI 141 | silent on reject |
| dry_penalty_last_n | reject | decl 153, call 154 | 0 .. INT32_MAX | POST 564; CLI 142 | sentinel agrees; silent on reject |
| min_keep | reject | decl 183, call 184 | 0 .. INT32_MAX | POST 590 | silent on reject |
| reasoning_budget_tokens | reject | decl 335, call 336 | -1 .. INT32_MAX | CLI 238 only (`--reasoning-budget`) | disagree on what -1 means |
| speculative.n_max | reject, dead | decl 200, call 201, inside `#if 0` 198-227 | 0 .. INT32_MAX | CLI 264 (server flag, not a request field) | dead |
| speculative.n_min | reject, dead | decl 204, call 205, same `#if 0` | 0 .. INT32_MAX | CLI 265 | dead |
| speculative.p_min | reject, dead | decl 208, call 209, same `#if 0` | 0 .. 1 f | CLI 270 | dead |

Live calls: 14 reject + 8 clamp. Three more calls sit in `#if 0` and are not registered.

## Quotes and flags

### sse_ping_interval

- Schema 41-42: `set_hard_limits(-1, INT32_MAX)`; desc says -1 disables pings.
- POST 606: "Overrides the server `--sse-ping-interval` setting for this request, `-1` disables pings. Default: server setting".
- CLI 221: "server SSE ping interval in seconds (-1 = disabled, default: 30)".
- Flag: -1 agrees. README does not say values below -1 or above `INT32_MAX` are rejected.

### n_predict

- Schema 45-48: `set_hard_limits(-1, INT32_MAX)`; aliases `max_completion_tokens`, `max_tokens`; desc includes "When 0, no tokens will be generated".
- POST 532: "When 0, no tokens will be generated but the prompt is evaluated into the cache. Default: `-1`, where `-1` is infinity."
- CLI 51: "number of tokens to predict (default: -1, -1 = infinity)".
- Anthropic 1642, for the `max_tokens` alias: "Maximum tokens to generate (default: 4096)". `server_chat_convert_anthropic_to_oai` writes 4096 when `max_tokens` is omitted (`server-chat.cpp` 585-589). That default is inside the hard interval; it is not the `/completion` default.
- Flag: silent on the hard reject of values below -1. The "may exceed the set limit slightly" note on POST 532 is about multibyte tokens, not schema validation.

### n_indent

- Schema 51: `set_hard_limits(0, INT32_MAX)`.
- POST 534: "Default: `0`". No CLI row.
- Flag: silent. No range, no reject.

### n_keep

- Schema 55-56: `set_hard_limits(-1, INT32_MAX)`; desc "Use -1 to retain all tokens from the prompt".
- POST 536-537: "By default, this value is set to `0`, meaning no tokens are kept. Use `-1` to retain all tokens from the prompt."
- CLI 54: "number of tokens to keep from the initial prompt (default: 0, -1 = all)".
- Flag: -1 agrees. README does not say values below -1 are rejected rather than clamped to -1.

### n_discard

- Schema 59-60: `set_hard_limits(0, INT32_MAX)`; desc "0 = half context".
- README has no option paragraph and no CLI flag. The name appears only as `"n_discard": 0` inside `/props` and `/slots` examples (885, 1028, 1093).
- Flag: silent.

### n_cmpl

- Schema 63-65: `set_hard_limits(1, params_base.n_parallel)`; alias `n`.
- POST 539: "Number of completions to generate from the current prompt. If input has multiple prompts, the output will have N prompts times `n_cmpl` entries." No default, no range.
- CLI 177 documents `--parallel`, not `n_cmpl`: "number of server slots (default: -1, -1 = auto)".
- The hard max is whatever `n_parallel` is when the schema runs. `common.h` 462 initializes it to 1. Startup rewrites a negative value: `server.cpp` 169-172 sets `n_parallel = 4` when `n_parallel` is negative. README never says `n_cmpl` is at least 1 or at most the slot count.
- Struct default if the field is omitted is 1 (`server-task.h` 64). README does not say that.
- Flag: silent on both ends of the hard interval.

### n_cache_reuse

- Schema 68-69: `set_hard_limits(0, INT32_MAX)`.
- POST 541: "Default: `0`, which is disabled."
- CLI 224: "min chunk size to attempt reusing from the cache via KV shifting, requires prompt caching to be enabled (default: 0)".
- Flag: silent on reject of negatives.

### t_max_predict_ms

- Schema 75-76: `set_hard_limits(-1, std::numeric_limits<int64_t>::max())`. The desc does not say 0 or -1 disables the timer.
- POST 592: "Default: `0`, which is disabled."
- Stored default is `-1`, comment "if positive, limit the generation phase to this time limit" (`server-task.h` 69). The stop check is `t_max_predict_ms > 0` (`server-context.cpp` 2085), so both 0 and -1 disable the timer. README's default of 0 is not the stored default.
- Flag: **disagree on the default**. Behavior of 0 ("disabled") matches the positive-only check. README does not say values below -1 are a 400 even though those values would also fail that check.

### top_k

- Schema 90-91: `set_limits(0, INT32_MAX)` (clamp); desc "0 = disabled".
- POST 526: "Default: `40`". Does not mention 0.
- CLI 128: "top-k sampling (default: 40, 0 = disabled)".
- Anthropic 1650: "Top-k sampling". No default, no range. The Anthropic converter copies `top_k` through (`server-chat.cpp` 593-595).
- Flag: CLI sentinel agrees with the schema desc. Silent that negative values are clamped to 0, not rejected.

### top_p

- Schema 94-95: `set_limits(0.0f, 1.0f)` (clamp); desc "1.0 = disabled".
- POST 528: "Default: `0.95`". No 1.0 note, no range.
- CLI 129: "top-p sampling (default: 0.95, 1.0 = disabled)".
- Anthropic 1648: "Nucleus sampling (default: 1.0)". The converter does not inject 1.0 when the field is absent (`server-chat.cpp` 593-595), so an omitted Anthropic `top_p` keeps the server default 0.95, not 1.0.
- Flag: silent on clamp to [0, 1]. Anthropic default disagrees with what the converter actually forwards.

### min_p

- Schema 98-99: `set_limits(0.0f, 1.0f)` (clamp); desc "0 = disabled".
- POST 530: "Default: `0.05`". No 0 note, no range.
- CLI 130: "min-p sampling (default: 0.05, 0.0 = disabled)".
- Flag: silent on clamp.

### xtc_probability

- Schema 105-106: `set_limits(0.0f, 1.0f)` (clamp); desc "0 = disabled".
- POST 568: "Default: `0.0`, which is disabled."
- CLI 132: "xtc probability (default: 0.00, 0.0 = disabled)".
- Flag: silent that values outside [0, 1] are clamped.

### xtc_threshold

- Schema 109-110: `set_limits(0.0f, 1.0f)` (clamp); desc says a threshold above 0.5 disables XTC.
- POST 570: "Default: `0.1` (> `0.5` disables XTC)". Agrees with the schema desc.
- CLI 133: "xtc threshold (default: 0.10, 1.0 = disabled)".
- Flag: **disagree**. The CLI names 1.0 as the disable point. The POST section and the schema desc name values above 0.5. 1.0 is also the clamp ceiling, so a value above 1 is stored as 1, which the desc would treat as disabled, but the disable test in the desc is not the clamp boundary.

### temperature

- Schema 117-118: `set_limits(0.0f, std::numeric_limits<float>::infinity())` (clamp); desc "0 = greedy".
- POST 520: "Default: `0.8`". No range.
- CLI 127: "temperature (default: 0.80)". No range.
- POST 588, under `n_probs`: "Note that for temperature < 0 the tokens are sampled greedily but token probabilities are still being calculated via a simple softmax of the logits without considering any other sampler settings."
- Anthropic 1646: "Sampling temperature 0-1 (default: 1.0)". The converter copies `temperature` unchanged (`server-chat.cpp` 593-595) and does not inject 1.0 when it is omitted.
- Flag: **disagree**. A request value below 0 is clamped to 0 before it is stored; the README sentence treats a negative temperature as a value that still exists at sampling time. The Anthropic "0-1" range is not what the schema enforces: values above 1 are kept, values below 0 are clamped to 0, and nothing in this path rejects them. `/v1/completions` (1320-1322) and `/v1/chat/completions` (1351) point at OpenAI's docs and do not restate a number.

### mirostat

- Schema 158-159: `set_limits(0, 2)` (clamp); desc "0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0".
- POST 572: "Default: `0`, where `0` is disabled, `1` is Mirostat, and `2` is Mirostat 2.0."
- CLI 148: "(default: 0, 0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0)". Also says Top K, Nucleus, and Locally Typical are ignored if Mirostat is used.
- Flag: the named set matches the clamp interval. README does not say a value outside 0..2 is clamped into it (3 becomes 2, -1 becomes 0) rather than rejected. This is the clamp-versus-reject ambiguity: the README states a closed set and never says which enforcement it is.

### adaptive_target

- Schema 168-169: `set_limits(-std::numeric_limits<float>::max(), 1.0f)` (clamp); desc "valid range 0.0 to 1.0; negative = disabled".
- No POST `/completion` option.
- CLI 144: "adaptive-p: select tokens near this probability (valid range 0.0 to 1.0; negative = disabled) (default: -1.00)".
- Flag: **disagree** if "valid range" is read as the accepted interval. The code accepts every negative down to `-FLT_MAX` (not clamped up to 0) and **clamps** values above 1 down to 1. It does not reject either side. The default -1.00 is inside the clamp interval. POST is silent.

### adaptive_decay

- Schema 172-173: `set_hard_limits(0.0f, 0.99f)`. The desc does not repeat the numbers.
- No POST `/completion` option.
- CLI 145: "(valid range 0.0 to 0.99) (default: 0.90)".
- Flag: the numbers match the hard bounds. README does not say an out-of-range request is a 400 rather than a clamp. POST is silent.

### repeat_last_n

- Schema 127-128: `set_hard_limits(0, INT32_MAX)`; desc "0 = disabled".
- POST 552: "Default: `64`, where `0` is disabled."
- CLI 135: "last n tokens to consider for penalize (default: 64, 0 = disabled)".
- Flag: 0 agrees. Silent on reject of negatives.

### dry_allowed_length

- Schema 150: `set_hard_limits(0, INT32_MAX)`.
- POST 562: "Default: `2`".
- CLI 141: "set allowed length for DRY sampling (default: 2)".
- Flag: silent on reject.

### dry_penalty_last_n

- Schema 154-155: `set_hard_limits(0, INT32_MAX)`; desc "0 = disabled".
- POST 564: "Default: `64`, where `0` is disabled."
- CLI 142: "set DRY penalty for the last n tokens (default: 64, 0 = disable)".
- Flag: 0 agrees. Silent on reject.

### min_keep

- Schema 184-185: `set_hard_limits(0, INT32_MAX)`; desc "If greater than 0, ...".
- POST 590: "If greater than 0, force samplers to return N possible tokens at minimum. Default: `0`".
- Flag: silent. "If greater than 0" does not say a negative is rejected.

### reasoning_budget_tokens

- Schema 336-337: `set_hard_limits(-1, INT32_MAX)`; desc "(-1 = disabled)".
- No POST `/completion` option for this name.
- CLI 238, flag `--reasoning-budget` (not the request-field name): "token budget for thinking: -1 for unrestricted, 0 for immediate end, N>0 for token budget (default: -1)".
- The CLI parser rejects values below -1 (`common/arg.cpp` 3763-3764), which matches the hard floor, but the README line does not say that.
- The two in-tree sentences disagree with each other: README "unrestricted" versus schema desc "disabled". `common.h` 292 also says "-1 = disabled, >= 0 = token budget". The sampler skips the budget sampler when the value is negative unless `grammar_lazy` or `reasoning_control` is set, and when it does build one it passes `INT_MAX` for a negative budget (`common/sampling.cpp` 315 and 321). So -1 is "disabled" on the skip path and "unrestricted" on the forced path. README states only the second.
- Flag: **disagree** on the -1 word. The hard interval itself is not stated in the README. Anthropic `thinking.budget_tokens` is copied to `thinking_budget_tokens` (`server-chat.cpp` 604-605), a different key, so that README section is not this field.

### speculative.n_max, speculative.n_min, speculative.p_min

- Schema 198-227 is `#if 0`, with the comment "we disable speculative parameter adjustments for now". The three `set_hard_limits` calls are not compiled and are not request fields.
- CLI only, as process flags: 264 "number of tokens to draft for speculative decoding (default: 3)"; 265 "minimum number of draft tokens to use for speculative decoding (default: 0)"; 270 "minimum speculative decoding probability (greedy) (default: 0.00)".
- Flag: dead schema. README is silent on them as POST fields. The CLI defaults are not a request-body contract.

## What the README never says

For every live row, the README does not say the server clamps, and it does not say the server returns 400. The only place the numeric interval in the README matches a hard call exactly is `adaptive_decay` (CLI 145 vs schema 172). The only place a README sentence describes a value the clamp erases is negative temperature (README 588 vs schema 117). The only place a README range is narrower than a soft clamp, and would be wrong if read as a reject, is `adaptive_target` (CLI 144 vs schema 168) and Anthropic temperature "0-1" (README 1646 vs schema 117).
