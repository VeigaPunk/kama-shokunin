# ConnectorSiblings — sibling-overlap scan for kama C1 (round 28)

Scope: read-only scan of sibling lane repos `/home/vgpnk/Projects/shokunin/*-shokunin` (excluding `kama-shokunin`) for knowledge about llama-server/llama.cpp request parameters, sampling-field limits, generation_settings, or server-schema.cpp. No tracked lane files edited; no git writes.

## Exact commands run

Primary (per sibling, bounded output):

```
git -C /home/vgpnk/Projects/shokunin/<lane>-shokunin grep -n -i -E "server-schema|generation_settings|set_hard_limits|n_probs|repeat_last_n|llama-server"
```

Follow-up filters (to separate genuine sibling knowledge from sandbox copies of kama and OMP evidence):

```
# generation_settings hits, excluding scratch/sandboxes copies
git -C <repo> grep -n -i "generation_settings" | grep -v "/scratch/" | grep -v "/sandboxes/"

# server-schema hits, excluding scratch/sandboxes copies
git -C <repo> grep -n -i "server-schema" | grep -v "/scratch/" | grep -v "/sandboxes/"

# set_hard_limits / n_probs hits, excluding scratch/sandboxes copies
git -C <repo> grep -n -i "set_hard_limits"
git -C <repo> grep -n -i "n_probs" | grep -v "/scratch/" | grep -v "/sandboxes/"
```

## Axis touched
Adjacency (contested scope). C1 surface is kama's province (local model serving); no sibling claims request-field schema.

## Per-lane verdict

| Lane | Hit type | Province | Contradict / duplicate? |
|---|---|---|---|
| audio | none | n/a | no |
| chousa | none | n/a | no |
| game-dev-2d | none | n/a | no |
| game-dev-3d | none | n/a | no |
| kagi | `llama-server` only in endpoint-identity/operational context (PROVINCE.md, SKILL.md, handler-trust-boundary.md, op-cli-surface.md, lessons) | kagi = secrets/vault + consumer endpoint config; explicitly defers serving plane to kama | no — operational, not request-field schema |
| kaidoku | `llama-server` only in EXAMPLE.kama.md (reference copy of kama MINT, describes kama province) | kaidoku = bounty/security research; documents kama as owner | no — descriptive, not a competing table |
| kasegi | none | n/a | no |
| kengaku | `llama-server` operational (process pin, slots.json, props.json default_generation_settings); PROVINCE.md explicitly "Not owned: the model-serving plane" | kengaku = LLM eval/research; consumes endpoints, defers serving plane | no contradiction; kengaku's `corpus/evidence/round10-fleet/props.json` and `slots.json` hold a *default* generation_settings snapshot (fleet evidence), not a reject/effective outcome table. Kama's new table does not duplicate it (different surface: out-of-range/transformed values vs. defaults) |
| kotoba | `server-schema` / `generation_settings` hits are OMP provider schemas (`openai-chat-server-schema`, `anthropic-messages-server-schema`) and `default_generation_settings` inside an OMP binary strings dump (`.ufo/round-44/evidence/omp-live-18.12.2-strings.txt`) | kotoba = prompt/skill craft; these are OMP client-side schemas, unrelated to llama.cpp server-schema.cpp | no — different schema, different owner |
| kotodama | none | n/a | no |
| kumitate | none (outside scratch) | kumitate = orchestration/route resolution mechanism; defers "what a resolved endpoint serves" to kama | no |
| lore | none | n/a | no |
| mado | `llama-server` only in tooling/audit reports (pgrep verification) | mado = tooling audits | no |
| mori | `llama-server` only in SiblingBoundary (routing model-server failures to kama) | mori = fleet unit failure triage | no — explicitly routes to kama |
| revenger | none | n/a | no |
| souji | none | n/a | no |
| tabi | none | n/a | no |
| tameshi | `llama-server` only in Overlap2 (tameshi runs on non-registered port) | tameshi = test/verification | no |
| tsukuroi | `llama-server` only in province/adjacency captures (describes kama) | tsukuroi = host/package/boot plane | no |

## Contested scope
None. No sibling lane holds a decision table of llama-server request-field outcomes, sampling-field limits, or server-schema.cpp declaring lines. The only sibling touching generation_settings content is kengaku, as fleet evidence (default params snapshot) under its explicitly "not owned / reported out" model-serving plane; kama's new table neither contradicts nor duplicates it. Kotoba's server-schema references are OMP provider schemas, a different substrate.

## Absorption decision
Report contested scope only; do not absorb. Kama proceeds with C1 on its own province. No sibling handoff required.

## Notes on excluded noise
Sandbox copies of kama under `.ufo/waves/round-28/scratch/*` in kengaku/kotoba/etc. are clones of kama and were excluded as non-sibling knowledge. OMP binary strings in kotoba round-44 evidence are unrelated to llama.cpp.
