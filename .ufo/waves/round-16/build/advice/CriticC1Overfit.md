# CriticC1Overfit — C1 scope attack (round 16, build wave)

Seat: read-only critic. Advice only; L1 owns judgment and every measurement. Nothing was run against the lane. No installs.
Axes touched: **calibration** (primary), **operability** (snapshot/baseline compatibility).

## Verdict in one line
Keep the exact match (message + type + integer code + HTTP 503). Widening buys almost nothing reachable on `/v1/models` and opens the substring traps listed below. State the limits honestly, though. C1 covers **single-model llama-server at b11755**. It does **not** cover router mode, other engines, or future message changes. The matrix also needs the negatives in §3, or C1 passes vacuously.

## 1. Counterexamples and evidence

### CE-1: Router-mode llama-server "loading" is graded MODEL_OK. The claim says "a loading llama.cpp server", which is too broad.
- In router mode, `is_ready` becomes true before any model loads. `server.cpp:460` `ctx_http.is_ready.store(true);` runs before `server.cpp:472` `models_routes->models.load_startup_models();` (https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server.cpp).
- In router mode, `/v1/models` is `get_router_models` (`server.cpp:269`). It returns 200 with `data[]` rows carrying `{"status", status}` (`server-models.cpp:2370`). README @ b11755 :2068-2070 shows `"status": { "value": "loading", ... }`.
- [INFERENCE] The current probe returns `MODEL_OK matched` (exit 0) for a router whose expected model is still `loading`, `unloaded`, or `failed: true`. `classify()` treats any 2xx with `data[]` as a model array (`tools/kama-probe.sh:479-503`, pre-edit numbering).
- Impact: this is a calibration false-healthy, and it is worse than the C1 defect. It is out of C1's scope, so do **not** widen C1 to fix it. C1's limit statement must say "single-model (non-router) llama-server". Router per-model status should be logged as a residual unknown or a next-round candidate.

### CE-2: Future or changed llama.cpp message
- The message is a hard-coded English literal: `server-http.cpp:318-320` `{"message", "Loading model"}, {"type", "unavailable_error"}, {"code", 503}`. There is no i18n layer. A grep for `gettext` found nothing in server.cpp, server-context.cpp or server-models.cpp. **Localization is not a real risk at b11755. A literal change in a future release is a real risk.**
- With an exact match, a renamed message falls back to the pre-C1 verdict (`FOREIGN_SERVICE non-2xx-non-model-http`, exit 2). The failure stays fail-safe: drift either way, and never a false MODEL_OK. The only loss is calibration drifting back to today's state, not a new regression. Honest statement: "recognised only for the b11755 loading envelope; other builds are not claimed".

### CE-3: Widening to `type=="unavailable_error" && code==503` is also wrong on llama.cpp's own surfaces
- `server-common.cpp:119-121`: `ERROR_TYPE_UNAVAILABLE` → `type_str = "unavailable_error"; code = 503;`. It is shared by `"no slot available"` (`server-context.cpp:5396`) and `"Stream owner model is loading, retry later"` (`server-models.cpp:2585`). Neither is the startup-load state.
- Matching on `message contains "loading"` would take the stream-owner message, which is router mode on a non-`/v1/models` path. Exact equality is the only rule that encodes the b11755 middleware state at `server-http.cpp:307-325` and nothing else.

### CE-4: Other engines are not claimed, and a forged envelope is graded MODEL_LOADING by design
- [INFERENCE, not verified this seat] Ollama, vLLM and TGI do not emit this envelope while loading. vLLM and TGI typically bind only after load (→ DEAD), and Ollama loads lazily per request. Their 503s keep `non-2xx-non-model-http`. Limit statement: "other engines' loading states are not recognised".
- Any service can return these exact bytes. Grading it MODEL_LOADING is the declared tradeoff. It is acceptable because MODEL_LOADING still means drift=true and exit 2, so there is no false-healthy. The matrix should pin this with one row (see N-SPOOF) so the tradeoff is explicit and not hidden.

