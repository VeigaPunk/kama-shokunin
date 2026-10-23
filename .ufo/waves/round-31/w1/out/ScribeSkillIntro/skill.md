## Round-31 chat-completions parameter outcomes (b11755 fixture, owner: kama)

This section records one live observation per OpenAI-compatible parameter sent to `POST /v1/chat/completions`. The C1 claim is met only when the frozen counter counts at least 12 rows. Its base request is sent before each row request; the row body is the base body with `{param: sent}` applied and then `also` merged. Each counted row also needs a new `S###` source row, absent at the base revision, that cites a pinned filename, line, and commit `704366d`, and whose quoted substring is rechecked against that pinned source.

The fixture uses `~/.local/opt/llama-b11755/llama-server` (server SHA-256 `b6a31a8e…d804`) and `~/.cache/kama-shokunin/models/stories260K.gguf` (model SHA-256 `270cba1b…256d`). The default server arguments are `-m <model> --host 127.0.0.1 --port <port>`; the counter verifies server, implementation-library, and model digests against the registry and verifies the served model path through `/props`. Preregistration limits the measurement to `n_slots` 4.

The pinned llama.cpp snapshot is commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (`.ufo/waves/round-31/sources/SNAPSHOT.json`):

- `tools/server/server-common.cpp` — SHA-256 `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`
- `tools/server/server-schema.cpp` — SHA-256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
- `tools/server/server-task.cpp` — SHA-256 `4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495`
- `tools/server/server-chat.cpp` — SHA-256 `91f48e09afc5a345033866380e82db1c3ad4d18baf1cec38ffa6cddaf6a6263e`

<!-- TABLE -->

Outcome cells are rendered by the counter as follows:

- `reject` means the response status equals the recorded status and the error object has exactly `{code,message,type}`; `code` equals the status, `type` equals the recorded type, and `message` matches byte for byte. The cell form is `reject <status> <type>: <message>`.
- `slot` means HTTP 200 and every recorded `outcome.set` key/value is present in the newest slot's `params` from `/slots` (numeric values use float32 tolerance). This says what the server stored for that task; it does not prove the sampler used it. The cell form is `200, <sorted key> = <JSON value>, ...`.
- `ignored` means HTTP 200, the newest slot's entire `params` object matches the base request (same key set, float32 tolerance), and the normalized response is unchanged. Normalization compares `top_keys`, `n_choices`, `choice_keys`, `has_logprobs`, `usage_keys`, and `prompt_tokens`; it does not establish the absence of effects invisible to those observations. The cell form is `200, no slot-parameter or response change`.
- `response` means HTTP 200 and the named OpenAI-compatible response check holds. The cell form is `200, <check> = <JSON value>`.

The four response checks are `n_choices` (the length of `choices`), `has_logprobs` (`choices[0].logprobs` is not null), `sse` (the body contains at least one `data: ` line, a `data: [DONE]` line, and at least one non-DONE JSON frame), and `sse_usage` (some non-DONE frame carries a non-empty `usage` object).

Only adapter-layer outcomes that require the live measurement count; outcomes predictable from the pinned native schema's declared type or bounds are excluded. A `reject` counts only when its message occurs verbatim in pinned `server-common.cpp` (an adapter-authored message, not schema bounds text). A `slot` counts only if at least one stored key differs from the request parameter name, a mapping not declared by the schema. A `response` counts only for one of the four response-contract checks above. An `ignored` counts only when the parameter is absent from every `field_*(` and `add_alias(` declaration in pinned `server-schema.cpp` and is in the counter's frozen `OAI_STANDARD` list.

Re-derive with the frozen counter:

```sh
/usr/bin/python3 .ufo/waves/round-31/count-c1.py --lane <lane> --repo <scratch clone> --tip <full commit> --out <receipt.json>
```

The counter starts its own pinned server, sends the base and row requests, checks the live outcomes, and stops its server. These results are limited to one request per parameter on one build, model, and default argv, with `n_slots` 4: each row is one observed point, not the parameter's full response function.