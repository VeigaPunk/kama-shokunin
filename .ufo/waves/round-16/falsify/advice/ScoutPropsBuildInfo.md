VERDICT: confirm — llama.cpp @704366d76 unconditionally emits `model_alias`, `build_info`, `is_sleeping`, and `default_generation_settings.n_ctx` in every GET `/props` 200 body; the receipt's four props fields are real, correctly typed, and sourced from that response body. Two non-blocking gaps are recorded below: the README at the same commit does not mention `model_alias`, and the receipt gate validates only `model_alias` of the four.

# What I attacked

The C2 live receipt's `captures.props.fields` claims:

```json
{"build_info": "b11755-704366d76",
 "default_generation_settings.n_ctx": 256,
 "is_sleeping": false,
 "model_alias": "kama-stories260k",
 "total_slots": 4}
```

(`.ufo/waves/round-16/live/receipt.json`, `captures.props`, status 200, Content-Length 2070, `body_read_truncated: false`; identical five-field object in `receipt-frozen-probe.json`.)

I checked each claimed field against the upstream source at commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (tag b11755) and against the shipped artifact.

# Chain, end to end

All line numbers are as of `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`. `server-context.cpp` is not in the lane pin set (gap G1); I fetched it at the full commit and cross-checked two hosts.

1. Route wiring binds GET `/props` to `server_routes::get_props`.
   Pinned `.../sources/llama.cpp-704366d/server.cpp:281`
   `ctx_http.get ("/props",                    ex_wrapper(routes.get_props));`
   The router override (`routes.get_props = models_routes->get_router_props;`) is at `server.cpp:268`, inside `if (is_router_server)` (`:231`); `is_router_server` requires empty model/hf_repo/docker_repo (`server.cpp:152-155`). The receipt argv contains `-m …/stories260K.gguf`, so this is **not** router mode and the normal handler is wired.

2. Metadata is attached after load, before the readiness flag.
   `server.cpp:514` `routes.update_meta(ctx_server);` — immediately after `load_model` (`:508`) and before `ctx_http.is_ready.store(true)` (`:515`). So a 200 `/props` necessarily sees populated metadata.

3. `update_meta` copies `server_context::get_meta()` into the route's `meta`:
   `server-context.h:126-127` `this->meta = std::make_unique<server_context_meta>(ctx_server.get_meta());`
   Fields exist in `server_context_meta`: `std::string build_info; std::string model_name; int slot_n_ctx;` (`server-context.h:17,18,28`).

4. `get_meta()` fills those fields (upstream @ commit):
   `server-context.cpp:4818` `/* build_info */ std::string(llama_build_info()),`
   `server-context.cpp:4819` `/* model_name */ impl->model_name,`
   `server-context.cpp:4829` `/* slot_n_ctx */ impl->n_ctx_slot(),`

5. The handler serializes them (upstream @ commit, `server-context.cpp:5229-5280`):
   ```cpp
   static json get_res_props(const server_context_meta & meta, const common_params & params, bool is_sleeping) {
       ...
       json default_generation_settings_for_props = json {
           { "params", tparams.to_json(true) },
           { "n_ctx",  meta.slot_n_ctx },
       };
       ...
       json props = {
           { "default_generation_settings", default_generation_settings_for_props },   // :5243
           { "total_slots",                 params.n_parallel },                       // :5244
           { "model_alias",                 meta.model_name },                         // :5245
           ...
           { "build_info",                  meta.build_info },                         // :5263
           { "is_sleeping",                 is_sleeping },                             // :5264
           ...
       };
   ```
   None of the four keys is conditional, and `props.erase(...)` is never called.

6. GET route always serves a body with them:
   `server-context.cpp:5438-5446`
   ```cpp
   this->get_props = [this](const server_http_req &) {
       auto res = create_response(true);
       if (queue_tasks.is_sleeping()) {
           std::unique_lock<std::mutex> lock(mutex_cache);
           res->ok(cached_props);
       } else {
           res->ok(get_res_props(*meta, params, false));
       }
       return res;
   };
   ```
   Awake path passes `is_sleeping = false`; sleeping path serves `cached_props`, itself built by `get_res_props(*meta, params, true)` (`server-context.cpp:6301-6306`). Receipt's `false` matches the awake path.

