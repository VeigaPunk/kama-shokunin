# ScoutLmStudioServer — LM Studio local server `/v1/models` semantics

Read-only seat. All live pages fetched 2026-10-20; docs current context is LM Studio
0.4.26 (released 2026-10-13 per `https://lmstudio.ai/api/changelog?offset=0&limit=1`).
Page "dates" are last-commit dates from the public docs source repo
`github.com/lmstudio-ai/docs` (the site shows no per-page dates). No installs.

## Findings (observed)

**F1 — `/v1/models` is download-scoped when JIT is on.**
`https://lmstudio.ai/docs/developer/openai-compat/models` (source
`1_developer/3_openai-compat/models.md`, last commit 2025-10-29):
"Returns the models visible to the server. The list may include all downloaded
models when Just‑In‑Time loading is enabled."

**F2 — explicit loaded-vs-downloaded split, conditional on JIT.**
`https://lmstudio.ai/docs/developer/core/headless` (source
`1_developer/0_core/headless.md`, last commit 2026-04-14), JIT ON:
"Calls to OpenAI-compatible `/v1/models` will return all downloaded models, not only
the ones loaded into memory"; "Calls to inference endpoints will load the model into
memory if it's not already loaded." JIT OFF: "Calls to OpenAI-compatible `/v1/models`
will return only the models loaded into memory"; "You have to first load the model
into memory before being able to use it."

**F3 — v1 REST list carries readiness per model, in-band, status 200.**
`https://lmstudio.ai/docs/developer/rest/list` (source `1_developer/2_rest/list.md`,
last commit 2026-10-08): `GET /api/v1/models` response field `loaded_instances` is
"List of currently loaded instances of this model." The documented example returns a
downloaded, not-loaded model with `"loaded_instances": []` (deepseek-r1) and a loaded
one with a non-empty array (gemma). The endpoint has no request parameters.

**F4 — v0 REST names the not-ready state explicitly, also status 200.**
`https://lmstudio.ai/docs/developer/rest/endpoints` (source
`1_developer/2_rest/endpoints.mdx`, last commit 2026-04-14): `GET /api/v0/models`
"List all loaded and downloaded models"; every example entry carries
`"state": "not-loaded"`. The page advertises "rich information about models such as
loaded vs unloaded, max context, quantization, and more." The docs never enumerate
other `state` values (only `not-loaded` appears in examples).

**F5 — no documented HTTP "not ready" status for `/v1/models`.**
A grep of the full docs source tree at `main` (229 `.md`/`.mdx` files, tarball fetched
2026-10-20) finds **zero** occurrences of `503`, and no "not ready"/"still loading"
wording; model loading is described as slow but request-scoped ("AI models are huge.
It can take a while to load them into memory.", `https://lmstudio.ai/docs/typescript/
manage-models/loading`). The only documented server-readiness surface is the CLI:
`https://lmstudio.ai/docs/cli/serve/server-status` (source
`3_cli/1_serve/server-status.md`, last commit 2026-04-14) →
`The server is running on port 1234.` / JSON `{ "running": true, "port": 1234 }`.
No `/health` endpoint appears anywhere in the docs.

**F6 — the aggregated `llms.txt` is stale on this point; quote pages, not it.**
`https://lmstudio.ai/llms.txt` still says under `/v1/models`: "Lists the currently
loaded models." That contradicts F1/F2. The legacy URLs `/docs/api/openai-api` and
`/docs/app/api/endpoints/openai` now 302 to `/docs/developer/openai-compat`, so the
stale sentence survives only in the aggregation, not on any current page.

## Bearing on C1 (calibration)

- LM Studio documents only in-band readiness (`state`, `loaded_instances`) inside a
  200 list response. It documents no loading-time non-2xx for `/v1/models`.
- Therefore a 503 "Loading model" body on `/v1/models` is a **runtime-specific
  llama.cpp signal**, not a generic "non-model service" signal. Adding
  `MODEL_LOADING` with reason `llamacpp-loading`, gated on exact
  `message`/`type`/`code` equality, is consistent with this corpus: generic 503s and
  other `unavailable_error` bodies (e.g. "no slot available") must stay
  `FOREIGN_SERVICE`, and LM Studio-shaped 200s must never become `MODEL_LOADING`.
- Keep the new verdict keyed to `/v1/models` only, as claimed. Do not let `/health`
  drive it: LM Studio documents no `/health`, and llama.cpp's `/health` 503 is a
  second surface that would widen the verdict past the calibration evidence.
- Calibration caveat for any future LM Studio consumer row (out of C1 scope): with
  JIT on (default), a model id in `/v1/models` is **not** proof the model is in
  memory; only `/api/v1/models[].loaded_instances` (or v0 `state`) distinguishes
  loaded from merely downloaded. [INFERENCE] The probe's id-only `MODEL_OK` would
  overstate readiness on an LM Studio host.

## Bearing on C2 (operability)

The C2 live harness rightly pins llama.cpp-only surfaces (`/health`, `/v1/models`
alias + `owned_by`, `/slots`, `/metrics`). None of those has a documented LM Studio
equivalent, and LM Studio's lifecycle is managed by `lms`/llmster rather than a
one-shot server binary. Do not generalize the captured surface set to "any
OpenAI-compatible server"; LM Studio's documented introspection is
`GET /api/v1/models` (`loaded_instances`) plus `lms server status`.

## Limitations

- Docs are descriptive, not normative about status codes; absence of a 503 in docs is
  not proof LM Studio never returns one. [INFERENCE] `/v1/models` likely answers 200
  regardless of load state, since JIT-off-with-no-model is described as listing only
  loaded models (empty set), not as an error.
- LM Studio itself was not installed or run; every LM Studio claim above is docs-only.
- `llms.txt`/`llms-full.txt` lag the page sources (F6); do not cite them for this.

## Installs

None.