### CE-5: Wire key order differs from the README. A byte-literal matcher overfits one of them.
- Wire order is insertion order. `common/json.h:24` says "object keys keep the order in which they are added", which gives `message,type,code`. That matches L1's 10:17 smoke observation.
- README @ b11755 :486 documents `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`, which is a different order.
- A grep or byte matcher built from either source misses the other. The detector must parse JSON. The positive controls must include both key orders and a whitespace variant.

### CE-6: The no-python fallback path is not exercised by the matrix
- The probe chooses its JSON path at runtime: `tools/kama-probe.sh:72-73` `HAVE_PY=0` / `command -v python3 ... && HAVE_PY=1`. The existing fallbacks are loose greps (`:410` `grep -qE '"(data|models)"...'`).
- If the loading detector gets a grep fallback, every python-run matrix row leaves that path untested. A loose grep would accept N-CASE, N-SUBSTR or N-FLOAT below.
- Smallest correction, either one:
  - (a) With `HAVE_PY=0`, never emit MODEL_LOADING; keep the old verdict and state this as a limit.
  - (b) L1 reruns the matrix with `python3` removed from the probe's PATH.

### CE-7: Hidden operability regression in snapshot baseline validation
- The live file is mid-edit. `VOCAB` already includes MODEL_LOADING (`tools/kama-probe.sh:60`), but the latest.tsv validator still hard-codes the old six: `:900` `*\ MODEL_OK\ *|*\ MODEL_MISMATCH\ *|...|*\ NOT_HTTP\ *) : ;;`. It drops anything else with `"dropping malformed baseline row"` (`:901`).
- Result: a consumer snapshotted while loading gets its baseline row dropped as malformed on the next snapshot. Its transition record is lost and a false malformed-row note appears.
- The listeners summary counters (`:685-690`) have no MODEL_LOADING bucket, so the row is counted nowhere.
- Correction: add MODEL_LOADING at `:900`. Either add a `loading` summary counter or state that listeners counts it nowhere. Include one snapshot round-trip row (loading → ok) in L1's measurement. This probably overlaps the SnapshotCompat seat; L1 should dedupe.

## 2. Honest limit statement (proposed wording for C1)
> MODEL_LOADING/llamacpp-loading is emitted only when GET /v1/models returns HTTP 503 and the body parses as a JSON object. Its `error` object must have message == "Loading model", type == "unavailable_error", and code == integer 503 (not bool, float or string). This is the startup middleware of single-model llama-server b11755 (server-http.cpp:307-325).
>
> Not claimed:
> - router-mode per-model loading (200 + data[].status.value, still graded by the model-array rule);
> - other llama.cpp unavailable_error messages;
> - other engines' loading states;
> - message changes in later builds.
>
> All of these keep their pre-C1 verdict. A non-llama.cpp service emitting the identical envelope is graded MODEL_LOADING. That is accepted because MODEL_LOADING is always drift (exit 2).

## 3. Matrix rows required for non-vacuity
All rows use `/v1/models` unless stated. "Frozen = repaired" means the row must give an identical (verdict, reason, exit) on the frozen probe (sha256 93ee4302…cd64, verified identical to the pre-edit tools/kama-probe.sh this seat hashed) and on the repaired probe. That is the anti-regression invariant. Only the P-rows may change.

**Positives** (defeat reject-all; each red on frozen = FOREIGN_SERVICE/non-2xx-non-model-http, green = MODEL_LOADING/llamacpp-loading, exit 2):
- P-WIRE: `body_text` exactly `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}`, with `Content-Type: application/json; charset=utf-8` and `Server: llama.cpp`.
- P-README-ORDER: keys in `code,message,type` order (README :486).
- P-PRETTY: same object pretty-printed with spaces and newlines.
- P-EXPECT: P-WIRE run with both `--expect '*'` and a concrete id. The verdict must not depend on `--expect`, and the exit must be 2 for both. This defeats an implementation that maps loading to exit 0.
- P-NOSERVER: P-WIRE without a `Server` header → still MODEL_LOADING. This pins that the Server header is not proof, consistent with `:476` "status code / Server header alone is not proof".
- N-SPOOF: same as P-NOSERVER, with a `why` that documents the spoof tradeoff.
- P-EXTRA-KEY (decision row, pin either way): error object plus `"param": null`, or an extra top-level key. The spec says "has", so extra keys are allowed. Write that down and test it.

