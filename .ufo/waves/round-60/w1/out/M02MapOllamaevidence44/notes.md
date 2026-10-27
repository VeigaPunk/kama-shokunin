# M02 — base population line corpus/knowledge/ollama-evidence-replay.md:44

Base blob: `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b:corpus/knowledge/ollama-evidence-replay.md`
Line 44 text (verbatim): `**[INFERENCE]** for real-world exports, not a documented ps field. The tags`

Surrounding statement (lines 42-46): "The `/api/ps` OpenAPI schema declares no `remote_model` or
`remote_host` field. Accepting a ps entry that carries those fields as a remote marker is lane policy
**[INFERENCE]** for real-world exports, not a documented ps field. The tags remote fields are
documented; the conclusion that a remote tags entry cannot be counted as locally loaded is also
**[INFERENCE]** ...". Two policy clauses land on line 44: the ps remote-marker acceptance label, and
the opening of the tags clause.

Evidence base: committed receipt `.ufo/waves/round-60/live/receipt.json` plus one independent fresh
run of `tools/kama-ollama-live.py --work <scratch>/run --out <scratch>/r.json --nonce ol02fresh1`
(verdict MODEL_OK, exit 0, 16 checks, none failed; copy kept at `fresh-receipt.json`). Both receipts
agree on every value used below.

## Row OL02A — confirmed (evaluated, falsifiable)

- Documented statement (my words): a live Ollama ps entry carries the fields the page documents for
  `/api/ps` and carries no `remote_model`/`remote_host`, so treating such a field as a ps remote
  marker has nothing to attach to on this surface. Scope limit: this is the live v0.40.11 entry, not
  the OpenAPI document itself; the harness captures no schema document.
- Observed: `ps-after.models[0]` keys = `context_length, details, digest, expires_at, model, name,
  runner, size, size_vram`; `remote_model` and `remote_host` absent. `ps-before` = `{"models": []}`.
  `tags.models[0]` keys = `capabilities, details, digest, model, modified_at, name, size`; no remote
  fields. Fresh run: same ps key set, same absence.
- Predicate (true on the committed captures, true on the fresh receipt):
  `len(c["ps-after"]["models"]) == 1 and sorted(c["ps-after"]["models"][0]) == ["context_length",
  "details", "digest", "expires_at", "model", "name", "runner", "size", "size_vram"]`
- Can it fail: yes. With `remote_model` added to the ps entry the predicate is False; with an empty
  ps models list it is False; the counter's `falsifiable()` returns True (sentinel mutation of
  `c["ps-after"]["models"]` flips it through `len`).

## Row OL02B — not-observable (no predicate)

- Documented statement (my words): whether the lane's classifier may accept a ps entry's
  remote marker, and whether a remote tags entry may be counted as locally loaded, are lane policy
  and a documentation claim, not Ollama behaviour recorded in these captures.
- Observed: both captures hold only the locally imported fixture entry; no ps entry and no tags entry
  in any of the 11 captures carries `remote_model` or `remote_host`, so the remote path is never
  exercised.
- Why not observable: the live server was started with `OLLAMA_NO_CLOUD=1` against a local model
  store and a local GGUF, so no capture can produce a remote entry; and the policy/provenance status
  of a hypothetical field is a statement about the lane's classifier and the upstream document, which
  no HTTP body can decide. No captured surface tests it — hence empty predicate, not a tautology.

## Amendments

None. Both rows are `confirmed` / `not-observable`, so no contradiction exists for this line and
nothing is proposed for `corpus/knowledge/ollama-live-amendment-r60.md`.

## Boundary notes (advisory, outside this line)

- The live `ps-after` entry carries `runner` (`llamacpp`), which is not in the documented `/api/ps`
  field list quoted on line 40 (`size`, `size_vram`, `context_length`, `details`, `expires_at`,
  `name`, `model`, `digest`). That bears on the line-40/42 table row, not on line 44, and it does not
  contradict line 44: line 44 only denies that `remote_model`/`remote_host` are documented ps fields.
- Line 42's clause "The `/api/ps` OpenAPI schema declares no ..." is not tested by these captures at
  all: `kama-ollama-live.py` captures `/`, `/api/version`, `/api/tags`, `/api/ps`, `/v1/models`,
  `/v1/models/<id>`, `/api/show`, `/api/generate` — no `/openapi.json`, `/docs` or `/api/openapi`.
  Whoever owns line 42 should not claim a capture-based confirmation.

## Validation actually run

`python3` importlib of `tools/round60-c2-counter.py`:
`caps,ok=m.receipt_caps(<committed receipt>)` -> ok=True; `parse_registry(rows.tsv)` -> 2 rows, 0
bad, 8 columns each; each quote is a substring of the base line and 3-25 words; `safe_compile` ->
`evaluate`=True and `falsifiable`=True for OL02A; `score(pop=<14-line population>, rows, receipt,
amend='')` -> `covered=1 evaluated=1 sensitive=1 bound=1 errors=0 good_rows=2 receipt_ok=True`
(the registry alone cannot reach met=True because the other 13 population lines belong to sibling
seats).
