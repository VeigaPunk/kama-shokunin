# ScoutFaultSurvey — C1 recon (llama-server b11755 fault surface)

Date: 2026-10-23. Seat: KamaR26.ScoutFaultSurvey (leaf, no subagents).
Lane tip frozen a23c0e042114016a909eb15173aa6df74b5b7eb0. Pinned server
binary sha256 b6a31a8e…cd804 (build 11755, commit 704366d), fixture model
stories260K.gguf sha256 270cba1b…256d. Port block 47680-47683 (all free before
each run; no leftover llama-server on the block after runs; `pgrep -af
llama-server` shows only sibling executors' servers on 47605/47624/47652/47666,
untouched).

## Method

- Read counter predicate (count-c1.py docstring), preregistration A0/A1, pinned
  sources under `.ufo/waves/round-26/sources/llama.cpp-704366d/`.
- Enumerated the server route table (server.cpp:264-360) and error emitters
  (server-context.cpp, server-http.cpp, server-task.cpp, server-common.cpp).
- Mapped executor families (metrics/slots/props/embeddings/rerank/infill off,
  slot actions, missing/junk model, bad args, port in use, prompt too long,
  chat format, LoRA/audio, request params, api key, router/models) to the
  literals they plausibly cover; picked uncovered literals; confirmed each by a
  live run on 127.0.0.1:47680-47683 with `timeout 90` wrapper, `-t 2`, health
  wait, then kill + port-closed check.

## Confirmed live candidates (8)

All are http-channel, status >= 400, signature >= 20 bytes, absent from base
1560e4d8 (git grep -F on SKILL.md corpus: exit 1 for each), absent from
`llama-server --help` (checked verbatim), not echoed from request.

| # | Signature | Source (pinned, verbatim) | Trigger | Live status |
|---|-----------|---------------------------|---------|-------------|
| 1 | `missing completion id` | server-context.cpp:5595 | POST /v1/chat/completions/control body `{}` | 400 |
| 2 | `unknown control action` | server-context.cpp:5599 | POST /v1/chat/completions/control body `{"id":"x","action":"bogus"}` | 400 |
| 3 | `This model is not a decision model` | server-context.cpp:5884 | POST /v1/systemone body `{"questions":[]}` | 501 |
| 4 | `Request body must be an array` | server-context.cpp:5998 | POST /lora-adapters body `{}` | 400 |
| 5 | `Pooling type 'none' is not OAI compatible. Please use a different pooling type` | server-context.cpp:6137 | `--embeddings`, POST /v1/embeddings body `{}` | 400 |
| 6 | `"input" or "content" must be provided` | server-context.cpp:6151 | `--embeddings`, POST /embedding body `{}` | 400 |
| 7 | `The format to return the embeddings in. Can be either float or base64` | server-context.cpp:6161 | `--embeddings`, POST /embedding body `{"input":"x","encoding_format":"bogus"}` | 400 |
| 8 | `"prompt" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.` | server-common.cpp:1114 | POST /completion body `{"prompt":42}` | 400 |

No pair of the eight is a substring/superstring of another; all eight triggers
differ (registry clause g safe within this set).

## Evidence (commands, outputs, exit codes)

Runs: `/fast/scratch/hyaku/kama-r26/ScoutFaultSurvey/run_candidates.sh`,
`run_candidates2.sh`, `run_candidates3.sh` (scripts recorded under scratch).
Each run: server launch log `<name>.server.log`, response body `<name>.body`,
summary `<name>.summary` in
`/fast/scratch/hyaku/kama-r26/ScoutFaultSurvey/live/`.
Script exit codes: all 0.

### Candidate 1 (ctl_missing_id, port 47680)
Command: `curl -s -m 30 -X POST -H 'Content-Type: application/json' -d '{}' -w '%{http_code}' http://127.0.0.1:47680/v1/chat/completions/control`
Exit 0, HTTP 400.
Body: `{"error":{"code":400,"message":"missing completion id","type":"invalid_request_error"}}`
Server log tail ends with `cleaning up before exit...`; port closed=yes.

### Candidate 2 (ctl_unknown_action, port 47681)
Command: same, body `{"id":"x","action":"bogus"}`, path `/v1/chat/completions/control`
Exit 0, HTTP 400.
Body: `{"error":{"code":400,"message":"unknown control action","type":"invalid_request_error"}}`
Port closed=yes.

### Candidate 3 (systemone_not_decision, port 47682)
Command: same, body `{"questions":[]}`, path `/v1/systemone`
Exit 0, HTTP 501.
Body: `{"error":{"code":501,"message":"This model is not a decision model","type":"not_supported_error"}}`
Port closed=yes.

### Candidate 4 (lora_not_array, port 47683)
Command: same, body `{}`, path `/lora-adapters`
Exit 0, HTTP 400.
Body: `{"error":{"code":400,"message":"Request body must be an array","type":"invalid_request_error"}}`
Port closed=yes.

### Candidate 5 (emb_missing_input, port 47680, `--embeddings`)
Command: same, body `{}`, path `/v1/embeddings`
Exit 0, HTTP 400.
Body: `{"error":{"code":400,"message":"Pooling type 'none' is not OAI compatible. Please use a different pooling type","type":"invalid_request_error"}}`
Port closed=yes. (Same literal also returned for `{"input":""}` and
`{"input":"x","encoding_format":"bogus"}` on the OAI path — pooling check runs
before input checks.)

