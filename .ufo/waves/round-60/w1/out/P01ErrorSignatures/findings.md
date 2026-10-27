# P01 error signatures — live Ollama v0.40.11 (round 60, w1)

Seat: `P01ErrorSignatures` (leaf, advisory). Item: observe the exact error and non-error
signatures a consumer sees against a lane-owned Ollama v0.40.11, plus the gate between
"model not loaded yet" and "model unknown". No verdict, no lane edit.

Bears on: C1-r60 (`live-ollama-lifecycle`: the HTTP surfaces a consumer actually meets) and
C2-r60 (lane `INFERENCE` statements about Ollama vs live captures). Readings are evidence;
claim grading is the L1's.

## Environment and provenance

| item | value |
|---|---|
| server binary | `/home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama` — sha256 `b0a4becfaf872e3ad5d2e9051244e0dfe55409f03d6e2cd9bd9c34400e201b4c` (matches frozen constant) |
| fixture model | `~/.cache/kama-shokunin/models/stories260K.gguf` — sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches) |
| version body | `{"version":"0.40.11"}` |
| imported model name | `p01errsig-b79648f8` (`ollama create … -f Modelfile`, `FROM <gguf>`; `success`) |
| servers | four lane-owned instances, one per pass, ports 46653 / 58765 / 45993 / 37183; each started and killed by its own PID in the same shell (`PID_DEAD` recorded) |
| env | `env -i`, `OLLAMA_NO_CLOUD=1`, `OLLAMA_NOPRUNE=1`, CUDA/HIP/Vulkan device vars `-1`, `OLLAMA_HOST=127.0.0.1:<port>`, private `HOME`/`OLLAMA_MODELS` |
| method | Python `http.client`, no redirect following, exact status + selected headers + body; every request body recorded |
| captures | `captures.jsonl` (49 rows, sha256 `39fd2b96…a1cc2`), `captures-extra.jsonl` (21, `6f450120…74937`), `captures-full.jsonl` (9, `64f79170…0dc17`), `captures-empty.jsonl` (9, `de320ada…d95`); 88 rows total |
| provenance | `session.txt` (listen lines + ports + version), `meta.txt` (digests), drivers in `drivers/` |

All servers loopback-only, no auth/TLS/proxy, no registered consumer, CPU only. Everything
below was observed on this one binary and one 293K-parameter llama GGUF.

## What a consumer sees: five signature families

**1. Native `/api/*` errors — JSON object with a single string key.**
Content-Type `application/json; charset=utf-8`. Model-unknown is 404; parse/validation is 400.

| exact body | status | route(s) |
|---|---|---|
| `{"error":"model 'p01-does-not-exist' not found"}` | 404 | `/api/generate`, `/api/chat`, `/api/embed` |
| `{"error":"model 'p01-does-not-exist:latest' not found"}` | 404 | `/api/show` (adds `:latest` when the caller omitted a tag) |
| `{"error":"unexpected EOF"}` | 400 | `/api/generate`, `/api/show` on truncated JSON (`{"model": `) |
| `{"error":"invalid character 'o' in literal null (expecting 'u')"}` | 400 | `/api/generate`, `/api/chat` on `not-json` |
| `{"error":"missing request body"}` | 400 | `/api/generate` with zero-length body |
| `{"error":"model is required"}` | 400 | `/api/show` with `{}` |
| `{"error":"model '' not found"}` | 404 | `/api/generate` with `{}` — generate validates the model by lookup only, so an absent field surfaces as a *model-404*, not a 400 (route-inconsistent validation) |

There is no `, try pulling it first` suffix in 0.40.11; the older text is not emitted.

**2. OpenAI-compatible `/v1/*` errors — nested envelope plus trailing newline.**
Content-Type `application/json` (no charset). Shape:
`{"error":{"message":"…","type":"not_found_error"|"invalid_request_error","param":null,"code":null}}\n`.

- `/v1/chat/completions`, `/v1/completions`, `/v1/embeddings` unknown model → 404, message echoes
  the **bare** name: `model 'p01-does-not-exist' not found`.
