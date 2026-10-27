# M13MapServedidentity103 — base line `corpus/knowledge/served-identity-crosswalk.md:103`

Population coordinate (base `ec3b0d58`): the line in the "Correction — round 12 D4" note that closes the
S031 parenthetical and opens the locality inference. Exact base text (line 103):

```
  row's claim cell as the upstream Ollama URL). [INFERENCE] Because the page
```

The sentence it belongs to runs lines 96–108: the locality conclusion is kama's `[INFERENCE]`, its documented
basis is SOURCES row S031 (`/api/tags` `ModelSummary` `remote_model` / `remote_host`), and the inference is that
because `/api/tags` membership *can* be remote, membership alone cannot establish locally resident weights.
Line 103 itself carries two things: a cross-reference into kama's own S031 claim cell, and the beginning of the
inference ("Because the page ..."). Neither is an Ollama behaviour claim in its own right.

Evidence used: the committed live receipt `.ufo/waves/round-60/live/receipt.json`
(`receipt_caps` → ok=True, 10 parsed bodies: version, tags, tags-empty, v1-models, v1-models-empty,
v1-model-single, show, ps-before, generate, ps-after). No fresh run was needed: the committed captures answer
every question line 103 can raise, and a second run changes no field that matters here (same pin, same flags).

## Row OL13A — `not-observable`

Documented statement, in my words: the description of `remote_host` as "the upstream Ollama URL" lives in
**kama's own registry cell** (SOURCES row S031), not in the page text quoted on line 101-102.
Observed: `corpus/SOURCES.md:43` claim cell reads "`remote_model` names the upstream model and `remote_host` the
upstream Ollama URL" — so the crosswalk's attribution is accurate at the document level. That check is a
doc-to-doc cross-check, not a capture: the receipt holds only HTTP bodies and no registry text, so no captured
surface can decide what a registry cell says. Hence `not-observable` with an empty predicate.
No amendment (row is not contradicted).

## Row OL13B — `not-observable`

Documented statement, in my words: the *premise* of the inference is a documentation fact — that the
docs.ollama.com/api/tags page documents `remote_model` / `remote_host`, i.e. that membership can be remote.
Observed: `c['tags']` = `{"models":[{"name":"kama-b61c98ad5747:latest", ... "capabilities":["completion"]}]}` —
one entry, keys `capabilities, details, digest, model, modified_at, name, size`, **no** `remote_model` and no
`remote_host`; the run sets `OLLAMA_NO_CLOUD=1` (`tools/kama-ollama-live.py:185`) and imports one local GGUF,
with no pull, so zero remote entries can ever appear. A capture cannot read a documentation page, and this
capture cannot exhibit remote membership; no captured surface can test the premise. `not-observable`.
No amendment (row is not contradicted).

## Row OL13C — `confirmed` (the one live-bearing clause)

Documented statement, in my words: the empirical point the inference leans on — a `/api/tags` entry is an
inventory fact and does not by itself report loaded/resident state; the residency surface is `/api/ps`.
Predicate: `len(c['tags']['models']) == 1 and 'remote_model' not in c['tags']['models'][0] and
'remote_host' not in c['tags']['models'][0] and c['ps-before']['models'] == []`
Observed: tags lists exactly one entry with no remote marker while `ps-before` is `{"models":[]}`; after one
generation `ps-after` lists the model with digest `8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792`,
equal to the tags digest — residency is established by a digest join on `/api/ps`, never by membership.
Evaluation on the committed receipt: `True` (= confirmed); `falsifiable=True`. Sensitivity shown by hand:
adding `remote_host` to the tags entry flips it to `False`, and making `ps-before` loaded flips it to `False`.
Scope limit stated: this confirms the tags-vs-ps surface separation on this run; it does **not** confirm the
remote-membership premise (that is OL13B) and it does not make the inference itself measured fact.

## What the line cannot get, and why that is the honest result

The only two capture-dependent facts line 103 could want are (a) that a remote entry exists in `/api/tags`, and
(b) that remote membership coexists with non-local weights. The committed run has neither: it is a CPU-only,
cloud-disabled, single local import. Marking either as confirmed here would be laundry. The lane's wider C2
claim needs its 5 evaluated rows / 4 distinct lines from lines that actually carry behaviour statements
(lines 104-106 and the `ollama-evidence-replay.md` population), not from this cross-reference line.
