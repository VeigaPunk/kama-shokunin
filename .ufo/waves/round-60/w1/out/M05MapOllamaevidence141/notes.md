# OL05 — mapping of base line 141 to the round-60 live Ollama receipt

Base population coordinate: `corpus/knowledge/ollama-evidence-replay.md:141` at
`ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`.

Base line (exact): `### Matching and policy — all **[INFERENCE]** lane rules`

The line is a section heading, so the statements it carries are those of the eight numbered
rules it introduces (base lines 143-176). No S0xx SOURCES row is cited anywhere in the section
(lines 130-200 of the base blob contain no `Sddd` token); the section's authority is the lane's
own classifier reasoning, which is why every rule is labelled `[INFERENCE]`.

Evidence used: the committed receipt `.ufo/waves/round-60/live/receipt.json`
(schema `kama-ollama-live/v1`, binary sha256 `b0a4becf...1b4c`, `verdict` `MODEL_OK`,
capture hashes re-verified by `m.receipt_caps` -> `ok=True`). No fresh run was needed: every
statement mapped below is decided by a committed capture body, so a second live instance would
add no discriminating surface. No lane-owned server was started and no scratch run was kept.

## OL05a — statement: rule 1 (exact identity on the server's own name/model strings)

Documented statement, in my words: selection compares `--expect` to the tags entry's `name` or
`model` as exact strings, with no trimming, basename, `.gguf` stripping, `:latest` completion,
case folding or digest normalization; identity is therefore whatever string the server puts in
those two fields.

Observed: `/api/tags` holds exactly one entry whose `name` and `model` are both the identical
server-assigned string `kama-b61c98ad5747:latest`, with a 64-hex digest
`8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792`. The model was created from
the bare nonce name `kama-b61c98ad5747`; the server appended `:latest` itself.

Verdict: confirmed. The matching surface is two plain equal strings plus a present digest, so the
no-normalization stance is applied to a real surface rather than a guessed one.

Calibration caveat (not a contradiction, no amendment requested): the same model is reported as
`kama-b61c98ad5747:latest` on `/api/tags` and `/v1/models` but as bare `kama-b61c98ad5747` on
`/v1/models/{model}` (receipt observation `v1_single_id_equals_list_id=false`). Rule 1 forbids
reconciling those forms, so an `--expect` written from the single-model id can never select the
tags entry. The rule is correct as written and expensive in practice; the lane may want a note,
but it is not evidence that the rule is false.

## OL05b — statement: rule 8 (a valid empty ps array is a valid capture with no running entries)

Documented statement, in my words: availability is decided from the tags array alone; a selected
local tags entry with a nonempty digest plus no selected ps entry is `available_not_loaded`, and a
valid empty ps array is a valid capture with no running entries — not proof of an unloaded daemon.

Observed: the pre-generation `/api/ps` body is literally `{"models": []}` while `/api/tags`
carries the one selected entry. This is the exact shape rule 8 calls `available_not_loaded`, on a
live server, before any generation request. (After one `generate` the ps body holds one entry with
the same digest and an `expires_at`, i.e. the empty pre-state was a real transient, which is what
rule 8's caution says an empty array cannot establish.)

Verdict: confirmed.

## OL05c — statement: the section's precedence ordering (rules 2-7 sequencing)

Documented statement, in my words: the order in which the classifier applies structure checks,
duplicate selection, the inventory gate, alias conflict, digest presence and remote markers is
fixed by the lane's own code path; the heading labels the whole ordering an inference.

Observed: the committed captures contain one entry per surface, equal `name`/`model`, no duplicate
selection, no malformed or non-UTF-8 body, and no `remote_model`/`remote_host` key on the
`ps-after` entry — so the ordering is never exercised by this run in a way that could distinguish
one order from another.

Verdict: not-observable, with reason: rule precedence is a property of the lane's classifier, and
no captured HTTP body encodes it; the live surfaces show state, never which predicate was applied
first. A future capture carrying duplicate selections or ps remote markers could make a narrower
ordering statement testable.

## Validation run (this seat)

`importlib` load of `tools/round60-c2-counter.py` against the committed receipt:
`receipt_caps(...)` -> `ok=True`; `safe_compile` accepted both predicates; `evaluate` ->
`True/True`; `falsifiable` -> `True/True`; `score` on this seat's rows over the frozen base
population -> `rows=3 covered=1 evaluated=2 sensitive=2 bound=2 contradicted=0 errors=0
good_rows=3 receipt_ok=1`.
