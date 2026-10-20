source: S016 https://developers.openai.com/api/reference/resources/models/methods/list §List models; S001 https://github.com/ggml-org/llama.cpp/blob/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md §GET `/v1/models`, §GET `/models`, §Sleeping on idle (single-model, router and sleep text verified at this pinned revision); S010 https://docs.ollama.com/api/openai-compatibility §Endpoints `/v1/models` + §Models; S011 https://docs.ollama.com/api/tags §OpenAPI `ModelSummary`; S012 https://docs.ollama.com/api/ps §OpenAPI `/api/ps`; S031 https://docs.ollama.com/api/tags §OpenAPI `ModelSummary` (remote-entry caveat; supersedes S011's local-residency implication)
verified-at: 2026-10-20 (actual UTC review date, `date -u`; steered round label 2026-10-19) — five public documentation pages re-opened read-only this round; historical round-10 observations keep their 2026-10-19 date; no local runtime contacted
recheck: on-release — S001 §GET `/v1/models` + §GET `/models` + §Sleeping on idle, S010 §Endpoints; 90d — S011, S012, S016, S031 list pages

# Served identity crosswalk — what a model-list route actually proves

## Claim

The OpenAI-shaped model-list routes here do not guarantee residency or readiness: OpenAI's reference lists catalog availability, llama.cpp's `/v1/models` reports "information about the loaded model" but can answer while that model is still loading, and Ollama's compatibility page documents model metadata without a loaded-state guarantee. Ollama's separate native `/api/ps` does report loaded models, bounded by an unload time; `/api/tags` reports available inventory that may include remote entries. A `MODEL_OK` id match therefore proves only that the expected id was listed at sample time — not that weights are loaded, local, or ready to execute.

## Prior coverage (credited, not re-claimed)

The bare Ollama split — `/api/tags` = available models, `/api/ps` = running models — is already in the corpus at `corpus/knowledge/runtime-health-surface-matrix.md:17`; this entry credits that matrix row and claims none of the split as new. What is new here: `/api/tags` entries can be remote (`remote_model`/`remote_host`, S031), `/api/ps` loaded state is time-bounded (`expires_at`, S012), alias/name and digest-join limits (S010, S011, S012), llama.cpp `/v1/models` answering while loading (S001), and llama.cpp router-mode `status` states (S001). The matrix row's original S-id cell (`S009, S010`) is corrected by its appended round-11 section to S011/S012.

Prior registry knowledge is also credited: S012 already named expiry fields and
S016 already separated a catalog from local readiness. The historical alias
observations in `listener-census.md`, `consumer-registry.md` and the local
normalization convention in `endpoint-identity.md` are not new findings here.
C2 counts this as one knowledge extension, not additional coverage gains for
the accompanying corrections to older entries.

## Crosswalk

