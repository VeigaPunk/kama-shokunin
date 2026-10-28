# S06 Ollama API/OpenAPI freshness findings

Scope: current public Ollama API docs and OpenAPI schema as relevant to POST `/api/generate`, GET `/api/tags` digest semantics, and S525’s located quote. Read-only source recon; no runtime contacted.

## Evidence and anchors

- API index: https://docs.ollama.com/api — current index links the Generate a response route. Route page https://docs.ollama.com/api/generate identifies `POST /api/generate`, summary “Generate a response”, operationId `generate`.
- Current OpenAPI: https://docs.ollama.com/openapi.yaml, OpenAPI 3.1.0, info.version 0.1.0. Anchors are YAML path/schema names below (the fetched document has no stable line numbering).
- `POST /api/generate` → requestBody required; `application/json` → `GenerateRequest`; `GenerateRequest.required: [model]`. Request properties: `model` string (required), `prompt` string, `suffix` string, `images` array of base64 strings, `format` string or object (JSON / JSON schema), `system` string, `stream` boolean default true, `think` ThinkValue, `raw` boolean, `keep_alive` string or number, `options` ModelOptions, `logprobs` boolean, `top_logprobs` integer. `ModelOptions` includes seed, temperature, top_k, top_p, min_p, stop string-or-string-array, num_ctx, num_predict, plus additionalProperties true.
- Generate 200 response allows JSON `GenerateResponse` and `application/x-ndjson` `GenerateStreamEvent`. Response properties include `model`, `created_at`, `response`, `thinking`, `done`, `done_reason`, timing/count fields (`total_duration`, `load_duration`, `prompt_eval_count`, `prompt_eval_cached_count`, `prompt_eval_duration`, `eval_count`, `eval_duration`) and optional `logprobs`. JSON example is terminal (`done: true`); schema does not mark response properties required. Thus do not overstate every response as guaranteed to contain all these fields. `stream` defaults true; docs demonstrate stream:false for non-streaming.
- `GET /api/tags` → `ListResponse.models[]` references `ModelSummary`. Its `digest` property is a string, described exactly: “SHA256 digest identifier of the model contents”. `ModelSummary` also gives name/model, optional remote_model/remote_host, modified_at, disk `size`, and `details`. This supports reporting the documented digest field and its stated meaning; it does not itself describe a cross-endpoint foreign-key/join guarantee or identity semantics between tags and ps.
- S525 located-quote freshness: `PsResponse.properties.expires_at` in current OpenAPI still has `type: string`, `description: "Time when the model will be unloaded"` (verbatim). The earlier located quote in `corpus/lessons/round-61.md:12` remains valid. The current spec also locates the same field under the Ps response schema (the schema can be identified by searching `PsResponse` / `expires_at`; `/api/ps` 200 describes “Models currently loaded into memory”).

## Existing corpus anchors

- `corpus/SOURCES.md:277` — S525 row, URL, scope, version, quote, fetched date.
- `corpus/lessons/round-61.md:12` — prior S525 admission record and located quote.
- Current official spec route/schema anchors: `paths./api/generate.post`; `components.schemas.GenerateRequest`; `GenerateResponse`; `GenerateStreamEvent`; `paths./api/tags.get`; `components.schemas.ListResponse`; `ModelSummary.properties.digest`; `PsResponse.properties.expires_at`.

## Calibration notes / limits

Observed documentation only, fetched 2026-10-28. “Digest join between tags and ps” is an inference one could make from both schemas exposing digest, not a documented relation; preserve that distinction in any lesson. The generated answer contract documents schema and content types, not quality/correctness of generated text. No S525 semantic drift detected for the expires_at quote. No tools installed or updated.
