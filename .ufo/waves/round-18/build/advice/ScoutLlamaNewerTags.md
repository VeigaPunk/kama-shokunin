VERDICT: confirm — the newest llama.cpp tag (b11759) is byte-identical to the pinned 704366d76 for every pinned server file; only unreleased master moves, and none of its changes touch /health, /v1/models, /props, /metrics, signal handling or the loading middleware.

# Scope
Read-only freshness recon: `tools/server/{server,server-context,server-http,server-queue}.cpp` pinned at 704366d76 (= tag b11755) vs the newest tag, plus a master-HEAD delta for early warning. No files written outside this Report; scratch dir `/tmp/kama-r18-ScoutLlamaNewerTags` removed at end. No installs.

# 1. Tags newer than b11757
`git ls-remote --tags https://github.com/ggml-org/llama.cpp`; numeric `b####` tags are the build tags (all `master-<sha>` tags are 2023-era, e.g. `master-fff0e0e` → commit date 2023-07-20, not new).

| tag | commit | commit date (UTC) |
|---|---|---|
| b11755 (pin) | 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad | 2026-10-20T11:02:05Z |
| b11756 | d80619397c2ba5cf1366c29f7d43699ca3a159b9 | 2026-10-20T11:23:41Z |
| b11757 | 13786fbb3a1aaf4ff445c0b92d9f21cbe0af6d42 | 2026-10-20T11:30:50Z |
| **b11758** | 83c2d012a273ff1f58fc145fe4219c332e5dd3a3 | 2026-10-20T11:31:10Z |
| **b11759 (newest)** | 522f2b6eedce1b1767e6aa81fcdb78a6f4cf82fa | 2026-10-20T11:31:35Z |

Newer than b11757: **b11758, b11759**. Source: `https://api.github.com/repos/ggml-org/llama.cpp/commits/<tag>` ("704366d76f 2026-10-20T11:02:05Z", "522f2b6eed 2026-10-20T11:31:35Z").

Installed binary matches the pin: `~/.local/opt/llama-b11755/llama-server --version` → `version: 0.7.0-dev (build 11755, commit 704366d76)`; `~/.local/bin/llama-server` symlinks to it. [OBSERVED]

# 2. sha256 at the newest tag (b11759) vs pins.json
`curl -fsSL https://raw.githubusercontent.com/ggml-org/llama.cpp/b11759/tools/server/<f> | sha256sum`

| file | b11759 sha256 | pins.json sha256 | equal |
|---|---|---|---|
| server.cpp | 2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4 | same | yes |
| server-context.cpp | dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329 | same | yes |
| server-http.cpp | 24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb | same | yes |
| server-queue.cpp | 168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba | same | yes |
| README.md | 714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37 | same | yes |
| server-queue.h | d77a3eac479e8ad772b325db643225ea3e68a9715709e375d859295c31161924 | same | yes |

Also byte-identical at b11756, b11757, b11758 for all four .cpp files (hashed per tag; all four hashes above).

**Conclusion:** at the newest tag, zero changed lines. No change to /health, /v1/models, /props, /metrics, signal handling, or the loading middleware.

# 3. Commits b11755 → b11759 (4 commits; only one touches tools/server)
`https://api.github.com/repos/ggml-org/llama.cpp/compare/704366d76...b11759` ("ahead_by 4 total_commits 4"):

| commit | subject | files | named-surface touch? |
|---|---|---|---|
| d80619397c | "server : pass id_slot through the Anthropic /v1/messages conversion (#28554)" | `tools/server/server-chat.cpp` +1 -1 | **no** — `/v1/messages` request conversion only (registered at server.cpp:295); not /health, /v1/models, /props, /metrics, signal, middleware |
| 13786fbb3a | "CUDA: Clear CUDA graphs after legacy memory pool flush (#26771)" | non-server | no |
| 83c2d012a2 | "spec : save the dynamic ngram cache file (#22055)" | non-server | no |
| 522f2b6eed | "ggml-zdnn: introduce flash attention op (#30512)" | non-server | no |

Per-commit file lists come from `https://api.github.com/repos/ggml-org/llama.cpp/commits/d80619397c` ("modified tools/server/server-chat.cpp +1 -1").

# 4. Master HEAD delta (b11759 → 52ffa027455662ea59f78d0e4e5a8f38ee63a5fe, 19 commits) — early warning
Hashes at master: `server.cpp` **unchanged**, `server-http.cpp` **unchanged**; `server-context.cpp` → 4184b692…, `server-queue.cpp` → 65c4a0e8…. `common/arg.cpp` (argv parsing, incl. `--host/--port/--api-key`) **unchanged** at master.

`diff -u <pin> <master>/server-context.cpp` = 5 hunks (15 added / 9 removed lines). Mapped to commits:

| hunk (pin line) | change (verbatim) | commit | named-surface touch? |
|---|---|---|---|
| ~1183 | `if (has_mmproj && params_base.fit_params && !is_resume) {` — comment "on resume params_base already holds the margin from the first load" | 5a9a34d888 "server : avoid repeated mmproj memory margin addition on sleep/resume (#28233)" | no — sleep/resume fit only |
| 4521–4540 | `auto spec_i_batch = std::move(slot.spec_i_batch);` replacing `slot.spec_i_batch` across the accept calls | ead9f32058 "server: Support logprobs with speculative decoding (#27196)" | no — speculative-decode acceptance |
| 4635 | `if (slot.task->params.sampling.n_probs > 0 && !slot.task->params.post_sampling_probs) {` `populate_token_probs(..., spec_i_batch[i]);` | ead9f32058 | no — completion logprobs payload, not the named endpoints |
| 5895 | `const json state = decision.prepare_state(decision.parse_state(body, files));` | 7e3eeee048 "model : add H2O-Lightning-4B decision model (#30361)" | no — `post_systemone` decision endpoint only |