- `/v1/models/<unknown>` → 404, message normalizes to `model 'p01-does-not-exist:latest' not found`.
- Malformed body → 400 with `"type":"invalid_request_error"` and `"message":"unexpected EOF"`.
- Streaming (`stream:true`) unknown model → plain 404 envelope; no NDJSON frame is opened.

**3. Routing errors — text/plain, no JSON at all.**
Content-Type `text/plain` (no charset):

| body | status | example |
|---|---|---|
| `404 page not found` (18 B) | 404 | `/health`, `/props`, `/slots`, `/metrics`, `/nope` |
| `405 method not allowed` (22 B) | 405 + `Allow:` header | `POST /api/tags` → `Allow: HEAD, GET`; `GET /api/generate` → `Allow: POST`; `POST /api/ps` → `Allow: GET`; `GET /v1/chat/completions` → `Allow: POST`; `OPTIONS` anywhere → 405 |

Consequence: a consumer that parses every error as JSON breaks on method/route errors, and a
status-404 test cannot tell **route missing** from **model missing** without the Content-Type.

**4. Redirect — `/v1/models/` (trailing slash) is 301, not 200.**
`301`, Content-Type `text/html; charset=utf-8`, `Location: /v1/models`, body
`<a href="/v1/models">Moved Permanently</a>.\n\n`. A raw client that does not follow redirects
gets HTML where it expected JSON; a base URL that keeps the slash never reaches the list route.

**5. Empty inventory shapes — a non-error trap.**
With **zero** models imported (`OLLAMA_MODELS` empty):

| route | status | body |
|---|---|---|
| `GET /v1/models` | 200 | `{"object":"list","data":null}\n` — **`data` is `null`, not `[]`** |
| `GET /api/tags` | 200 | `{"models":[]}` |
| `GET /api/ps` | 200 | `{"models":[]}` |
| `GET /api/version` | 200 | `{"version":"0.40.11"}` |

`data:null` reproduces the committed receipt's `v1-models-empty` capture independently (different
nonce, model-free server). An OpenAI client that does `for m in body["data"]` raises on a healthy
empty server; `data or []` is required.

Headers worth recording: `/api/show` responses are **chunked** (no `Content-Length`); `/api/*`
bodies carry no trailing newline, `/v1/*` bodies do; HEAD `/` → 200 empty body, `Content-Length 17`;
HEAD `/api/version` → 200 empty body, `Content-Length 21`; HEAD `/api/tags` → 200 empty body,
`Content-Length 477`; HEAD `/health` → 404 empty body.

## Full capture table

Generated from the JSONL by `drivers/table.py` (all 79 non-empty-inventory rows; the 9
empty-inventory rows are in the section above and in `captures-empty.jsonl`).

#### A. Baseline and identity surfaces

