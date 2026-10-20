# ReviewIdentity — C2 served-identity source hierarchy review (kama round 11)

verified-at: actual review 2026-10-20T02:14:27Z (`date -u`); the steered round label 2026-10-19 is retained in this heading only. Historic S-row fields (opened 2026-10-19, pins, quotes) are reported unchanged. Everything marked "re-opened" was read by this seat today (2026-10-20 UTC) via public vendor docs or the raw llama.cpp master README. No endpoint was contacted, no build/lint/test was run, and no file other than this report was written.
recheck: after the parent's SOURCES.md status reconciliation and after the served-identity-crosswalk draft lands.
tools: none installed or upgraded.

Scope: `corpus/SOURCES.md` (S001, S010, S011, S012, S016), `.ufo/round-10/fragments/KamaExecHealth-sources.md`, `corpus/lessons/round-10.md` §Gate, `corpus/knowledge/runtime-health-surface-matrix.md`, `corpus/knowledge/endpoint-identity.md`, `corpus/knowledge/served-model-identity.md`.

## Summary

Five public source pages were re-opened. The quotes the registry and lesson carry for S010, S011, S012 and S016 are verbatim on the page today. The S001 `/health` quote is verbatim on the raw master README. Three things are not safe to draft from as written:

1. The registry says S011/S012/S016 are `queued` while the lesson records them as opened. The status cells must be reconciled before the C2 entry cites them as `mined`.
2. "Locally available" (S011) is overstated: the Ollama schema models remote/cloud entries in the same list.
3. The llama.cpp router mode (a current-master behaviour I read today) changes what `/health` and `/v1/models` mean. The health matrix describes only single-model semantics, and the pinned revision c0fd7862 was not what I read.

## Findings (by severity)

### F1 — HIGH — registry status contradicts the lesson's Gate (S011, S012, S016)
- `corpus/SOURCES.md` rows S011, S012, S016: status `queued`, used-by `—`, opened `2026-10-19`.
- `corpus/lessons/round-10.md` §Gate table lists quotes for the same three rows, and §Admissions defers K02 because "rows S011 S012 S016 are opened and `queued`".
- The lesson's opened/queued wording is internally inconsistent: a row cannot be "opened" with a quote and still "queued" with no used-by. The `queued` status is the operative one for `SOURCES-CONTRACT-v1`.
- Consequence: the C2 entry must not cite S011/S012/S016 as tier-A `mined` evidence until SourceCurator updates the status cells. Parent integration decision.

### F2 — HIGH — S011 "locally available" overstates the /api/tags schema
- Re-opened: `https://docs.ollama.com/api/tags` (actual review 2026-10-20 UTC), §OpenAPI `ModelSummary`. Quote: "Summary information for a locally available model". Also property `remote_model`: "Name of the upstream model, if the model is remote"; `remote_host`: "URL of the upstream Ollama host, if the model is remote".
- Re-opened: `https://docs.ollama.com/api/openai-compatibility`, §"Direct cloud access" and the local-server passage (artifact read, lines ~354-378 of the page): "Direct cloud requests use the identifiers from `https://ollama.com/api/tags`" and "select a cloud model such as `gemma4:cloud`".
- SOURCES S011 teaches "Lists locally available models"; scope says "locally available model inventory". The schema shows a list that can include remote entries.
- Check after draft: no crosswalk line may equate `/api/tags` with local weights on disk. An entry must carry the `remote_model`/`remote_host` distinction or state it as undocumented.

### F3 — HIGH — /v1/models identity semantics for Ollama are undocumented in the opened pages
- Re-opened S010 (`docs.ollama.com/api/openai-compatibility`, §Endpoints `/v1/models` Notes): the only semantic stated is "`created` corresponds to when the model was last modified". The page does not say whether `/v1/models` lists installed, running, cloud, or copied names.
- The health matrix's Ollama row names `/v1/models` as the identity route. That is supported only as a route, not as a loaded-model or local-weight statement. It is also a surface on which `ollama cp` aliases appear. Re-opened same page, §Default model names: "use `ollama cp` to copy an existing model name to a temporary name" — so a served name can be a copy alias of a different model.
- Check after draft: the Ollama identity row must say "served name per /v1/models is not documented to be the digest of loaded weights" and must not pick a single authority by name alone. [INFERENCE] name-only matching is unsafe because of the `ollama cp` alias path.

