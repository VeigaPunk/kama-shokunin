## Round-31 chat-completions parameter outcomes (b11755 fixture, owner: kama)

This section records one live observation per OpenAI-compatible parameter sent to `POST /v1/chat/completions`. The C1 claim is met only when the frozen counter counts at least 12 rows. Its base request is sent before each row request; the row body is the base body with `{param: sent}` applied and then `also` merged. Each counted row also needs a new `S###` source row, absent at the base revision, that cites a pinned filename, line, and commit `704366d`, and whose quoted substring is rechecked against that pinned source.

The fixture uses `~/.local/opt/llama-b11755/llama-server` (server SHA-256 `b6a31a8e…d804`) and `~/.cache/kama-shokunin/models/stories260K.gguf` (model SHA-256 `270cba1b…256d`). The default server arguments are `-m <model> --host 127.0.0.1 --port <port>`; the counter verifies server, implementation-library, and model digests against the registry and verifies the served model path through `/props`. Preregistration limits the measurement to `n_slots` 4.

The pinned llama.cpp snapshot is commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (`.ufo/waves/round-31/sources/SNAPSHOT.json`):

- `tools/server/server-common.cpp` — SHA-256 `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`
- `tools/server/server-schema.cpp` — SHA-256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
- `tools/server/server-task.cpp` — SHA-256 `4c3f413b9b54d4cc0e7b5998e6979a2389f5ff716e20cb1510ca7745fa233495`
- `tools/server/server-chat.cpp` — SHA-256 `91f48e09afc5a345033866380e82db1c3ad4d18baf1cec38ffa6cddaf6a6263e`

| id | param | sent | outcome | meaning | source |
|---|---|---|---|---|---|
| K31-N01 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N02 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N03 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N04 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N05 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N06 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N07 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N08 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N09 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N10 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N11 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |
| K31-N12 | max_tokens | 1 | 200, max_tokens = 1, n_predict = 1 | Alias of the base token budget; this row asserts the value the base request already sent, not an observed parameter effect. | S189 |


Limits, in the words of the limits seat (appended, not a counter input):

# C1 outcome limits

A `reject` row establishes the measured API error contract for that request, not a model refusal: C1 checks the HTTP status and exact `{code,message,type}` envelope, while the pinned chat-parameter parser is an endpoint adapter that throws for request conditions such as unsupported tool configuration or `response_format`; the formatter maps invalid requests to code 400, but context-size errors also map to 400, so status alone does not identify the cause (`.ufo/waves/round-31/count-c1.py` docstring L24-L29; `sources/llama.cpp-704366d/server-common.cpp` L91-L132, L123-L126, L1326-L1347, L1357-L1375). A `slot` row establishes only that the measured keys and values were present in the newest slot's stored `params`; the parser builds and returns task parameters and documents a sampling-layer pass-through, but this counter does not observe whether sampling used the stored setting or changed generated behavior (`count-c1.py` docstring L30-L31; `server-common.cpp` L1496-L1510, L1524-L1543). An `ignored` row establishes equality only for the base-versus-probe request's full slot parameters and the counter's normalized response fields; it is not a general claim that a parameter has no effect, because those checks cover a bounded request/profile and selected response summary, while the parser copies remaining request properties into `llama_params` and removes session-owned keys (`count-c1.py` docstring L24-L26, L36-L39, L46-L48; `preregistration.json` L21-L26; `server-common.cpp` L1524-L1541). A `response` row establishes only its named response-contract check: `n_choices` is `len(choices)`, not a measure of answer quality, and the counter admits only four such checks; the pinned parser creates the chat session and returns parameters without a quality judgment (`count-c1.py` docstring L32-L39, L56-L57; `server-common.cpp` L1489-L1494, L1524-L1543).

## Client-facing rules
