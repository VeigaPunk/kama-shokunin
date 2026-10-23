# ExecRouterModels — wave 1 advice (fault family: model-name and router errors)

Seat: KamaR26.ExecRouterModels (leaf executor). Claim C1 (data: candidate
signature rows). Port block 47668-47671 (all used, all closed afterwards).

## Verdict

**Zero countable C1 signatures exist in the assigned fault family on the frozen
counter.** Every family member either emits no error at all (unknown model name
is silently accepted), emits the already-base-documented generic 404, or lives
in router mode, which the counter's launches can never reach. candidates.json
therefore carries an honest empty `signatures` list.

## What was measured

Fixture and pins verified first (sha256 bank match count-c1.py): llama-server
b11755 = 704366d, `b6a31a8e…cd804`; stories260K.gguf `270cba1b…256d`; counter
`6501737c…588` (== preregistration counter_sha256). Loopback only, ports
47668-47671 free before each launch (`ss -ltn`), one child at a time, `-t 2`,
wrapped in `timeout`, SIGTERM teardown, port closed verified after each run.

Four launches, three full reproductions of the family probes:

| run | port | server pid | key family observations |
|---|---|---|---|
| probe1 | 47668 | 3417514 | unknown model -> 200 on /v1/chat/completions, /v1/completions, /tokenize; /models/load+/models/unload+/models -> 404 File Not Found; GET /does-not-exist-xyz -> same 404 |
| probe2 | 47669 | 3472037 | unknown model -> 200 on /completion, /completions, /v1/responses, /responses, /v1/messages, /v1/chat/completions/input_tokens, /responses/input_tokens, /v1/messages/count_tokens, /infill(501 feature), /apply-template, /detokenize; model field number/null/array/absent -> 200; GET /v1/models/<any> -> 404 File Not Found |
| probe3 | 47670 | (script) | same family probes as probe1, all statuses identical |
| probe4 | 47671 | (script) | registered /v1/chat/completions/control -> 400 "missing completion id" (control route, not model-name); /completion without prompt -> 400 "key 'prompt' not found"; /slots/7 -> 501 slots action |

Evidence files (in w1-build/out/ExecRouterModels/): probe{1,2,3,4}/raw.txt +
server.log, probe{1,2,4}.sh, candidate.json, counter/counter-{A,B,C}.json,
RUNS.txt (every command + exit code).

## Family-by-family findings

1. **Requests naming an unknown model — no error exists.** Single-model mode
   ignores the request `model` field: every inference endpoint probed (legacy,
   OpenAI, Anthropic, responses, input_tokens, tokenize, apply-template,
   detokenize) answers 200 and echoes the server's own model name. Model field
   given as number, null, array, or absent: still 200. This is a silent
   misbehaviour (documented at base in corpus/knowledge/listener-census.md), not
   an error signature; predicate clause (e) needs status >= 400, so nothing to
   sign.
2. **/models load/unload on a single-model server — 404, already at base.**
   POST /models/load, /models/unload, /models and GET /models/<id> are
   registered only in router mode (server.cpp:271-275); single-model mode falls
   through to the generic 404 handler (server-http.cpp:199-207) with body
   `{"error":{"message":"File Not Found","type":"not_found_error","code":404}}`.
   That exact body is already present in SKILL.md at base 1560e4d8 (row
   "llama.cpp's normal root 404"), so clause (b) fails for it and every
   substring. Scratch counter run B confirms: row R26TestFNF404 fails
   `b_new_at_base` (and, additionally, `d_in_source` because the compact JSON
   envelope never occurs verbatim inside server-http.cpp).
3. **Router-mode literals (server-models.cpp) — unreachable under the counter.**
   All named error strings in server-models.cpp ("model is not found" 2317/2461,
   "model is already running" 2321, "model is not loaded" 2176, "model is not
   running" 2465, "model must be a non-empty string" 2497/2541, "request
   cancelled by a stop while the model was loading" 2302, "model '%s' not
   found" 2170) live in router-only handlers. The counter always launches with
   `-m <model>` (fixture/missing/junk), which forces single-model mode
   (`is_router_server` requires an empty model path, server.cpp:152-154). The
   trigger therefore always answers the 404 envelope, never the router literal.
   Scratch counter run C proves it end-to-end: row R26TestRouterNF
   ("model is already running", source S902 server-models.cpp) passes every
   static check — including d_source_pinned and d_in_source — but the live run
   shows status 404 and `e_signature_seen` false.
4. **"Loading model" 503 window — already at base and uncatchable.** The body
   `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`
   is documented at base (SKILL.md MODEL_LOADING row, SOURCES S035/S036, corpus
   knowledge). Additionally the counter's http channel waits for `/health` 200
   (wait_ready) before sending the trigger, so it can never observe the
   pre-ready 503 window; the startup channel needs a non-zero exit, which a
   successful launch does not produce.

## Files written

- `.ufo/waves/round-26/w1-build/out/ExecRouterModels/candidates.json`
  (schema kama-r26-c1-candidates/v1; signatures [] with reason_empty)
- `.ufo/waves/round-26/w1-build/out/ExecRouterModels/RUNS.txt`
- `.ufo/waves/round-26/w1-build/out/ExecRouterModels/probe{1,2,3,4}/raw.txt`
  and `server.log`
- `.ufo/waves/round-26/w1-build/out/ExecRouterModels/probe.sh`,
  `probe2.sh`, `probe4.sh`
- `.ufo/waves/round-26/w1-build/out/ExecRouterModels/counter/counter-{A,B,C}.json`
- `.ufo/waves/round-26/w1-build/advice/ExecRouterModels.md` (this report)

Scratch root (not lane files): /fast/scratch/hyaku/kama-r26/ExecRouterModels/
(probes, extract/, counter outputs).

## Risks / notes for the L1

- The 404 "File Not Found" envelope is shared by every unknown route; even if
  clause (b) did not block it, it is not specific to the /models routes (one
  fault per row would be unprovable).
- If the overall claim still needs signatures from this family, it would require
  a counter/predicate change (e.g. launching router mode without `-m`), but the
  predicate, pins and target are frozen by preregistration.json; that is out of
  scope here.
- Other seats probing feature-gate 501/400 errors (embeddings, props, rerank,
  slots, infill, systemone, lora, control) have live, base-absent, source-anchored
  signatures available (observed in my probes and passed to the L1 as
  observations only, not candidates): e.g. "This server does not support
  embeddings. Start it with `--embeddings`" (server-context.cpp:6132),
  "This server does not support changing global properties. Start it with
  `--props`" (server-context.cpp:5453), "This server does not support
  reranking. Start it with `--reranking`" (server-context.cpp:5803), "This
  server does not support slots action. Start it with `--slot-save-path`"
  (server-context.cpp:5408). These were NOT evaluated this round (outside the
  assigned family).
