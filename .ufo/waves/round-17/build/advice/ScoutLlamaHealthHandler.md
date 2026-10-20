VERDICT: confirm — at 704366d76 the only ready-state `/health` 200 body is exactly `{"status":"ok"}` (15 bytes); no slots/error 200 path exists.

# Scout — llama.cpp `/health` handler and its ready-state 200 body (C2 source)

Commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad, read from raw.githubusercontent.com and from
the commit tarball; `server-context.cpp` is byte-identical to the pinned lane copy
`.ufo/waves/round-16/sources/llama.cpp-704366d/server-context.cpp` (sha256
`dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`). Read-only: no server was
started, no gate or measurement script was run, and nothing in the lane was edited.

## 1. The handler

`server_routes::get_health`, built in `server_routes::init_routes`, answers both `/health` and
`/v1/health`.

- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L5288-L5299
  - L5288: `this->get_health = [this](const server_http_req &) {`
  - L5289: `// error and loading states are handled by middleware`
  - L5290: `auto res = create_response(true);` — `true` is `bypass_sleep`, so the endpoint
    answers during `--sleep-idle-seconds` idle (README:2335 and the exempt list at 2341-2342).
  - L5294-5295: `bool ctx_server; // do NOT delete this line` / `GGML_UNUSED(ctx_server);` —
    a deliberate guard so the handler cannot touch model state.
  - L5297: `res->ok({{"status", "ok"}});`
- Registration: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server.cpp#L278-L279
  - L278: `ctx_http.get ("/health",                   ex_wrapper(routes.get_health)); // public endpoint (no API key check)`
  - L279 registers `/v1/health` to the same handler.

## 2. The exact body literal (not the README spelling)

`ok()` sets status 200 and stores the serialized JSON; there is no whitespace, no newline.

- https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp#L4868-L4871
  - L4869: `status = 200;`
  - L4870: `data = safe_json_to_str(response_data);`
- `safe_json_to_str` → `data.dump_safe()`:
  https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp#L1695-L1697
  (`return data.dump_safe();`).
- `dump_safe` with the default `indent = -1` is a compact dump:
  https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/common/json.cpp#L343-L344
  (`dump(indent, ' ', false, ordered_json::error_handler_t::replace)`).
