# Seat M14MapServedidentity132 — base line mapping notes

Base population coordinate: `corpus/knowledge/served-identity-crosswalk.md:132`
(base `ec3b0d58…`, line text: ``... local (vs remote) provenance on Ollama"); it carries the same `[INFERENCE]` ``).

## What the base line actually says

Line 132 sits in the "Scope over `## Grounded failure cases`" paragraph. It does three things:

1. It restates that the locality conclusion of case 6 ("Available inventory is not proof of local
   weights", premise sourced to S031 + S010's signed-in-server precondition) is the `[INFERENCE]`.
2. It records that the same locality conclusion is restated in the `## What cannot be concluded`
   `MODEL_OK` bullet, and quotes that bullet: "never establishes ... local (vs remote) provenance on
   Ollama".
3. It assigns that bullet the same `[INFERENCE]` status and asserts it "is not an additional page quote".

Locator check (document-internal, not a capture): `git show base:… | cat -n` gives line 52 =
`` - **A `MODEL_OK` verdict is an inventory statement at sample time.** It never establishes loaded
weights, local (vs remote) provenance on Ollama, or execution readiness — and on llama.cpp single-model
it can even be observed mid-load. `` — the cross-reference in line 132 is correct as written.

The capture-testable proposition in the line is therefore only the locality conclusion: an Ollama
inventory hit supplies no local-vs-remote provenance signal. Statements 2 (locator) and 3 (label status,
"not an additional page quote") are properties of the lane's own text, not of any Ollama response.

## Rows

### OL14a — `/api/tags` supplies identity and size, no provenance field (confirmed)

Documented statement (my words): a live `/api/tags` hit carries `name`/`model`, `size`, `digest`,
`details`, and `capabilities`, and carries neither `remote_host` nor `remote_model` — the only two
fields S031 documents as provenance-relevant ("if the model is remote"). So inventory membership alone
cannot establish local (vs remote) provenance, which is what line 52 (restated here) claims.

Observed (committed receipt `.ufo/waves/round-60/live/receipt.json`, capture `tags`, status 200):
one model object, keys `name, model, modified_at, size, digest, details, capabilities`; `digest`
`8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792`; no `remote_host`/`remote_model`.

Predicate: `'remote_host' not in c['tags']['models'][0] and 'remote_model' not in
c['tags']['models'][0] and 'digest' in c['tags']['models'][0]` → True; falsifiable=True (mutation of
the `digest` chain path to `{}`/`""` flips it).

### OL14b — the OpenAI-compatible listing carries no provenance field either (confirmed)

Documented statement (my words): the second Ollama inventory surface the crosswalk names, `/v1/models`,
returns one entry with `id`, `object`, `created`, `owned_by` only — no content digest and no
`remote_host`/`remote_model`. The same locality conclusion therefore holds on that surface too: an
OpenAI-compatible list answer says nothing about where the weights are.

Observed: `{"object":"list","data":[{"id":"kama-b61c98ad5747:latest","object":"model","created":1793136550,"owned_by":"library"}]}`
(status 200); `owned_by` is the documented default `library`.

Predicate: `len(c['v1-models']['data']) == 1 and 'remote_host' not in c['v1-models']['data'][0] and
'remote_model' not in c['v1-models']['data'][0] and 'digest' not in c['v1-models']['data'][0]` →
True; falsifiable=True (empty-list mutation flips `len(...)==1`).

### OL14c — label status / "not an additional page quote" (not-observable)

Documented statement (my words): the quoted `MODEL_OK` sentence bears the same `[INFERENCE]` label as
case 6's conclusion and is not a paraphrase of a cited page.

Why no capture can test it: the receipt's captures are HTTP bodies only (`root` is non-JSON and absent
from `c`; `version`, `tags-empty`, `v1-models-empty`, `tags`, `v1-models`, `v1-model-single`, `show`,
`ps-before`, `generate`, `ps-after` are JSON). None records which sentence the lane labelled
`[INFERENCE]`, nor whether a sentence is a quote of S010/S011/S031 — label and quote-provenance are
text/intent properties of `corpus/`, testable only by reading the corpus and its registry rows, not by
any server answer. Reason recorded (193 chars) names this.

## What this mapping does NOT establish (stated before the verdicts are used)

- The receipt contains **no remote-model capture** (`OLLAMA_NO_CLOUD=1`, one locally imported GGUF).
  The rows therefore record that the captured inventory entry carries no provenance field; they cannot
  show how a remote entry *would* look, and absence of `remote_host` for a local entry is consistent
  with — not proof of — local weights. The `[INFERENCE]` status on line 52 stays correct for exactly
  that reason, and a confirmed row here is confirmed for this one run only (freeze limits clause).
- Locality evidence that *does* exist in the capture lives on a different surface: `show` reports
  `FROM /fast/scratch/hyaku/kama-r60/live1/models/blobs/sha256-270cba1bd5…` (the imported local blob),
  and `tags.digest` (`8cf91c71…`) is not the GGUF's sha256 (`270cba1b…`). That is `show`, not
  inventory, so it does not falsify the inventory caveat; it explains why the caveat is placed on an
  inventory verdict rather than on `show`.
- No contradicted row is written, so no amendment paragraph is proposed from this seat. If w2 falsifies
  OL14a/OL14b (e.g. a remote entry appearing with `remote_host` set in a re-run receipt), the honest
  correction is narrow: the tags/v1 listing *can* carry a provenance marker when the entry is remote,
  while membership still does not prove local weights.

## Validation actually run

`importlib` on `tools/round60-c2-counter.py`: `receipt_caps(...)` → `(caps, ok=True)`,
`population(base)` → 14 lines, and per row: key in population True, quote 6/6/4 words and an exact
base-line substring, `evaluate`/`falsifiable` True/True for OL14a and OL14b, verdict matches
evaluation; OL14c empty predicate with a 193-character reason.
