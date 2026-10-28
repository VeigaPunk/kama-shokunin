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
  and accounting only, so any completion string would pass the same checks.
- **Registered consumers.** The probe serves on an unregistered loopback port;
  consumer-facing endpoints are not contacted and their health is not sampled.
- **Timing values, ids, adapter extras.** Only `predicted_n`/`predicted_ms` presence is graded, never magnitude; `id`, `created`, `logprobs`, `index` and `prompt_tokens_details.cached_tokens` are recorded but ungraded.

## Receipt integrity

Every capture records `status`, `body`, `body_sha256` and `body_truncated`
(headers are not kept). The request-plane checks are `completion_envelope`,
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