| Engine / documented revision | Actual model routes | id / name / digest fields | Available vs loaded semantics | What cannot be concluded |
|---|---|---|---|---|
| OpenAI reference (S016, OpenAPI commit c396f25f, metadata 2.3.0) | `GET /models` (base `/v1/models`) | `data[].id` ("The model identifier, which can be referenced in the API endpoints"); `object`, `created`, `owned_by`, optional `shutdown_date`; no digest field | "Lists the currently available models, and provides basic information about each one such as the owner and availability." — catalog/account availability only; no loaded/running field | Nothing about a local server: not its health, not loaded weights, not that a listed id will execute. The reference shape is not local runtime proof |
| llama.cpp single-model (S001 @c0fd7862) | `GET /v1/models` (one element); `GET /props` (`model_path`); `/health` load-state wording is not a sleeping/router readiness guarantee | `data[].id` defaults to the `-m` path, overridable via `--alias`; `created`, `owned_by` (example `"llamacpp"`), `architecture.input_modalities`/`output_modalities`, `meta` GGUF metadata | The documented list always has one element; `meta` can be `null` "for example, while the model is still loading". [INFERENCE] Identifier listing alone is not a load-completion guarantee | The documented response has no digest field; the choice among comma-separated aliases is undocumented; alias-to-path mapping is not a documented identity proof |
| llama.cpp router mode (S001; launch without `-m`) | `GET /models` (cache listing); `/v1/models` (forwarded per loaded model); `GET /props?model=` for sleeping status | `id` is the preset/repo tag with a separate `path` field; `status.value` is `loaded` / `unloaded` / `loading` / `sleeping` / `downloading` / `incomplete` | "Listing all models in cache. The model metadata will also include a field to indicate the status of the model"; "When the model is loaded, the info from `/v1/models` is forwarded to router's `/v1/models`." Sleep mode unloads "the model and its associated memory (including the KV cache) ... from RAM" | `/health` is server-level here and does not name a model; `/health`, `/props`, `/models`, `/metrics` are exempt from incoming tasks — "They do not trigger model reloading and do not reset the idle timer", so a 200 does not wake a sleeping model; the single-model `-m`-path `id` rule must not be applied to router ids |
| Ollama (S010 @c1737589; S011; S012; S031) | `/api/tags` (native available list); `/api/ps` (native running list); `/v1/models` and `/v1/models/{model}` (OpenAI-compatible) | tags: `name`, `model`, `remote_model`/`remote_host` ("if the model is remote"), `modified_at`, `size` ("Total size of the model on disk in bytes"), `digest` ("SHA256 digest identifier of the model contents"), `details`; ps: `name`, `model`, `size`, `digest`, `details`, `expires_at`, `size_vram`, `context_length`; `/v1/models` documents only that "`created` corresponds to when the model was last modified" and "`owned_by` corresponds to the ollama username, defaulting to `\"library\"`" | tags = "Summary information for a locally available model" (200 description: "List available models"), membership may be remote; ps = "Models currently loaded into memory" with `expires_at` = "Time when the model will be unloaded"; `/v1/models` documents metadata only, not residency | `/v1/models` cannot be read as loaded residency (the page does not say whether it lists installed, running, cloud or copied names); a tags entry does not prove local weights (S031); a ps sample is not durable (unload time); name-only matching is unsafe because `ollama cp` copies "an existing model name to a temporary name"; joining tags/ps by digest is [INFERENCE] — the pages do not describe the join and prove no on-disk artifact identity |

## Grounded failure cases

1. **llama.cpp during load** — the documented list always has one element and `meta` can be `null` "for example, while the model is still loading". [INFERENCE] Therefore identifier listing alone cannot be used as a load-completion guarantee (S001); this is not a runtime observation.
2. **llama.cpp router sleep/unload** — `/models` lists a model with `status.value: "unloaded"` or `"sleeping"` while `/health` still answers, because the exempt routes "do not trigger model reloading and do not reset the idle timer"; a health 200 names no model (S001).
3. **Ollama tag without a ps entry** — a tag can be listed in `/api/tags` and absent from an `/api/ps` sample; these pages do not document on-demand load behavior, so absence at one sample must not be concluded either way (S011/S012; KQ9).
4. **Ollama expiry** — `expires_at` is "Time when the model will be unloaded": a `/api/ps` hit is a time-bounded observation, not durable readiness (S012).
5. **Ollama alias** — `ollama cp` and `ollama create` (context-size variant) produce additional names; whether the copy keeps the digest is not documented, so a name match can match a name that maps to a different or duplicated artifact (S010/S011/S012).
6. **Ollama remote entry** — a tag may carry `remote_model`/`remote_host`. S010's cloud-model selection example requires a **signed-in local server**; do not drop that precondition. Available inventory is not proof of local weights (S031/S010).
7. **OpenAI reference misuse** — `shutdown_date` and `owned_by` are catalog lifecycle/ownership fields; reading them as local readiness or loaded weights is unfounded (S016).

## Aliases and path normalization limits

- llama.cpp: `id` defaults to the `-m` path; `--alias` overrides it, and `-a, --alias STRING` is "set model name aliases, comma-separated (to be used by API)" — the docs do not state which alias lands in `id` when several are given. `--tags` is "set model tags, comma-separated (informational, not used for routing)". Router ids are preset/repo tags plus a separate `path`; the `-m`-path rule does not transfer (S001).
- kama's probe normalization (basename after the final `/`, strip one trailing lowercase `.gguf`, case-sensitive compare) is kama's own convention recorded in `endpoint-identity.md` and `SKILL.md` — not an engine-documented equivalence, and it must not be presented as one (S001, S010 vs `endpoint-identity.md`).
- Ollama: `name` and `model` are both just "Model name"; only `digest` is content-addressed ("SHA256 digest identifier of the model contents" / "SHA256 digest of the model"), and the tags-to-ps digest join is an [INFERENCE] candidate, not a documented mapping (S010/S011/S012).
- Cross-engine: OpenAI ids are opaque references; id string equality across engines is not content identity. S016's reference schema has no digest field; that is not a claim that every OpenAI-compatible implementation omits extension fields.

