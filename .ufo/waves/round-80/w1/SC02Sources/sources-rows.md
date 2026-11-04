# SC02 — round-80 SOURCES rows (S554, S555, S556)

Filing: append the three data rows below to `corpus/SOURCES.md` §Registry after S553. The
header row is reproduced only to show the 11-column contract-v1 shape; it is not re-filed.
No cell contains a `|`. `opened` is the access date of this round's own fetch (2026-11-04);
every URL, byte count and sha256 is the curl receipt in `curl.txt` beside this file.

| id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by |
|---|---|---|---|---|---|---|---|---|---|---|
| S554 | Ollama API docs/api.md at v0.40.11 — https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md | docs | A | Ollama v0.40.11 native `GET /api/tags`: the model list is an inventory of models available locally; not the OpenAI-compatible `/v1/models` route (S010) and not loaded-model or readiness state (S012) | §List Local Models (heading line 1352), `GET /api/tags` line 1355, definition line 1358 `List models that are available locally`; raw file sha256 `96db03080e385dbabf5d70e75f298d41b75983bc30975cae56f7119f848dd0f5`, 54614 bytes (2026-11-04) | A tags answer is an inventory of locally available models carrying `name`, `digest`, `size`, `modified_at` and `details` format and quantization; the list proves a model API answers, not that any model is loaded, so it is exactly the second engine's class input and no more | mined | 2026-11-04 | on-release | corpus/knowledge/unregistered-class-second-engine.md |
| S555 | llama.cpp server README @ 39febd2a, model-list anchor re-derived — https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/tools/server/README.md | docs | A | the router's model list is an inventory: unloaded models are listed and each carries a status.value; docs of the list's semantics at 39febd2a, not S479's router listing code at an older pin and not S037's router-mode is_ready ordering | §GET /models: List available models (heading line 2197; the literal heading puts /models in backticks), note 1 line 2225, unloaded-model bullet line 2227; raw file sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6`, 135608 bytes (2026-11-04) | supersedes S553 — anchor correction only: the heading is `### GET /models: List available models` at line 2197 and note 1's second bullet at line 2227 states that a model not running is still added or updated; no heading in the file carries S553's region label `Router mode`. The rest of S553 stands: a model that is not running is still listed, so a model list is not proof of a loaded model or of consumer readiness | mined | 2026-11-04 | on-release | corpus/knowledge/unregistered-listener-census.md, corpus/knowledge/unregistered-class-second-engine.md |
| S556 | llama.cpp docs/preset.md @ 39febd2a — https://raw.githubusercontent.com/ggml-org/llama.cpp/39febd2adb947b70da35e95f9351b3bf58ad170a/docs/preset.md | docs | A | llama.cpp INI presets: per-model parameter files, Hugging Face presets, named presets and system-level config precedence; no claim in round 80 parses a preset file | §Using Presets with the Server and §System-level config (config file applied first, then overridden by ENV variables, CLI arguments and model presets in router mode); raw file sha256 `3e6643541e12ff3dfee2a23c23a57357403bf4500beced780f010eaebbbdfe13`, 4090 bytes (2026-11-04) | REJECTED: the round's `registered` census class reads a model list only and the probe parses no preset file, so a row would scope a configuration format no claim reads (ground, not tier, is the question); flip: a round that grades preset-inherited parameters on a lane-owned fixture | rejected | 2026-11-04 | on-release | — |

## Gate-block handoff for C3's sourced claim

`plans/round-80-claims.md` §C3 requires the round-80 lesson's Gate block to carry the URL,
access date and a located ≤25-word quote for S554. Hand this block to whoever writes
`corpus/lessons/round-80.md`:

- URL: `https://raw.githubusercontent.com/ollama/ollama/v0.40.11/docs/api.md` — opened
  2026-11-04, HTTP 200, 54614 bytes, sha256
  `96db03080e385dbabf5d70e75f298d41b75983bc30975cae56f7119f848dd0f5`.
- Located quote (7 words), under `## List Local Models` (line 1352), immediately after the
  `GET /api/tags` fence at line 1355: "List models that are available locally." (line 1358).
- The same sentence names the limit the C3 claim needs: an inventory of what is available
  locally is not proof any model is loaded, so a second engine's model list is exactly the
  census class's input and no more.
- Tag identity: `refs/tags/v0.40.11` resolves to
  `675150d6ad2747df1e218ef59de9194bc4a7e538` (`git ls-remote --tags`, this round).

## Why S555 supersedes S553 rather than editing it

Round-79's routed defect R79V6: S553's anchor named `§Router mode`, a region label that no
heading in the file carries. This round re-opened the same bytes (identical sha256
`8fd5abde…`, so the file did not change between the two reads) and located the heading that
actually holds note 1: `### GET /models: List available models` at line 2197, note 1 at
line 2225, its unloaded-model bullet at line 2227. The supersession is lane-registry scope
only — S553's text, scope and consequence stand; only the anchor's locator changes, and
S553 is not edited.