**Negatives** (defeat loading-all and substring/loose matchers; every one has frozen = repaired):
- N-503-TEXT: 503 `text/plain` "Service Unavailable" → FOREIGN_SERVICE non-2xx-non-model-http.
- N-503-EMPTY: 503 with an empty body → same.
- N-NOSLOT: 503 `{"error":{"message":"no slot available","type":"unavailable_error","code":503}}` → same.
- N-SUBSTR: 503 message "Stream owner model is loading, retry later" (real llama.cpp text, server-models.cpp:2585) → same.
- N-CASE: message "loading model". N-PUNCT: message "Loading model." N-SPACE: message "Loading model " → same.
- N-TYPE: type "server_error" with the exact message → same.
- N-CODE-STR: `"code":"503"`. N-CODE-FLOAT: `"code":503.0`. N-CODE-BOOL: `"code":true`. N-CODE-500: `"code":500` → same. Python's `503.0 == 503` is True, so an `==`-only check fails N-CODE-FLOAT.
- N-FLAT: `{"error":"Loading model"}` (flat string error) → same.
- N-TOPLEVEL: `{"message":"Loading model","type":"unavailable_error","code":503}` with no `error` wrapper → same.
- N-ARRAY: `[{"error":{...exact...}}]` → same.
- N-TRUNC: exact body cut mid-object (invalid JSON) → same.
- N-STATUS-200: exact loading body with HTTP 200 + JSON → FOREIGN_SERVICE schema-unrecognized, exit 2.
- N-STATUS-500, N-STATUS-502, N-STATUS-504: exact body → non-2xx-non-model-http.
- N-STATUS-401 / N-STATUS-403: exact body → UNAUTHORIZED_SERVICE http-401 / http-403. Auth precedence is unchanged. Real llama.cpp checks the loading state before the API key (`server-http.cpp` pre-routing: `middleware_server_state` then `middleware_validate_api_key`), so a real loading server with `--api-key` still returns 503.
- N-HTML: 503 `text/html` body containing "Loading model" → FOREIGN_SERVICE html-non-model.
- Decision row N-HTML-CT-JSONBODY: exact JSON body labelled `text/html`. The result depends on whether the new branch runs before the html check at `:506`. Pin the choice; the recommendation is "body decides" → MODEL_LOADING.
- C-OK: 200 `data[{"id":X}]` with `--expect X` → MODEL_OK matched, exit 0. This regression control proves the repaired probe can still pass.
- C-DEAD: closed port → DEAD connection-refused. A loading check must not run before the rc switch.

**Harness requirement:** the matrix fails if fewer than one P-row is red on frozen, if any N/C row differs between frozen and repaired, or if the harness ran only with `HAVE_PY=1` while the detector has a grep fallback (CE-6).

## 4. Smallest safe corrections (fixable defects, not judge rejections)
1. Narrow C1's wording to "single-model llama-server b11755" and add the §2 limit statement. Without this, CE-1 makes the claim an overreach of its own.
2. The detector must parse JSON. Require `type(code) is int` (not bool, not float), exact string equality, and HTTP 503. Without python, emit nothing (CE-6a).
3. Add MODEL_LOADING to the baseline validator at `tools/kama-probe.sh:900`, and account for it in the listeners summary (CE-7).
4. Add the §3 frozen = repaired invariant over all N/C rows.

## Limitations
- I did not read peer matrix files: `tests/probe-verdicts/` did not exist at review time. The detector body was not yet written in the live probe, so CE-6 and CE-7 are against intent plus the current partial edit.
- Router-mode behavior is from source and README reading only, with no live router run. Engine behavior in CE-4 is [INFERENCE].
- Sources: raw.githubusercontent.com/ggml-org/llama.cpp/b11755/{tools/server/server-http.cpp, server.cpp, server-models.cpp, server-context.cpp, server-common.cpp, README.md, common/json.h}. Temporary copies are in /tmp/critc1_*; nothing was written inside the lane except this report.
