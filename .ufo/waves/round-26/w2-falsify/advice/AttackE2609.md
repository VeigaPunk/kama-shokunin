ATTACK E26-09 (SKILL.md:1092, registry/error-signatures-r26.json:216, S122): partial

The signature, trigger, source line, status, SOURCES row and Gate quote all hold.
The one defect is in the 'next action' cell. "Model capability, not server
configuration" goes too far: a launch flag (`--override-kv`) gets past the guard on
the same fixture model, observed live (HTTP 200). Severity: low. It does not affect
C1 counting.

Seat: KamaR26.AttackE2609. Port block 47732-47735; used 47732, 47733, 47734, one
server at a time. Scratch: /fast/scratch/hyaku/kama-r26w2/AttackE2609/.

Pins (observed): `sha256sum ~/.local/bin/llama-server` gives b6a31a8e…cd804 (resolves
to ~/.local/opt/llama-b11755/llama-server). `--version` prints "build 11755, commit
704366d76". The model stories260K.gguf hashes to 270cba1b…256d. All match the pins in
count-c1.py. count-c1.py sha256 is 6501737c…c796588, which matches the preregistration.

## (1) Live re-run of the registered trigger: holds

Command: `timeout 120 python3 run.py <port> <tag>` (scratch run.py). It reads the
E26-09 registry entry and launches
`~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port P -t 2`.
This is the counter's argv plus registry args `["-t","2"]`, with model 'fixture'. The
script waits for /health = 200, sends the registered POST /infill, then sends three
controls. It stops the server with SIGTERM to its process group and confirms the port
is closed.

- run1 (port 47732) and run2 (port 47733): the registered body
  `{"input_prefix": "int add(int a, int b) {\n    return ", "input_suffix": ";\n}", "prompt": "a + b"}`
  returned **HTTP 501**. Raw body:
  `{"error":{"code":501,"message":"Infill is not supported by this model: prefix token is missing. suffix token is missing. middle token is missing. ","type":"not_supported_error"}}`
- Both runs gave the same result. The server exited with 0 after SIGTERM,
  `port_closed: true`, and run.py exited with 0 in both runs.
- Positive control on the same server: `POST /completion` returned 200 with
  `"content":", there was a little girl"` (run1) and `"…little boy"` (run2).
- Files: run1/{argv.txt,server.log,result.json}, run2/{argv.txt,server.log,result.json}.

## (2) The signature is the fault's own text (F1, F2, F3): holds

- F1 (a warning on an unrelated path) does not apply. The channel is http, and the
  signature is in the 501 response body. `sig_in_server_log: false` in both runs. The
  only copy of the signature in the pinned sources is server-context.cpp:5476
  (`grep -rn "Infill is not supported" sources/llama.cpp-704366d/` gives one hit).
  `llama-server --help` and `--version` piped to `grep -ci "infill is not supported"`
  give 0 and 0. The base 1560e4d8 SKILL.md contains it 0 times.
- F2 (echo of a decoded request field) does not apply. The guard runs before the body
  is parsed: `json::parse(req.body)` is at server-context.cpp:5481, after the return
  at 5477. Live controls on both runs:
  - body `{}`: 501, same message;
  - body `not json at all`: 501, same message;
  - no body: 501, same message.
  
  The request bytes contain no "Infill" (`sig_in_request: false` for every case).
  There are no headers and no query string.
- F3 (echo from an argument file) does not apply. The args are `-t 2` only and no
  file is passed.

## (3) Source line and 'meaning (code)' cell: holds

- Fresh fetch:
  `curl -sSfL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp`
  exited with 0. Its sha256 is dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329,
  and `cmp` against the lane snapshot exits with 0. server-common.cpp was fetched the
  same way: b4f4aae7…d442, equal to the snapshot.
- Line 5462 is `this->post_infill = [this](const server_http_req & req) {`.
  Lines 5466/5469/5472 test `llama_vocab_fim_pre/suf/mid(ctx_server.vocab) == LLAMA_TOKEN_NULL`
  and append "prefix/suffix/middle token is missing. ". Line 5475 is
  `if (!err.empty())`. Line 5476 is the `res->error(… "Infill is not supported by this model: %s" …, ERROR_TYPE_NOT_SUPPORTED)`.
  Line 5477 is `return res;` and line 5478 is `}`. The cited range 5462-5478 is exact.
- "refuses when any is missing" matches the code: there are three independent ifs and
  any non-empty `err` triggers the refusal. "The message lists which tokens are
  missing" matches the code and the live body.
