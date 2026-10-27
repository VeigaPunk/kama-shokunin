# M08MapOllamaevidence301 — OL08 rows over base line 301

Base population coordinate: `corpus/knowledge/ollama-evidence-replay.md:301` (base ec3b0d5).
Base line text: `- KQ13: available inventory, loaded residency, advertised identity and inference`
The claim the line belongs to is the entry's QUALITY clearance item KQ13: the four Ollama dimensions
(available inventory = `/api/tags`, loaded residency = `/api/ps`, advertised identity = model names/ids,
inference readiness = an actual generation) are kept apart, and the digest join between them is labelled
`[INFERENCE]`. Evidence used: the committed receipt `.ufo/waves/round-60/live/receipt.json`
(schema `kama-ollama-live/v1`, all sha256 bodies intact: `receipt_caps` -> `ok True`), plus one fresh
independent run of `tools/kama-ollama-live.py` as a second look (verdict `MODEL_OK`, port 37909,
`teardown.port_closed=true`, same pin digests, nonce `2afc7aed4e2e`).

## OL08a — "available inventory, loaded residency" (confirmed)

Documented statement, in my words: what the server lists as available (`/api/tags`) and what it reports
as resident in memory (`/api/ps`) are two different surfaces and are not treated as one.
Observed: `tags` carries exactly one entry (`kama-b61c98ad5747:latest`, digest `8cf91c71…c792`);
`ps-before` is exactly `{"models":[]}`; `ps-after` carries the same model. Predicate
`len(c['tags']['models']) == 1 and c['ps-before']['models'] == [] and len(c['ps-after']['models']) == 1`
evaluates True and is falsifiable (each of the three `models` chains flips it). The fresh repeat run
reproduced the same shape (tags=1, ps-before=[], ps-after=1) under a different nonce and port.

## OL08b — "advertised identity and inference" (confirmed)

Documented statement, in my words: an advertised identity is not by itself evidence of inference
readiness; readiness is what an actual request to the model demonstrates.
Observed: `tags[0].name` = `v1-models.data[0].id` = `kama-b61c98ad5747:latest`; `generate` returned
`done:true`, `done_reason:"length"`, `response:" upon a time,"`; `ps-before` was empty at that moment.
Predicate `c['tags']['models'][0]['name'] == c['v1-models']['data'][0]['id'] and c['generate']['done'] is
True and c['ps-before']['models'] == []` evaluates True and is falsifiable. So the identity was advertised
on both the native and the OpenAI-shaped surface while nothing was loaded, and readiness came only from
the generation.

## OL08c — "available inventory, loaded residency, advertised identity" (not-observable)

Documented statement, in my words: KQ13 states a rule the lane's classifier keeps — four dimensions are
never merged into one finding. This is a statement about the lane's own classifier, not about Ollama:
no captured HTTP body records which finding `tools/kama-ollama-evidence.py` emitted for this run, and the
receipt holds only server responses. Reason recorded in the row: no captured surface can test it.

## No contradicted row

Nothing in the committed receipt or the fresh repeat contradicts line 301, so no amendment paragraph is
offered; `observed` cells are included anyway for direct pasting if the lane later decides to cite them.

## Adjacent observation (not a row; does not contradict 301)

The identity surface is not internally uniform: `/v1/models` lists `kama-b61c98ad5747:latest` while
`/v1/models/{model}` returns `id":"kama-b61c98ad5747"` (tag stripped) — the committed receipt and the
fresh repeat both show this (`v1_single_id_equals_list_id: false`). This is a difference *inside* the
advertised-identity dimension, so it strengthens rather than tests KQ13's separation. It does bear on the
entry's exact, case-sensitive name-matching policy elsewhere in the document, which is a different line of
the population and not mapped here. `ps-after.details.parent_model` is `""` while `tags[0].details.parent_model`
is `stories260K.gguf` — also a surface difference, same status.

## Second-look run (evidence, not a row)

`tools/kama-ollama-live.py --work <scratch>/run --out <scratch>/r.json`, exit 0, 1.46 s elapsed,
own scratch HOME/model store, `OLLAMA_NO_CLOUD=1`, CPU-only device variables, own free port 37909
(no reuse of any seat's server, no port 8080/34113/11434). Receipt copied here as
`live-repeat-r.json`; scratch deleted after the copy.
