VERDICT: n/a — freshness lead, no declared claim; answer: none of the three graded mechanisms changed from b11755 (704366d76) to b11757 (13786fbb).

# Scout: llama.cpp releases after b11755 — server contract vs 704366d76

Read-only scout. Installed runtime verified: `~/.local/bin/llama-server` → `version: 0.7.0-dev (build 11755, commit 704366d76)`, matching the C2 baseline.

## 1. Releases after b11755

Source: GitHub compare API + Atom feed (`https://github.com/ggml-org/llama.cpp/releases.atom`); the unauthenticated REST releases endpoint was rate-limited (see Limitations), so tags were resolved with authenticated `gh api repos/ggml-org/llama.cpp/commits/<tag>`.

| tag | commit (full) | commit date | release published |
|---|---|---|---|
| b11755 (baseline) | `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` | 2026-10-20T11:02:05Z | 2026-10-20T11:22:04Z |
| b11756 | `d80619397c2ba5cf1366c29f7d43699ca3a159b9` | 2026-10-20T11:23:41Z | 2026-10-20T13:52:00Z |
| b11757 | `13786fbb3a1aaf4ff445c0b92d9f21cbe0af6d42` | 2026-10-20T11:30:50Z | 2026-10-20T11:30:50Z |

Exactly **two** releases exist after b11755. Newest build = **b11757**; b11756 was *published* later (13:52Z) than b11757 (11:30Z) due to build backfill, but both are ancestors/descendants as `ahead_by: 2` from `704366d76...13786fbb`, i.e. b11757 contains b11756. No b11754 or b11758 exists.

Release subjects (feed):
- b11756: `server : pass id_slot through the Anthropic /v1/messages conversion (#28554)`
- b11757: `CUDA: Clear CUDA graphs after legacy memory pool flush (#26771)`

## 2. Complete file delta b11755 → b11757

`gh api repos/ggml-org/llama.cpp/compare/704366d76...13786fbb` → `ahead_by: 2`, exactly **3 changed files**:

| file | status | changes |
|---|---|---|
| `ggml/src/ggml-cuda/common.cuh` | modified | 4 |
| `ggml/src/ggml-cuda/ggml-cuda.cu` | modified | 27 |
| `tools/server/server-chat.cpp` | modified | 2 |

The only server-side change is the Anthropic param allowlist in `server_chat_convert_anthropic_to_oai`:

> `-    for (const auto & key : {"temperature", "top_p", "top_k", "stream", "chat_template_kwargs"}) {`
> `+    for (const auto & key : {"temperature", "top_p", "top_k", "stream", "chat_template_kwargs", "id_slot"}) {`

(compare API patch, `tools/server/server-chat.cpp` @@ -590,7 +590,7 @@)

Neither `tools/server/server-http.cpp`, `tools/server/server.cpp`, `tools/server/server-context.cpp` nor `tools/server/README.md` appears in the delta. Raw fetches confirm byte-identity at b11757 vs 704366d76:

```
24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb  server-http.cpp   (both revisions)
2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4  server.cpp        (both revisions)
dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329  server-context.cpp (both revisions)
```

## 3. Loading 503 envelope — UNCHANGED

`https://github.com/ggml-org/llama.cpp/blob/b11757/tools/server/server-http.cpp#L307-L325`

It is a pre-routing middleware, not a per-route body, so it gates **every** path except declared frontend assets:

- L308 `if (!is_ready.load()) {`
- L309-311 frontend bypass: `return true; // frontend asset, allow it to load and show "loading"`
- L314 `res.status = 503;`
- L318 `{"message", "Loading model"},`
- L319 `{"type", "unavailable_error"},`
- L320 `{"code", 503}`
- L323 `"application/json; charset=utf-8"`

Documented contract, `tools/server/README.md:485-487`:

> `- HTTP status code 503`
> `  - Body: \`{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}\``
> `  - Explanation: the model is still being loaded.`

**Byte-form caveat (important for an "exact envelope" check).** The body is serialized by `safe_json_to_str` → `common_json::dump_safe()` → `nlohmann::ordered_json`, which preserves *insertion* order, compactly:

- `tools/server/server-common.cpp:1695-1697`: `std::string safe_json_to_str(const json & data) { return data.dump_safe(); }`
- `common/json.cpp:343-345`: `return as_json(this).dump(indent, ' ', false, ordered_json::error_handler_t::replace);` with `dump_safe(int indent = -1)` (`common/json.h:265`)
- `common/json.cpp:30-32` / `:168` cast the pimpl to `ordered_json`
- `tools/server/server-common.h:25`: `using json = common_json;`

[INFERENCE] Therefore the wire body is key-ordered as written in source — `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` — whereas README:486 lists `code, message, type`. The two are JSON-equal but **not byte-equal**. A grader that byte-compares against the README literal will fail a compliant server.

## 4. `/health` ready body — UNCHANGED

Handler binding, `tools/server/server.cpp:278-279`:

> `ctx_http.get ("/health",                   ex_wrapper(routes.get_health)); // public endpoint (no API key check)`

Definition, `https://github.com/ggml-org/llama.cpp/blob/b11757/tools/server/server-context.cpp#L5288-L5299`:

- L5288 `this->get_health = [this](const server_http_req &) {`
- L5289 `// error and loading states are handled by middleware`
- L5297 `res->ok({{"status", "ok"}});`

`ok()` sets the status explicitly, `server-context.cpp:4868-4871`:

> `void ok(const json & response_data) {`
> `    status = 200;`
> `    data = safe_json_to_str(response_data);`

So the ready response is exactly 200 `{"status":"ok"}` — single key, no `degraded`/`loading` variant emitted by the handler.

`degraded` does not occur anywhere in `tools/server` at b11757 (0 hits). The only occurrence in the extracted tree is unrelated: `common/hf-cache.cpp:469` `LOG_WRN("%s: switching to degraded mode\n", __func__);` (HuggingFace cache fallback). [OBSERVED] A `200 {"status":"degraded"}` is therefore a fabricated/foreign body, never produced by b11757.

Other ready/loading state facts unchanged:
- `tools/server/README.md:489` documents 200 `{"status": "ok" }`.
- `tools/server/server.cpp:284` `ctx_http.get ("/v1/models", ex_wrapper(routes.get_models));` — the route the probe must hit is unchanged in the route table.

## 5. Signal shutdown path — UNCHANGED

`https://github.com/ggml-org/llama.cpp/blob/b11757/tools/server/server.cpp#L29-L38`

> `static inline void signal_handler(int signal) {`
> `    if (is_terminating.test_and_set()) {`
> `        fprintf(stderr, "Received second interrupt, terminating immediately.\n");`
> `        exit(1);`
> `    shutdown_handler(signal);`

- Registration, L527-534, is conditional on `if (!is_run_by_cli)`, and L133 defines `bool is_run_by_cli = (argv == nullptr);`. A standalone `llama-server` invocation passes argv, so SIGINT **and** SIGTERM are both registered (`sigaction(SIGTERM, &sigint_action, NULL);`, L534).
- Non-router shutdown handler, L519-523: `shutdown_handler = [&](int) { mcp_mgr.shutdown(); /* this will unblock start_loop() */ ctx_server.terminate(); };`
- Blocking loop L576 `ctx_server.start_loop();`, then normal teardown, L590 `return 0;`

Consequences unchanged for C2's teardown predicate:
- SIGTERM → `terminate()` → unblocked `start_loop()` → `return 0` is the documented graceful path; rc 0 is expected.
- A **second** signal force-exits with `exit(1)`; a SIGKILL'ed child has rc -9. Both are distinguishable from the graceful path without consulting the harness's own `sigterm_sent` flag.
- A self-exit rc 0 with `sigterm_sent false` means the child exited without the harness's signal — the harness currently cannot distinguish this, matching review `ReviewLiveHarnessCode.md`.

## 6. Loading window is real and observable (unchanged)

`server.cpp` non-router branch binds the socket *before* loading, so the 503 envelope exists on the live port during load:

- L494 `if (!ctx_http.start()) {`
- L507 `if (!ctx_server.load_model(params)) {`
- L515 `ctx_http.is_ready.store(true);`

[INFERENCE] A harness that records the loading envelope must connect between L494 and L515; after L515 `/health` flips to 200 `{"status":"ok"}` and the 503 body becomes unreachable. This ordering is identical at 704366d76 (file byte-identical).

## 7. What this means for the round-17 claims (advice only)

- **C1 (calibration):** no bearing on the verdict-matrix mutants themselves — the probe contract targets stub rows, not a live server. But if any graded invariant is "loading envelope exact", it must compare *parsed* JSON (or the insertion-order literal above), never the README byte string.
- **C2 (operability):** the health and teardown predicates can cite a stable, unchanged upstream contract. Two concrete pins for `kama-llamacpp-live/v2`:
  1. Ready body = 200 with exactly one key `status` = `ok`; reject `degraded`, reject extra keys if byte-grading (use parsed compare).
  2. Graceful teardown = harness-sent SIGTERM → rc 0; treat rc -9 (SIGKILL) and `sigterm_sent false` as failures, not passes.
- **Freshness:** no migration work is forced by b11756/b11757. The delta is CUDA-internal plus one Anthropic param allowlist entry. [INFERENCE] Upstream nonetheless moved b11755→b11757 in ~30 min, so parsed-JSON assertions are the durable choice for a probe/gate that must survive tag churn.

## Limitations

- Did not build b11757, start a server, or capture a live 503 body; the exact byte string in §3 is [INFERENCE] from `ordered_json` + `dump_safe(-1)`, not from a capture. Round-16's real receipt (`{"status":"ok"}`, rc 0, sigterm_sent true) is consistent with §4/§5.
- Unauthenticated `api.github.com/repos/.../releases?per_page=15` returned `API rate limit exceeded` (280-byte body). Release list therefore comes from the Atom feed plus authenticated `gh api` commit resolution; tag→commit links were cross-checked for all three tags.
- `degraded` grep covered the extracted b11757 tree (`tools/server`, `common`, `vendor`), not the full repository.
- Only `tools/server` sources were inspected for the three mechanisms; no other subsystem was audited.

## Installs / updates

None. No pacman transactions attempted (host-wide pause observed); no `uv`, `npx` or binary installs. Scratch artifacts only: `/tmp/new/`, `/tmp/tree/`, `/tmp/llama_releases.json`, `/tmp/ll.tar.gz`.
