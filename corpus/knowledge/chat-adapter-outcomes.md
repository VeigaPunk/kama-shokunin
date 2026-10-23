# The chat-completions adapter: what it maps, refuses, and drops

source: S180-S192 (llama.cpp b11755 `tools/server/server-common.cpp` and `server-schema.cpp` @ 704366d76, opened 2026-10-23)
verified-at: 2026-10-23, lane fixture (llama-server `b6a31a8e…d804`, `stories260K.gguf` `270cba1b…256d`, default argv, `n_slots` 4), live rows in `registry/chat-param-outcomes-r31.json`
recheck: on release (a new llama.cpp build; the pinned lines are the recheck anchor)

`POST /v1/chat/completions` is a conversion layer over the same task parameters
the native `/completion` endpoint uses, so the question a client faces is not
"which fields exist" but "what did the adapter do with the field I sent".
That question has four answerable forms on this fixture, each measured once per
parameter and re-derived by `.ufo/waves/round-31/count-c1.py`:

| Form | What it means | How it was observed |
|---|---|---|
| reject | the request is refused before inference | HTTP status plus an `error` object with exactly `code`, `message`, `type` |
| slot | the value reaches the stored task parameters, sometimes under another key | the newest `/slots` entry's `params` |
| ignored | no observable change | zero delta on the full `params` object and an unchanged normalized response |
| response | the OpenAI-compatible response contract changes | `choices` length, `logprobs` presence, SSE framing, SSE usage frame |

## What the layer does

- **Aliases resolve through the schema, not the adapter.** `max_tokens` is
  declared as an alias of `n_predict` (`server-schema.cpp:47`) and `n` as the
  fallback alias of the multiple-completion count (`server-schema.cpp:64`). A
  chat body that sends `max_tokens: 3` is stored as both `max_tokens = 3` and
  `n_predict = 3`; `max_completion_tokens: 3` reaches the same pair through the
  adapter's property copy (`server-common.cpp:1530`). Treat the two stored keys
  as one budget, not two.
- **`logprobs` is a mapping, not a boolean effect.** With `logprobs: true` the
  adapter sets `n_probs` to `top_logprobs` or 20 when that field is absent
  (`server-common.cpp:1519`). `top_logprobs` alone is refused
  (`server-common.cpp:1521`).
- **Validation lives in the adapter and the messages are its own.**
  `messages` must be an array (`:1390`); every non-assistant message needs
  `content` (`:1395`); an assistant message needs `content` or `tool_calls`
  (`:1399`); `content` must be a string or an array (`:1411`);
  `response_format.type` must be `text` or `json_object` (`:1375`); a request
  carrying both `json_schema` and `grammar` raises a **500 `server_error`**, not
  a 400 (`:1360`). The status and the error `type` are decided by the HTTP
  layer's exception mapping, so the same adapter exception class can surface as
  either code: read the message and type together, never the status alone.
- **Undeclared OpenAI-standard keys are copied and then pruned.** The adapter
  copies every remaining key into the task parameters (`:1530`); the schema then
  keeps only what it declares. `user`, `parallel_tool_calls` and `tools` (with
  the lane's default argv and no tool-capable template effect) produced no
  stored change and no response change, while `stream` and `stream_options` did
  change the response contract. Absence from the schema predicts "no generation
  effect" but does not by itself prove it: the adapter reads several keys
  (`parallel_tool_calls`, `add_generation_prompt`, `chat_template_kwargs`)
  before the copy loop, so a no-op needs the live observation.

## Limits

- One request per parameter on one build, model and argv: a row is one observed
  point, not the parameter's response function.
- A `slot` value is what the server stored for that task, not proof the sampler
  used it; a grammar carried in the chat session never appears in `/slots`, so
  "no slot delta" does not exclude a template or grammar effect.
- The counter's normalization (`top_keys`, `n_choices`, `choice_keys`,
  `has_logprobs`, `usage_keys`, `prompt_tokens`) cannot see effects outside
  those fields; the round-31 falsify wave demonstrated two ways a row can be
  counted while proving nothing (a mapping whose stored value equals the base's,
  and an `ignored` claim on a field the session layer consumes). Those are
  counter defects recorded in `corpus/lessons/round-31.md`, not evidence for the
  rows involved.
