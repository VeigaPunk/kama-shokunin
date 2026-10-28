source: S526 — llama.cpp server README @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (release b11755), §POST `/v1/completions` lines 1314-1336 and §Timings and context usage lines 1428-1471, raw file sha256 714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37; own-work live receipt `kama-completion-live/v1` at `.ufo/waves/round-62/w1/out/W02KnowledgeDraft/receipt.json` (nonce `w02-r62-kn-draft-1`; tool `tools/kama-completion-live.py` sha256 71ac4f2c45570a79cb1e80db91e85268609f28bf4dd421d628ffb9d10243771f at tip 65d7cad0fce90e34de37527cde22e97b63b118bf)
verified-at: 2026-10-28 — one hold-mode run of that tip's tool on the pinned fixture (`llama-server` sha256 b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804, `stories260K.gguf` sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d, alias `kama-completion-probe`, unregistered loopback port): verdict `REQUEST_OK`, 17/17 evaluated checks passed; every response-field claim below is read from that receipt's captured bodies, not from the docs
recheck: 90d, and on any `llama-server` or model pin change — re-run `python3 tools/kama-completion-live.py --work <scratch> --hold-dir <hold> --nonce <fresh>` and require `REQUEST_OK` with `system_fingerprint` still `b11755-*`; a new build restarts this entry rather than inheriting it

# llama.cpp `/v1/completions` — the request plane

The lifecycle harness (`tools/kama-llamacpp-live.py`) proves the server *starts*
and answers inventory surfaces; this entry records what a real generation
request returns on the pinned b11755 single-model build.

## Documented contract (S526)

The README names `POST /v1/completions` as the OpenAI-compatible completions
route (heading, line 1314) and defers its options to the OpenAI Completions
API reference, making no strong compatibility claim; llama.cpp `/completion`-
specific features (e.g. `mirostat`) are supported. The shared "Timings and
context usage" example names `usage`/`timings`; the route field set is observed.

## Observed contract (receipt `kama-completion-live/v1`)

A `POST /v1/completions` carrying `{"prompt", "n_predict", "temperature": 0.0,
"seed": 7, "timings_per_token": false}` and no `model` field answers 200 with:

| Field | Observed contract |
|---|---|
| `object` | literal `"text_completion"`, not `"chat.completion"` (graded) |
| `choices[0].text` | the generated string; a string is graded, its content never |
| `choices[0].finish_reason` | `"length"` or `"stop"` (graded; `length` here at `n_predict` 8) |
| `model` | echoes the `--alias` value (`kama-completion-probe`), never the model file path |
| `system_fingerprint` | shape `b<digits>-<9-40 hex>` graded as shape only; observed `b11755-704366d76` |
| `usage.prompt_tokens` / `completion_tokens` / `total_tokens` | integers ≥1, total = prompt + completion (graded); `prompt_tokens_details.cached_tokens` present, ungraded |
| `timings.predicted_n` / `predicted_ms` | `predicted_n` an integer equal to `usage.completion_tokens`, `predicted_ms` numeric (graded); `cache_n`, `prompt_n` and the per-token rates ungraded |

Determinism at `temperature: 0.0` + fixed `seed`: two byte-identical requests returned the same `choices[0].text`; the bodies differ in `id`, `timings.cache_n`/`prompt_n` and `usage.prompt_tokens_details.cached_tokens`,
so only the text is the invariant — the check is skipped, not passed, when temperature ≠ 0.

Error surface: a request without `prompt` answers 400 with an `error` object —
`{"error":{"code":400,"message":"[json.exception.out_of_range.403] key 'prompt' not found","type":"invalid_request_error"}}` —
the tool grades status 400 or 500 plus `error` being an object, never the message text or its build-specific json-exception prefix.

## Non-invariants (never graded)

- **Text content.** Model quality is out of scope: the run grades the envelope
  and accounting only, so any non-empty completion string passes the same checks
  (v1 graded a string, and its determinism leg a non-empty one; v2 adds non-empty text to the choice-shape check for the fixed request).
- **Registered consumers.** The probe serves on an unregistered loopback port;
  consumer-facing endpoints are not contacted and their health is not sampled.
- **Timing values, ids, adapter extras (round-62 v1 reading; superseded in part by the last section).** At v1 only `predicted_n`/`predicted_ms` presence was graded; `id`, `created`, `logprobs`, `index` and `prompt_tokens_details.cached_tokens` were recorded but ungraded. At v2 those five and `cache_n`/`prompt_n` are graded as the last section states; magnitudes remain ungraded.

## Receipt integrity

Every capture records `status`, `body`, `body_sha256` and `body_truncated`
(v1: headers were not kept; v2 keeps them, plus the byte count and request bytes). The request-plane checks are `completion_envelope`,
`completion_finish_reason`, `completion_model_id`, `completion_fingerprint`,
`completion_usage`, `completion_timings`, `completion_deterministic` and
`bad_request_graded`; the same receipt binds the alias through
`listener_owned`, `models_alias_id` and `props_alias`. The round-62 counter
`tools/round62-c1-counter.py` re-hashes each body and recomputes every check
from captured bytes — a tampered field is rejected by grading, not trusted.

