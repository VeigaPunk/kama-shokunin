# ScoutProvince — round-31 surface check

## Current PROVINCE coverage

- `PROVINCE.md:6-15` lists producer discovery, consumer baseURL pins, served-model-id reconciliation, liveness/readiness, endpoint drift/history, and the endpoint-consumer registry. These govern adjacent endpoint identity/health facts, but none lists `/v1/chat/completions` request-adapter behavior or parameter/payload outcomes as a surface.
- The exact prior boundary is `PROVINCE.md:109-115`:

  > **Round-28 core note — request-field schema.** llama-server's per-request field schema (`tools/server/server-schema.cpp` @704366d76: hard-bound rejects, silent clamps, handler transforms, as stored in `generation_settings`) enters held ground for the lane-owned b11755 fixture via SKILL.md "## Round-28 request-field outcomes" (S140-S173). It describes what the server accepts and stores for one request, not sampling quality, model identity or registered endpoint health. Other endpoints, builds and engines remain frontier.

  That note is specifically the native `POST /completion` schema, not the chat-completions adapter. The frozen round-31 preregistration makes the distinction explicit: C1 says the lane “has never held the chat-adapter surface” and round 28 “covers only native POST /completion fields” (`.ufo/waves/round-31/preregistration.json:12`).
- `PROVINCE.md:40-43` keeps adjacent domains out: “model quality/eval (kengaku), credential material & auth flows (kagi), dispatch/route mechanism (kumitate), remote web surfaces (kake)” and defines kama's question as whether a baseURL reaches the expected model, “never ‘is the model good’ or ‘is the request safe’.” Server-side request adaptation is distinct from those exclusions; the entry below must not claim consumer request safety.

## Draft row to append

Append this line to the `**Owns (surfaces):**` table after its current final row (`PROVINCE.md:15`):

```markdown
| llama-server `/v1/chat/completions` request-adapter outcomes on the lane-owned b11755 fixture | `SKILL.md` “## Round-31 chat-completions parameter outcomes”, `registry/chat-param-outcomes-r31.json` and `corpus/SOURCES.md` S### rows: one measured outcome per selected request parameter or chat-payload shape (adapter rejection, generation-setting mapping, accepted no-effect, or response-contract behavior), for the pinned build/model/argv only; not universal OpenAI compatibility, other builds/engines, sampling quality, endpoint identity/health, or server-install ownership |
```

This scopes the new holding to the specific fixture and measured inputs; it does not imply complete API conformance or generalize one observation to every value of a parameter.

## Sibling-lane check

- The 20 sibling `PROVINCE.md` files were searched for `chat-completions`, `chat/completions`, `OpenAI`, `llama-server`, `adapter`, and `API`. The only explicit `/v1/chat/completions` mention is `kengaku-shokunin/PROVINCE.md:14`, in its served-local-model endpoint inventory. Kengaku's `PROVINCE.md:24-25` explicitly says the model-serving plane (llama-server flags, slot/batch config) is “Not owned” by Kengaku and says no lane owns it; that is an endpoint reference, not a claim to adapter semantics.
- `corpus/knowledge/cross-lane-scope.md:15` classifies Kengaku's direct `chat/completions` calls as a one-off runtime consumer: Kama owns endpoint identity/availability, while Kengaku owns task set, generation, grading, and evaluation claims. It does not assign Kengaku ownership of server-side parameter handling.
- Kagi's `PROVINCE.md:3-4,41-43` is the secrets/vault and consumer endpoint-credential domain; it mentions the configured model endpoint but not the chat adapter. The cross-lane rule at `cross-lane-scope.md:3` likewise preserves consumer credentials, evaluation, routing, and instruction ownership separately from Kama's local endpoint identity/health.

## Evidence and limits

- Read-only reads/searches only; no lane or sibling file was edited. The only output produced is this report.
- No shell command or live server/probe was run; the request concerns documentation coverage and ownership, not current endpoint health. The report does not assert that the fixture's server is currently running or that any sibling was tested against it.