### F4 — HIGH — available vs running join key for Ollama (S011 vs S012)
- Re-opened S012 `https://docs.ollama.com/api/ps`, §OpenAPI `/api/ps` 200 response: "Models currently loaded into memory" (summary: "Retrieve a list of models that are currently running"). Fields include `digest`, `expires_at`, `size_vram`, `context_length`.
- Re-opened S011 `/api/tags`: fields include `digest` ("SHA256 digest identifier of the model contents").
- Both schemas expose `digest`, so a digest join between "available" and "running" is possible from documented fields. [INFERENCE] the join is not described by Ollama; it is a candidate, not a verified mapping.
- Trap: an empty or absent `/api/ps` entry at one instant is not "not running" in general; `expires_at` shows unload is time-based. A timestamped observation only (matches endpoint-identity.md's "a verdict is a timestamped observation").

### F5 — HIGH — llama.cpp `/health` is server-level, not per-model, in router mode
- Re-opened raw master README (`https://raw.githubusercontent.com/ggml-org/llama.cpp/master/tools/server/README.md`), §GET `/health` (lines 483-494): "This endpoint is public (no API key check). `/v1/health` also works." 503 body "Loading model"; 200 body `{"status": "ok" }`; "Explanation: the model is successfully loaded and the server is ready."
- Router-mode text (same file, sleep section ~2337-2342): "The following endpoints are exempt ... `GET /health` ... They do not trigger model reloading and do not reset the idle timer."
- So in router mode, a 200 `/health` does not say which model is loaded, and a model may be unloaded or sleeping while `/health` answers 200. The matrix's llama.cpp readiness cell ("200 `{"status": "ok"}` when loaded") is accurate only for the single-model reading and must say so.
- The S001 quote used in the lesson/fragment is verbatim on the master file (line 494). The pinned revision c0fd7862 was NOT read today; the router text may postdate it. Parent must mark this as a master-observed claim, or re-pin.

### F6 — HIGH — llama.cpp `/v1/models` vs `/models` split is missing from the matrix
- Re-opened same README, §GET `/v1/models` (lines 1256-1260): "Returns information about the loaded model." "The returned list always has one single element. The `meta` field can be `null` (for example, while the model is still loading)."
- Re-opened §GET `/models` (lines 1996-2030, router mode): "Listing all models in cache. The model metadata will also include a field to indicate the status of the model." Status values observed in the text: `unloaded`, `loading`, `loaded`, `sleeping`, `downloading`, `incomplete`.
- Id rule (lines 1286): model `id` is the `-m` path unless `--alias` is set. This matches the matrix and the served-model-identity probe output.
- Required crosswalk split for llama.cpp: availability = `GET /models` (`status`), running/loaded = `status.value == "loaded"` (or per-model `GET /props?model=`), identity = `/v1/models` `data[].id`. The matrix currently has no router row. Draft must add it or scope the llama.cpp row to single-model mode.

### F7 — MEDIUM — health matrix and endpoint-identity are consistent with each other, but the Ollama row is thin
- `runtime-health-surface-matrix.md` Ollama row: "No dedicated health route in the two opened pages"; S009 re-opened today (`docs.ollama.com/api/introduction`, §Base URLs and §Versioning) contains no health route. Consistent with the row.
- The matrix correctly says absence is not non-existence. Lead still open: Ollama root/liveness route not checked in any opened page. Do not assert it either way.

### F8 — MEDIUM — served-model-identity.md is a historical snapshot
- The file contains only a readiness-field probe block with outputs `{"status":"ok"}`, `/slots` with two idle slots, and `llamacpp:` metrics, all from one llama.cpp listener at `127.0.0.1:34113`. These are dated captures, not current state. `endpoint-identity.md` already treats them as frozen L1 evidence.
- Check after draft: the crosswalk must not reuse these outputs as present-tense evidence. It may cite them as historical.

### F9 — MEDIUM — registry S016 scope vs. the lesson quote
- S016 (OpenAI `GET /models`) re-opened today: "Lists the currently available models, and provides basic information about each one such as the owner and availability." The description says "available", not "loaded"; the schema has no loaded/running field. Registry scope ("not local readiness") is accurate. The crosswalk may use it only as a reference list shape.

## Verified quotes (re-opened 2026-10-20 UTC; the S-row historic open date is 2026-10-19 and is unchanged)

| id | URL | location | quote (≤25 words) | status vs registry |
|---|---|---|---|---|
| S011 | https://docs.ollama.com/api/tags | §OpenAPI `ModelSummary` | "Summary information for a locally available model" | matches lesson; contradicted by `remote_model` schema (F2) |
| S012 | https://docs.ollama.com/api/ps | §OpenAPI `/api/ps` 200 | "Models currently loaded into memory" | matches lesson |
| S016 | https://developers.openai.com/api/reference/resources/models/methods/list | §List models, description | "Lists the currently available models, and provides basic information about each one such as the owner and availability." | matches lesson verbatim |
| S010 | https://docs.ollama.com/api/openai-compatibility | §Endpoints `/v1/models` Notes | "`created` corresponds to when the model was last modified" | matches registry scope; semantics otherwise undocumented (F3) |
| S010 | same page | §Default model names on a local server | "use `ollama cp` to copy an existing model name to a temporary name" | new; supports alias-identity caution (F3) |
| S001 | raw master README | §GET `/health` 200 branch (line 494) | "Explanation: the model is successfully loaded and the server is ready." | verbatim on master today; pinned c0fd7862 not read (F5) |
| S001 | raw master README | §GET `/health` (line 485) | "This endpoint is public (no API key check)." | new; supports F5 |
| S001 | raw master README | §GET `/v1/models` (line 1258) | "Returns information about the loaded model." | new; supports F6 |
| S001 | raw master README | §GET `/models` (line 1998) | "Listing all models in cache. The model metadata will also include a field to indicate the status of the model:" | new; router split (F6) |

## Required independent checks after the C2 draft (not run here)

1. SOURCES.md: S011/S012/S016 status cells and used-by reconciled by SourceCurator; S001/S010 used-by lists the crosswalk path. Parent to confirm before the entry cites them.
2. Crosswalk Ollama row: separate `/api/tags` (available, may include remote), `/api/ps` (running, time-bounded), `/v1/models` (identity, semantics undocumented), with the `ollama cp` alias case and a digest-join candidate labelled [INFERENCE].
3. Crosswalk llama.cpp row: state single-model vs router mode; `/health` is not identity and not per-model; `/models` `status` for availability; pin the revision the router text came from (master today vs c0fd7862).
4. Crosswalk must not present the served-model-identity.md captures as current.
5. Each source row quote re-checked by a non-author reviewer against the page, with the actual access date (UTC) recorded alongside the historic open date.

## Residual risk and verification gaps

- The vLLM (S002/S004) and SGLang (S006/S020) rows were not re-opened in this pass; they are outside the assigned slice.
- The Ollama root/liveness route is unchecked (lead, not a claim).
- The router-mode text is from master today; its revision relationship to the pinned c0fd7862 is unknown.
- No local runtime was contacted; nothing here says any engine is running today.
- Line numbers cited for raw README content refer to the reader output of the master file read today; they are not the pinned revision's line numbers.

## Post-draft review — final `corpus/knowledge/served-identity-crosswalk.md` (appended; earlier findings above unchanged)

verified-at: actual review 2026-10-20T02:21Z (`date -u`; `git ls-remote` HEAD sampled 02:21Z); steered round label 2026-10-19 retained in heading only. No build, test, or runtime contact. Historic open dates unchanged.

### Resolved from the earlier review

- My F5/F6 open question ("the router text may postdate the pinned c0fd7862") is closed. I downloaded `https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md` (2400 lines, to /tmp). It contains the router `GET /models` `status` block, `/v1/models` "always has one single element", `meta` may be `null` while loading, `GET /props` `is_sleeping`, and the sleep exemption for `GET /health`, `GET /props`, `GET /models`, `GET /metrics`. The matrix correction block (`runtime-health-surface-matrix.md:52-56`) is therefore correct about the pinned revision.
- HEAD check: `git ls-remote` returns `3bb63cbc` at 02:21Z, matching the crosswalk header.
- Quotes re-verified against the pages: S011 "Summary information for a locally available model"; S012 "Models currently loaded into memory"; S016 description verbatim; S010 `created`/`owned_by` notes; S001 `meta` null (pinned line 1256); `/props` `model_path` (pinned ~931); `owned_by`: "llamacpp" (master ~1302); `ollama create` with `num_ctx` ("Use the `ollama create mymodel` command to create a new model with the updated context size") supports failure case 5.
- `PROVINCE.md:10,27-28` confirms the qwen-coder unit is deleted/row-absent, which supports the crosswalk's "not currently serving" wording.
- `corpus/SOURCES.md` S031 row: tier A, `mined`, opened 2026-10-20, used-by crosswalk, quotes its `remote_model`/`remote_host` descriptions correctly.
- `endpoint-identity.md:155-164` correction: states the predicate scope; verdict vocabulary and probe implementation are stated as unchanged. I did not find an overreach there.

### Post-draft defects (ordered by severity)

**D1 — MEDIUM — negative claim overgeneralised (crosswalk "What cannot be concluded" / cross-engine bullet, line ~39).** "no digest exists on the OpenAI-shaped surface (S016)" turns one reference page into a claim about every OpenAI-shaped surface. S016 only shows the reference shape has no digest field (line 19 already says this correctly). KQ9 requires "not documented in the opened page". Fix: "S016's reference shape has no digest field."

**D2 — MEDIUM — quote drops its condition (failure case 6, line ~31).** The crosswalk quotes "select a cloud model such as `gemma4:cloud`" without the qualifier that precedes it in S010 (§Default model names): "Through a signed-in local server, select a cloud model such as `gemma4:cloud`." The qualifier decides whether a local server can list cloud entries, so it must appear in the quote or be stated beside it.

**D3 — MEDIUM — registry S011 still teaches the overstated claim (SOURCES.md row S011, line 23).** The S011 row's scope and teaches cells still read "Ollama locally available model inventory" and "Lists locally available models". The crosswalk (Province handoff, line ~52) says this correction is "already handled by S031's supersession", but nothing in the S011 row points to S031. A reader who starts from S011 gets the overstated claim with no pointer. Fix (SourceCurator, append-only status/annotation): add "superseded in part by S031 (remote entries)" to the S011 teaches cell. Do not rewrite the quoted text.

**D4 — MEDIUM — index row still false (`corpus/README.md:32`).** It describes `served-model-identity.md` as "served-model reconciliation (`/v1/models` vs `--alias` vs configured id) + the minimal proof procedure". The file is 37 lines and contains only the readiness-field probe block (historical llama.cpp captures). The crosswalk flags this as "parent correction pending"; I confirmed it is still uncorrected at 02:21Z.

**D5 — LOW-MEDIUM — inference stated as documented (crosswalk row llama.cpp single-model, line ~20; Claim paragraph).** "the id can be listed before loading finishes" and "/v1/models can answer while that model is still loading" are inferences from "always has one single element" and "`meta` can be `null` (for example, while the model is still loading)". The text does not state that `data[].id` is present during load. Mark as [INFERENCE] or quote the exact sentence.

**D6 — LOW-MEDIUM — table cell not scoped (`runtime-health-surface-matrix.md:14`).** The cell still reads "200 proves a model finished loading, not which model". The round-11 correction block (lines 52-56) says this must not generalise to router state, but the cell itself is unscoped. Fix: add "(single-model mode)".

**D7 — LOW — heading casing (crosswalk header line 3 and Cited sources).** The crosswalk cites "§Sleeping on Idle"; the pinned README heading is "Sleeping on idle" (anchor `#sleeping-on-idle`). Fix the casing.

**D8 — LOW — provenance understated (crosswalk header line 3).** It says "router sections re-checked on master 2026-10-20". The pinned `c0fd7862` file also contains them (verified today, see above). Add "and present at pinned c0fd7862, fetched 2026-10-20" so the revision pin is actually supported.

### Not defects (checked)

- Crosswalk `/props` `model_path`, `owned_by` "llamacpp", router `id` plus separate `path`, `status.value` set (`loaded`/`unloaded`/`loading`/`sleeping`/`downloading`/`incomplete`), and `GET /props?model=` for sleeping status all match the README.
- "Sleep mode unloads the model ... from RAM" matches the sleep section.
- The `/health` 503 "Loading model" / 200 `{"status": "ok"}` wording in the matrix matches the pinned README.

### Residual gaps (post-draft)

- I did not re-open the Ollama `/v1/models` page's full `/v1/models/{model}` section beyond the header; the crosswalk cites only the notes, which I did check.
- The S001 `Sleeping on idle` section was checked by grep and read at pinned lines 2336-2342; I did not read the whole section.
- No Ollama root/liveness route check was done; it stays a lead.
- Earlier F1-F9 findings are unchanged and remain valid.

