# RevengerEnvelopeHistory — provenance and stability of llama.cpp's `Loading model` 503 envelope

Read-only seat. Sources fetched 2026-10-20 from `raw.githubusercontent.com/ggml-org/llama.cpp/<tag>/<path>` and from
`api.github.com` / `github.com/.../commit/<sha>.patch`. No lane file was modified except this report. No installs.

Axes walked: (1) first-appearance provenance, (2) stability of the `(status, message, type, code)` tuple across
releases, (3) route coverage of the envelope (`GET /v1/models`), (4) wire form vs byte form, (5) doc/code agreement.

## Headline

1. **The envelope was not introduced by #5548/#4746.** It first appears in
   `Server: format error to json (#5961)`, commit `caa106d4e05a`, merged **2024-03-11T09:56:41Z**
   ([commit API](https://api.github.com/repos/ggml-org/llama.cpp/commits/caa106d4e0)); tag `b2400`
   resolves to exactly that commit (`git ls-remote` → `caa106d4e05a…`).
   Patch adds `res_error(res, format_error_response("Loading model", ERROR_TYPE_UNAVAILABLE));`.
2. **PR #5548 only added slot fields to `/health`.** Merged 2024-02-18T16:31:28Z, closes #4746;
   body: "Add `slots_idle` and `slots_processing` fields in the `health` endpoint response, answer `503` if not slot
   are available." Its patch (`e75c6279.patch`) contains no `Loading model` / `unavailable_error` line.
   Issue #4746 ("Healthcheck endpoint?") was created 2024-01-03T03:40:37Z, closed 2024-02-18T16:31:29Z.
3. **The triple is stable from b2400 through b11755** in all 16 tags sampled
   (`b2400, b3500, b4000, b4500, b6000, b6500, b7251, b7502, b7731, b7903, b7999, b8323, b9000, b10000, b11000, b11755`):
   `message == "Loading model"`, `type == "unavailable_error"`, integer `code == 503`. No rename, no case change,
   no string-code variant.
4. **Route coverage is not stable.** `GET /v1/models` is gated (503 envelope) at `b4000`–`b4500`, exempted at
   `b6000`–`b7502`, gated again from `b7731` onward. `MODEL_LOADING` can only fire where the gate covers `/v1/models`.
5. **Wire key order changed** (sorted vs insertion) — an exact-match rule must compare decoded fields, never body bytes.

## Version table

`gated` = does the loading 503 middleware intercept `GET /v1/models`.

| tag (sha8) | loading response body | `/v1/models` gated | evidence |
|---|---|---|---|
| b2000 (172ac826) | 503 `{"status": "loading model"}` — no `error` object | no gate outside `/health` | `examples/server/server.cpp:2450` |
| b2300 (6ea0f010) | 503 `{"status": "loading model"}` | no | `examples/server/server.cpp:2811` |
| **b2400 = caa106d4 (2024-03-11)** | 503 `{"error":{"code":503,"message":"Loading model","type":"unavailable_error"}}` | no — envelope reachable only from the `/health` state switch | `examples/server/server.cpp:2962-2964`; mapping `examples/server/utils.hpp:585-587` |
| b3500 | same envelope, same `/health`-branch placement | no (gate-all not yet present) | `examples/server/server.cpp:2748` |
| b4000 (c02e5ab2) | same | **yes** — `middleware_server_state` rejects every non-HTML path | `examples/server/server.cpp:2406`, `:2414` |
| b4500 (a133566d) | same | **yes** | `examples/server/server.cpp:3312`, `:3320` |
| b6000 (4762ad73) | same | **no** — `"/models"`, `"/v1/models"`, `"/api/tags"` return `true` early | `tools/server/server.cpp:3820`, `:3823` |
| b6500 | same | **no** | `tools/server/server.cpp:4213`, `:4221`, `:4224` |
| b7251 / b7502 | same | **no** | `tools/server/server-http.cpp:175`, `:183`, `:190` |
| b7731 (7d587e55) | same | **yes** — exemption removed | `tools/server/server-http.cpp:175`, `:189` |
| b7903 / b7999 / b8323 / b9000 / b10000 / b11000 | same | **yes** | e.g. b8323 `tools/server/server-http.cpp:181-195` |
| **b11755 = 704366d7** | same | **yes** | `tools/server/server-http.cpp:307-325` |

Tag→sha pairs from `git ls-remote --tags`; `b11755` = `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (the C2 pin commit).

### Evidence quotes (each ≤25 words)

- b11755 `tools/server/server-http.cpp:308-320`: `if (!is_ready.load())` … `{"message", "Loading model"}, {"type", "unavailable_error"}, {"code", 503}`.
- b11755 `tools/server/server-http.cpp:312`: "no endpoints are allowed to be accessed when the server is not ready".
- b11755 `tools/server/README.md:485-486`: Body `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`; "the model is still being loaded."
- b11755 `tools/server/server-common.cpp:119-122`: `case ERROR_TYPE_UNAVAILABLE: type_str = "unavailable_error"; code = 503;`.
- b11755 `tools/server/server-context.cpp:5396`: `format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE)`.
- b2400 `examples/server/server.cpp:2770-2773`: `json final_response {{"error", error_data}};` … `res.status = json_value(error_data, "code", 500);`.
- b2400 `examples/server/utils.hpp:585-587`: `type_str = "unavailable_error"; code = 503;`.
- b4000 `examples/server/server.cpp:2406-2414`: `middleware_server_state` … `else { res_error(res, format_error_response("Loading model", ERROR_TYPE_UNAVAILABLE)); }`.
- b6000 `tools/server/server.cpp:3820`: "allow the models endpoint to be accessed during loading".
- b7251/b7502 `tools/server/server-http.cpp:183`: same exemption comment, still present.
- b7731 `tools/server/server-http.cpp:181-195`: `} else {` … `{"message", "Loading model"}` with no models exemption.
- b2000 `examples/server/server.cpp:2450`: `{"status": "loading model"}` at HTTP 503.
- b2350 `examples/server/README.md:160`, b3400 `:415`: `503 -> {"status": "loading model"}`.
- b3600 `examples/server/README.md:376`: `Body: {"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`.

## Stability judgment for an exact-match rule

**Verdict: admit the exact triple, reject any widening, and match on decoded fields only.**

1. **Stable triple.** From the first release carrying it (b2400) to the pinned b11755, all 16 sampled tags emit
   `"Loading model"` + `"unavailable_error"` + integer `503`. The mapping lives in one place
   (`ERROR_TYPE_UNAVAILABLE → unavailable_error/503`) and the middleware keeps the literal `"Loading model"`.
   An exact three-field match is therefore safe across ~2.5 years of releases.
2. **Prehistory is a non-event.** b2000/b2300 answer 503 with `{"status": "loading model"}` and no `error` object.
   The exact rule cannot fire there; such a server keeps `FOREIGN_SERVICE non-2xx-non-model-http`. That is a missed
   detection on pre-2024-03 builds, never a false `MODEL_LOADING`. Acceptable: the new verdict only claims what it saw.
3. **Do not match bytes.** b2400 used `using json = nlohmann::json;` (`examples/server/utils.hpp:15`, sorted keys →
   `code,message,type`); b4000 switched to `using json = nlohmann::ordered_json;` (`examples/server/utils.hpp:26`,
   insertion order). b11755 inserts `message,type,code` directly, and the L1 smoke body is exactly that order, while
   the README prints `code,message,type`. Any byte-exact or serialized-substring rule is version-fragile.
4. **Do not widen.** `"no slot available"` is also `ERROR_TYPE_UNAVAILABLE` with code 503
   (b11755 `tools/server/server-context.cpp:5396`); only message equality separates it from the loading envelope.
   This is exactly the contract's stated scope limit and it is load-bearing, not cosmetic.
5. **Route coverage is the one real caveat.** On b6000–b7502 the middleware lets `/models`, `/v1/models`, `/api/tags`
   through while loading, so `GET /v1/models` does not return the envelope and `MODEL_LOADING` cannot fire. [INFERENCE]
   on those builds a still-loading server can be graded `MODEL_OK` (the model list is static) or `DEAD timeout`, i.e.
   a missed detection, not a misclassification introduced by the new verdict. From b7731 onward, and on the pinned
   b11755, the gate covers every non-frontend path including `/v1/models`, which is what C1's stub models.
6. **`/health` is equally gated** on b11755 (`frontend_paths` exempts only embedded UI assets,
   `tools/server/server-http.cpp:240-250`), so adding a `/health` probe would not restore detection in the exempt
   window; it would return the same envelope on modern builds. No probe change is implied by this history.
7. **README is a lagging witness, not a source.** The `/health` section documented `{"status": "loading model"}` from
   b2350 through b3400 — including at b2400, the very commit that changed the body — and only documents the envelope
   from b3600. The code is authoritative; at b11755 both agree, so citing the b11755 README for C1 is sound.

### Calibration note for the C1 implementation (advisory, not history)

The contract says "integer code == 503 (all exact)". In Python `503.0 == 503` is `True` and
`isinstance(True, int)` is `True`; a body with `"code": 503.0` or `"code": true` would slip through a bare `==`
check. The helper should assert `type(code) is int and code == 503`. llama.cpp has always emitted an integer literal
here (b11755 `:320`, b2400 `utils.hpp:587`), so this only tightens the negative controls, it does not change the
positive path.

## Limitations

- Sampled tags, not an exhaustive walk: the tag list is non-contiguous (e.g. `b5000`/`b5500` do not exist as tags), so
  the "gate-all appears between b3500 and b4000" and "exemption removed between b7502 and b7731" brackets are
  measured bounds, not bisected commits.
- GitHub REST API hit its unauthenticated rate limit mid-run; dates are reported only where measured
  (#5961 = 2024-03-11, #5548 = 2024-02-18, #4746 = opened 2024-01-03 / closed 2024-02-18). Other rows are ordered by
  monotonically increasing build tag, which is the project's release ordering.
- No build was executed and no installed binary was disassembled; the source at the pinned commit equals the b11755
  tag SHA, and runtime behavior is L1's measurement (`kama-llamacpp-live.py`), not this report's.
- [INFERENCE] items are marked inline; everything else is a literal source/API observation.
