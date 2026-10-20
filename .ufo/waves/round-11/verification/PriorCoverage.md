# PriorCoverage — round 11 verification (critic, advisory only)

Seat: `KamaR11.PriorCoverage`. Scope: compare the original bytes of `corpus/knowledge/runtime-health-surface-matrix.md` (HEAD `2f7303c`, 40 lines / 6073 bytes) with the untracked `corpus/knowledge/served-identity-crosswalk.md` (78 lines). Do not count the `/api/tags` vs `/api/ps` split as new. List the distinctions that are new and sourced. Axis source: `../shokunin.conf:52`, `kama|kama-shokunin|operability + calibration (local model serving and endpoint health)`.

This report is advisory. A separate non-author review is still required. No checks, tests, builds, or linters were run. No implementation, corpus, or fleet file was edited. **Installs: none.**

## Method (read-only)

- I took the original matrix bytes from `git show HEAD:corpus/knowledge/runtime-health-surface-matrix.md`. I searched all of HEAD (`git grep HEAD -- corpus tools SKILL.md PROVINCE.md`) for each claimed-new term: `remote_model`, `remote_host`, `expires_at`/`expir`, `meta` null, `loading`, `router`, `sleeping`, `status.value`, `--alias`, `comma-separated`, `digest`, `ollama cp`, `shutdown_date`, `owned_by`, `/props`, `/api/ps`, `/api/tags`, `size_vram`, `locally available`, `catalog`.
- `cmp` of the HEAD bytes against the first 6073 bytes of the working-tree matrix returned `PREFIX_IDENTICAL`. `git diff` shows only 17 appended lines (working-tree lines 41–57). The original prefix is preserved, so the matrix:14 and matrix:17 anchors cited by the crosswalk are still valid.
- On 2026-10-20 I opened the public docs read-only with `curl` piped straight to `grep`/`sed`. Nothing was saved, and no local runtime or service was contacted.

## Located quotes (opened 2026-10-20)

| S-id | URL / location | Quote (≤25 words) |
|---|---|---|
| S001 | raw README @`c0fd78626405c6d9b934efef0ec7291fcc20e3d6` L1256 | "The returned list always has one single element. The `meta` field can be `null` (for example, while the model is still loading)." |
| S001 | same, L1995 | "Listing all models in cache. The model metadata will also include a field to indicate the status of the model" |
| S001 | same, L2339 | "the following endpoints are exempt from being considered as incoming tasks. They do not trigger model reloading and do not reset the idle timer" |
| S001 | same, L190 | "`-a, --alias STRING` \| set model name aliases, comma-separated (to be used by API)" |
| S011/S031 | https://docs.ollama.com/api/tags (OpenAPI `ModelSummary`) | `remote_model`: "Name of the upstream model, if the model is remote"; `remote_host`: "URL of the upstream Ollama host, if the model is remote" |
| S012 | https://docs.ollama.com/api/ps | `expires_at`: "Time when the model will be unloaded"; 200: "Models currently loaded into memory" |
| S010 | https://docs.ollama.com/api/openai-compatibility | "use `ollama cp` to copy an existing model name to a temporary name"; "Through a signed-in local server, select a cloud model" |
| S016 | https://developers.openai.com/api/reference/resources/models/methods/list | "Lists the currently available models, and provides basic information about each one such as the owner and availability." |

Every one of these quotes matches the crosswalk text it supports (`served-identity-crosswalk.md:20-22,26-38`).

## Prior coverage at HEAD (what is not new)

| Distinction | Already present at HEAD | Credited by the crosswalk? |
|---|---|---|
| `/api/tags` = available vs `/api/ps` = running | `runtime-health-surface-matrix.md:17`; `SOURCES.md:23` ("availability is distinct from running state"); `SOURCES.md:24` ("Separates running models from the available-model list") | Yes, matrix:17 (`crosswalk:13`). The SOURCES rows are not credited |
| `/api/ps` exposes expiry, digest, context length, VRAM | `SOURCES.md:24` ("exposes digest, context length, VRAM use, and expiry") | **No.** `crosswalk:13` lists `expires_at` as new |
| `/api/tags` carries digests | `SOURCES.md:23` ("names, digests, and format or quantization metadata") | No |
| OpenAI reference is not local readiness | `SOURCES.md:28` ("does not establish local-server health or loaded weights") | No. This is the lead clause of `crosswalk:9` |
| `/health` 200 proves load completion, not which model | `runtime-health-surface-matrix.md:14`; `endpoint-identity.md:123` | Yes (`crosswalk:43`) |
| One `/health` shape has no portable readiness meaning | `runtime-health-surface-matrix.md:8` | Partly. `crosswalk:43` extends it to model-list routes |
| llama.cpp `id` = `-m` path unless `--alias` | `SOURCES.md:13`; `runtime-health-surface-matrix.md:14` | Implicitly. Not listed as new |
| Alias = full GGUF path breaks consumer match; kama basename/`.gguf` normalization is kama's own rule | `listener-census.md:86-90`; `endpoint-identity.md:21,127`; `consumer-registry.md:155` (observed `"aliases":[...]` plus `models[]`); `endpoint-identity.md:63` (F4 `models[]`+`data[]`) | **No.** `crosswalk:13` says "alias/name ... limits" are new without crediting these. `crosswalk:37` repeats `endpoint-identity.md:21` |

## Distinctions that are new and sourced (relative to HEAD)

Each item had zero hits in HEAD's knowledge or registry text, or exists at HEAD only as a registry field note (marked).

