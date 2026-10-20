VERDICT: confirm — at 704366d76 `/metrics` without `--metrics` is HTTP 501 (NOT_SUPPORTED→`code = 501`), GET `/props` is ungated and carries `model_alias` = server model name, and `/v1/models` `data[].id` = that same name with `owned_by` `llamacpp`; all six round-17 pins still match this host's upstream bytes.

# Pins (opened 2026-10-20)

Commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (installed `llama-server` reports `build 11755, commit 704366d76`, readlink `~/.local/opt/llama-b11755/llama-server`).

Round-17 pinned copies under `.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/` hash **identically** to `.ufo/waves/round-17/sources/pins.json` and to a fresh fetch of the raw URL this round:

| file | sha256 | pins.json | live fetch |
|---|---|---|---|
| server-context.cpp | `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329` | match | match |
| server-http.cpp | `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` | match | match |
| server.cpp | `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` | match | match |
| README.md | `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37` | match | not fetched this round |
| server-queue.cpp | `168385b752fa70df9790f51179e34e375284a296cd44af92b41c5d25da32a2ba` | match | not fetched this round |
| server-queue.h | `d77a3eac479e8ad772b325db643225ea3e68a9715709e375d859295c31161924` | match | not fetched this round |

Four files cited below are **not** in `pins.json`'s six-file set; hashes measured this round (fresh raw fetch) and recorded here so L1 can pin them:

- `tools/server/server-common.cpp` `b4f4aae7eed919f914d132ae64416a0e7cfb23442161af6f63ba8d902954d442` (2147 lines)
- `tools/server/server-common.h` `ee401cf81ed0fb515f9870b018c762074903e72712dcb81a652e49761fe1577b`
- `common/arg.cpp` `bf4c58c189a774f2308acfe88e4ec5cebb0c43f60cf05cef4c5b2b9affd5822d`
- `common/common.h` `8bcc5708c856653b0094ba312030df9c2f43ec2703e8ad78474fd4339d2540a9`
- `common/common.cpp` `d10ea1ff4253a1d6aedef3e73f16c3f2297975ca17254a82fac395aa2213ebd4` (fetched to confirm `get_name` is *not* defined there; it is inline in `common.h`)
- `tools/server/server-http.h` `fafbdb8db708656d702f3cef1adb0d341a67d68d49636a5559b9769518b5e50a` (only `int status = 200;` matters)

[INFERENCE] Source hashes identify source, not the binary: the installed binary's own sha256 is `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`; build-id agreement is a version-string observation, not byte equivalence.

# 1. `/metrics` answers exactly 501 when disabled

Causal chain, in order:

1. Gate: `server-context.cpp:5301-5306` — quote `if (!params.endpoint_metrics) {` / `res->error(format_error_response("This server does not support metrics endpoint. Start it with \`--metrics\`", ERROR_TYPE_NOT_SUPPORTED));`
2. Flag → status mapping (different file): `server-common.cpp:115-117` — quote `case ERROR_TYPE_NOT_SUPPORTED:` `type_str = "not_supported_error";` `code = 501;`
3. Error object → HTTP status: `server-context.cpp:4872-4875` — quote `void error(const json & error_data) {` `status = json_value(error_data, "code", 500);`
4. Wire body: `server-common.cpp:128-132` returns keys in the order `code`, `message`, `type`, wrapped once more by `{"error", error_data}`, so the 501 body is `{"error":{"code":501,"message":"This server does not support metrics endpoint. Start it with \`--metrics\`","type":"not_supported_error"}}`.
5. Enabled path: `common/arg.cpp:3632-3638` — quote `{"--metrics"},` … `params.endpoint_metrics = true;`; default disabled in `common/common.h:688` — quote `bool endpoint_metrics = false;`
6. Docs agree: `README.md:1133` — quote `This endpoint is only accessible if \`--metrics\` is set.`; `README.md:225` — quote `` `--metrics` | enable prometheus compatible metrics endpoint (default: disabled) ``

