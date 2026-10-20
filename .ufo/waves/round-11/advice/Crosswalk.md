# Crosswalk — served-identity crosswalk entry (C2), kama round 11

Seat: `Crosswalk` (executor, leaf). Actual UTC work window: 2026-10-20T02:14–02:35Z (`date -u` 2026-10-20T02:14:40Z); steered round label 2026-10-19 is retained only as the round name, and historical round-10 dates stay 2026-10-19. No local runtime contacted, no build/lint/test/formatter run, no installs or upgrades.

## Files changed

| File | Change |
|---|---|
| `corpus/knowledge/served-identity-crosswalk.md` | NEW entry (14437 bytes). Begins `source:` / `verified-at:` / `recheck:`; per-engine route/field/semantics/cannot-conclude crosswalk (OpenAI reference, llama.cpp single-model, llama.cpp router, Ollama); grounded failure cases; alias + path-normalization limits; universal-readiness/loaded-weight limits; province handoff; QUALITY clearance; cited sources. |
| `.ufo/waves/round-11/advice/Crosswalk.md` | This report (only other write). |

No other file was written or modified; sibling reports untouched; SOURCES.md left to SourceCurator.

## Behavior / deliverable

The entry separates four predicates the corpus previously mixed: **availability**, **loaded residency**, **alias identity**, **readiness**. It credits `runtime-health-surface-matrix.md:17` for the existing tags-vs-ps split and claims only new distinctions: remote entries in `/api/tags` (S031), `expires_at` lifecycle (S012), alias and digest-join limits (S010/S011/S012), llama.cpp `/v1/models` answering while loading (S001), llama.cpp router-mode `status` states and exempt routes (S001). It states no runtime fact and calls nothing integration.

## Retained evidence (all five public URLs re-opened this round)

Quotes ≤25 words; locations as on the page; all accessed 2026-10-20 UTC unless marked historic.

| id | URL | location | quote | note |
|---|---|---|---|---|
| S016 | https://developers.openai.com/api/reference/resources/models/methods/list | §List models | "Lists the currently available models, and provides basic information about each one such as the owner and availability." | catalog availability only; no residency field |
| S001 | https://raw.githubusercontent.com/ggml-org/llama.cpp/c0fd78626405c6d9b934efef0ec7291fcc20e3d6/tools/server/README.md | §GET `/v1/models` | "Returns information about the loaded model." | single-model route |
| S001 | same, §GET `/v1/models` | | "The returned list always has one single element. The `meta` field can be `null` (for example, while the model is still loading)." | id listed mid-load |
| S001 | same, §GET `/v1/models` | | "By default, model `id` field is the path to model file, specified via `-m`." | alias override follows |
| S001 | same, §Options | | "set model name aliases, comma-separated (to be used by API)" | `-a, --alias STRING` |
| S001 | same, §GET `/models` | | "Listing all models in cache. The model metadata will also include a field to indicate the status of the model" | router mode |
| S001 | same, §Sleeping on Idle | | "They do not trigger model reloading and do not reset the idle timer" | `/health` `/props` `/models` `/metrics` exempt |
| S010 | https://docs.ollama.com/api/openai-compatibility | §Endpoints `/v1/models` Notes | "`created` corresponds to when the model was last modified" | metadata only |
| S010 | same, §Default model names on a local server | | "use `ollama cp` to copy an existing model name to a temporary name" | alias case |
| S010 | same, §Models | | "select a cloud model such as `gemma4:cloud`" | cloud entry reachable locally |
| S011 | https://docs.ollama.com/api/tags | §OpenAPI `ModelSummary` | "Summary information for a locally available model" | row prose caveat → S031 |
| S031 | same `/api/tags` page, §OpenAPI `ModelSummary` | | "Name of the upstream model, if the model is remote" / "URL of the upstream Ollama host, if the model is remote" | available ≠ local |
| S012 | https://docs.ollama.com/api/ps | §OpenAPI `/api/ps` 200 | "Models currently loaded into memory" | loaded list |
| S012 | same, `Ps.expires_at` | | "Time when the model will be unloaded" | time-bounded |
| S012 | same, `Ps.digest` | | "SHA256 digest of the model" | join candidate vs tags digest "SHA256 digest identifier of the model contents" — labelled [INFERENCE] |

Anchors: S001 read at pinned file commit `c0fd78626405c6d9b934efef0ec7291fcc20e3d6`; master re-checked 2026-10-20T02:14Z — `git ls-remote` HEAD `3bb63cbcbfb62056c84fe9e521b0f3d756d29c32` (master had moved past the row's `4c3c5810` note and the scouts' earlier fetch); router sections confirmed present on master at that check. S010 source pinned `ollama/ollama docs/api/openai-compatibility.mdx @ c1737589973d5cefd676ef16eb43835663540035`. S011/S012/S031: OpenAPI 3.1.0, info.version 0.1.0, server `http://localhost:11434`.

## Integration of peer review

- `ReviewIdentity.md` caveats all incorporated: remote_model/remote_host (F2 → S031), Ollama `/v1/models` documents metadata not residency (F3), digest join stated as [INFERENCE] with no artifact proof (F4), llama.cpp split single-model vs router with `/health` server-level and exempt (F5/F6), `served-model-identity.md` cited only as historical, not alias coverage (F8), S016 used only as reference shape (F9).
- `AttackCoverage.md` incorporated: prior coverage credited (`matrix.md:17`), expansion rests on U1–U6 as above; the Ollama `/v1/models` backend (ListHandler) is **not** asserted — per parent instruction the entry states only what the opened docs do not guarantee. Matrix:17 S-id defect and `corpus/README.md:32` over-description are left as parent-owned corrections.
- Parent erratum (C1 axis = calibration, not freshness) does not change this slice; the entry carries provenance fields with actual-vs-historic dates.

## Risks / limits

- S001 master drift: master moved during the wave (`3bb63cbc` at my 02:14Z check; scout reported `7adf160c` earlier). Entry pins the router text to `c0fd7862` and records the master re-check; if the parent wants a fresh master pin in S001, that is a SOURCES.md edit owned by SourceCurator.
- No runtime was contacted; every statement is documentation-scoped and says so (KQ4/KQ6). `MODEL_OK` semantics unchanged — no probe behavior modified.
- S011 row prose still reads "locally available"; superseded by S031's row. Matrix:17 S-id cell still `S009, S010`; both corrections are parent/SourceCurator-owned, not rewritten by this seat.
- Sibling files were read (advice reports) but not written; no coordination message was required.

## Tooling

No installs or upgrades (nothing needed). Commands used: `read`/`grep`/`write`, `bash` for `date -u`, `md5sum`/`grep`/`git status`/`git log`/`git ls-remote` (read-only).
