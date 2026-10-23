# RevChatSource — chat-adapter source vs the planned rows (round 31, C1 falsification)

Surface read: `oaicompat_chat_params_parse` end to end at 704366d
(`.ufo/waves/round-31/sources/llama.cpp-704366d/server-common.cpp:1326-1540`), cross-checked
against the pinned `server-schema.cpp`, `server-task.cpp` snapshots and the frozen
`count-c1.py` bytes (rules (b)-(e), `schema_declares`, `render`, live checks).
Line numbers below are pinned-snapshot lines. Handler-level facts: the call site of
`oaicompat_chat_params_parse` and the exception→error-type catch arms live in **unpinned**
`server-http.cpp:921-924` (`invalid_argument → ERROR_TYPE_INVALID_REQUEST`, other
`std::exception → ERROR_TYPE_SERVER`); only the type→code/type-string table is pinned
(`server-common.cpp:93-130`). Consequence used throughout: **reject rows are class- and
message-predictable from source, but their exact HTTP status/type are live-decided.**

## 1. Planned rows: what source alone predicts vs what needs the live run

| planned row | pinned evidence | source-predicted outcome | live required? |
|---|---|---|---|
| max_tokens (alias) | schema `field_num("n_predict")` `add_alias("max_tokens")` (server-schema.cpp:44-48); chat passthrough with `n_predict` precedence (server-common.cpp:1526-1531) | `slot` `{"n_predict": <sent>}` — alias declared in the pinned schema | counter rule (d) always runs live; live is **confirmatory**, not deciding |
| logprobs | `llama_params["n_probs"] = json_value(body,"top_logprobs",20)` (server-common.cpp:1519); schema alias `logprobs`→`n_probs` (server-schema.cpp:179-181); response fills `choice["logprobs"]` when probs non-empty (server-task.cpp:425-428) | `slot` `{"n_probs": 20}` (also `response has_logprobs=true` available) — both source-predicted | live pins the stored value (20 vs sent `top_logprobs`) |
| top_logprobs (without logprobs) | server-common.cpp:1521 `throw std::invalid_argument("top_logprobs requires logprobs to be set to true")` | `reject`, message pinned verbatim | **yes — status/type live-decided** (unpinned catch arm) |
| `user` | passthrough loop copies it (server-common.cpp:1528-1531); schema parse is pull-based over declared fields only (`eval_llama_cmpl_schema` loops `f->eval(ctx,data)`, server-schema.cpp:493-500); no `user` field | `ignored` (no slot delta, normalized response unchanged) | live required by (d); class predictable |
| `parallel_tool_calls` | read into template inputs only (server-common.cpp:1426), no schema field → never eval'd | `ignored` on the no-`--jinja` default argv | live required by (d); class predictable |
| `tools` | `throw std::runtime_error("tools param requires --jinja flag")` (server-common.cpp:1343), default argv has no `--jinja` | `reject`, message pinned | **status/type live-decided** |
| `n` | schema `field_num("n_cmpl")` `add_alias("n")` (server-schema.cpp:62-65); chat formatter emits **exactly one** choice (server-task.cpp:433-441 `json::array({choice})`; stream deltas 463-487) | `slot` `{"n_cmpl": <sent>}`; a `response n_choices=2` row would fail live | live decides slot vs an unpinned-handler guard (no `oaicompat_chat_params_parse` call site in the snapshot) |
| `stream` | schema `field_bool("stream")` (server-schema.cpp:23); SSE transport framing is in unpinned `server-http.cpp` | `response` (`sse=true`); a `slot` row is impossible — key `stream == param` fails (e); an `ignored` row fails (e) via schema declaration | live pins the check value |
| `stream_options` | `field_nested("stream_options")` → subfield `include_usage` (server-schema.cpp:26-29); usage-only final chunk (server-task.cpp:494-505) | `slot` `{"include_usage": true}` and/or `response sse_usage=true` — both source-predicted; only one outcome kind per row | live decides/pins the value |
| four adapter rejections | messages pinned verbatim: 1343 (tools), 1346 (tool_choice), 1360 (json_schema+grammar), 1521 (top_logprobs) — see the reachability finding below | `reject` class + exact message source-predicted | **status/type live-decided for every reject row** |
| json_schema+grammar (status class) | server-common.cpp:1360 `throw std::runtime_error("Cannot use both json_schema and grammar")` | `reject`, message pinned; pinned bytes alone cannot give the status (needs the unpinned runtime_error arm → 500/`server_error`) | **yes — exactly the "(status class)" gap the plan flagged** |