`diff -u <pin> <master>/server-queue.cpp` = 2 hunks (2 added / 1 removed lines):
```
+    const auto deadline = std::chrono::steady_clock::now() + std::chrono::seconds(timeout);
-        std::cv_status cr_res = condition_results.wait_for(lock, std::chrono::seconds(timeout));
+        std::cv_status cr_res = condition_results.wait_until(lock, deadline);
```
Commit 4e201388c3 "server: Router wasn't propagating the client disconnects fully to the child, the response wait could cause a delayed cancellation (#29707)" (also `tools/server/server-models.cpp` +2 −1: `this->cleanup_pipes = [pipe, cli]() { … cli->stop(); };`). Classification: **no** for the six named surfaces; it changes timeout accounting for task-result waits (completion-style handlers) and router child-client teardown. [INFERENCE] It could only matter to a probe that waits on a queued task during teardown; it does not alter /health, /v1/models, /props, /metrics, the middleware, or signal registration.

Also in the 19-commit range: 1ba568c5ad "server: fix missing output_index in Responses API SSE events" (`server-task.cpp` +21) — Responses SSE only; not named.

# 5. The named surface is intact (registration → handler, pin and master)
- `/health`, `/v1/health` registration: `tools/server/server.cpp:278-279` "ctx_http.get (\"/health\", … routes.get_health)); // public endpoint (no API key check)". server.cpp identical at b11759 and master → registration and signal handling unchanged (pin ranges 529-534 SIGINT/SIGTERM, 519-523 single-mode shutdown handler, 462-469 router shutdown handler all inside the identical file).
- `/metrics`: `server.cpp:280` → `get_metrics`; `/props`: `server.cpp:281-282` → `get_props`/`post_props`; `/v1/models`: `server.cpp:284` → `get_models`.
- Handler bodies: pin `server-context.cpp` `get_health` 5288, `get_metrics` 5301, `get_props` 5438, `post_props` 5450, `get_models` 5725; master 5294 / 5307 / 5444 / 5456 / 5731 — a uniform **+6** offset from the hunks above, i.e. bodies byte-identical, every changed hunk lies outside them.
- Loading middleware: `tools/server/server-http.cpp:307-328`; file identical at b11759 and master, so the envelope is unchanged: `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` (`server-http.cpp:316-322`, `res.set_content` at :315) with `res.status = 503` at :314. `is_ready` is set after model load in single-model mode (`server.cpp:515` "ctx_http.is_ready.store(true);") and immediately in router mode (`server.cpp:460`).
- Precedence that C1 relies on: `middleware_server_state` runs before `middleware_validate_api_key` (`server-http.cpp:354` vs :357), so during loading an unauthenticated `/v1/models` still gets the 503 envelope, not 401 — stable at pin, b11759 and master.
- Fields C1 pins on /v1/models: `{"id", meta.model_name}` `server-context.cpp:5172`, `{"aliases", meta.model_aliases}` :5173, `{"owned_by", "llamacpp"}` :5182, assembled by `get_res_models` at :5196 (`{"data", json::array({ get_res_model_info(meta) })}` :5223). `/props` carries `{ "model_alias", meta.model_name }` :5245. `/metrics` without `--metrics` returns the NOT_SUPPORTED error (:5304 "This server does not support metrics endpoint. Start it with `--metrics`"). All unchanged through b11759 and master.
- Signal teardown chain (`sigaction(SIGINT/SIGTERM)` → `shutdown_handler` → `ctx_server.terminate()` → `queue_tasks.terminate()`, server.cpp:529-534, 519-523, server-queue.cpp:132-136) lives entirely in files that are identical at b11759; only master's `recv_with_timeout` deadline (above) is new, and it does not touch `terminate()`.

# 6. Implications for round 18
- The declared claims and the tool's 3.14/kernel/RFC sourcing need no refresh for llama.cpp: the pinned receipt-facing behavior (loading envelope, /v1/models field names, /props alias, /metrics disabled error, SIGINT/SIGTERM teardown) is valid at the newest tag. Upgrading the pin from b11755 to b11759 would change **no server code**.
- If anyone proposes re-pinning later, the first thing to re-check is master's `recv_with_timeout` deadline (cancellation timing) even though it misses the six named surfaces.

# Limitations
- Source-only recon; no build or run of b11758/b11759, no measurement, no gate run.
- Four assigned files compared at every tag in the range; README.md, server-queue.h compared at b11759; server-models.cpp/server-task.cpp at master only; common/arg.cpp at b11755/b11759/master. Not fetched: server-chat.cpp, server-stream.cpp, server-common.cpp, server-decision.cpp, server-mcp.cpp at b11759/master (server-chat.cpp's only b11755→b11759 change is classified from the commit API, not a fetched diff).
- `tools/server/server-params.cpp` does not exist at b11755/b11759 (404); server argv parsing is `common/arg.cpp` (`{"--host"}` :3335, `{"--port"}` :3351, `{"--api-key"}` :3533), byte-identical at b11755, b11759 and master. [INFERENCE] `--host/--port/--api-key` parsing semantics therefore unchanged.
- master is unreleased and not a tag; its 19 commits may be amended before b11760.
- [INFERENCE] "Does not touch the named surface" is judged by diff hunk location and commit file lists, not by executing newer builds.
- Remaining unknown: whether master's `server-stream.cpp`/`server-common.cpp` changes (files not fetched) alter chunked/SSE framing in ways a probe would observe; not a named surface.

# Installs
None.
