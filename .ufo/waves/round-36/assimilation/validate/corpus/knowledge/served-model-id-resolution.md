# Resolving the served model identifier from a local OpenAI-compatible endpoint

source: S223 — https://docs.gitlab.com/administration/gitlab_duo_self_hosted/supported_llm_serving_platforms/ — §Find the model name — quote located 2026-10-24: "the model name is the value of the `data.id` field in the response"
verified-at: 2026-10-24
recheck: 90d — re-run `curl -fsSL 'https://docs.gitlab.com/administration/gitlab_duo_self_hosted/supported_llm_serving_platforms/' | grep -c 'data.id'` (expect ≥1) (re-ran 2026-10-24: count=1)

### The procedure a consumer actually follows

Two rules, both stated by a consumer that has to configure the endpoint rather than
run it. First the address: "The URL must be suffixed with /v1", and behind a proxy
or load balancer the port may be omitted entirely. Second the identifier: after the
model is deployed, "the model name is the value of the `data.id` field in the
response" from a `GET /v1/models` call.

### Why the field name matters

The response carries two identifiers for one model, and they are not the same thing.
`id` is the name the endpoint serves and the name a client must send; `root` is the
underlying checkpoint, here `mistralai/Mixtral-8x22B-Instruct-v0.1` behind a served
`id` of `Mixtral-8x22B-Instruct-v0.1`. A reconciliation that compares the client's
request against the checkpoint path will report a mismatch for every deployment that
renames its served model — which is what `--served-model-name` exists to do, and what
the wave-1 vLLM row records as the first-name-wins rule.

The two identifiers are also separate from the name a deployment was *launched* with,
which is why the request in the worked example carries a configured `--served_model_name`
rather than the repository path.

### What this entry does not establish

This is one consumer's configuration guide. It states how that consumer resolves and
sends a model identifier; it does not define the `/v1/models` response schema for any
engine, and the `data.id` / `root` split it shows is that platform's observed shape
rather than an OpenAI specification. The lane still holds no row that states the
schema itself.

### A related gap this round could not close

The same guide records that a vLLM `/health` handler returns 503 when the engine
raises `EngineDeadError`, while the wave-1 vLLM engine-arguments row records that
`/v1/chat/completions` returns 503 as a deliberate admission rejection. The two
routes therefore use the same status code for different conditions, which is exactly
the distinction the lane's "an error is not a verdict" discipline needs. The lane
already holds that handler as S004, whose anchor is the same source block, so no new
row was opened for it in this round; the observation is recorded in
`CANNOT-ANSWER.md` for the next wave that touches that file.