## 2. Candidate rows the source suggests that the plan does not have

1. `tool_choice: "required"` → `reject "tool_choice param requires --jinja flag"`
   (server-common.cpp:1346). Decider: HTTP status + error envelope.
2. `top_logprobs: 5` alone → `reject "top_logprobs requires logprobs to be set to true"`
   (1521), if the plan's logprobs/top_logprobs row does not already cover it. Decider:
   status + envelope. Passes (e): message is in server-common.cpp.
3. `metadata` / `store` / `service_tier` → `ignored`: OAI_STANDARD, not schema-declared,
   passthrough then never eval'd. Decider: newest slot `params` key-set and values equal to
   base + normalized response equal to base.
4. `max_completion_tokens` → `slot {"n_predict": v}` via `add_alias` (server-schema.cpp:46) —
   distinct param, distinct S### anchor, same mapping as max_tokens.
5. `response_format {"type":"json_object"}` → schema converted to grammar in the chat parse
   (server-common.cpp:1364-1382), session-owned grammar with `grammar`/`json_schema` erased
   from llama_params (1534-1540) — observable only as a slot `grammar` delta whose exact GBNF
   string **cannot be written from source**; requires a live look at `/slots` before the
   registry entry exists.

Source-suggested non-rows (must NOT become counted rows): `stop` (slot key == param → fails
(e) `slot-not-a-mapping`; normalization at server-common.cpp:1350-1355); `echo` (session echo
~1452 — invisible to the four response checks and to slot params, logit_bias rule);
`reasoning_budget_tokens`/`thinking_budget_tokens` (gated on `thinking_end_tags()` non-empty,
~1455-1475; stories260K has no thinking tags → no-op) `[INFERENCE: model template not read]`.

## 3. Planned rows predicted to FAIL the counter

1. **Unreachable rejections on the pinned default argv (no `--jinja`):** the jinja guard at
   server-common.cpp:1340-1347 throws for *any* non-empty `tools` (and any
   `tool_choice != "auto"`) **before** the later gates at 1455
   (`"Cannot use custom grammar constraints with tools."`, requires tools) and 1517
   (`"logprobs is not supported with tools + stream"`, requires tools). On this fixture those
   two messages can never be observed: a request carrying `tools` rejects at 1343 first; one
   without `tools` never reaches those branches. If either is one of "the four adapter
   rejections", its row fails live (observed status/message will be the 1343 one, or no
   rejection at all). Reachable adapter rejections are exactly: 1343, 1346, 1360, 1521.
2. Any `ignored` classification for `stream` or `stream_options` → `ignored-declared-in-schema`
   (`field_bool("stream",` server-schema.cpp:23; `field_nested("stream_options",` :26).
3. Any reject row whose trigger is a schema bounds violation (e.g. `n: 0` outside `n_cmpl`
   hard limits 1..n_parallel, `max_tokens` beyond `n_predict` hard limits −1..INT32_MAX):
   the message is schema-authored — `"Value must be between <min> <= value <= <max>, but got
   <v>"` (server-schema.cpp:543, wrapped as `Field '<name>': …` by `handle_with_catch`
   :520-523) — absent from server-common.cpp → `reject-message-not-adapter`.
4. `n` planned as `response n_choices=2` → live fail `response-value:1`
   (server-task.cpp:433-441 single-choice formatter).
5. Rationale-vs-code divergence to record, not to fix (frozen bytes win): the three alias slot
   rows (max_tokens→`n_predict` server-schema.cpp:47, logprobs→`n_probs` :180, n→`n_cmpl` :64)
   are schema-**declared** mappings, yet rule (e) counts them because its operative test is
   only "some key of `set` differs from `param`". The count-c1.py docstring's rationale —
   "a mapping the schema does not declare for that name" — and KQ38's declared-bounds
   exclusion (QUALITY.md:283) do not match the operative code for aliases. If the plan needs
   these three to reach 12, a KQ38-letter critic strike predicts `met False`; the discriminator
   for `ignored` rows (`schema_declares`) shows the stricter check exists but is not applied
   to slot rows.

Confidence: high on all pinned-source statements (line-quoted); medium on live statuses/types
(derived from the unpinned catch arm at server-http.cpp:921-924, read for orientation, not
counted as pinned evidence); the stories260K thinking-tags point is inference.
