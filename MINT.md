# MINT.md — kama-shokunin

**Minted by:** L0 integrator session (operator directive, `2026-09-28`), on aggregator evidence.
**Domain claimed:** local model serving & endpoint health — local LLM endpoints
(`llama-server`, janitor-pinned `opencode` overlays, OMP model routing that resolves to local
`baseURL`s), endpoint drift, liveness/readiness probes, model-id vs served-model reconciliation.

## Reasoning and cause

Two *independent* lane lanes discovered the same unplaceable defect class, on different
surfaces, in different rounds:

1. **kagi round 3** (`.ufo/reports/round-3/kagi.md`): a live probe found the janitor-pinned
   `baseURL` pointing at port 8080, which had silently become a *Jitsi* service while the actual
   local model server had moved to 34113 — credential-bearing requests were aimed at a chat
   server. Secrets/vault ops owns the *request hygiene* around that endpoint, but not the
   endpoint itself.
2. **kengaku round 4** (`.ufo/reports/round-4/kengaku.md` + aggregator r4 routing table): the
   model-evaluation lane's bench batteries probe the same endpoint family; it recorded drift
   (`8080(Jitsi)→34113(llama-server)`), consumers spanning kagi / kengaku / kotoba
   (`agents/janitor.md` mentions 8080) / kumitate (OMP routing) — the routing table row is
   "model serving — **no province owns it**".

The `~/wikillm/llm-wiki` path kengaku's SKILL.md cited (`SKILL.md:8-12`) was also found absent —
the real wiki lives at `~/Projects/webzites/repos/llm-wiki`; the repo had never been
`migrate`d. Same defect class: an assumed path/endpoint drifted and no lane's contract made
catching it their job.

## Roster scan (rejected fits)

`MANIFEST.json` roster at mint time, and why none absorb this:

| Lane | Province | Why the demand doesn't fit |
|---|---|---|
| kasegi | bounty/security research (`~/Projects/bounties`) | target-scope; no local-serving infra |
| kengaku | LLM eval/research (`llm-wiki`, bench-arena, telemetry) | *consumes* endpoints for batteries; doesn't own their health — its own probes detected drift as a side-effect |
| kake | web properties & publishing | remote surfaces (ds4cc, kimi mirrors, GH Pages), not local model processes |
| kumitate | orchestration & tooling (ufo-fsd runtime, dispatch) | owns *how* routes are resolved, not *what a resolved endpoint serves* |
| kotoba | prompt & skill craft | instruction surfaces, not services |
| kagi | secrets & vault ops | owns credential hygiene *to* endpoints, not endpoint identity/liveness |
| aggregator | cross-lane quality | meta-lane; owns no domain surface |
| protocol | main-repo protocol | meta-lane; owns no domain surface |

Aggregator rulings: **round 4** — "kama meets the written mint bar (two documented demand
instances; no province owns the surface)"; **round 6** — "remains mint-eligible … and remains
unruled"; **round 7** — standing mint table row, dated 2026-09-28. `ROADMAP.md` line 80
carries the same call pending integrator decision.

## Domain boundary (claimed)

**Owns:** local model-serving surfaces — `llama-server`/equivalent processes, their ports,
`baseURL` values referenced by consumer configs, model-id vs `GET /v1/models` served-model
reconciliation, liveness/readiness probe conventions, endpoint-drift detection, the
"endpoint consumers" cross-lane registry (which lane config points at which port).

**Refuses:** model *quality*/eval (kengaku), credential material & auth flows (kagi),
dispatch/route *mechanism* (kumitate), remote web surfaces (kake). Boundary rule: kama
answers "is the thing at this baseURL the model this config believes it is, right now" —
never "is the model good" or "is the request safe".

## Probation

Per PROTOCOL.md §Lifecycle "Sibling mint": this lane self-iterates ≥3 verified rounds building
`corpus/` + `PROVINCE.md` before the operator adds a `MANIFEST.json` roster row.