Router-mode caveat: `README.md:1135` — quote `In *router mode* the query param \`?model={model_id}\` has to be set.` A control staged behind router mode would not exercise this gate as written.

# 2. GET `/props` is ungated and returns `model_alias`

- Body field: `server-context.cpp:5245` — quote `{ "model_alias",                 meta.model_name },`
- GET handler: `server-context.cpp:5438-5448` — quote `this->get_props = [this](const server_http_req &) {` — no `endpoint_props` test anywhere in it.
- Only POST is gated: `server-context.cpp:5450-5455` — quote `if (!params.endpoint_props) {` … `Start it with \`--props\``.
- Upstream documents this asymmetry itself: `common/common.h:687` — quote `bool endpoint_props   = false; // only control POST requests, not GET`
- Docs: `README.md:841` — quote `By default, it is read-only. To make POST request to change global properties, you need to start server with \`--props\``

Consequence for `props_alias`: passing or omitting `--props` is irrelevant; the control must corrupt the GET body's `model_alias` (or drop it — the tool's `.get('model_alias')` then yields `None`).

# 3. `/v1/models`: `id` = model name (alias), `owned_by` = literal `llamacpp`

- Both routes share one handler: `server.cpp:283-284` — quote `ctx_http.get ("/v1/models",                ex_wrapper(routes.get_models));`
- Envelope: `server-context.cpp:5196` `static json get_res_models(...)`, `5222-5225` — quote `{"data", json::array({` `get_res_model_info(meta),`
- `id`: `server-context.cpp:5172` — quote `{"id",       meta.model_name},`
- alias precedence: `server-context.cpp:1521-1526` — quote `if (!params_base.model_alias.empty()) {` `// backward compat: use first alias as model name` `model_name = *params_base.model_alias.begin();`
- fallback chain: `server-context.cpp:1524-1531` — `get_name()` then `model_path.filename().string()`; `common/common.h:312-320` `get_name()` returns `hf_repo`, else `docker_repo`, else `path`; `common/arg.cpp:3024-3035` splits `--alias` on commas, strips, inserts into a set.
- `owned_by`: `server-context.cpp:5182` — quote `{"owned_by", "llamacpp"},` (a literal, not derived).
- `aliases` array is a **separate** field: `server-context.cpp:5173` — quote `{"aliases",  meta.model_aliases},`
- Docs: `README.md:1284` — quote `By default, model \`id\` field is the path to model file, specified via \`-m\`.`; example at `README.md:1293` (`"id": "../models/Meta-Llama-3.1-8B-Instruct-Q4_K_M.gguf"`) and `README.md:1300` (`"owned_by": "llamacpp"`).