| case | method | route | status | content-type | body (first 150 chars) | reading |
|---|---|---|---|---|---|---|
| `version` | GET | `/api/version` | 200 | `application/json; charset=utf-8` | `{"version":"0.40.11"}` | Version route; JSON envelope `{"version":...}`, not the llama.cpp `/api/version` contract. |
| `root_get` | GET | `/` | 200 | `text/plain; charset=utf-8` | `Ollama is running` | Liveness marker is text/plain, not JSON. |
| `root_head` | HEAD | `/` | 200 | `text/plain; charset=utf-8` | `` | HEAD works; empty body, Content-Length 17. |
| `tags` | GET | `/api/tags` | 200 | `application/json; charset=utf-8` | `{"models":[{"name":"p01errsig-b79648f8:latest","model":"p01errsig-b79648f8:latest","modified_at":"2026-10-27T18:36:17.037706714-03:00","size":11854...` | Inventory (model, digest, details, capabilities); says nothing about residency. |
| `ps_before_load` | GET | `/api/ps` | 200 | `application/json; charset=utf-8` | `{"models":[]}` | Residency empty: imported but never loaded. |
| `v1_models` | GET | `/v1/models` | 200 | `application/json` | `{"object":"list","data":[{"id":"p01errsig-b79648f8:latest","object":"model","created":1793136977,"owned_by":"library"}]}\n` | OpenAI list; id carries `:latest`. |
| `v1_models_trailing_slash` | GET | `/v1/models/` | 301 | `text/html; charset=utf-8` | `<a href="/v1/models">Moved Permanently</a>.\n\n` | 301 with HTML body and `Location: /v1/models`; raw clients do not follow. |
| `v1_models_known` | GET | `/v1/models/p01errsig-b79648f8` | 200 | `application/json` | `{"id":"p01errsig-b79648f8","object":"model","created":1793136977,"owned_by":"library"}\n` | Detail route echoes the requested form, so a bare request yields a bare `id`. |
| `show_known` | POST | `/api/show` | 200 | `application/json; charset=utf-8` | `{"modelfile":"# Modelfile generated by \"ollama show\"\n# ...FROM p01errsig-b79648f8:lat...` | Metadata: modelfile, model_info, details, capabilities, template; chunked. |
| `ps_after_show` | GET | `/api/ps` | 200 | `application/json; charset=utf-8` | `{"models":[]}` | `/api/show` did not load the model; ps still empty. |
| `show_known_latest` | POST | `/api/show` | 200 | `application/json; charset=utf-8` | same metadata | Tagged form accepted; same metadata. |
| `show_legacy_name_known` | POST | `/api/show` | 200 | `application/json; charset=utf-8` | same metadata | Legacy `name` field still accepted. |
| `v1_models_known_latest` | GET | `/v1/models/p01errsig-b79648f8:latest` | 200 | `application/json` | `{"id":"p01errsig-b79648f8:latest",...}` | Detail route returns the tag exactly as requested. |

#### B. Unknown model, every named surface

| case | method | route | status | content-type | body (first 150 chars) | reading |
|---|---|---|---|---|---|---|
| `show_unknown` | POST | `/api/show` | 404 | `application/json; charset=utf-8` | `{"error":"model 'p01-does-not-exist:latest' not found"}` | Model-404 as JSON; name normalized with `:latest`. |
| `show_unknown_latest` | POST | `/api/show` | 404 | `application/json; charset=utf-8` | same | Byte-identical to the bare-name case. |
| `show_legacy_name_unknown` | POST | `/api/show` | 404 | `application/json; charset=utf-8` | same | Legacy field normalizes unknown name to `:latest`. |
| `generate_unknown` | POST | `/api/generate` | 404 | `application/json; charset=utf-8` | `{"error":"model 'p01-does-not-exist' not found"}` | Bare name echoed; no `try pulling` suffix in 0.40.11. |
| `chat_unknown` | POST | `/api/chat` | 404 | `application/json; charset=utf-8` | same | Same JSON error shape as generate. |
| `embed_unknown` | POST | `/api/embed` | 404 | `application/json; charset=utf-8` | same | Same JSON error shape. |
| `v1_chat_unknown` | POST | `/v1/chat/completions` | 404 | `application/json` | `{"error":{"message":"model 'p01-does-not-exist' not found","type":"not_found_error","param":null,"code":null}}\n` | OpenAI envelope; bare name; trailing newline. |
| `v1_models_unknown` | GET | `/v1/models/p01-does-not-exist` | 404 | `application/json` | `{"error":{"message":"model 'p01-does-not-exist:latest' not found",...}}\n` | OpenAI envelope; name normalized with `:latest`. |
| `v1_models_unknown_latest` | GET | `/v1/models/p01-does-not-exist:latest` | 404 | `application/json` | same | Identical to the bare-name case. |
| `v1_completions_unknown` | POST | `/v1/completions` | 404 | `application/json` | `{"error":{"message":"model 'p01-does-not-exist' not found",...}}\n` | OpenAI envelope; bare name. |
| `v1_embeddings_unknown` | POST | `/v1/embeddings` | 404 | `application/json` | same | OpenAI envelope; bare name. |
| `v1_chat_stream_unknown` | POST | `/v1/chat/completions` | 404 | `application/json` | same | 404 envelope; no NDJSON stream is opened. |
| `generate_stream_unknown` | POST | `/api/generate` | 404 | `application/json; charset=utf-8` | `{"error":"model 'p01-does-not-exist' not found"}` | 404 JSON before any stream frame. |
| `chat_stream_unknown` | POST | `/api/chat` | 404 | `application/json; charset=utf-8` | same | 404 JSON before any stream frame. |
| `show_uppercase_unknown` | POST | `/api/show` | 404 | `application/json; charset=utf-8` | `{"error":"model 'P01-DOES-NOT-EXIST:latest' not found"}` | Name case is preserved verbatim in the message. |
| `v1_models_uppercase_unknown` | GET | `/v1/models/P01-DOES-NOT-EXIST` | 404 | `application/json` | `{"error":{"message":"model 'P01-DOES-NOT-EXIST:latest' not found",...}}\n` | Case preserved; `:latest` appended. |

