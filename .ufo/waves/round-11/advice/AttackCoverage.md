# AttackCoverage — C2 falsification (round 11, critic seat)

Review run: 2026-10-20T02:14Z UTC (`date -u`). The round label is 2026-10-19; every source below was reopened on 2026-10-20 UTC. Read-only. No endpoint contacted, no installs, no edits outside this file. `corpus/knowledge/served-identity-crosswalk.md` did not exist yet, so I attacked the claim itself and not a draft.

## Verdict

**C2 is partly duplicative.** The bare split "`/api/tags` = available, `/api/ps` = running" is already in the corpus, so restating it is row growth, not expansion. Genuine uncovered ground does exist (U1–U6 below). C2 counts as expansion only if the entry rests its claim on those cases.

## Counterexample 1: the split already exists (duplication)

- `corpus/knowledge/runtime-health-surface-matrix.md:17`, Ollama row, identity cell: "`/api/tags` (available models), `/api/ps` (running models); OpenAI-compat `/v1/models`". The S-id cell is `S009, S010`.
- `SCORECARD.md:216` already credits this matrix with Ollama coverage.
- If the crosswalk's Ollama row only restates available-vs-running, that is duplication. The crosswalk must cite matrix:17 as prior coverage.

## Defect found: matrix:17 has false provenance

I reopened both cited pages on 2026-10-20 UTC:
- S009 https://docs.ollama.com/api/introduction (§Base URLs, §Versioning): neither `/api/tags` nor `/api/ps` appears.
- S010 https://docs.ollama.com/api/openai-compatibility: `/api/ps` is absent. `/api/tags` appears only in the cloud sense, §Models: "Direct cloud requests use the identifiers from `https://ollama.com/api/tags` and do not require a pull."
- The pages that actually ground the cell are S011 and S012. `corpus/SOURCES.md:23-24` lists both as `queued` with used-by `—`.

The matrix's KQ6 line ("cites an opened `SOURCES.md` row") is therefore false for this cell. This is a provenance correction, not new coverage. The parent should record it as an appended correction. It must not be counted toward C2.

## served-model-identity.md: no coverage, and README over-claims it

- The file is a 37-line fragment and has been since `c6199a2` (2026-09-28). `git show` at that commit has the same 37 lines. It starts with blank lines, then `### Exact readiness-field probes`.
- Its content is llama.cpp `/health`, `/props`, `/slots`, `/metrics` samples only. It has no Ollama content, no `/api/tags`, no `/api/ps`.
- `corpus/README.md:32` describes it as "served-model reconciliation (`/v1/models` vs `--alias` vs configured id) + the minimal proof procedure". The file contains none of that. The crosswalk must not cite this file for alias reconciliation. The live rule is in `SKILL.md` §Served-id normalization and `endpoint-identity.md:127`.

## Uncovered ground (genuine expansion), pinned

Neither matrix:14/17, nor served-model-identity.md, nor endpoint-identity.md covers these:

| # | Case | Evidence (opened 2026-10-20 UTC) | Why it is new |
|---|---|---|---|
| U1 | **Ollama `/v1/models` lists available models, not running ones.** If kama's `MODEL_OK` gate (`/v1/models` + id) runs against Ollama, it proves only that the model is available. Strongest counterexample: model pulled but not loaded → `/v1/models` lists it, `/api/ps` is empty, and the gate still returns `MODEL_OK`. | `ollama/ollama` `server/routes.go` on main (latest path commit `4ed3ba13`, 2026-10-19T21:37Z): L2382 `r.GET("/api/tags", s.ListHandler)`, L2404 `r.GET("/api/ps", s.PsHandler)`, L2417 `r.GET("/v1/models", middleware.ListMiddleware(), s.ListHandler)`. `openai/openai.go` @ `31547a6c` L508: "ToListCompletion converts an api.ListResponse to ListCompletion"; `Created: m.ModifiedAt.Unix()`. | Matrix:17 lists `/v1/models` next to tags/ps without saying which side it is on. S010 does not say either: it only states "`created` corresponds to when the model was last modified". The grounding is code, and no S-row covers it. Either register a new source row (code, revision-pinned) or state it as "not documented in S010" plus `[INFERENCE]` from the `created` note. |
| U2 | **llama.cpp `/v1/models` can answer while the model is still loading**, so seeing the id does not mean the model is loaded. | S001 README at pinned `c0fd7862` and at master `7adf160c` (2026-10-19T22:23Z), L1256: "The returned list always has one single element. The `meta` field can be `null` (for example, while the model is still loading)." | `endpoint-identity.md:89` labels `/v1/models` "Identity readiness … Gate traffic on a matching expected ID". Matrix:14 puts loading state only on `/health`. Identity and readiness are conflated in the existing corpus. |
| U3 | **llama.cpp router mode separates available models from loaded ones on a different route.** `GET /models` is "List available models" and carries a `status` value: `loaded`, `unloaded`, `loading`, `sleeping`, `downloading`, `incomplete`. The router's `/v1/models` gets forwarded info "When the model is loaded". With no `-m`, the claim "`data[].id` = `-m` path" does not hold. | S001 L1849: "`llama-server` can be launched in a **router mode** that exposes an API for dynamically loading and unloading models." L1995 heading `GET /models: List available models`. L2026 "When the model is loaded, the info from `/v1/models` is forwarded to router's `/v1/models`." L2337: sleep mode unloads the model from RAM. All present at pinned `c0fd7862` (grep hit L1993, L2024). | Matrix:14 assumes single-model mode. This is the llama.cpp analogue of tags/ps and does not appear anywhere in the corpus. |
| U4 | **An Ollama "available" entry can be a remote upstream, not local weights.** | S011 `ModelSummary`: `remote_model` "Name of the upstream model, if the model is remote"; `remote_host` "URL of the upstream Ollama host, if the model is remote". S010 §Models: "Through a signed-in local server, select a cloud model such as `gemma4:cloud`." | Not covered anywhere. "Available" is not the same as "local". |
| U5 | **Alias identity differs by engine.** Ollama `ollama cp llama3.2 gpt-3.5-turbo` creates a second name. `ollama create` with `num_ctx` creates a new name for the same base model. llama.cpp `--alias` now takes a comma-separated list. | S010 §Default model names on a local server; §Setting the local context size. S001 L190: "`-a, --alias STRING` \| set model name aliases, comma-separated (to be used by API)". S011/S012 both expose `digest` (tags: "SHA256 digest identifier of the model contents"; ps: "SHA256 digest of the model"). | The digest is the only documented field shared by tags and ps that could serve as a join key. The opened pages do **not** say whether `cp` keeps the digest, so the entry must state that as not documented (KQ9), not as a fact. |
| U6 | **Loaded state on Ollama expires.** | S012 `Ps`: `expires_at` "Time when the model will be unloaded"; also `size_vram`, `context_length`. | A `/api/ps` hit is a dated sample with an expiry, not durable readiness. No existing entry says this. |

## Impacted axes

- **Coverage (C2):** counts as expansion only through U1–U6. The available/running split alone is not expansion.
- **Freshness / provenance:** matrix:17 cites the wrong sources. The README:32 description of served-model-identity.md over-claims.
- **Operability:** U1 and U2 mean `MODEL_OK` does not mean "loaded" on Ollama, or on llama.cpp during load. That bounds what the probe verdict means. No probe change is proposed here; this is a documentation boundary.

## Smallest safe correction

1. The crosswalk cites `runtime-health-surface-matrix.md:17` as prior coverage of the tags/ps split and claims none of it as new.
2. The expansion claim names U1 and U2 at minimum: which side of available/loaded each engine's `/v1/models` falls on. Add U3–U6 where sourced.
3. U1 must not rest on S010 alone. Either add a revision-pinned code source row for `server/routes.go`, or write "not documented in S010" + `[INFERENCE]`.
4. Parent appends a correction to matrix:17: S-id `S009, S010` → S011, S012 for the tags/ps claim. Flag README:32 as over-describing served-model-identity.md.
5. Suggested acceptance for Measure: the crosswalk must contain at least one claim that cannot be derived from matrix:14/17 + `endpoint-identity.md:82-93`, and every such claim must name its S-id and section.

## Limits

- Ollama `routes.go` line numbers come from a main-branch fetch, with commit `4ed3ba13` as the latest path commit at fetch time. They will drift, so pin by commit.
- I did not check whether llama.cpp `/health` returns 200 while a model is sleeping. L2342 only says `GET /health` does not trigger a reload.
- No runtime behavior is claimed. All findings are documentation and source facts.
- Installs/updates: none.
