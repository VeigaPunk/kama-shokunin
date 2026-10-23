ATTACK SKILL.md row E26-06 + SOURCES S119 (llama-server b11755 "Pooling type 'none' is not OAI compatible"): holds

Run by KamaR26.AttackE2606, 2026-10-23, lane /home/vgpnk/Projects/shokunin/kama-shokunin
at landed tip f4066979 (read-only). Port block 47720-47723, one server at a time.
Scratch: /fast/scratch/hyaku/kama-r26w2/AttackE2606/

Pins re-checked before anything else:
  $ sha256sum ~/.local/bin/llama-server ~/.cache/kama-shokunin/models/stories260K.gguf
  b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804  ~/.local/bin/llama-server
  270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d  ~/.cache/kama-shokunin/models/stories260K.gguf
  $ ~/.local/bin/llama-server --version   -> version: 0.7.0-dev (build 11755, commit 704366d76)
  $ ss -ltn | grep 4772[0-3]              -> free at start and closed at end; pgrep -af llama-server
                                             shows no process on 4772x of mine when done.

Check (1) — registered trigger, twice: HOLDS
  Command (counter argv order + registry args/request):
    llama-server -m <fixture> --host 127.0.0.1 --port 47720 --embeddings -t 2
    curl -sS -X POST http://127.0.0.1:47720/v1/embeddings -H 'Content-Type: application/json' \
         -d '{"input":"hello world"}' -w '\nHTTP_STATUS=%{http_code}\n'
  Output, run 1 and run 2 byte-identical (resp1.txt, resp2.txt, 161 bytes each; curl exit 0 both):
    {"error":{"code":400,"message":"Pooling type 'none' is not OAI compatible. Please use a different pooling type","type":"invalid_request_error"}}
    HTTP_STATUS=400
  Registry fields used exactly: channel http, args ["--embeddings","-t","2"], model fixture,
  request POST /v1/embeddings {"input":"hello world"}; no --pooling passed, i.e. the fixture's
  default pooling (llama-context.cpp:302-306 resolves UNSPECIFIED to LLAMA_POOLING_TYPE_NONE).
  The registered trigger reproduces twice with status 400 (predicate e: status >= 400).

Check (2) — own fault text, not warning / not echo (F1, F2, F3): HOLDS
  F1 (warning on unrelated startup failure): the text is an HTTP error body from the handler,
  not a log line. grep -c "not OAI compatible" over all four server logs -> 0,0,0,0
  (srv.log, srv_mean2.log, srv3.log, srv_none.log). Startup was clean and /health answered 200
  before every request. Source has exactly one emission of this text:
  grep -n "not OAI compatible" server-context.cpp -> 5537 (comment), 6137 (the res->error),
  6148 (comment); the literal lives once in the loaded library:
  grep -a -o "Pooling type 'none' is not OAI compatible. Please use a different pooling type"
  libllama-server-impl.so -> 1 hit.
  F2 (request echo): the message is a compile-time literal with no interpolation
  (server-context.cpp:6137), and it is body-independent. On one server (--embeddings, default
  pooling) the same 400 body came back for: empty body (eb.txt), body "not json at all {]"
  (gb.txt), and a body that itself contained the whole signature (ec.txt). A reply that does not
  change with the request cannot be an echo.
  F3 (argument file contents): registry args carry no file argument (["--embeddings","-t","2"]).
  A1 (help text) also clear: `llama-server --help | grep -c "is not OAI compatible"` -> 0;
  `llama-server --version | grep -c "not OAI compatible"` -> 0.
  GET /v1/embeddings -> 404 {"error":{"message":"File Not Found",...}} (route is POST only), so the
  signature is not coming from a route-level fallback either.

Check (3) — meaning (code) cell: HOLDS (guard, lines, status all correct; one wording nit)
  Source, lane snapshot == fresh fetch at 704366d
  (curl raw.githubusercontent.com/.../704366d76.../tools/server/server-context.cpp;
   sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329, 6320 lines):
    6136  if (res_type != TASK_RESPONSE_TYPE_NONE && meta->pooling_type == LLAMA_POOLING_TYPE_NONE) {
    6137      res->error(format_error_response("Pooling type 'none' is not OAI compatible. Please use a different pooling type", ERROR_TYPE_INVALID_REQUEST));
    6138      return res;
  Guard condition: only /v1/embeddings passes a non-NONE res_type — server-context.cpp:5793
  (post_embeddings -> TASK_RESPONSE_TYPE_NONE, native /embedding) vs :5797 (post_embeddings_oai ->
  TASK_RESPONSE_TYPE_OAI_EMBD, /v1/embeddings); these are the only two callers of
  handle_embeddings_impl (grep: 5793, 5797, definition 6129). "the OpenAI-style route" is the
  right discriminator.
  Line range 6136-6138 is exact (guard, error, return). Status 400 is right:
  server-common.cpp:95-100 maps ERROR_TYPE_INVALID_REQUEST -> code 400; live 400 twice.
  Nit D1: the cell says "when the model's pooling type is `none`". The compared value is
  `meta->pooling_type`, which is filled from the context, not the model file:
  server-context.cpp:4830 `/* pooling_type */ llama_pooling_type(impl->ctx_tgt)`, and that value is
  params.pooling_type when given (`--pooling`, arg.cpp:2317-2327), else the model's hparams, else
  NONE (llama-context.cpp:302-306). Live: launching with an explicit `--pooling none` on this
  fixture also returns the 400 (pnone.txt), i.e. the flag, not only the model default, drives it.
  [INFERENCE] on a model whose GGUF declares a pooling type, `--pooling none` would give the same
  message while the model's own type is not none — no such model exists on this host to test.
  Smallest correction: "it refuses when the server's pooling type (`--pooling`; default: the
  model's) is `none`". Optional mirror in the S119 teaches cell.

Check (4) — next action supported: HOLDS (both remedies work; one wording nit)
  "Launch with `--pooling mean`": port 47722, `--embeddings --pooling mean` ->
  POST /v1/embeddings {"input":"hello world"} -> HTTP_STATUS=200 (mean_oai.json), OAI shape
  keys ['model','object','usage','data'], object 'list', data[0].embedding dim 64.
  "or use the non-OpenAI `/embedding` route with `content`, which returns per-token output":
  same pooling-none server (47720), POST /embedding {"content":"hello world"} -> 200
  (native_content.txt), body = [{index, embedding}] with embedding = 7 vectors x 64 = one vector
  per output token; code agrees (server-context.cpp:2310-2325 pushes one row per output token when
  pooling is NONE, and returns json(responses) unpooled for res_type NONE at :6240-6243).
  Also tested the trap the sentence could have set: /v1/embeddings with `content` still -> 400
  (guard runs before body parse at :6136 vs :6148), so the row correctly points at the native
  route, not at passing `content` to the OAI route.
  Nit D2: on `/embedding`, `content` is not required — `/embedding` with `{"input":"hello world"}`
  returned the identical 200 shape (same 7x64 per-token body). The sentence reads as if `content`
  were necessary there. Smallest correction: "or use the non-OpenAI `/embedding` route (it takes
  `input` or `content`), which returns per-token output".