## What cannot be concluded

- **No universal readiness predicate.** Nothing in these pages defines one predicate meaning "weights resident and ready" across engines: llama.cpp's single-model list can answer while loading, its router list includes unloaded/sleeping models, Ollama `/v1/models` documents metadata only, the OpenAI reference has no residency field, and `/health` is not identity (`runtime-health-surface-matrix.md:14`).
- **No inference-readiness guarantee from inventory.** Loaded-residency statements exist where documented: llama.cpp router `status.value == "loaded"` and `/props` for sleeping, and Ollama `/api/ps` entries bounded by `expires_at`. Neither is a durable readiness guarantee. Ollama's compatibility documentation does not specify equivalent residency fields.
- **A `MODEL_OK` verdict is an inventory statement at sample time.** It never establishes loaded weights, local (vs remote) provenance on Ollama, or execution readiness — and on llama.cpp single-model it can even be observed mid-load.
- **Docs are not integration (KQ4).** No local runtime was contacted; nothing here says any engine is installed, running, or conforms to its docs today. The historical llama.cpp captures in `served-model-identity.md` are historical listener samples, not current state, and that file contains no alias-reconciliation coverage despite the original `corpus/README.md:32` description; the index's appended round-11 correction limits that description.

## Province handoff

- Local endpoint identity/liveness stays kama (`endpoint-identity.md`; `tools/kama-probe.sh check`). This entry authorizes no new probe and changes no probe behavior.
- Route/gateway selection (which upstream or model answers a request) → kumitate (`cross-lane-scope.md` adjacency rule); model quality/eval → kengaku; credentials/auth → kagi; remote web properties → kake; host config/service changes → operator (`PROVINCE.md` write boundary).
- Registry prose correction (S011 "locally available") is already handled by S031's supersession; the matrix:17 S-id correction and the `corpus/README.md:32` description correction are parent-appended, not rewritten here.

## kama use

- Keep `check` metadata-only: a matching `/v1/models` id is an inventory statement. On Ollama that is availability, not loaded residency (S031/S010); on llama.cpp single-model it can be observed before loading completes (S001).
- If loaded residency is the question, only cite the documented fields: llama.cpp router `status.value == "loaded"` / `/props` sleeping state, or Ollama `/api/ps` with its `expires_at` bound — and treat each as a dated observation, never as readiness.
- Never compare names across engines as identity; digests exist only on Ollama's native routes, and their join is a candidate, not a documented mapping.

## QUALITY clearance — author self-check, not outside verification

- KQ1: no present endpoint claim; every row is a documentation statement pinned to revision and section.
- KQ2: pin provenance and effective-runtime selection untouched; no endpoint verdict or effective-URL claim is made.
- KQ3: each anchor names section plus commit SHA or dated page; recheck cadence declared; historical captures left dated.
- KQ4: docs-scoped crosswalk; no runtime, fixture, or monitoring claim is made; the historical probes are cited as historical only.
- KQ5: no service started, no request sent, no credentials read; external remediation stays operator-owned.
- KQ6: every engine statement names engine + documented revision (commit or dated page) + section and cites an opened `SOURCES.md` row (tier A for its scope; no C-tier row supports this entry); never asserted as local runtime fact.
- KQ7–KQ10: not a correction entry (KQ7); no privilege-bounded verdict (KQ8); absences are stated as 'not documented in the opened pages', not as non-existence (KQ9); no census or probe was run for this entry (KQ10).

## Cited sources

