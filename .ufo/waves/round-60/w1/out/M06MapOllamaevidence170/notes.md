# M06 — base line 170 mapping notes

Base population line: `corpus/knowledge/ollama-evidence-replay.md:170`
(frozen base `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`):

    170:    markers is a conservative lane inference, not a ps OpenAPI field.

Its statement, in context, is rule 7 of the replay contract: "Any nonempty string
`remote_model` or `remote_host` on the selected tags or ps entry is
`remote_inventory` ... Recognizing ps-side markers is a conservative lane inference,
not a ps OpenAPI field." The line therefore carries two separable statements: (i) a
claim about the lane's own classifier (the ps-side recognition is an inference, i.e. a
design choice rather than a documented field), and (ii) a claim about Ollama's
`/api/ps` surface (model objects carry no `remote_model`/`remote_host` field).

## OL06a — quote "not a ps OpenAPI field" — confirmed

- Documented statement: the live `/api/ps` model objects do not expose the
  `remote_model` / `remote_host` marker fields, so recognizing those markers on a ps
  entry is not reading a field the endpoint publishes.
- Predicate: at least one loaded model in `ps-after`, and neither `ps-after` nor
  `ps-before` model object contains `remote_model` or `remote_host`.
- Observed (committed receipt, nonce b61c98ad5747): `ps-after` has one model with keys
  `name, model, size, digest, details, expires_at, size_vram, context_length, runner`;
  `ps-before` is `{"models": []}`; neither key appears on either capture.
- Replication (own lane-owned child, nonce c72aafd1c719, port 55195, verdict
  MODEL_OK, exit 0): identical ps key set, no remote markers; `ps-before` empty.
- Limit: absence of a key in a v0.40.11 response is evidence about that version's
  emitted field set, not proof about an OpenAPI document, and not proof that the field
  can never appear. The row confirms only "not observed on the emitted ps entries".

## OL06b — quote "markers is a conservative lane inference" — not-observable

- Documented statement: whether the ps-side marker recognition is *conservative* is a
  property of the lane's own classifier design (the rule was written because the ps
  field is not documented), not of any server response.
- No capture surface decides it: the receipt carries only HTTP bodies and checks, none
  of which record the lane's rationale, its source reading, or the provenance of the
  rule. The tags capture likewise does not even carry remote markers in this version,
  so it cannot speak to ps-side provenance either.
- Reason length 220 chars; predicate empty as required for not-observable.

## Contradictions

None. No row in this slice is contradicted, so no amendment paragraph is proposed for
`corpus/knowledge/ollama-live-amendment-r60.md` from this seat. If the lane wants to
tighten the wording, the safe change is to say "no `remote_model`/`remote_host` key is
emitted on ps entries in the captured v0.40.11 run" rather than "not a ps OpenAPI
field", because a single capture cannot settle a schema question.

## Validation (counter functions, committed receipt)

`python3` importlib of `tools/round60-c2-counter.py`:
`receipt_ok=True`, 2 rows, 8 columns each, quotes exact substrings of base line 170
(5 and 6 words), OL06a `evaluate=True` and `falsifiable=True`, OL06b not-observable
with empty predicate; `score(...)` on these two rows only:
`covered=1 population=14 evaluated=1 eval_lines=1 sensitive=1/1 bound=1
contradicted=0 amended=0/0 receipt_ok=True good_rows=2 errors=0 met=False`
(met is false only because the other 13 population lines belong to the other mapping
seats). Fresh receipt from my own run: same predicate `eval=True`,
`falsifiable=True`, `receipt_ok=True`.