#### C. Malformed and empty bodies

| case | method | route | status | content-type | body (first 150 chars) | reading |
|---|---|---|---|---|---|---|
| `generate_malformed` | POST | `/api/generate` | 400 | `application/json; charset=utf-8` | `{"error":"unexpected EOF"}` | Go JSON decoder text inside the native error envelope. |
| `generate_not_json` | POST | `/api/generate` | 400 | `application/json; charset=utf-8` | `{"error":"invalid character 'o' in literal null (expecting 'u')"}` | Decoder reports the offending character and literal. |
| `chat_not_json` | POST | `/api/chat` | 400 | `application/json; charset=utf-8` | same | Same decoder text on chat. |
| `show_malformed` | POST | `/api/show` | 400 | `application/json; charset=utf-8` | `{"error":"unexpected EOF"}` | Same `unexpected EOF` decoder text. |
| `v1_chat_malformed` | POST | `/v1/chat/completions` | 400 | `application/json; charset=utf-8` | `{"error":{"message":"unexpected EOF","type":"invalid_request_error",...}}` | OpenAI envelope, `type: invalid_request_error`. |
| `generate_empty_body` | POST | `/api/generate` | 400 | `application/json; charset=utf-8` | `{"error":"missing request body"}` | Body-level validation error, not a JSON parse error. |
| `show_empty_object` | POST | `/api/show` | 400 | `application/json; charset=utf-8` | `{"error":"model is required"}` | `model is required` at 400. |
| `generate_empty_object` | POST | `/api/generate` | 404 | `application/json; charset=utf-8` | `{"error":"model '' not found"}` | `{}` becomes `model '' not found` at 404: generate validates by lookup only. |

#### D. Wrong method

| case | method | route | status | content-type | body (first 150 chars) | reading |
|---|---|---|---|---|---|---|
| `tags_post` | POST | `/api/tags` | 405 | `text/plain` | `405 method not allowed` | Routing-level 405 with `Allow: HEAD, GET`; never JSON. |
| `tags_delete` | DELETE | `/api/tags` | 405 | `text/plain` | `405 method not allowed` | Same 405; `Allow: HEAD, GET`. |
| `version_post` | POST | `/api/version` | 405 | `text/plain` | `405 method not allowed` | Same 405, `Allow: HEAD, GET`. |
| `version_put` | PUT | `/api/version` | 405 | `text/plain` | `405 method not allowed` | Same 405, `Allow: HEAD, GET`. |
| `version_head` | HEAD | `/api/version` | 200 | `application/json; charset=utf-8` | `` | HEAD 200; empty body, Content-Length 21. |
| `generate_get` | GET | `/api/generate` | 405 | `text/plain` | `405 method not allowed` | 405, `Allow: POST`. |
| `ps_post` | POST | `/api/ps` | 405 | `text/plain` | `405 method not allowed` | 405, `Allow: GET`. |
| `v1_chat_get` | GET | `/v1/chat/completions` | 405 | `text/plain` | `405 method not allowed` | 405 text/plain, not an OpenAI envelope; `Allow: POST`. |
| `options_tags` | OPTIONS | `/api/tags` | 405 | `text/plain` | `405 method not allowed` | No CORS preflight; `Allow: HEAD, GET`. |
| `options_generate` | OPTIONS | `/api/generate` | 405 | `text/plain` | `405 method not allowed` | Same; browser consumers cannot preflight. |
| `show_get` | GET | `/api/show` | 405 | `text/plain` | `405 method not allowed` | 405, `Allow: POST`. |
| `head_tags` | HEAD | `/api/tags` | 200 | `application/json; charset=utf-8` | `` | HEAD 200; empty body, Content-Length 477. |
| `post_v1_models` | POST | `/v1/models` | 405 | `text/plain` | `405 method not allowed` | 405, `Allow: GET`. |