- S016 — OpenAI List models, §List models + §Returns, OpenAPI commit `c396f25f2f8112d7761097b7b0217808dc65ddd4`, metadata version 2.3.0 (round-10 open 2026-10-19; re-opened 2026-10-20)
- S001 — llama.cpp server README, §GET `/v1/models` + §GET `/models` + §Sleeping on idle @ `c0fd78626405c6d9b934efef0ec7291fcc20e3d6`; all three sections verified at that pinned revision on 2026-10-20. Moving-master reads in seat reports are supplemental, not the authority for this entry.
- S010 — Ollama OpenAI compatibility, §Endpoints `/v1/models` Notes + §Models + §Default model names on a local server, source `docs/api/openai-compatibility.mdx` @ `c1737589973d5cefd676ef16eb43835663540035` (2026-09-23); re-opened 2026-10-20
- S011 — Ollama List models, §OpenAPI `ModelSummary` / `GET /api/tags`, OpenAPI 3.1.0 info.version 0.1.0 (round-10 open 2026-10-19; re-opened 2026-10-20)
- S012 — Ollama List running models, §OpenAPI `/api/ps`, OpenAPI 3.1.0 info.version 0.1.0 (round-10 open 2026-10-19; re-opened 2026-10-20)
- S031 — Ollama List models (remote entries), same `/api/tags` page §OpenAPI `ModelSummary`; supersedes S011's local-residency implication (opened 2026-10-20)
- Cross-references (not re-derived here): `runtime-health-surface-matrix.md:14,17`; `endpoint-identity.md` §ID normalization; `corpus/README.md:32`; `PROVINCE.md` outage/write-boundary state; `cross-lane-scope.md` adjacency rule.

## Correction — round 12 D4 (authored 2026-10-20 UTC)

This note adds the two labels D4 of `corpus/lessons/round-11-verifier-spotcheck.md`
requests. It reopens no page and adds no source row, fact, or coverage claim; it
cites the registry rows as recorded and leaves every original line, date and
citation above unchanged, including `verified-at`/`recheck` and the QUALITY
clearance. `corpus/SOURCES.md` cells are not rewritten; the label is carried
here because registry cells are append-only.

- **The locality conclusion is [INFERENCE].** The "a tags entry does not prove
  local weights (S031)" clause at line 29 and failure case 6 at line 38
  ("Available inventory is not proof of local weights") are kama's inference,
  not text from the opened page. The documented basis is the S031 row
  (`corpus/SOURCES.md` §Registry row S031, `docs` / tier A, opened 2026-10-20):
  `/api/tags` `ModelSummary` carries optional `remote_model` ("Name of the
  upstream model, if the model is remote") and `remote_host` (described in that
  row's claim cell as the upstream Ollama URL). [INFERENCE] Because the page
  documents that `/api/tags` membership can be remote, membership alone cannot
  establish locally resident weights; the page's "locally available" summary
  wording is not a per-entry locality guarantee. S011
  (`corpus/SOURCES.md` §Registry row S011, opened 2026-10-19) carries the same
  implication, so the same label applies to its summary wording.
- **`supersedes S011` is registry supersession, not an upstream change.** The
  line 1 and line 84 phrases "supersedes S011's local-residency implication"
  record a scope relation inside kama's `SOURCES-CONTRACT-v1` registry: S031 and
  S011 are two rows over the same `https://docs.ollama.com/api/tags` page, opened
  2026-10-20 and 2026-10-19 respectively, and S031 narrows S011's
  local-residency wording only (`corpus/SOURCES.md` §Registry rows S011 and
  S031; the registry search
  log records the review finding: "A same-page review finding (remote entries
  exist) produced one new row: S031", and that "S011's non-status fields stay as
  written"). It is not evidence that Ollama changed its documentation between
  the two opens, not a claim that the page said something different on
  2026-10-19, and not a retraction of S011's non-status cells — `name`, `digest`,
  `size`, `details`, and the available-vs-loaded distinction remain as recorded.
  No upstream diff was observed between the two opens, and none is claimed.

**Scope over `## Grounded failure cases`.** These labels govern that section
(heading at line 31), not only the table: "Grounded" describes each case's
documented premise, not every sentence in it — case 1 at line 33 already carries
an inline `[INFERENCE]` for its conclusion. In case 6 at line 38 the premise
(tags may carry the remote fields; S010's signed-in local-server precondition) is
documented, while the concluding sentence "Available inventory is not proof of
local weights" is the `[INFERENCE]` identified above. The same locality
conclusion is restated in the `MODEL_OK` bullet at line 52 ("never establishes
... local (vs remote) provenance on Ollama"); it carries the same `[INFERENCE]`
status and is not an additional page quote. No other failure-case sentence is
reclassified, and no case is added or removed.