1. **Ollama `/api/tags` can list remote entries** (`remote_model`/`remote_host`). Inventory is not proof of local weights. S031/S011. HEAD hits for `remote_model`: 0. **New.**
2. **An `/api/ps` hit is bounded in time** (`expires_at`), so it is not durable readiness. S012. **New as a knowledge claim.** The field itself was already registered at `SOURCES.md:24` (status `queued`, used-by `—`). Count the stated consequence, not the field.
3. **llama.cpp `/v1/models` can respond while the model is loading** (`meta: null`). S001 L1256. HEAD hits for `meta`/null and "still loading": 0. **New.**
4. **llama.cpp router mode**: the `GET /models` `status.value` enum (`loaded`/`unloaded`/`loading`/`sleeping`/`downloading`/`incomplete`), router `id` = preset/repo tag with a separate `path`, and `/v1/models` is forwarded only once the model is loaded. S001 L1847–2115. HEAD hits for `router`: 0. **New.**
5. **Sleep mode exempts `/health`/`/props`/`/models`/`/metrics`**, so a 200 does not wake the model or name it. S001 L2335–2339. **New.**
6. **Documented alias ambiguity**: `--alias` is comma-separated and the docs don't say which alias becomes `id` (S001 L190). Ollama `ollama cp`/`ollama create` produce extra names (S010). **New at the documentation level.** The local full-path alias observation is prior (see table).
7. **A tags↔ps digest join is inference, not a documented mapping.** S011/S012. Digest *presence* is prior (`SOURCES.md:23-24`); the *join limit* is new.
8. (Marginal) OpenAI `shutdown_date`/`owned_by` are catalog lifecycle fields and must not be read as residency. S016. The general non-readiness point is prior (`SOURCES.md:28`).

Not new: the tags/ps split, OpenAI non-readiness in general, `/health`≠identity, the `-m`/`--alias` default, and the claim that kama normalization is kama-owned.

## Defects and smallest repairs

| # | Sev | Path:line | Defect | Smallest repair |
|---|---|---|---|---|
| P1 | low (KQ12) | `served-identity-crosswalk.md:13` | The prior-coverage paragraph credits only `matrix:17`. It lists `expires_at` and "alias/name and digest-join limits" as new without crediting `SOURCES.md:23,24,28` (digest/expiry/non-readiness field notes) or the alias observations at `listener-census.md:86-90`, `endpoint-identity.md:21,63,127`, `consumer-registry.md:155`. KQ12 requires claims to "identify ... prior overlapping coverage" (`QUALITY.md` KQ12). | Add one sentence: "Field presence of `digest`/`expires_at` and OpenAI non-readiness were pre-registered at `SOURCES.md:23,24,28`; the local full-path alias mismatch and kama normalization are prior at `listener-census.md:86-90` and `endpoint-identity.md:21,127`. New here is the expiry consequence, the doc-level alias ambiguity, and the join limit." |
| P2 | medium (counting) | `runtime-health-surface-matrix.md:41-57` (appended); `endpoint-identity.md` appended "Readiness terminology correction"; `served-identity-crosswalk.md:9,45` | The same round-11 distinctions appear in three files: remote tags, nullable `meta`, router status, the `/health` sleep exemption, and "matching id ≠ readiness". This is not prior coverage. For C2 it is **one** new entry plus two corrections, not three coverage gains. The matrix correction does not cite the crosswalk, so there are two co-equal statements and the risk of duplicate authorities. | Count the C2 delta once, at the crosswalk. Optionally append to the matrix and endpoint-identity corrections: "Authority: `served-identity-crosswalk.md`." Do not change the scores. |
| P3 | low | `SOURCES.md:43` vs `:23` | S031 is the same URL and OpenAPI operation as S011, and both stay `mined`. The crosswalk cites both for one page (`crosswalk:1,22,77`). This is a second S-id for one document; supersession is the only thing that distinguishes them. | This is a tradeoff, not a correctness bug: keep it if registry supersession is the accepted convention. Otherwise mark S011 as superseded in its own row. |
| P4 | info | `served-identity-crosswalk.md:20` | The llama.cpp single-model field list leaves out the `aliases` array and `models[]` wrapper that the corpus has already observed (`consumer-registry.md:155`, `endpoint-identity.md:63`). The pinned README example (L1288–1310) does not document them either, so "documented" is accurate. Readers may still conflate the two. | Optional: "observed historically, not in the pinned docs: `aliases[]`, `models[]` (`consumer-registry.md:155`)." |

## Already correct

- The matrix's original bytes are preserved exactly. The change is append-only. Line anchors 8, 14, and 17 are stable.
- `crosswalk:13` explicitly says it claims none of the tags/ps split, which satisfies the target's rejection condition.
- All eight quotes above were re-opened on 2026-10-20 and match the crosswalk text. The `[INFERENCE]` labels on load completion (`:20,26`) and the digest join (`:38`) fit KQ13.
- `crosswalk:46` is right that HEAD's `served-model-identity.md` holds only the `/health`/`/props`/`/slots`/`/metrics` readiness probes and no alias reconciliation.
- The crosswalk opens with the provenance trio (`:1-3`), as KQ11 requires for new entries. It is the only knowledge file with a trio before its H1, but that order is what KQ11 asks for.
- It makes no runtime-freshness claim (`:2,46`). No service was contacted.

## Score impact

C2: roughly 7 new sourced distinctions (items 1–7), plus 1 marginal one, sit in **one** new entry. Neither file defines an objective coverage denominator: `MISSION.md`/SCORECARD were not consulted for one, and the goal says scores stay unchanged without one. **Recommendation: leave the scores unchanged** and record the delta qualitatively. P1 and P2 are wording and counting fixes; neither blocks admission.

Axes affected: coverage (P1, P2 counting) and calibration (no overclaim found). Operability is not affected.