#### E. llama.cpp-convention routes

| case | method | route | status | content-type | body (first 150 chars) | reading |
|---|---|---|---|---|---|---|
| `health` | GET | `/health` | 404 | `text/plain` | `404 page not found` | No `/health`; text/plain route-404, not a readiness signal. |
| `props` | GET | `/props` | 404 | `text/plain` | `404 page not found` | No `/props`; text/plain route-404. |
| `slots` | GET | `/slots` | 404 | `text/plain` | `404 page not found` | No `/slots`; text/plain route-404. |
| `metrics` | GET | `/metrics` | 404 | `text/plain` | `404 page not found` | No `/metrics`; no openmetrics surface. |
| `unknown_route` | GET | `/nope` | 404 | `text/plain` | `404 page not found` | Route-404 is byte-identical to `/health`, `/props`, `/slots`, `/metrics`. |
| `head_health` | HEAD | `/health` | 404 | `text/plain` | `` | HEAD 404, empty body; status-only liveness still sees 404. |

#### F. Load gate and residency

| case | method | route | status | content-type | body (first 150 chars) | reading |
|---|---|---|---|---|---|---|
| `generate_known_load` | POST | `/api/generate` | 200 | `application/json; charset=utf-8` | `{"model":"p01errsig-b79648f8","created_at":"…","response":" upon a","done":true,"done_reason":"length","context":[403,...` | Known model auto-loads; `load_duration` present (≈253 ms). |
| `ps_after_load` | GET | `/api/ps` | 200 | `application/json; charset=utf-8` | `{"models":[{"name":"p01errsig-b79648f8:latest","model":…,"size":6312427,"digest":"8cf91c71…"` | Resident entry with `expires_at`, `size_vram:0` (CPU), runner `llamacpp`. |
| `tags_after_load` | GET | `/api/tags` | 200 | `application/json; charset=utf-8` | same inventory | Inventory unchanged by loading. |
| `v1_models_after_load` | GET | `/v1/models` | 200 | `application/json` | same list | OpenAI list unchanged by loading. |
| `v1_chat_known_after_load` | POST | `/v1/chat/completions` | 200 | `application/json` | `{"id":"chatcmpl-996","object":"chat.completion","model":"p01errsig-b79648f8","system_fingerprint":"fp_ollama",...}` | OpenAI chat.completion works on the same model. |
| `generate_unknown_after_load` | POST | `/api/generate` | 404 | `application/json; charset=utf-8` | `{"error":"model 'p01-does-not-exist' not found"}` | Unknown still 404 while another model is resident. |
| `show_unknown_after_load` | POST | `/api/show` | 404 | `application/json; charset=utf-8` | `{"error":"model 'p01-does-not-exist:latest' not found"}` | Same while resident. |
| `v1_chat_unknown_after_load` | POST | `/v1/chat/completions` | 404 | `application/json` | same envelope | Same envelope after load. |
| `v1_models_unknown_after_load` | GET | `/v1/models/p01-does-not-exist` | 404 | `application/json` | same envelope | Same envelope after load. |
| `show_known_full` | POST | `/api/show` | 200 | `application/json; charset=utf-8` | `{"modelfile":"# Modelfile generated by \"ollama show\"…` | Untruncated metadata, 10413 B; capabilities `["completion"]`; chunked. |
| `tags_full` | GET | `/api/tags` | 200 | `application/json; charset=utf-8` | `{"models":[{…,"size":1185492,…,"capabilities":["completion"]}]}` | Disk `size` 1185492 vs ps memory `size` 6312427; same digest `8cf91c71…`. |
| `generate_keepalive_default` | POST | `/api/generate` | 200 | `application/json; charset=utf-8` | generate body | Loads with default 5-minute keep-alive. |
| `ps_loaded` | GET | `/api/ps` | 200 | `application/json; charset=utf-8` | resident entry | `size_vram` 0, `context_length` 2048. |
| `show_while_loaded` | POST | `/api/show` | 200 | `application/json; charset=utf-8` | metadata | Identical metadata while resident. |
| `generate_unload_keepalive0` | POST | `/api/generate` | 200 | `application/json; charset=utf-8` | generate body | `keep_alive:0` unloads immediately. |
| `ps_after_unload` | GET | `/api/ps` | 200 | `application/json; charset=utf-8` | `{"models":[]}` | Residency back to empty after unload. |
| `show_after_unload` | POST | `/api/show` | 200 | `application/json; charset=utf-8` | metadata | Known and unloaded: still 200. |
| `v1_models_after_unload` | GET | `/v1/models` | 200 | `application/json` | list | List still serves the model while unloaded. |

