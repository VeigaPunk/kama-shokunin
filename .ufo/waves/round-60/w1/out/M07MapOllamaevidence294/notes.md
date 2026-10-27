# M07 — base line 294 mapping notes

Base population line: `corpus/knowledge/ollama-evidence-replay.md:294` (frozen base
`ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`):

    294:  S012/S031; every classification rule is labeled **[INFERENCE]** lane policy.

It is the second physical line of KQ6 (`## QUALITY clearance`), whose full sentence reads
"the two upstream statements are field semantics from opened tier-A rows / S012/S031; every
classification rule is labeled **[INFERENCE]** lane policy." The two upstream statements are
described in `## What the two documented pages actually provide`: `/api/tags` (S031,
`ModelSummary`) documents `name`, `model`, `digest`, `remote_model`, `remote_host`; `/api/ps`
(S012, `Ps`) documents `name`, `model`, `digest` and (as fields the replay may not use)
`expires_at`, `size`, `size_vram`, `context_length`, `details`. The line therefore carries
three separable mappings: the S012 field-semantics citation, the S031 field-semantics
citation, and the lane-labelling policy sentence.

## OL07A — quote "S012/S031; every classification rule is labeled" — confirmed

- Documented statement: the `/api/ps` field semantics the entry credits to tier-A row S012 —
  the running-model objects expose identity (`name`, `model`, `digest`) plus context length,
  VRAM use and expiry — are what the live `/api/ps` response actually publishes.
- Predicate (restricted Python over parsed capture bodies): `ps-after` has at least one model
  and every `ps-after` model object carries the keys `name`, `model`, `digest`,
  `context_length`, `size_vram`, `expires_at`.
- Observed (committed receipt, nonce b61c98ad5747, verdict MODEL_OK): `ps-after` =
  `{"models":[{name: kama-b61c98ad5747:latest, model: kama-b61c98ad5747:latest, digest:
  8cf91c71…c792, context_length: 2048, size_vram: 0, expires_at:
  2026-10-27T18:34:10.425205706-03:00, size: 6312427, details: {...}, runner: llamacpp}]}`;
  key set `context_length, details, digest, expires_at, model, name, runner, size, size_vram`.
- Limit: this confirms field *exposure* on one v0.40.11 capture of one fixture model. It does
  not confirm that S012's OpenAPI text says so, that `expires_at` is ever evaluated, or that
  the replay is permitted to use the ignored fields; the entry's own table says those are not
  used, and the predicate only asserts presence.

## OL07B — quote "S012/S031; every classification rule is labeled **[INFERENCE]** lane policy" — confirmed

- Documented statement: the `/api/tags` summary field semantics the entry credits to tier-A
  row S031 — each `models` entry is a model summary carrying identity (`name`, `model`) and a
  content `digest` — are what the live `/api/tags` response actually publishes.
- Predicate: `tags` has at least one model and every `tags` model object carries `name`,
  `model`, `digest`.
- Observed: `tags` = `{"models":[{name: kama-b61c98ad5747:latest, model:
  kama-b61c98ad5747:latest, modified_at: 2026-10-27T18:29:10.137112591-03:00, size: 1185492,
  digest: 8cf91c71…c792, details: {...}, capabilities: ["completion"]}]}`; key set
  `capabilities, details, digest, model, modified_at, name, size`.
- Limit: `remote_model`/`remote_host` are optional ModelSummary fields for remote entries and
  are correctly absent for a locally created model, so this row asserts nothing about them
  (that is OL06's line, not this one). Single-version, single-model evidence.

## OL07C — quote "every classification rule is labeled **[INFERENCE]** lane policy" — not-observable

- Documented statement: every classification rule of the lane's own replay classifier is
  labelled `[INFERENCE]` lane policy in the document rather than presented as upstream
  behaviour.
- Why no capture decides it: the statement is about how the lane labels its own rules. The
  receipt carries only HTTP status/body captures (`version`, `tags-empty`, `tags`,
  `v1-models*`, `show`, `ps-before`, `generate`, `ps-after`) plus run bookkeeping; none
  records the classifier's rule set, its rationale, or its document labels. Even a perfect
  capture cannot show a markdown label. Empty predicate, as the counter requires.

## Amendment

No contradicted row in this seat, so no amendment paragraph is proposed. Both live predicates
hold on the committed receipt and on the second look (own lane-owned child, nonce 9f0726f01d0f,
port 44075, verdict MODEL_OK, exit 0: identical ps and tags key sets, `evaluate=True
falsifiable=True` for both). If a later capture dropped `size_vram`/`context_length`/`expires_at`
from ps or `digest` from tags, OL07A/OL07B would flip to contradicted and the amendment should
append (not rewrite) the observed key set with the version and nonce.

## Advisory (outside this seat's write scope)

`corpus/SOURCES.md` already carries S012 (line 24, `/api/ps`) and S031 (line 43, `/api/tags`),
so the citation on line 294 resolves; the round's frontier step's next free id is S519.
