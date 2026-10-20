VERDICT: confirm — the receipt's `metrics_not_enabled` expectation (HTTP status exactly 501 when the server runs without `--metrics`) is grounded in llama.cpp @704366d76 code, not merely in the README. The code path is `server-context.cpp` (handler) → `server-common.cpp` (error type→code) → `server_res_generator::error` (code→HTTP status). Two non-load-bearing gaps are recorded below: the lane's pin set omits `server-context.cpp`, and the source error message has a suffix that the pinned README example lacks.

## Chain, end to end

All line numbers are as of commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (tag b11755).

1. Route registration (pinned bytes, sha256 `24ede…`/manifest-verified):
   `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/sources/llama.cpp-704366d/server.cpp:280`
   `ctx_http.get ("/metrics",  ex_wrapper(routes.get_metrics));`
   Slot declared at `.../server-context.h:133` (`server_http_context::handler_t get_metrics;`).
   The router override at `server.cpp:242` (`routes.get_metrics = models_routes->proxy_get;`) is inside `if (is_router_server)` (`:231`), and `is_router_server` requires empty model/hf_repo/docker_repo (`:152-154`). C2 passes `-m`, so the normal handler is the one wired.

2. Handler branch (upstream @ commit; NOT in the lane pin set — see gap G1):
   `server-context.cpp:5301-5306`
   ```cpp
   this->get_metrics = [this](const server_http_req & req) {
       auto res = create_response(true);
       if (!params.endpoint_metrics) {
           res->error(format_error_response("This server does not support metrics endpoint. Start it with `--metrics`", ERROR_TYPE_NOT_SUPPORTED));
           return res;
       }
   ```
   There is no other early return before the `!params.endpoint_metrics` check.

3. Type→code mapping (pinned, sha256 `b4f4aae7…`, equals `pins.json`):
   `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/sources/llama.cpp-704366d/server-common.cpp:91-133`
   `:115-118` `case ERROR_TYPE_NOT_SUPPORTED: type_str = "not_supported_error"; code = 501;`
   `:128-132` returns `json {{"code", code}, {"message", message}, {"type", type_str}}`.

4. Code→HTTP status (upstream @ commit):
   `server-context.cpp:4872-4875`
   ```cpp
   void error(const json & error_data) {
       status = json_value(error_data, "code", 500);
       data = safe_json_to_str({{ "error", error_data }});
   }
   ```
   and the non-streaming write path at pinned `server-http.cpp:668`
   `res.status = response->status;` → the JSON `code` 501 becomes the HTTP status; body is `{"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with `--metrics`","type":"not_supported_error"}}`.

5. Why `!params.endpoint_metrics` holds in the receipt (supporting):
   `common/common.h:688` `bool endpoint_metrics = false;`; `common/arg.cpp:3632-3638` only `--metrics` sets it true (env `LLAMA_ARG_ENDPOINT_METRICS`). Pinned README:225 says `--metrics … (default: disabled)`; README:1133 "This endpoint is only accessible if `--metrics` is set."
   The harness child env is stripped to `CHILD_ENV_KEYS = ('PATH','HOME','LANG','LC_ALL','TMPDIR')` (`/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:73`, applied `:784`), so the env alias cannot flip the flag; receipt `child_env_keys` is exactly `["HOME","LANG","PATH"]`.

6. Docs concur on the 501 body: pinned `README.md:2368-2377` (heading "When /metrics or /slots endpoint is disabled") shows `"code": 501`, `"type": "not_supported_error"`. The installed binary's help agrees with the default: `llama-server --help` line 624 `--metrics  enable prometheus compatible metrics endpoint (default: disabled)`.

## Receipt evidence (what the check actually asserts)

- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/live/receipt.json` and `live/receipt-frozen-probe.json`:
  `captures.metrics = {"error": null, "path": "/metrics", "status": 501}` in both.
  `checks[metrics_not_enabled] = {documented_by: "llama.cpp tools/server README @ b11755: GET /metrics requires the --metrics flag; without it the endpoint answers exactly 501", observed: {status: 501}, passed: true}`.
- Launch argv in both receipts contains no `--metrics` (verified `argv.count('--metrics') == 0`; argv is `-m … --alias … --host 127.0.0.1 --port … -c 256 -t 1 --no-webui --offline`).
- The harness's check is strict equality, not "non-200": `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-llamacpp-live.py:889-893` requires `captures['metrics']['status'] is not None and captures['metrics']['status'] == 501`. The capture happens only after readiness (`:848-866` raises `SetupError` unless ready); `_capture` keeps only status/error/body hash (`:527`, `keep_body=False`), so the receipt makes no body/type claim — correctly so.
- Therefore the observed 501 is not a loading artifact: the loading middleware's 503 (`server-http.cpp:307-328`) would fail this check if captured, and it cannot precede the handler on a ready server.

## Gaps / corrections (do not change the verdict)

- **G1 — the code path is not pinned.** `pins.json` covers only `README.md`, `server-common.cpp`, `server-common.h`, `server-http.cpp`; `server-context.cpp` (the file with the 501 branch) is absent. I fetched it at the full commit and cross-checked two hosts: raw.githubusercontent and jsDelivr both give sha256 `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`. `server-common.cpp` and `server-http.cpp` fetches reproduced the pinned sha256 exactly (`b4f4aae7…`, `24ede172…`). Recommendation: add `tools/server/server-context.cpp` (optionally `common/common.h`, `common/arg.cpp`) to the pin set if the lane wants every check's code path inside the frozen evidence. The receipt's README-only `documented_by` is an accurate summary but not the complete proof chain for the phrase "answers" (HTTP status).
- **G2 — message drift between source and README.** Source message is `"This server does not support metrics endpoint. Start it with `--metrics`"` (`server-context.cpp:5304`); the pinned README example (`README.md:2374`) shows the prefix without the `Start it with …` suffix. The receipt does not quote the message, so this is cosmetic; build advice `CriticC2ToyModel.md:51` quotes the README wording as though it were the source string — imprecise, not load-bearing.
- **G3 — stale critique in build advice.** `RevengerRound1Live.md:138` describes the check as a `status != 200` predicate at `tools/kama-llamacpp-live.py:626-630`. The shipped tool now requires `== 501` at `:889-893`; the same file's line 249-250 advice ("treat as exact 501 if precision is wanted") is already satisfied. L1 should not repeat the non-200 characterization.
- **G4 — router-mode boundary.** `documented_by` says "the endpoint answers exactly 501" unconditionally. In router mode (`-m` absent, `server.cpp:152-154`) `server.cpp:242` replaces the handler with `models_routes->proxy_get`, which needs `?model` and can answer 400 first (README:1135; `server-models.cpp:2266-2278`). C2 is not router mode (argv has `-m`), so the receipt is valid; the generalized wording should stay scoped to a single-model server. [INFERENCE] a router proxying to a child without `--metrics` would still surface the child's 501, but I did not exercise that.

## What I ran (exit codes)

1. `ls -la .ufo/waves/round-16/sources/` → 0; only `README.md`, `server-common.cpp`, `server-common.h`, `server-http.cpp`, `server.cpp` under `llama.cpp-704366d/` (plus `pin.py`, `pins.json`).
2. `grep -n -i metrics <pinned *.cpp *.h>` → 0; hits include `server-http.cpp:60`, `server.cpp:242,280`, `server-common.h:395,486-512`.
3. `grep -n -i -E "metrics|501" <pinned README.md>` → 0; `:225`, `:1133`, `:2368-2374`.
4. `curl -fsSL https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` → 0; sha256 `dd1de0f2…`.
5. `curl -fsSL https://cdn.jsdelivr.net/gh/ggml-org/llama.cpp@704366d76…/tools/server/server-context.cpp` → 0; identical sha256 `dd1de0f2…` (cross-host).
6. `curl -fsSL …/tools/server/server-common.cpp` → 0; sha256 `b4f4aae7…` == `pins.json`. `…/tools/server/server-http.cpp` → 0; sha256 `24ede172…` == `pins.json`.
7. `curl -fsSL …/common/common.h`; `…/common/arg.cpp` → 0; `endpoint_metrics = false` (common.h:688), `--metrics` setter (arg.cpp:3632-3638).
8. `python3` extraction of both live receipts → 0; both show `captures.metrics.status == 501`, zero `--metrics` argv occurrences, `child_env_keys == ["HOME","LANG","PATH"]`.
9. `/home/vgpnk/.local/opt/llama-b11755/llama-server --help | grep -- --metrics` → PIPESTATUS[0] 0; `(default: disabled)` at line 624.
10. `pgrep -x llama-server` → 1 (no process); I started no server.

Scratch under `/tmp/kama-r16-ScoutMetricsSource/` was removed after the digests above were captured. **Installs/updates: none.**

## Limitations

- Source-level confirmation only: my item does not authorize starting llama-server, so I did not reproduce the 501 live. The installed binary is taken as b11755/704366d76 from the receipt (`server.sha256` present; not rebuilt here).
- `server-context.cpp` provenance is commit-addressed raw + jsDelivr agreement, not a lane pin; G1 states the consequence. GitHub's REST contents API returned 403 (unauthenticated rate limit), so it was not used.