## The gate: "not loaded yet" vs "model unknown"

| question | probe (observed) | unknown model | known, **not** loaded | known, loaded |
|---|---|---|---|---|
| Is the name known? | `POST /api/show {"model":N}` | **404** `{"error":"model 'N:latest' not found"}` | 200 metadata | 200 same metadata |
| Is it known, OpenAI view? | `GET /v1/models/N` | 404 `not_found_error` | 200 detail | 200 detail |
| Is it resident? | `GET /api/ps` | `{"models":[]}` | **`{"models":[]}`** | one entry: `expires_at`, `size_vram:0`, `runner:"llamacpp"`, `context_length:2048` |
| Is it in inventory? | `GET /api/tags` | `{"models":[]}` (model-free server) | lists it (digest `8cf91c71…`) | byte-identical to unloaded |
| Does a generation work? | `POST /api/generate` | 404 `model 'N' not found` | **200**, `load_duration` ≈253 ms | 200 |

Readings:

1. **Ollama has no "not loaded" error.** A known but unloaded model is not an error state on any
   observed route: `/api/generate` simply loads it (`load_duration` present) and returns 200.
   The only 404 on these surfaces is *model unknown*.
2. **`/api/show` is a load-free known/unknown gate.** It returned the full 10 413 B metadata while
   `/api/ps` stayed `{"models":[]}` both before and after the call, so "known" can be established
   without loading or evicting anything.
3. **`/api/ps` is the residency gate, and empty is healthy.** `{"models":[]}` is what a freshly
   started server with imported models returns; it must not be read as endpoint death.
4. **Residency and identity are independent axes.** `keep_alive:0` flipped `/api/ps` to
   `{"models":[]}` while `/api/show`, `/api/tags` and `/v1/models` all stayed 200 for the same
   model. Loading changed `/api/ps` and nothing else; unloading changed `/api/ps` and nothing else.
5. **A 404 from these surfaces is model-unknown, not route-missing — but only the Content-Type
   tells them apart** (family 1/2 vs family 3). The lane's rule "404 ⇒ check content-type before
   concluding" is directly supported.

Not observed, therefore marked **[INFERENCE]**: any `503`/`409` "loading"/"busy" response while a
model is being loaded or the server is saturated (the tiny fixture loads in ~0.25 s and requests
were serial); the state of a `/api/ps` entry *during* load; behaviour under `OLLAMA_KEEP_ALIVE`
override or multi-model eviction; any difference with GPU placement or a second Ollama version.

## Lane-convention collision (operability reading)

The lane's readiness fragment (`corpus/knowledge/served-model-identity.md`, `/health` `/props`
`/slots` `/metrics` block; `endpoint-identity.md` liveness/readiness rows) is a llama.cpp contract.
Against this Ollama server:

- `/health`, `/props`, `/slots`, `/metrics` are **all 404 `text/plain` `404 page not found`**, byte-
  identical to a nonsense route. `curl -sS http://host/health` exits **0** and prints that text
  (no `-f`), so a check that only inspects exit status or non-empty output accepts a missing route;
  a JSON parser raises; `curl -f` reads 404 and would call the endpoint dead — while
  `/api/version` on the same server is 200.