7. Value provenance for the receipt's exact values:
   - `model_alias` = `meta.model_name` = `impl->model_name`, set at `server-context.cpp:1521-1523`
     `if (!params_base.model_alias.empty()) { model_name = *params_base.model_alias.begin(); }` — argv passes `--alias kama-stories260k`, so `kama-stories260k`. (`server.cpp:191-192` only seeds the alias from the model name when none is given.)
   - `build_info` = `llama_build_info()`; definition at `common/build-info.cpp.in` (fetched, 959 bytes):
     `static std::string s = "b" + std::to_string(LLAMA_BUILD_NUMBER) + "-" + LLAMA_COMMIT;`
     With build 11755 and commit 704366d76 that is exactly `b11755-704366d76`.
   - `default_generation_settings.n_ctx` = `meta.slot_n_ctx` = `impl->n_ctx_slot()`; the function (`server-context.cpp:4655-4665`) returns `min(llama_n_ctx_seq(ctx), [kv_unified_per_slot,] n_ctx_train)`. With argv `-c 256` and no `--parallel`, `n_parallel` auto-sets to 4 and `kv_unified = true` (`server.cpp:170-175`); `llama-context.cpp:377-380` then sets `cparams.n_ctx_seq = cparams.n_ctx` (n_ctx padded to 256 at `:376`), so the slot context is 256. Receipt: 256.
   - `is_sleeping` boolean `false`, as above.

8. Shipped-artifact corroboration (installed tree is the official b11755 build; `llama-server --version` exit 0 prints `version: 0.7.0-dev (build 11755, commit 704366d76)`):
   `strings -a ~/.local/opt/llama-b11755/libllama-server-impl.so` contains the exact literals `model_alias` (1 occurrence), `default_generation_settings` (1), `build_info` (3), `is_sleeping` (1).

9. Harness extraction is from the real body, not synthesized:
   `tools/kama-llamacpp-live.py:492-512` parses `props_res['body']` and reads `doc.get('model_alias')`, `doc.get('total_slots')`, `doc.get('is_sleeping')`, `doc.get('build_info')`, and `dgs.get('n_ctx')` where `dgs = doc.get('default_generation_settings')`. A missing key would serialize as `null`, not the values observed.

10. Two independent runs agree on all five fields but differ in the props body digest: `health`, `models`, `slots` body sha256 are identical across `receipt.json` and `receipt-frozen-probe.json`; only `props` differs (`0b2770e1…` vs `577f5617…`). Source explains this: `get_media_marker()` (`server-common.cpp:189-200`) returns a per-process random `"<__media_" + random_string() + "__>"` unless `LLAMA_MEDIA_MARKER` is set, and props includes `{"media_marker", get_media_marker()}` (`server-context.cpp:5253`). [INFERENCE] the random marker is the only differing body key (the two receipts keep only digests, not bodies), which also confirms the two receipts came from separate server processes while the named fields stayed stable.

# Commands run and exit codes

