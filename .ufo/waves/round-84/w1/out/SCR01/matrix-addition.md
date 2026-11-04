## Round-84 addition — SGLang v0.5.23 readiness and ping (2026-11-04)

source: S574 — https://raw.githubusercontent.com/sgl-project/sglang/v0.5.23/docs/docs/basic_usage/native_api.mdx — `## Health Check` line 108, routes lines 111-112 at v0.5.23.
verified-at: 2026-11-04 — SCR01 fetched the document with `curl -sS`; HTTP 200, 18295 bytes, sha256 `3ed171186990d6a67a1d950f1d491fe83986cf539bf24d1e65b95481e7d87a3c`; documentary verification only, no endpoint sampled.
recheck: 30d — reopen the same tagged native API page and locate both route sentences; a new release requires its own located reading before extending this version-bound claim.

The SGLang server process documented at v0.5.23 has two additional health surfaces:

| Route | Documented response | Source anchor |
|---|---|---|
| `/ready` | 200 when the server accepts new requests; 503 while starting, paused, unhealthy, or shutting down | S574, native_api.mdx:111 |
| `/ping` | SageMaker health check: 200 once the server is up; 503 while starting, unhealthy, or shutting down; remains 200 while generation is paused | S574, native_api.mdx:112 |

Line 112 further states that a failed `/health` or `/health_generate` probe marks the server unhealthy until a later probe succeeds. In particular, the documented paused-state distinction means `/ping` is not interchangeable with `/ready`. These are version-bound documentation statements, not observations of an installed server, endpoint conformance, model identity, or generation readiness on this host. The earlier SGLang row remains historical; no preceding line is rewritten.
