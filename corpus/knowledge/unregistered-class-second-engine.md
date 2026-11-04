source: S554 — Ollama docs/api.md at v0.40.11, §List Local Models `GET /api/tags` (the page's own definition, line 1358: "List models that are available locally"); the inventory limit is read against S555 — llama.cpp server README @ 39febd2a, `### GET /models: List available models`, note 1 line 2227; the class itself is read from `tools/kama-probe.sh` `classify_registration`; lane policy: `plans/round-80-claims.md` §C3.
verified-at: 2026-11-04 — both URLs opened this round (S554 HTTP 200, 54614 bytes, sha256 `96db03080e385dbabf5d70e75f298d41b75983bc30975cae56f7119f848dd0f5`; S555 HTTP 200, 135608 bytes, sha256 `8fd5abde2fb52de3b30f30a170631d4c0d92febecc8da44d0541e48b132b35c6`), and the Ollama tag resolves as `v0.40.11` → `675150d6ad2747df1e218ef59de9194bc4a7e538`. No census run is asserted here; the second-engine exercise is the round's C3 claim on its own receipt.
recheck: `python3 tools/round80-ollama-census.py --repo .` must print `OLLAMA_CENSUS port=<p> engine=ollama unregistered=1 governed=1 class_missing=0` and exit 0, and its `--audit` must print `CLASS_ENGINES engines=2 verified=2 stale=0`; at the next Ollama release, re-open docs/api.md at the new tag before reusing this entry.

# A model list is a class input on every engine, not a loaded-model claim

The `registered` census class (`unregistered-listener-census.md`) asks one question per
loopback listener: does a registry row declare this port? Round 79 answered it on llama.cpp
only. The open question is whether the class is about engines at all.

## What `/api/tags` is

Ollama's native model list. The v0.40.11 page defines it in one line — "List models that are
available locally" — and the response carries `name`, `model`, `modified_at`, `size`,
`digest` and `details` (`format`, `family`, `parameter_size`, `quantization_level`). It is an
inventory of what the local store holds: not `/api/ps` (S012), which lists the models
currently loaded into memory, and not the OpenAI-compatible `/v1/models` route (S010).

## What the probe reads

Every listener the probe classifies is fetched at `/v1/models` (the `classify` fetch in
`tools/kama-probe.sh`), and `MODEL_OK` requires a model array in the body — a status code or
a `Server: llama.cpp` header alone is not proof (the v3 rule in the same file). On Ollama
that is the OpenAI-compatible surface, not `/api/tags`; the tags route is the native twin of
the same inventory question, which is why documenting it grounds the class without changing
what the probe does.

## Why the class is engine-agnostic

`classify_registration` takes two inputs: the verdict class (`MODEL_OK`, `MODEL_MISMATCH`,
`MODEL_LOADING`, `UNAUTHORIZED_SERVICE`) and the ports parsed out of each registry row's
`declared_baseurl` through `url_port`. It never reads `served_model`, the `Server` header, a
version string or an engine name. A second engine is therefore not a second class: it is a
second receipt showing the same column move with the registry, which is all the round-80 C3
audit asks the engine register to carry.

## The limit

An inventory is neither a loaded-model claim nor a readiness claim. A listener that answers a
model list is evidence that something serves a model API at that port — the class's whole
input — and says nothing about which model is resident, whether a load is in progress, or
whether any declared consumer can use it. `/api/tags` inherits exactly that limit: it lists
what the store has, loaded or not.

## Round-80 addendum — the route the probe reads is documented at the pinned tag

`corpus/SOURCES.md` S557 adds the other half: at v0.40.11 the OpenAI-compatible surface is documented
too (`docs/api/openai-compatibility.mdx`, `### /v1/models` line 290), so the probe's `/v1/models` fetch
is not an undocumented side door. The response notes put `created` at the model's last modification and
`owned_by` at the Ollama username defaulting to `"library"` — inventory fields, no residency field. The
limit above is therefore the same on both routes: a models list is an inventory, and residency lives on
`/api/ps` (`GET /v1/models` never claims a model is loaded).

Provenance boundary: S010 already holds the docs-site page `docs.ollama.com/api/openai-compatibility`
(2026-09-23) for the same surface, so S557 is not a discovery — it pins the same route to the release's
own bytes (`v0.40.11`, `docs/api/openai-compatibility.mdx`, sha256 `44071a12…`) with line anchors, which is
what a recheck needs when the docs site moves ahead of the tag.
