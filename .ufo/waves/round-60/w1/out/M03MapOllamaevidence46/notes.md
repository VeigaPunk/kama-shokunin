# M03 — base line `corpus/knowledge/ollama-evidence-replay.md:46`

Base blob `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b`, frozen line text:
"counted as locally loaded is also **[INFERENCE]** (and is already labeled that"

Statement it belongs to (base lines 43-47, read from the base blob): after stating that `/api/ps` has no
`remote_model`/`remote_host` field, the entry says the *conclusion* that a remote `/api/tags` entry
"cannot be counted as locally loaded" is kama lane policy marked `[INFERENCE]`, and that the label is
already carried in `served-identity-crosswalk.md`. So the line bundles (a) a counting rule for the
lane's own classifier, (b) the labelling of that rule as inference, and (c) a pointer to where the
label already lives. It is not a claim about documented Ollama fields.

## Rows

### OL03A — quote `counted as locally loaded` — confirmed
Documented statement, my words: an entry is counted as locally loaded only when `/api/ps` reports it;
membership in `/api/tags` alone is not counted as loaded (this is the mechanism the remote-entry rule
at the head of the sentence qualifies).
Observed: `/api/tags` holds exactly one entry (`kama-b61c98ad5747:latest`, digest
`8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792`) *before* any generation, while
`ps-before` is `{"models":[]}`; after one `POST /api/generate`, `ps-after` holds one entry with the same
digest. Replayed through the lane classifier this is `available_not_loaded` exit 1 before and
`loaded_same_digest` exit 0 after (receipt checks `evidence-before-load`, `evidence-after-load`,
`ps-lists-loaded`, all `passed: true`).
Predicate (TAB column in rows.tsv), evaluated True on the committed receipt and falsifiable — forcing
`ps-before.models` non-empty, emptying `tags.models`, or emptying `ps-after.models` each flips it to False.
Scope: this exercises the **local** branch only. Nothing here exercises a remote tags entry, so the
statement's actual exclusion clause stays untested — that is OL03B, not a stronger reading of this row.

### OL03B — quote `is also **[INFERENCE]**` — not-observable
Documented statement, my words: the conclusion "a remote tags entry cannot be counted as locally loaded"
is lane policy, not upstream behaviour; the receipt cannot decide it.
Observed: the receipt's `tags` entry keys are `capabilities/details/digest/model/modified_at/name/size`,
and `ps-after` adds `context_length/expires_at/runner/size_vram`; no captured entry anywhere carries
`remote_model` or `remote_host` (checked over the committed bodies). The rule exists in the lane's own
code — `tools/kama-ollama-evidence.py:244-246` returns `remote_inventory` on a tags marker before any ps
match — but no capture contains a marker, so no surface in this receipt decides the clause.
Correction: none (no contradiction found).

### OL03C — quote `and is already labeled that` — not-observable
Documented statement, my words: the locality conclusion is already labelled `[INFERENCE]` in
`served-identity-crosswalk.md`; the sentence is a prose cross-reference.
Observed: receipt captures are 11 HTTP responses (10 JSON, root plain text), carrying no document text,
so no capture can test a wording/label sentence.
Supplementary, *not* part of the capture verdict: the pointer is textually correct at the tip —
`corpus/knowledge/served-identity-crosswalk.md:96` ("The locality conclusion is [INFERENCE]") and
`corpus/knowledge/served-identity-crosswalk.md:132` ("carries the same `[INFERENCE]`"). That is a repo
read, not a live observation, and the row therefore keeps `not-observable` and an empty predicate.

## Validation run (exact)

```
python3 -c "... importlib on tools/round60-c2-counter.py ..."
receipt ok: True caps keys: 10
population: 14 line46 in pop: True
OL03A eval True falsifiable True
  ps-before forced non-empty -> False
OL03B not-observable reason_len 201
OL03C not-observable reason_len 180
score: {'rows': 3, 'covered': 1, 'population': 14, 'evaluated': 1, 'eval_lines': 1,
        'sensitive': 1, 'bound': 1, 'contradicted': 0, 'amended': 0, 'receipt_ok': True,
        'good_rows': 3, 'errors': 0, 'met': False}
```

`met=False` is expected and not a failure of this seat: `score()` is run here over these three rows only,
so `covered=1` of the 14 frozen population lines (the other lines belong to sibling seats' rows) and
`evaluated=1` is below the registry-wide floor of 5. `good_rows=3`, `errors=0`, `receipt_ok=1` mean every
row this seat wrote is well-formed, quote-located on the base line, and verdict-consistent.

## Amendment text

No contradicted row, so this seat contributes no amendment paragraph. The line stands for this run:
its counting mechanism is confirmed on the local branch and its remote-exclusion clause is unexercised by
the committed receipt.