- `curl -sS -w 'HTTP %{http_code} bytes %{size_download}' -o server-context.cpp https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-context.cpp` → exit 0, `HTTP 200 bytes 264205`.
- `curl … cdn.jsdelivr.net/gh/ggml-org/llama.cpp@704366d…/tools/server/server-context.cpp` → exit 0, `HTTP 200 bytes 264205`; `sha256sum` both → `dd1de0f26536ce3e115e39110f2f0719427f2796885c2a1ea2db071b603c2329`; `cmp` → exit 0 (identical). Two hosts, same bytes.
- `curl … /tools/server/server-context.h` → exit 0, HTTP 200, 7116 bytes, sha256 `e4d0d9c488d43e3a6414f5ac7ee7a0c9de9671f7bff8ed12224c5bea4a355857`.
- `curl … /common/build-info.cpp.in` → exit 0, HTTP 200, 959 bytes, sha256 `e5157603f0dbaf1dc61a6be530a2ea5124644baed3170d32ea4bbcc645ef7ea6`.
- `grep -n` anchors for `model_alias|build_info|is_sleeping|n_ctx|default_generation_settings` in `server-context.cpp` / `server-context.h` → exit 0 (lines quoted above).
- `python3` assertion script (exact source literals present + receipt field names correct types) → exit 0, `ALL_OK`; receipt values `kama-stories260k` (str), `b11755-704366d76` (str), `False` (bool), `256` (int) all `type_ok True`.
- `~/.local/opt/llama-b11755/llama-server --version` → exit 0, `version: 0.7.0-dev (build 11755, commit 704366d76)`.
- `pgrep -x llama-server` → exit 1 (no server running; I started none and the receipt's teardown left none).
- `strings -a …/libllama-server-impl.so | grep -c <key>` → exit 0; counts 1/1/3/1 for `model_alias`/`default_generation_settings`/`build_info`/`is_sleeping`.
- `grep -n model_alias .../sources/llama.cpp-704366d/README.md` → exit 1 (absent, see G2).
- `curl https://api.github.com/repos/ggml-org/llama.cpp/commits/704366d…` → HTTP 403 (unauthenticated API rate limit); not used as evidence — the commit-pinned raw and jsDelivr fetches are the source of truth.
- `python3` receipt comparison (`captures.{health,models,props,slots}.body_sha256` across the two receipts) → exit 0: health/models/slots `same`, props `DIFF`; fields `same fields: True`.

No llama-server was started and no probe/matrix script was run (outside this item). No installs.

# Gaps / limitations (do not change the verdict)

- **G1 — source file not in the lane pin set.** `sources/pins.json` covers only `README.md`, `server-common.cpp`, `server-common.h`, `server-http.cpp`; the file containing `get_res_props` and the `/props` lambda (`tools/server/server-context.cpp`) is absent (the sibling `ScoutMetricsSource.md` found the same). I verified it at the full commit from two independent hosts (sha256 `dd1de0f2…`). Recommendation: pin `tools/server/server-context.cpp` (+ `server-context.h`, `common/build-info.cpp.in`) if the lane wants every receipt check's code path inside frozen evidence.
- **G2 — `model_alias` is undocumented in README at this commit.** `grep model_alias` over the pinned `README.md` returns nothing (exit 1). The README's GET `/props` sample documents `build_info` (`README.md:922`), `is_sleeping` (`:923`, bullet `:933`), and `default_generation_settings` with `n_ctx` (`:847-850`), but omits `model_alias`. The receipt's `documented_by` text for `props_alias` says "server_params -> props endpoint, b11755" and does not claim README coverage, so this is a knowledge/doc gap, not a false receipt. Any lane text that cites README for `model_alias` would be unsourced.
- **G3 — gate does not assert three of the four fields.** `tests/llamacpp-live/check-receipt.py:590-605` checks only `props_fields.model_alias == alias` (plus observed-vs-capture agreement). `build_info`, `is_sleeping`, and `default_generation_settings.n_ctx` appear only in the synthetic self-test fixture (`:829-831`), never in the live validation. So the receipt's "10/10" independently gates `model_alias` only; the other three are real per source and per harness extraction but are not falsified by the gate. (Filed here because it bounds what "receipt fields are real" is backed by; the gate's own coverage belongs to the receipt-gate reviewer.)
- **No fresh `/props` body.** This item does not authorize starting `llama-server`, so I did not re-capture. The four fields are proven present/typed from source; the live values are the L1 receipts' captured body hashes. The props bodies themselves are not retained (`keep_body=False`), so field values cannot be re-derived from the receipts alone — but the harness code path that writes them is direct body parsing, and the gate would fail a missing/incorrect `model_alias`.
- **`total_slots` incidental check.** Source sets `total_slots = params.n_parallel` (`server-context.cpp:5244`); argv has no `--parallel`, so auto `4` (`server.cpp:170-175`), matching the receipt. Not part of the named four.

Installs: none.