Check (5) — SOURCES S119 cells and lesson Gate quote: HOLDS
  corpus/SOURCES.md:11 header columns: | id | source | kind | tier | scope | anchor | teaches |
  status | opened | recheck | used-by |. S119 is corpus/SOURCES.md:131:
    source  "llama.cpp server-context.cpp @ 704366d (b11755) — https://github.com/ggml-org/llama.cpp/
            blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L6137"
            -> #L6137 is the line that holds the literal in the fresh fetch (sed -n '6137p').
    kind code; tier A.
    scope   "the E26-06 error emitted at server-context.cpp line 6137 and its guard, at commit
            704366d76 only; not other builds" -> matches the single emission site.
    anchor  "server-context.cpp line 6137 @ 704366d76...; sha256 dd1de0f26536ce3e115e39110f2f07
            19427f2796885c2a1ea2db071b603c2329" -> equals the fresh fetch AND the lane snapshot
            (both dd1de0f2...2329).
    teaches "the OpenAI-style route needs pooled output; it refuses when the model's pooling type
            is `none` (server-context.cpp:6136-6138). Live trigger and next action: SKILL.md row
            E26-06." -> consistent with code; carries nit D1.
    status mined; opened 2026-10-23; recheck on-release; used-by SKILL.md,
            registry/error-signatures-r26.json.
  Base absence: S119 does not exist at base 1560e4d8
    (git show 1560e4d8:corpus/SOURCES.md | grep -c '| S119 |' -> 0; max id at base S113).
  Lesson Gate quote, corpus/lessons/round-26.md:32, four cells:
    URL .../server-context.cpp#L6137 | 2026-10-23 | line 6137: `res->error(format_error_response(
    "Pooling type 'none' is not OAI compatible. Please use a different pooling type", ERROR_TYPE_INVALID_REQUEST));`
  Quote == source line 6137 character for character (python compare -> True); 14 words (limit 25).

Row-level predicate re-check (all true, for the record)
  (a) row starts with E26-06, contains the 78-byte signature verbatim and S119 (python check True);
  (b) 78 bytes >= 20; signature absent at base SKILL.md and in all 59 tracked corpus/ files at base
      (git show per file -> 0 hits);
  (c)/(d) see check 5; (e) see check 1; (f) help/version 0 hits; (g) only E26-06 among the 17 rows
      and only registry entry E26-06 contains this signature (17 rows, 17 registry entries).

Defects (both wording, neither breaks a check or changes the reader's action)
  D1 SKILL.md:1089 meaning cell (and corpus/SOURCES.md:131 teaches): "the model's pooling type" ->
     the resolved server pooling type. Correction in check 3.
  D2 SKILL.md:1089 next action: `content` is presented as necessary on `/embedding`; it is not.
     Correction in check 4.

Unknowns / not done here
  - No fixture model whose GGUF declares a pooling type, so the model-default branch is code-read
    only [INFERENCE]; the "--pooling none" override case was tested live.
  - I did not run the frozen counter (out of this seat's scope); the registered trigger was
    reproduced by hand twice instead.
  - Two other llama-server processes were running during my window on ports 47734 and 47740
    (peers' block); I did not touch them. All of my servers (47720, 47721, 47722, 47723) were
    killed and every port confirmed closed (`ss -ltn | grep 4772[0-3]` -> none).

Files written
  .ufo/waves/round-26/w2-falsify/advice/AttackE2606.md   (this report, in the lane)
  /fast/scratch/hyaku/kama-r26w2/AttackE2606/{resp1.txt,resp2.txt,eb.txt,gb.txt,ec.txt,get.txt,
    pnone.txt,native_content.txt,mean_oai.json,mean_native.json,srv.log,srv_mean.log,
    srv_mean2.log,srv3.log,srv_none.log} and fetch/server-context.cpp.fresh
  No installed tool changes were needed.
  Incident: my first write of this report used a relative path and landed at
  /home/vgpnk/Projects/shokunin/.ufo/waves/round-26/w2-falsify/advice/AttackE2606.md (fleet root).
  That copy is no longer present at that path; this absolute-path write is the deliverable.
