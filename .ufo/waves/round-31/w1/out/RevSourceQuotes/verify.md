# RevSourceQuotes — independent re-open of the C1 source rows (round 31, WAVE 1)

Pinned snapshot: `.ufo/waves/round-31/sources/llama.cpp-704366d/` @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad.
Pin integrity (my run, 2026-10-23): `sha256sum` → `server-common.cpp b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`,
`server-schema.cpp 1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` — both match SNAPSHOT.json.
Method: every line below read with `awk 'NR==n{printf "%d|%s\n", n, $0}' <file>` from the pinned bytes (a `read`-tool render of a range
elides lines, so byte-addressed awk is the instrument of record). No LSP server is attached to this bare snapshot directory (no build db);
quote verification is byte-level by design — the awk/grep outputs here are canonical evidence, not a text-grep fallback.
Claimed classes taken from the frozen measurement-seat specs `w1/items/DataA01–A18.md` (their `source` object and `Hint` line);
gates cited as `(a)–(e)` are the frozen counter docstring and `count-c1.py` lines 463–475, `schema_declares` at 269–274,
`OAI_STANDARD` at 93–96.

## server-common.cpp (all ten lines exist; contents byte-verified)

| L | verbatim line (trimmed) | cited by → claimed class | verdict |
|---|---|---|---|
| 1360 | `throw std::runtime_error("Cannot use both json_schema and grammar");` | K31-11 → reject | **SUPPORTS.** Message is static and byte-verbatim in the snapshot → passes gate (e) `reject-message-not-adapter`. `runtime_error` (not `invalid_argument`) is consistent with the hint's 500/server_error rather than a 400. |
| 1375 | `throw std::invalid_argument("response_format type must be one of \"text\" or \"json_object\", but got: " + response_type);` | K31-10 → reject | **Does NOT support a counted row.** The live message always ends with the dynamic type (`…but got: xml`); the assembled string occurs nowhere in the snapshot (`grep -c -F 'but got: xml'` = 0; sole `but got: ` occurrence is this line, with `+ response_type`). Gate (e) `reject-message-not-adapter` fires for every sent type, and (d) pins `outcome.message` to the live message byte-for-byte. The row can be honestly *observed* but can never be *counted*. K31-10 must not be relied on for `counted >= 12`. |
| 1390 | `throw std::invalid_argument("Expected 'messages' to be an array");` | K31-06 → reject | **SUPPORTS.** Static verbatim message; `messages: "hi"` reaches exactly this throw. |
| 1395 | `throw std::invalid_argument("All non-assistant messages must contain 'content'");` | K31-07 → reject | **SUPPORTS.** Static verbatim; `[{"role":"user"}]` hits it. |
| 1399 | `throw std::invalid_argument("Assistant message must contain either 'content' or 'tool_calls'!");` | K31-08 → reject | **SUPPORTS.** Static verbatim; `[{"role":"assistant"}]` hits it. |
| 1411 | `throw std::invalid_argument("Expected 'content' to be a string or an array");` | K31-09 → reject | **SUPPORTS.** Static verbatim; string/null content short-circuits at the preceding `continue`, so only `content: 42`-shaped bodies reach it. |
| 1517 | `throw std::invalid_argument("logprobs is not supported with tools + stream");` | K31-12 → reject | **SUPPORTS.** Static verbatim; requires `also = {stream: true, tools: [one function tool]}` as the hint says. |
| 1519 | `llama_params["n_probs"] = json_value(body, "top_logprobs", 20);` | K31-03 (logprobs→n_probs=20), K31-04 (top_logprobs→n_probs=3) → slot | **SUPPORTS both.** Direct rename; slot gate (e) `any(k != param)` holds (`n_probs` ≠ `logprobs`/`top_logprobs`). Nuance: schema L180 `->add_alias("logprobs")` on `n_probs` declares this mapping natively too, so the docstring's rationale "a mapping the schema does not declare for that name" is not literally true for logprobs — the counter's mechanical key≠param test still counts the rows. |
| 1521 | `throw std::invalid_argument("top_logprobs requires logprobs to be set to true");` | K31-05 → reject | **SUPPORTS.** Static verbatim; fires exactly when `top_logprobs` non-null without `logprobs`. |
| 1530 | `llama_params[item.key()] = item.value();` | K31-01, K31-02 → slot; K31-13, K31-14, K31-15 → ignored; K31-17, K31-18 → response | Split verdict per row below. |

Line 1530 (the copy-remaining-properties loop), per citing seat:

- **K31-01 / K31-02 (max_tokens / max_completion_tokens, slot): SUPPORTS jointly with schema L46/L47.** 1530 is where the OAI key enters `llama_params` under its own name; the rename to `n_predict` is the schema alias (L44 field + L46/L47 `add_alias`) applied at the task layer. The hint's "stores both" (both keys visible in slot params) is the beyond-schema part and is live-verifiable only. KQ38 note: the bare mapping *is* schema-declared, so the row's counted-ness rests on the OAI key surviving into slot params, not on the alias.
- **K31-13 (user, ignored): SUPPORTS as the only-treatment line.** Zero occurrences of `"user"` elsewhere in server-common.cpp; `schema_declares("user")` false; in `OAI_STANDARD`. 1530 shows the key's sole treatment is generic pass-through; the no-effect half of the claim is proven by the live (d) slot/response comparison, and 1530 is also the mechanism that would produce a delta if task parsing retained the key.
- **K31-14 (parallel_tool_calls, ignored): PARTIAL — do not cite 1530 alone.** The adapter consumes the key at L1426 (`inputs.parallel_tool_calls = json_value(body, "parallel_tool_calls", caps[...])`) into template inputs; "no processing" is false at the prompt layer. Only "no generation-setting slot delta + unchanged normalized response" can hold, live. Honest companion citation: L1426.
- **K31-15 (tools, ignored): PARTIAL — do not cite 1530 alone.** The adapter parses tools at L1336–L1337 (`auto tools = json_value(body, "tools", json()); auto has_tools = ...`) and gates on `has_tools` at L1516. Honest companion citations: L1336/L1337.
- **K31-17 (stream → response sse): DOES NOT SUPPORT the claimed class.** The streaming decision is read at L1338 (`auto stream = json_value(body, "stream", false);`) and realized by the response layer; 1530 merely copies `stream` into `llama_params`. The row may still be *counted* mechanically (response rows have no line-semantics gate), but citing 1530 for the SSE contract is the wrong line — cite L1338 (or the streaming response builder) instead.
- **K31-18 (stream_options → response sse_usage): DOES NOT SUPPORT the claimed class.** `include_usage` is consumed in server-task.cpp L494 (`if (include_usage) {`, preceded by the `chat.completion.chunk` assembly); 1530 shows only pass-through. Also note `stream_options` IS schema-declared (schema L26–L28 `field_nested("stream_options")` + include-usage field) — harmless for a response row, but it means an *ignored* row for stream_options would fail gate (e) `ignored-declared-in-schema`. Honest citation: server-task.cpp L494 region.

## server-schema.cpp (all five lines exist; contents byte-verified)

| L | verbatim line (trimmed) | verdict |
|---|---|---|
| 44 | `add((new field_num("n_predict", params.n_predict))` | Input-side declaration of `n_predict`; joint evidence for K31-01/K31-02's slot mapping (with L46/L47 and common L1530). Supports the input mapping only. |
| 45 | `->set_hard_limits(-1, INT32_MAX)` | **Supports NO counted row.** Pure bounds text — the canonical KQ38 CtlTypeGuess/CtlSchemaProjection trap; gate (e) requires a reject row's message to be adapter-authored, not the schema's bounds text, and no other class consumes hard limits. Rows must not cite it. |
| 46 | `->add_alias("max_completion_tokens")` | SUPPORTS K31-02's input mapping (the schema-declared alias), jointly with L44 and common L1530. |
| 47 | `->add_alias("max_tokens")` | SUPPORTS K31-01's input mapping, jointly with L44 and common L1530. |
| 64 | `->add_alias("n") // alias "n" as fallback (OpenAI completions API)` | **Insufficient as sole support for K31-16 (response, n_choices = 2).** It evidences only the input alias n→n_cmpl; the choices-array outcome is adapter response assembly (server-task.cpp builds `{"choices", json::array(...)}` at L379/L434/L464/L480/L1074/L1111). Per this seat's rule, a schema line naming a field whose observable outcome the adapter decides must not back the response claim. Mechanically countable; semantically the row needs a server-task.cpp companion citation. |

## Lines that would NOT support a row (rows must not cite them as support)

1. **schema L45** — bounds only; backs no counted class.
2. **schema L64 as sole support for K31-16** — input alias only; the n_choices outcome is decided in server-task.cpp response assembly.
3. **common L1375 for any COUNTED reject row (K31-10)** — the dynamic `+ response_type` suffix guarantees `reject-message-not-adapter` (assembled message verified absent from the snapshot). The plan must not count K31-10 toward `counted >= 12`; it is at most a prose/observational row, and if it stays in the registry as a reject row it will show as uncounted.
4. **common L1530 for K31-17 (stream/sse) and K31-18 (stream_options/sse_usage)** — wrong line for the class; honest lines are common L1338 and server-task.cpp L494 respectively.
5. **common L1530 as sole support for K31-14 and K31-15** — both keys are adapter-consumed (L1426; L1336–1337); a pass-through line cannot evidence the no-effect conclusion for them.

## Residual risk and verification gaps

- Whether slot params retain the copied keys (`max_tokens`, `user`, `parallel_tool_calls`, `tools`, `stream`, `stream_options`) is decidable only by the counter's live (d) checks; the ignored rows K31-13/14/15 live or die there, not in the source.
- K31-16's live outcome (does `n: 2` really yield `n_choices = 2` on this fixture, given `n_cmpl` fan-out with n_slots 4) is not provable from L64; the counter's live check is the authority.
- Static `schema_declares` results used here: `user`/`parallel_tool_calls`/`tools` = 0 occurrences (ignorable), `stream` (L23), `stream_options` (L26–28), `json_schema` (L252 + alias grammar L253), `logprobs` (L180 alias on n_probs), `n_probs` (L179) all declared.
- Class mapping assumed from the frozen DataA item specs; if the landing registry reassigns source rows or lines, re-run this verification against the actual registry.
