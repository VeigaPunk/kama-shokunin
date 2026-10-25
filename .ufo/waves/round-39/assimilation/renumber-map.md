# round-39 attempt-2 renumber map (by document)

Base: `d7954be870a785054287ef5d7b3690e6cca0478e` (lane origin/master).
Attempt-1 commits `eaa4106c`, `8e953f68` were made on stale base `6a4afdfe` and never reached the lane remote.

| staged id (attempt 1) | landed id (attempt 2) | document | URL / anchor |
|---|---|---|---|
| S472 | S473 | OpenAI List models — `created` field | https://developers.openai.com/api/reference/resources/models/methods/list/index.md — §List models → Returns → `created`, line 17 |

Reason: at the replay base the lane registry already holds `S472` for round 38's own-work SGLang release-tag inventory row (`corpus/SOURCES.md:225`). `S473` is the next unused id (`grep -c '^S473$' reg-ids-replay` = 0). The id follows the document; the URL, anchor and quote are unchanged.

Re-pointed live citations (all `S472` → `S473` for this source):

- `corpus/SOURCES.md` — registry row and the `## Paths` "Served-card field semantics" bullet
- `corpus/README.md` — round-39 coverage-map row and frontier disposition
- `corpus/knowledge/served-identity-crosswalk-amendment-2026-10-24-r16.md` — `source:` line
- `corpus/lessons/round-39.md` — Gate, id-collision, consideration, frontier, mistakes
- `SCORECARD.md` — round-39 claim rows and closure qualification
- `LOG.md` — round-39 entry

Kept byte-exact (attempt-1 receipts, superseded not edited): `S472.md`, `SOURCES-addition.md`, `claim-after.out`, `claim-after-initial.out`, `preregistration.json`, `preregistration-frozen.json`, `validate-partial.out`, `validate-partial/corpus/SOURCES.md`, `w1/**`.

Retained id: round 38's `S472` (SGLang release-tag inventory) is untouched.