Cross-check, observed elsewhere (not by this seat, and not a substitute for L1's run): `corpus/knowledge/llamacpp-loading-lifecycle.md:127-128` — quote `/metrics` 501 (no `--metrics`); `/slots` 200.` with `data[].id` `kama-stories260k` and `owned_by` `llamacpp`.

Nuance for controls: `*model_alias.begin()` on a `std::set<std::string>` is the lexicographically smallest alias, not the first listed. [INFERENCE: `std::set` comparison is byte-lexicographic.] Always pass exactly one alias.

# 4. The six new bad controls: minimal discriminating mutation

Each row names the upstream truth, the tool assertion it must flip, and the one seam in the existing fake that isolates it. Tool = `tools/kama-llamacpp-live.py` (sha256 `0efd1723…c46ac`, identical to `.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py`); fake = `tests/llamacpp-live/controls.py` (`aad8b1c7…e3a06`, identical to frozen).

| control | upstream truth | tool assertion | minimal fake mutation | isolation |
|---|---|---|---|---|
| `models_alias_id` | `server-context.cpp:5172` + `1521-1523` | `1186-1189`: quote `bool(ids) and all(i == args.alias for i in ids),` | serve `MODELS_OK` with `id` = full model path (or `alias + "-x"`) | body at `controls.py:167-168`, served at `211-218`; mutate `id` only, leave `aliases` |
| `models_owned_by_llamacpp` | `server-context.cpp:5182` | `1190-1193`: quote `bool(owners) and all(o == 'llamacpp' for o in owners),` | `owned_by` → `"openai"` or `"llama.cpp"` (case matters) | same body, different key |
| `metrics_not_enabled` | `server-context.cpp:5301-5306`, `server-common.cpp:115-117`, `4872-4874` | `1195-1199`: quote `captures['metrics']['status'] == 501,` | answer `/metrics` 200 (or 404/405) instead of 501 | `controls.py:237-240` |
| `props_alias` | `server-context.cpp:5245` (GET ungated, `5438-5448`) | `1201-1206`: quote `props_fields.get('model_alias') == args.alias,` | `PROPS['model_alias']` → `"default"` (or delete key) | `controls.py:169-171` body, `233-234` handler |
| `probe_model_ok` | probe classify `tools/kama-probe.sh:539` quote `0) C_VERDICT=MODEL_OK; C_REASON=matched ;;` then `883` quote `[ "$EV_DRIFT" -gt 0 ] && return 2 \|\| return 0` | `1224-1230` quote `ok_probe['exit'] == 0` | serve a **wrong id only to the probe** (User-Agent contains `curl`) → MODEL_MISMATCH | `controls.py:216` already splits `'curl' in ua`; changing the shared `MODELS_OK` would also break `models_alias_id` |
| `probe_mismatch` | `tools/kama-probe.sh:541` quote `*) C_VERDICT=MODEL_MISMATCH; C_REASON='served-id-mismatch' ;;` | `1231-1237` quote `bad_probe['exit'] == 2` | serve `id == kama-not-this-model` (tool `MISMATCH_EXPECT`, line 81) to the *second* curl request → MODEL_OK exit 0 | count probe requests (`controls.py:216-217` `probe_models`); first probe keeps `args.alias` so `probe_model_ok` still passes |

Non-discriminating mutations to avoid (they pass — they would be vacuous "bad" controls):

- `metrics_not_enabled`: returning 501 with a *different body* still passes — the tool stores only `path/status/error` for `/metrics` (`tools/kama-llamacpp-live.py:704-706`). Also note the current fake's 501 body type is `unavailable_error` (`controls.py:238-240`) whereas real upstream emits `not_supported_error` (`server-common.cpp:116`); harmless today, but tightening the check to compare `type`/`message` would instantly turn the **good** control K0 into a failure. Change the fake to `not_supported_error` first.
- `models_alias_id`: mutating only `aliases` (`server-context.cpp:5173`) changes nothing the tool reads.
- `probe_*`: mutating the unfiltered `/v1/models` body flips `models_alias_id` too, so the failed check is un-attributable (R5 "failed targeted check").

# 5. Integration hazards for C1 (observed, actionable)

1. Receipt argv has neither `--metrics` nor `--props`: `tools/kama-llamacpp-live.py:1084-1093` quote `server_real, '-m', args.model,` … `'--offline',`. A control that adds `--metrics` to demo a 200 also invalidates the argv re-derivation unless the receipt records it; prefer a fake-server bad control for `metrics_not_enabled`.
2. `source_binding` is **produced but never consumed**: `grep -in binding tests/llamacpp-live/check-receipt.py` → no output. Existing bindings cover only `health_ready`, `loading_envelope_graded`, `teardown_graceful` (`tools/kama-llamacpp-live.py:866-933`); none of the six new checks has a binding. Adding six bindings without a gate-side verifier is a detector that cannot fail — R7/C2 material.
3. Binding helper is single-file/single-sha (`_binding(check,row,path,first,last,file_sha256,span_text)` at `843-855`) with only three sha constants (`858-863`). A code-backed `metrics_not_enabled` span needs `server-common.cpp` (sha `b4f4aae7…d442`), which no constant or pin covers today.
4. `/v1/models` and `/props` derive from the same `meta.model_name`, so the two controls are causally coupled at the source; isolate at the response layer (as in §4), never by changing argv.
5. Probe `check` exit vocabulary: `0` = every declared consumer reconciles, `2` = at least one drift, `1` = probe error (`tools/kama-probe.sh:890-891`), and a single `--port/--expect` row is graded at `841-851`, drift returned at `883`. `probe_mismatch` therefore expects 2, not any non-zero.

# 6. Pin and SOURCES gaps, with provisional rows

`pins.json` has no pin for `/metrics`, `model_alias`, `owned_by`, or the NOT_SUPPORTED→501 mapping (`grep -n "metrics\|owned_by\|model_alias\|props" .ufo/waves/round-17/sources/pins.json` → no match) and lists only the six files in §Pins. Recommended new pin keys (same JSON shape): `metrics_not_enabled_501` (server-context.cpp 5301-5306), `error_type_not_supported_501` (server-common.cpp 115-118), `props_model_alias` (5242-5245), `props_get_not_gated` (5438-5448 + common.h 687), `models_id_alias` (1521-1524 + 5172), `models_owned_by` (5182), `metrics_flag_enables` (arg.cpp 3632-3638 + common.h 688), `alias_parse` (arg.cpp 3024-3035), `model_get_name` (common.h 312-320).

Provisional SOURCES rows — **S051-S053**, because S048-S050 are already provisionally claimed by `ScribeSourcesKernel` (`.ufo/waves/round-18/build/advice/ScribeSourcesKernel.md:1`); L1 renumbers. Shape follows the registry header `corpus/SOURCES.md:11`.

- S051 — llama.cpp server error-type→HTTP-status mapping @ 704366d76 — `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-common.cpp` — code, tier A, scope: HTTP status for `ERROR_TYPE_NOT_SUPPORTED` on a b11755 server; anchor `format_error_response` 91-132, quote `case ERROR_TYPE_NOT_SUPPORTED:` `code = 501;` (server-context.cpp `error()` 4872-4874 sets the status from `code`); raw sha256 `b4f4aae7…d442`; mined, 2026-10-20, on-release; used-by `corpus/knowledge/llamacpp-loading-lifecycle.md`, C1 `metrics_not_enabled`.
- S052 — llama.cpp `--metrics`/`--props` enablement and defaults @ 704366d76 — same raw base under `common/arg.cpp` (`3632-3645`) and `common/common.h` (`687-688`) — code, tier A, scope: what each flag gates; anchor quote `bool endpoint_props   = false; // only control POST requests, not GET`; sha256 `bf4c58c1…822d` and `8bcc5708…40a9`; mined, 2026-10-20, on-release; used-by C1 `props_alias`, `metrics_not_enabled`.
- S053 — llama.cpp served model identity (`id`, `model_alias`) @ 704366d76 — server-context.cpp `1521-1531`, `5172`, `5245`; `common/arg.cpp` `3024-3035`; `common/common.h` `312-320` — code, tier A, scope: how `--alias`/path/GGUF name become the API model name, single-model mode; quote `// backward compat: use first alias as model name`; sha256 `dd1de0f2…2329`, `bf4c58c1…822d`, `8bcc5708…40a9`; mined, 2026-10-20, on-release; used-by C1 `models_alias_id`, `props_alias`.

README quotes (`225`, `841`, `1133`, `1284`) sit at the pinned commit; cite them as an anchored addition to the pinned-README row rather than a new `master` row (S001 is `master`, which carries drift risk).

# 7. Limitations

- Source-only recon: I ran no llama-server and no lane gate (measurements belong to L1). The 501 / `owned_by` / alias values above are code-derived; the only runtime corroboration cited is round-17's own run (`corpus/knowledge/llamacpp-loading-lifecycle.md:127-128`).
- `server-common.cpp`, `server-common.h`, `common/*`, `server-http.h` were fetched fresh this round, not byte-compared to a round-17 pinned copy (none exists); their hashes are recorded above for pinning.
- `pins.json`'s `files` map is authoritative only for the six files it lists.
- Router mode (`server.cpp:269-275`) is out of scope and would change both `/v1/models` and `/metrics`.

# 8. Installs

None. No pacman, no uv, no npm.