### Candidate 6 (emb_legacy_missing, port 47680, `--embeddings`)
Command: same, body `{}`, path `/embedding` (legacy, non-OAI)
Exit 0, HTTP 400.
Body: `{"error":{"code":400,"message":"\"input\" or \"content\" must be provided","type":"invalid_request_error"}}`
Port closed=yes.

### Candidate 7 (emb_legacy_badfmt, port 47682, `--embeddings`)
Command: same, body `{"input":"x","encoding_format":"bogus"}`, path `/embedding`
Exit 0, HTTP 400.
Body: `{"error":{"code":400,"message":"The format to return the embeddings in. Can be either float or base64","type":"invalid_request_error"}}`
Port closed=yes.

### Candidate 8 (comp_prompt_type, port 47683)
Command: same, body `{"prompt":42}`, path `/completion`
Exit 0, HTTP 400.
Body: `{"error":{"code":400,"message":"\"prompt\" elements must be a string, a list of tokens, a JSON object containing a prompt string, or a list of mixed strings & tokens.","type":"invalid_request_error"}}`
Port closed=yes.

### Control checks
- `~/.local/bin/llama-server --help` exit 0 (750 lines); `--version` exit 0,
  prints `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- Base absence: for each of the 8 signatures,
  `git -C /home/vgpnk/Projects/shokunin/kama-shokunin grep -F -q -e '<sig>' 1560e4d83f42b04f40336357de6f9637eafa0f4b -- SKILL.md corpus`
  exit 1 (absent) for all 8.
- Help absence: `grep -Fq '<sig>' help.txt` exit 1 for all 8.
- No signature occurs in the request bytes of its own trigger (verified by
  inspection; counter re-checks).

## Route/flag survey (enumeration, family coverage)

Route table (server.cpp:264-360):

| Route | Method | Covered by family / notes |
|-------|--------|---------------------------|
| /health, /v1/health | GET | public; no error path exercised |
| /metrics | GET | metrics-off family (server-context.cpp:5304) |
| /props, /v1/… | GET/POST | props family (server-context.cpp:5453); with --props on: no distinct error found |
| /models, /v1/models, /models/load, /models/unload, /models/sse | GET/POST/DELETE | router/models family (server-models.cpp) |
| /completion, /completions, /v1/completions | POST | prompt-too-long family; candidate 8 (prompt type) uncovered |
| /chat/completions, /v1/chat/completions, /v1/responses, /responses, /v1/messages, /audio/transcriptions, /v1/audio/transcriptions | POST | chat-format family; audio-unsupported literal server-context.cpp:5655 (audio family) |
| /v1/chat/completions/control | POST | **uncovered — candidates 1,2** |
| /infill | POST | infill-off family (server-context.cpp:5476) |
| /embedding, /embeddings, /v1/embeddings | POST | embeddings-off family (server-context.cpp:6132); with --embeddings: candidates 5,6,7 |
| /rerank, /reranking, /v1/rerank, /v1/reranking | POST | rerank-off family (server-context.cpp:5803) |
| /v1/systemone | POST | **uncovered — candidate 3** |
| /tokenize, /detokenize, /apply-template | POST | request-params family; tokenize/detokenize with missing fields return 200 empty, no error |
| /chat/completions/input_tokens, /v1/chat/completions/input_tokens, /responses/input_tokens, /v1/responses/input_tokens, /v1/messages/count_tokens | POST | request-params family |
| /lora-adapters | GET/POST | LoRA family (ops); **body-shape error uncovered — candidate 4** |
| /slots, /slots/:id_slot | GET/POST | slots + slot-action families (server-context.cpp:5366-5434) |
| /v1/stream, /v1/streams/lookup (POST), /v1/stream (DELETE) | — | handlers in server-stream.h (not in pinned set — no countable literal) |
| static UI assets, OPTIONS CORS | GET | 404 "File Not Found" only 14 bytes; fails MIN_BYTES 20 |
| GCP compat /predict | POST | gated by AIP_MODE env (server-http.cpp:84-124); env not settable via registry trigger |

Flags: arg.cpp throw sites (invalid value / removed arg / failed file open / etc.)
are the bad-args family (A1 control refuses help-text literals; these messages are
not in --help, so a startup row remains possible but we did not add one to avoid
overlap with bad-args family). No additional distinct startup literal was
confirmed this round.

## Remaining unknowns

- "no slot available" (server-context.cpp:5396) needs two concurrent in-flight
  requests to occupy slots; unreachable with the single-request registry trigger.
- 6190 ("Input content cannot be empty") unconfirmed: `{"input":""}` on the
  legacy endpoint returns 200 with an embedding (empty string tokenizes to BOS);
  would need an input that tokenizes to zero tokens (e.g. a zero-token special
  sequence) — not found on this fixture.
- stream endpoints (server-stream.h) not countable because the header is not in
  the pinned 13-file set.

## Written artifacts

- This file: `.ufo/waves/round-26/w1-build/out/ScoutFaultSurvey/survey.md`
- Scratch under `/fast/scratch/hyaku/kama-r26/ScoutFaultSurvey/` (scripts,
  per-run logs/bodies/summaries).