- Wire form is therefore the 15-byte string `{"status":"ok"}`; content type comes from the
  response default `application/json; charset=utf-8`
  (https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.h#L22).
- The README documents the same object with different spacing — `{"status": "ok" }` at
  https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md#L488-L489.
  A check must pin parsed JSON equality or the 15-byte literal, never the README bytes.

Runtime cross-check already in the lane (not a new run):
`.ufo/waves/round-16/live/receipt.json:21-36` (health object) records `"body": "{\"status\":\"ok\"}"`,
`"Content-Length": "15"`, `"Content-Type": "application/json; charset=utf-8"`, and
`body_sha256 a29ee2b15c494311c52521766e44af56a3ad2248e7a8ab465e5206463c13d288`
(receipt line 24; Content-Length at line 30). I recomputed sha256 over the 15-byte literal and
it equals `a29ee2b1…d288`; the 16-byte variants `{"status": "ok"}` and the same literal plus a
trailing newline hash differently. Source and observed body are the same bytes for the
installed b11755 tree.

## 3. Can `/health` answer 200 with any other body once ready?

No, on the read evidence below. Other outcomes exist only with non-200 status, or with a
non-GET method:

- **Handler has one branch.** `get_health` calls `res->ok({{"status","ok"}})` unconditionally
  (L5297); it never reads slots, metrics or error state (the dummy `ctx_server` at 5294-5295
  exists to prevent that), so a slots-shaped or error-shaped 200 cannot originate here.
- **The 503 loading envelope cannot return after ready.** `is_ready` starts false
  (https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.h#L71)
  and `grep -rn is_ready tools/server` finds only `store(true)` at server.cpp:460 (router,
  before startup models load) and server.cpp:515 (single-model, after `load_model`); the lane
  harness runs single-model. No `store(false)` exists, so the gate
  `if (!is_ready.load())` (server-http.cpp:308) is one-way for the life of the process.
  [INFERENCE] absence of a reset is from exhaustive grep + reads of those files, not a run.
- **The loading body is a 503, with its own text.** server-http.cpp:307-325 sets
  `res.status = 503;` and `{"message", "Loading model"}`, `{"type", "unavailable_error"}`,
  `{"code", 503}` (L314, L317-321) — before the handler, and with no `/health` exemption.
- **`/health` never needs a key**, so 401 cannot replace the body:
  server-http.cpp:251-258 lists `"/health"` and `"/v1/health"` as public endpoints, and
  `server.cpp:278` repeats `public endpoint (no API key check)`.
- **Handler exceptions become 500, not 200.** `ex_wrapper` catches and sets `res->status = 500;`
  (server.cpp:56-80, L80); any throw from `create_response` or serialization would surface as
  that 500, never as a 200 with an error body.
- **Method caveat — `OPTIONS` yields 200 with an empty body.** The pre-routing CORS branch
  answers before the state gate: server-http.cpp:347 `if (req.method == "OPTIONS") {` and
  server-http.cpp:351 `res.set_content("", "text/html"); // blank response, no data`. A probe
  that ever used OPTIONS could see 200 with no body, so the body check must issue GET.
- **Route-path caveat `--api-prefix` [INFERENCE].** Routes are registered as
  `path_prefix + path` (server-http.cpp:690) while the public set compares the literal
  `"/health"` (251-258); with `--api-prefix` and `--api-key` together, the prefixed health
  path would fall under key validation and the bare `/health` would 404. Not reachable in the
  lane's harness: its argv passes neither flag
  (`tools/kama-llamacpp-live.py:860-869`, plain `--host 127.0.0.1 --port … --no-webui --offline`).

Consequence for C2: a 200 with a body other than `{"status":"ok"}` cannot come from this
llama.cpp handler at this commit — the branch does not exist. [INFERENCE] Such a response
means the answerer is something else (a proxy, a stale listener, a fake), which is exactly
the misbehaviour a body/headers check is able to catch and a status-only check cannot. The
claim's illustrative `{"status":"degraded"}` therefore marks a foreign responder, not a
llama.cpp state.

## 4. What this licenses in the harness (advice, not verdict)

`health_ready` currently grades only `captures['health']['status'] == 200`
(`tools/kama-llamacpp-live.py:937-939`), although `ready_captures` already stores the body,
`Content-Length` and `body_sha256` (`:567-571`). The fail-capable predicate the source
supports is exact: GET 200, body parses to `{"status":"ok"}`, body length 15, content type
`application/json; charset=utf-8`. Grading the stored `body_sha256` against
`a29ee2b1…d288` is a one-line check over data the tool already captures.

## 5. Candidate SOURCES row (refinement of the drafted S042)

`corpus/SOURCES.md` ends at S041 (`grep -oE '^\| S[0-9]{3}' corpus/SOURCES.md`); S042 is
already drafted for this exact URL by ScribeSourcesRows
(`.ufo/waves/round-17/build/drafts/sources-rows.md:11`), so this is a strengthened version of
that draft — not a second claim on the id. Other seats also proposed S042 for different
sources; L1 assigns ids. Append-ready, 11 columns:

| S042 | llama.cpp `/health` route handler @ 704366d76 (release b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp | code | A | llama.cpp `/health` success body and the boundary that no other 200 body is produced once ready, at commit 704366d76 (single-model and router); the 503 loading refusal is S036 and `/v1/models` is not this handler | `get_health` 5288-5299 (comment 5289, body 5297, dummy `bool ctx_server;` 5294); `server_res_generator::ok` 4868-4871; `safe_json_to_str` `server-common.cpp:1695-1697` and compact `dump(indent, ' ', …)` `common/json.cpp:344`; public registration `server.cpp:278-279`; `is_ready` init false `server-http.h:71`, only `store(true)` at `server.cpp:460`,`515`; blank 200 for OPTIONS `server-http.cpp:347-351`; raw file sha256 dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | The handler has one success branch, `{"status": "ok"}`, serialized compactly to 15 bytes; `is_ready` is only ever set true, so after ready the S036 503 envelope cannot return and no slots/error 200 body is produced. [INFERENCE] One-way `is_ready` is from code reads, not a run. | mined | 2026-10-20 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md |

Gate line for `lessons/round-17.md` §Gate, if L1 wants the narrower admission:

| Candidate | Decision | Source, location, quote |
|---|---|---|
| A ready `/health` 200 carries only `{"status":"ok"}`, no whitespace, 15 bytes | admit | S042 `server-context.cpp:5297` `res->ok({{"status", "ok"}});` + `:4869` `status = 200;`; compact dump `common/json.cpp:344`; lane receipt body_sha256 `a29ee2b1…d288` |
| A non-literal `/health` 200 body can be llama.cpp's ready response | reject | S042 one-branch handler (`:5297`); a different 200 body can only come from a non-llama.cpp answerer — that is the fault the check must catch |
| A `/health` status check is enough to grade readiness | reject | S042 `:5289` "error and loading states are handled by middleware"; status alone cannot separate a foreign 200 from the handler's |
| Once ready, `/health` can fall back to the 503 loading body | reject | S042 `is_ready` init false `server-http.h:71`; only `store(true)` at `server.cpp:460`,`515` |

## 6. Limitations

- Source-level only; the installed b11755 binary was not disassembled or run by this seat.
  The source→runtime link rests on the existing round-16 receipt (sha256 match above).
- `is_ready` one-way is a grep/read result, not a test; a future commit could add a reset
  (this row is scoped `on-release`).
- HEAD request behaviour through cpp-httplib was not read; the OPTIONS 200-with-empty-body
  finding is the only confirmed non-GET 200 for the path.
- The public-endpoint/`--api-prefix` interaction is [INFERENCE] from reading registration and
  middleware; not exercised.

## 7. Installs

None. No tool was installed, upgraded or removed; no network tooling was added. Only `curl`,
`grep`, `awk`, `sha256sum` and `python3` from the host were used. Artefacts fetched into
`/tmp` (`llama7043-*.cpp/.h`, `llama7043.tar.gz`, extracted
`/tmp/llama.cpp-704366d76…/`) are scratch only and outside the lane.