- The 501 claim holds. server-common.cpp:115-117 has
  `case ERROR_TYPE_NOT_SUPPORTED: type_str = "not_supported_error"; code = 501;`,
  and 501 was observed live.

## (4) 'next action' cell: BREAKS (overreach, low severity)

The cell reads: "Model capability, not server configuration. Use a code model with
fill-in-the-middle tokens, or send the task to `/completion`."

- The FIM token ids come from GGUF metadata keys
  (llama-vocab.cpp:2866 `{ LLM_KV_TOKENIZER_FIM_PRE_ID, special_fim_pre_id }`), read
  with `ml.get_key(...)` at llama-vocab.cpp:2890. If the keys are absent, the ids come
  from a token-text heuristic at llama-vocab.cpp:2999-3012. `get_key` applies
  `--override-kv` values through `try_override` (llama-model-loader.cpp:218-257).
  The flag itself is defined at arg.cpp:2949.
- llama-vocab.cpp was freshly fetched at 704366d: sha256
  75b8bcb686b9df653d9f3d69d8030da7da3db33a58bee127382cfc7ac05453a7. It is not in the
  lane snapshot.
- Live test on port 47734:
  `llama-server -m stories260K.gguf --host 127.0.0.1 --port 47734 -t 2 --override-kv tokenizer.ggml.fim_pre_token_id=int:3,tokenizer.ggml.fim_suf_token_id=int:4,tokenizer.ggml.fim_mid_token_id=int:5`.
  The same /infill request then returned **HTTP 200** with `"content":"l and as"` and
  `"tokens_evaluated":39`. Output is in ovr/infill.out.
- So a server launch flag does get past the guard. What stays true is that the output
  is nonsense, because the model has no fill-in-the-middle training [INFERENCE from
  the output text and the TinyStories model]. The "use a code model" advice is
  supported. The `/completion` fallback is supported (200 on the fixture), but it
  ignores `input_suffix`; it is plain prefix continuation.
- Smallest correction (SKILL.md:1092 next-action cell):
  "Model capability: the guard reads the model's fill-in-the-middle token ids. Use a
  code model that has them, or send the task to `/completion` (prefix only; the
  suffix is ignored). Forcing ids with `--override-kv tokenizer.ggml.fim_{pre,suf,mid}_token_id=int:N`
  passes the guard but does not give the model the skill."
  If the cell cites llama-vocab.cpp, a pinned snapshot plus a SOURCES row would be
  needed. Otherwise drop "not server configuration" and keep the rest.

## (5) SOURCES row S122 and the lesson Gate quote: holds

- corpus/SOURCES.md:134 S122:
  - URL `…/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5476`:
    the line is correct.
  - Anchor `server-context.cpp line 5476 @ 704366d76f87…; sha256 dd1de0f2…2329`:
    equals the fresh fetch.
  - Teaches "the E26-09 error emitted at server-context.cpp line 5476 and its guard,
    at commit 704366d76 only; not other builds": accurate.
  - The meaning cell repeats the SKILL.md text, which is correct per (3).
  - Kind `mined`, access date 2026-10-23, used-by `SKILL.md, registry/error-signatures-r26.json`.
  - Base 1560e4d8 SOURCES.md has 0 S122 rows, so the row is new.
- corpus/lessons/round-26.md:35: the Gate quote equals `src[5475].strip()`, which is
  line 5476 (python check gives `True`). It is 10 whitespace tokens, under the
  25-word cap. The access date is 2026-10-23.
- Since S122 "teaches" covers the guard only, the defect in (4) does not affect S122.

## Residual risk / gaps

- I did not run the frozen counter; it was not needed for this row. I did not
  inspect the full override server log; it shows no override or FIM lines at
  default verbosity, so the 200 response is the evidence.
- During the override test, my shell `kill $SP` failed ("kill: invalid usage").
  `timeout 90` bounded the server, and I stopped it with
  `pkill -TERM -f "llama-server.*--port 47734"` (PID 1454822). Afterwards
  `pgrep -af "llama-server.*--port 47734"` exited with 1 and
  `ss -ltn | grep -E ':4773[2-5]\b'` exited with 1. The llama-server processes still
  running are on ports 47740 and 47719, outside my block, and are not mine.

## Installs

None.

## Files written

- .ufo/waves/round-26/w2-falsify/advice/AttackE2609.md (this report)
- /fast/scratch/hyaku/kama-r26w2/AttackE2609/: run.py, run1/, run2/, ovr/{server.log,infill.out},
  server-context.cpp.fresh, server-common.cpp.fresh, llama-vocab.cpp.fresh