- There is **no openmetrics surface**: a `/metrics` scraper configured for llama.cpp receives an
  18-byte text 404, not an empty metric family.
- There is no `/props` (`default_generation_settings`) and no `/slots` (occupancy). The nearest
  Ollama equivalents are `/api/show` (metadata, capabilities, model_info), `/api/ps` (residency,
  `expires_at`), `/api/version` (build) — different routes, different shapes, different meanings.
- `/v1/models` is **canonical without the trailing slash**; `/v1/models/` is a 301 HTML redirect, so
  a consumer built from a base URL that keeps a trailing slash never receives JSON unless it
  follows redirects.
- **No CORS**: every `OPTIONS` probe returns 405 text/plain, so browser-based consumers cannot
  preflight (default build; `OLLAMA_ORIGINS` was not exercised).
- **Empty inventory is `data:null`** on `/v1/models` — an iterating client needs `data or []`.

[INFERENCE] The llama.cpp side of that contrast (a loading server answering `/health` with 503) is
the lane's documented llama.cpp behaviour; no llama.cpp server was started here, so only the Ollama
side is observed.

## Bearing on C2 (advisory; no verdict, no registry edit)

- Receipt captures reproduce in shape on independent runs: `ps-before` `{"models":[]}`; `ps-after`
  with `expires_at`, `size_vram:0`, `runner:"llamacpp"`; `show.details.format == "gguf"`; `root`
  `Ollama is running`; `version` `{"version":"0.40.11"}`.
- The receipt's `v1-models-empty` **`data:null`** was reproduced independently on a model-free
  server. A C2 predicate asserting the empty list is `[]` would be contradicted; `data is None`
  (or `not data`) is the shape that holds.
- Candidate falsifiable predicates the L1/registry could use (not applied here):
  `c['ps-before']['models'] == []`; `c['show']['details']['runner'] == 'llamacpp'`;
  `c['tags']['models'][0]['digest'] == '8cf91c71…'`; `c['v1-models-empty']['data'] is None`;
  `'try pulling it first' not in c['generate-unknown']['error']` (only meaningful if the receipt
  carries an unknown-model capture — the committed nonce receipt does not).
- Candidate knowledge entry (advisory, not written): "Ollama v0.40.11 consumer signatures — five
  families, the show/ps gate matrix, `data:null`". Candidate mined mistake (advisory): the lane's
  readiness fragment treats `/health`+`/props`+`/slots`+`/metrics` as endpoint-generic, while on
  Ollama all four are text/plain route-404s — a shared probe would misread a healthy Ollama as
  either dead (`curl -f`) or as llama.cpp (body presence).

## Limits

One binary (sha256 pinned), one 293K-parameter GGUF, CPU only, loopback only, four short-lived
servers, serial requests, no auth/TLS/proxy/cloud, no registered consumer, no other Ollama version,
no concurrency/saturation, no security testing of bind exposure. Captures are point-in-time; the
whole exercise is advisory and does not grade C1 or C2.

## Evidence index (this directory)

| file | rows | sha256 |
|---|---|---|
| `captures.jsonl` | 49 | `39fd2b96ab3d164e558cc8c9e61d6be55b7740bd278a9e08747f382c224a1cc2` |
| `captures-extra.jsonl` | 21 | `6f450120fcb40389826e28f5eb0898c3289883c6f195ba5df5d3ee9d11674937` |
| `captures-full.jsonl` | 9 | `64f79170b24ecd7db039795cf4a48325ceae8dd0842447f5222a55645050dc17` |
| `captures-empty.jsonl` | 9 | `de320ada90a94525992d5812011885277031dd3bbbddeed9f64c740b08856d95` |
| `session.txt` | — | provenance: ports 46653/58765/45993/37183, listen lines, version |
| `meta.txt` | — | binary + GGUF sha256 |
| `drivers/` | — | the four capture drivers, four runners, table generator (as run) |
