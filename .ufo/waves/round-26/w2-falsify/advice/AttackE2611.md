ATTACK E26-11 (`Request body must be an array`, S124 = server-context.cpp:5998): holds

The row reproduces, the signature is the fault's own text, and the source, line and status claims are exact. Two low-severity wording findings (the meaning cell and the next-action cell) are completeness issues, not falsifications; neither affects the C1 count.

Seat: KamaR26.AttackE2611 (read-only attack). Port block 47740-47743; only 47740 used, one child at a time, `-t 2`, under `timeout`.

## (1) Live re-run of the registered trigger — holds

Registry `registry/error-signatures-r26.json:267-292`: channel `http`, args `["-t","2"]`, model `fixture`, `POST /lora-adapters`, header `Content-Type: application/json`, body `{"id": 0, "scale": 1.0}`. Launch argv as the counter builds it: `~/.local/bin/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 47740 -t 2`.

Pins checked first: `sha256sum` llama-server = `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804` (also the resolved `~/.local/opt/llama-b11755/llama-server`), model = `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; `--version` → `version: 0.7.0-dev (build 11755, commit 704366d76)`. `ss -ltn` showed 47740-47743 free before start.

Command: `timeout 240 bash run.sh 1` then `timeout 240 bash run.sh 2` (script in out/AttackE2611/run.sh), each exit 0.

| run | health | status | raw body |
|---|---|---|---|
| 1 | 200 | HTTP 400 | `{"error":{"code":400,"message":"Request body must be an array","type":"invalid_request_error"}}` |
| 2 | 200 | HTTP 400 | `{"error":{"code":400,"message":"Request body must be an array","type":"invalid_request_error"}}` |

Both runs: `server exit 0` after SIGTERM, `port 47740 closed`. Byte-identical to the tip receipt excerpt (`.ufo/waves/round-26/final/c1-tip-receipt.json:289`, status 400, all checks true, `counted: true`).

## (2) F1/F2/F3 — holds

- F1 (warning or unrelated-path line): the channel is the http response body, not the log. The signature has exactly one emit site in the 13 pinned sources and in the fresh fetch: `grep -rn 'Request body must be an array'` → only `server-context.cpp:5998` (exit 0). It is the `res->error(...)` of the `!body.is_array()` guard, not a log or warning line. Server logs of all three of my runs contain it 0 times; `llama-server --help` (exit 0) contains it 0 times.
- F2 (echo through a decoded request field): the request bytes are path `/lora-adapters`, header `Content-Type: application/json`, body `{"id": 0, "scale": 1.0}`. There are no string values in the body, so a `\uXXXX`-escaped copy of the signature is impossible, and no query string is involved. The message is a C++ literal, not built from input.
- F3 (argument file): args are `-t 2` only. There is no file argument.

## (3) Pinned source and the meaning (code) cell — holds; one low-severity wording finding

Fresh fetch (2026-10-23, `curl -sSfL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/<f>`, each exit 0). The sha256 values equal the lane snapshot and the counter pins:

- server-context.cpp `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`
- server-common.cpp `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442`
- server.cpp `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`
- server-http.cpp `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`

Code at 704366d:
- `server-context.cpp:5994` is `this->post_lora_adapters = [this](const server_http_req & req) {`; `:5996` is `const json body = json::parse(req.body);`; `:5997` is `if (!body.is_array()) {`; `:5998` is the error; `:5999` is `return res;`. The cited range `5994-5999` covers the guard.
- Route registration: `server.cpp:316` `ctx_http.post("/lora-adapters", ex_wrapper(routes.post_lora_adapters));`.
- Status claim 400: `format_error_response` maps `ERROR_TYPE_INVALID_REQUEST` to `code = 400` (`server-common.cpp:95-97`). Observed 400 twice.

Finding M1 (low; wording, not counted-claim): the cell says "the LoRA route requires a JSON array of `{id, scale}` entries". The cited lines enforce only "is a JSON array". Entry shape is not validated:
- `parse_lora_request` (`server-common.cpp:280-291`) reads each entry with `json_value(entry, "id", -1)` and `json_value(entry, "scale", 0.0f)`.
- `json_value` (`server-common.h:44-56`, fresh fetch sha256 `ee401cf81ed0fb515f9870b018c762074903e72712dcb81a652e49761fe1577b`) returns the default for a missing key, a non-object or a wrong type.
- Live (run3.out): `[1, "x", {"scale": 2}]` → HTTP 200 `{"success":true}`.
- Also live (run1.out): a JSON string body `"x"` → the same 400 signature, so the guard fires on any non-array JSON value, not only objects. Non-JSON bodies take a different path: a json parse_error 400 (`not json`, empty body).

Smallest correction: "the LoRA route refuses any JSON body that is not an array (`server-context.cpp:5996-5999`); entries are documented as `{id, scale}` but not validated (`server-common.cpp:280-291`)".

## (4) Next action cell — holds (supported, no overreach); one low-severity completeness finding

Cell: "Client bug: wrap the entries in an array; read valid ids from `GET /lora-adapters`."

It is supported by the code (array guard above) and by the upstream README at 704366d. Fresh fetch `tools/server/README.md`, sha256 `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`; there is no lane snapshot of README.md. README lines 1235-1250 show the array request format, and line 1243 says "To know the `id` of the adapter, use GET `/lora-adapters`". It is also supported live: the wrapped body `[{"id": 0, "scale": 1.0}]` → HTTP 200 `{"success":true}`.

Finding N1 (low; omission, not overreach): after a client follows the advice, a 200 confirms nothing about the ids.
- Live: the fixture has no adapters (`GET /lora-adapters` → `[]`, HTTP 200), yet `[{"id":0,"scale":1.0}]` → `{"success":true}`, as does `[]`.
- Code: `construct_lora_list` (`server-context.cpp:1837-1847`) iterates only over the loaded adapters, ignores unknown ids, and sets every adapter not listed to scale 0. The SET_LORA handler stores the result and replies success (`server-context.cpp:3175-3187`). README:1239 states the removal semantics.

Wrapping only the one entry from a bad request therefore silently disables every other loaded adapter.

Smallest correction: append to the cell "A 200 `{\"success\":true}` does not validate ids (unknown ids are ignored); send the full list, because every adapter left out is set to scale 0 (`server-context.cpp:1837-1847`)."

## (5) SOURCES S124 and the lesson Gate quote — holds

- `corpus/SOURCES.md:136`, URL `.../704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5998`: line 5998 is the emitting line (verified above).
- Anchor cell: `server-context.cpp line 5998 @ 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad; sha256 dd1de0f2...b603c2329`. This equals the fresh fetch and the counter pin `count-c1.py:67`.
- Teaches cell: "the LoRA route requires a JSON array of `{id, scale}` entries (`server-context.cpp:5994-5999`)". It carries the same M1 imprecision; apply the same correction there.
- Scope cell ("the E26-11 error emitted at server-context.cpp line 5998 and its guard, at commit 704366d76 only"): correct.
- Lesson Gate `corpus/lessons/round-26.md:37`: the quote `res->error(format_error_response("Request body must be an array", ERROR_TYPE_INVALID_REQUEST));` equals `server-context.cpp:5998` byte for byte after leading indentation (8 words, within ≤25). The access date 2026-10-23 matches this fetch.
- `.ufo/waves/round-26/final/census-validate.out:40` W04 "duplicate url ... server-context.cpp across scopes": this is one of 49 W04 lines. [INFERENCE] The validator compares URLs without the `#L` fragment, so every server-context.cpp row warns. It is not an S124-specific defect.

## Residual risk and verification gaps

- I did not run the frozen counter (not needed for this row; the tip receipt already shows E26-11 counted, and peer RerunC1AtTip owns the re-run).
- The emit-site uniqueness check covers the 13 pinned files plus my fresh server-common.h. Other files of the llama.cpp tree at 704366d were not searched; [INFERENCE] they are not on the `/lora-adapters` path.
- I did not test behavior with real LoRA adapters loaded (`--lora`): there is no adapter fixture. The scale-0-for-omitted claim rests on code and README, not on a live observation.
- Process hygiene: run 3's in-script `kill` failed (`kill: invalid usage`; the background PID was not captured under the tool's shell). I sent SIGTERM to my pid 1465723 by hand. The script's `wait` then returned, and run3.out ends `server exit 0` and `port 47740 closed`. Afterwards `pgrep -af 'llama-server.*--port 4774[0-3]'` exited 1 (none). The llama-servers seen on ports 47565 (the counter's range) and 47719 (another seat's block) are not mine.

Installs: none.

## Files written

- `.ufo/waves/round-26/w2-falsify/advice/AttackE2611.md` (this report)
- `.ufo/waves/round-26/w2-falsify/out/AttackE2611/`: `run.sh`, `run1.out`, `run2.out`, `run3.out`, `server-run1.log`, `server-run2.log`, `server-run3.log`, `fresh-fetch.sha256`
- Scratch: `/fast/scratch/hyaku/kama-r26w2/AttackE2611/` (fresh-fetched sources, `help.txt`, the same run files)
