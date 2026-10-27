# M11 — mapping base line 45 of `corpus/knowledge/served-identity-crosswalk.md`

Base population coordinate: `ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b:corpus/knowledge/served-identity-crosswalk.md:45`
(the "Aliases and path normalization limits" list, bullet 3, citing S010/S011/S012).
Evidence base: the committed receipt `.ufo/waves/round-60/live/receipt.json`
(schema `kama-ollama-live/v1`, every capture sha256 re-verified against its body, `receipt_caps ok=True`).
Rows written: `rows.tsv` (3 rows, ids OL11a/OL11b/OL11c).

## OL11a — `name` and `model` are both just "Model name"

Documented statement, in my words: on Ollama's inventory (`/api/tags`) and loaded-model (`/api/ps`)
surfaces, `name` and `model` are the same human-facing model name, not a second identity field; the
name is a caller-chosen alias, so it carries no content information.

Observed (committed receipt): `tags.models[0]` and `ps-after.models[0]` both return
`name == model == "kama-b61c98ad5747:latest"`; `b61c98ad5747` is the caller nonce the harness supplied
(`ollama create kama-<nonce>`), and the same entry carries a separate 64-hex `digest`
(`8cf91c71…c792`). Predicate true; falsifiable (empty-list mutation of `c['tags']['models']` flips it).

## OL11b — only `digest` is content-addressed

Documented statement, in my words: across the two Ollama surfaces the only field that identifies the
artifact by content is `digest`; a name match is not a content match, and `size` is not a content
identity either.

Observed (committed receipt): `tags.models[0].digest == ps-after.models[0].digest ==
8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792` (64 hex) for the same
`name`, while `size` differs between the surfaces (1185492 in `/api/tags` — on-disk manifest size —
versus 6312427 in `/api/ps` — resident allocation). This is the tags-to-ps join the line labels an
[INFERENCE] candidate: it resolves for this run, on the digest, with `name` equal and `size` unequal.
Predicate true; falsifiable (nulling either digest flips it).

## OL11c — "the tags-to-ps digest join is an [INFERENCE] candidate, not a documented mapping"

Documented statement, in my words: the lane records the join as its own inference; S010/S011/S012 are
not claimed to document it.

Verdict: not-observable. The clause is a statement about what the cited pages say, and the committed
receipt holds only HTTP response bodies from one server run; no captured surface can report
documentation status. No predicate is attached (per the counter's rule) and the reason cell names why.
The runtime half of the clause (does the join resolve?) is carried by OL11b.

## No contradicted rows

Nothing on line 45 is contradicted by the capture. Consequently no amendment paragraph is owed by this
seat for `corpus/knowledge/ollama-live-amendment-r60.md`.

## Precision caveat for the frontier step (advisory, NOT a contradiction of line 45)

The served `digest` is a sha256 of the imported manifest, not of the GGUF file the caller handed to
`ollama create`. Line 45's parenthetical quotes the docs' gloss "SHA256 digest identifier of the model
contents"; the capture shows two distinct sha256 values for one artifact chain:
`/api/tags`+`/api/ps` `digest = 8cf91c71…c792`, while `show.modelfile` still names the source blob
`…/models/blobs/sha256-270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
(= the pinned fixture GGUF sha256). So a lane reader must not join `sha256sum <file>.gguf` to the
served `digest`. Line 45 does not assert that equality, so this is not a contradicted row; if the L1
wants it graded, it is testable from the committed receipt alone
(`c['tags']['models'][0]['digest'] != '270cba…'` and the blob path present in `c['show']['modelfile']`)
and would need its own quote/row and an amendment paragraph.

## Second-look corroboration (fresh lane-owned run, not the graded evidence)

`tools/kama-ollama-live.py --work <scratch>/run2 --nonce 3f9a11c2d7` (exit 0, verdict `MODEL_OK`,
port 54911, teardown `port_closed=true`, `sigkill_needed=false`; receipt copied to
`corroboration-r2.json` in this directory):

- `digest` identical to the committed run in both `/api/tags` and `/api/ps`: `8cf91c71…c792` under a
  different model name → the digest is deterministic over the imported content, the name is not.
- `name == model == "kama-3f9a11c2d7:latest"`; `size` 1185492 / 6312427, same split as the committed run.
- `blob` path again `sha256-270cba…` (source GGUF), serving `digest` again `8cf91c71…`.
- OL11b's predicate evaluates True on this receipt as well; OL11a's evaluates False only because its
  predicate is bound to the committed run's nonce literal — expected, not a defect.

## Validation actually run

`importlib` load of `tools/round60-c2-counter.py` against the committed receipt:
`receipt_caps ok=True`; per row `safe_compile` accepted, `evaluate`→True for OL11a/OL11b
(matching `confirmed`), `falsifiable`→True for both; OL11c has an empty predicate and a 192-character
reason; `score()` over this registry alone: rows=3, covered=1, evaluated=2, eval_lines=1, sensitive=2,
bound=2, contradicted=0, errors=0, good_rows=3 (isolated `met=False` is expected: the registry is
assembled from all seats and this seat owns one population line of fourteen).