## Scope and open bounds

- One build, one model, one request pair: b11755 `llama-server` on
  `stories260K.gguf` with `-c 512 -t 1`. Other builds, models and contexts,
  other engines (Ollama, SGLang, vLLM) and the chat route are outside this entry.
- `stream` was not set, so this records the non-streaming JSON body only; SSE
  framing and per-token timings are not observed here.
- `PROVINCE.md` still lists `/v1/completions` as frontier at the tip (round-31
  core note line 141; round-32 note line 160). This entry records the observed
  contract; the round-62 C1 claim owns whether the capability is acquired.
- The receipt is one dated sample of the lane's own fixture, never present
  service state of a registered consumer.

## Round-63 strict response grading, schema `kama-completion-live/v2` (S527, S528)

Round 62's grader left headers, body completeness, choice shape, `id`/`created`,
timing plausibility and the request bytes ungraded (seat R01C1Gap, round 62).
Round 63 adds nine checks to `tools/kama-completion-live.py` and recomputes each
from captured bytes in `tools/round63-c1-counter.py`. The ground for each is
marked: **source** = read in the pinned b11755 files (raw bytes retained under
`.ufo/waves/round-63/source/`), **observed** = read from the live receipt only.

| Check | Asserts | Ground | Failure signature |
|---|---|---|---|
| `completion_headers` | response `Content-Type` is `application/json` (parameters ignored) | observed (`application/json; charset=utf-8`; the server's HTTP layer was not opened this round) | a `text/plain` or absent header: the body may be an error page, not the API |
| `completion_untruncated` | `body_truncated` is false and, when `Content-Length` is sent, it equals the captured byte count | observed (620 bytes in the round-63 run; the tool reads at most 65,536) | truncation flag set, or length differs: the grader saw a partial body |
| `completion_choice_shape` | exactly one choice, `index` 0 (integer, not bool), `logprobs` null, `text` non-empty | source for `index`/`logprobs` (S527 lines 366-386: `logprobs` is `null` unless probabilities were requested; one `choices[0]`); the non-empty text is **observed for this fixed request**, not a general invariant — a model may legitimately emit an empty string | two choices, `index` 1, non-null `logprobs`, or empty text on the fixed request |
| `completion_finish_reason` | `length` or `stop` | source (S527 lines 374-377: `length` unless a stop word or EOS ended it) | any other string |
| `completion_id_created` | `id` is a non-empty string; `created` is an integer above 10^9 (epoch seconds) | source (S527 lines 387 and 392: `created` is `std::time(0)`, `id` is `oaicompat_cmpl_id`); the 10^9 floor is this entry's own bound | empty id, bool or tiny `created` |
| `completion_usage` | integer token counts that sum, plus `prompt_tokens_details.cached_tokens` an integer within `prompt_tokens` | source (S527 lines 357-363) | missing detail object, `cached_tokens` above `prompt_tokens` |
| `completion_timings` | `predicted_n` equals `usage.completion_tokens`; `cache_n` and `prompt_n` non-negative integers; `predicted_ms` finite and non-negative (not a bool, not NaN/Infinity) | field names source (S528 lines 139-160); the equality with `usage` and the value bounds are observed | a missing field or a negative, boolean or non-finite number |
| `completion_prompt_tokens` | `usage.prompt_tokens` equals the length of the server's own `/tokenize` answer (`add_special` true) for the request prompt | **observed** on the pinned fixture (8 = 8 for `The cat sat on the`); no pinned source line was opened for the special-token rule, so it holds for this tokenizer only | a count that does not match the server's own tokenization of the prompt |
| `completion_request_bound` | the recorded request bytes hash to `request_sha256` and carry the prompt the tool says it sent | own-work | an altered prompt or a missing hash |

The counter also (a) re-hashes the model and server files the receipt names,
where round 62 compared only the receipt's own digest strings; (b) no longer
derives `listener_owned` from the receipt's own bit — the stored bit must be
true and the counter's own outside contact must reach a listener owned by the
receipt's child pid and port; (c) sends its own nonce prompt during the hold
window, asks the held child's `/tokenize` for the prompt it actually sent, and
requires the answer's `usage.prompt_tokens` to equal that count and its
`system_fingerprint` to equal the receipt's captured one. A canned server must
therefore predict the token count of a fresh nonce prompt, and must also be the
receipt's child process.

**Proxy.** `http_post` previously used the default `urllib` opener, which honours
`HTTP_PROXY`; it now uses the lane's proxy-free opener, the one the GET paths
already used. Measured by wave seat EX06ProxyEnv (`.ufo/waves/round-63/w1/EX06ProxyEnv.md`): with all four proxy variables set, the round-62 tool sent both POSTs to the proxy listener (verdict FAIL), the round-63 tool made 0 proxy connections (verdict REQUEST_OK, 22/22 checks).

**Not asserted.** Token magnitudes, timing values, the `id` format, the text
itself and any streaming behaviour; `/v1/chat/completions` is a different route
(`chat-adapter-outcomes.md`).
