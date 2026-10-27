# M09 — base line 302 (`corpus/knowledge/ollama-evidence-replay.md`)

Base blob `ec3b0d58…` line 302 (2 leading spaces, no trailing):

    readiness stay separate; the digest join is **[INFERENCE]**.

It is the second half of KQ13 (lines 301–302): "available inventory, loaded residency, advertised
identity and inference readiness stay separate; the digest join is **[INFERENCE]**." Cited rows in
that section are S012 (`GET /api/ps`) and S031 (`GET /api/tags`); both surfaces are in the receipt.

Evidence: `.ufo/waves/round-60/live/receipt.json` (schema `kama-ollama-live/v1`, every capture body
sha256 matches, nonce `b61c98ad5747`, server 0.40.11). Second look: a fresh lane-owned run in my
scratch (nonce `9caa101f88a1`, port 39837, verdict MODEL_OK) reproduced every value used below;
receipt copy at `fresh-receipt-9caa101f88a1.json` next to this file.

## OL09a — "readiness stay separate" — confirmed

Documented statement, in my words: whether a model is *available* (`/api/tags`) is a different
surface from whether it is *resident* (`/api/ps`), so inventory must not be read as readiness.

Observed: `ps-before` = `{"models":[]}` while `tags` = one model, `kama-b61c98ad5747:latest`
(digest `8cf91c71…c792`). Predicate `c['ps-before']['models'] == [] and len(c['tags']['models']) == 1`
evaluates true; mutating either chain flips it, so it is falsifiable by construction. The same split
held on the fresh run (`ps-before` empty, `tags` one model). This is the specific separation the
line asserts: advertisement precedes residency, and only the later `generate` moves residency.

## OL09b — "stay separate; the digest join is" — confirmed

Documented statement, in my words: the surfaces are joined by digest, and the join is a distinct
question from name or size.

Observed: `tags` and `ps-after` carry the *same* digest
`8cf91c7109e77999ac0ae6e6eab27dfea00d9f83ffbe4559a3f26266e455c792` for the same model, while the
advertised sizes differ (`1185492` vs `6312427`) and the names agree. So on this run the digest is
the equality key across inventory and residency, and neither name nor size would serve: a size join
is falsified by the capture, which is the strongest calibration statement the line supports.
Predicate `c['tags']['models'][0]['digest'] == c['ps-after']['models'][0]['digest']` evaluates true
and falsifiability holds (mutating either digest chain flips it). Reproduced on the fresh run, where
the digest was identical again across a different nonce: the manifest digest is content-derived, so
it is stable while the nonce-named tag is not.

## OL09c — "the digest join is **[INFERENCE]**" — not-observable

Documented statement, in my words: the tag that marks the lane's *own* digest join as an inference
is a classification-policy label.

Observed: no capture body carries a lane classification label or the classifier's join decision.
`show` has no digest field at all; the only source digest in the capture is a substring of
`show.modelfile`'s `FROM …/blobs/sha256-270cba1…256d` line, i.e. text, not a field. That the served
digest (`8cf91c71…`) differs from that source blob digest is evidence *about* the join's
availability; it cannot test whether the lane is right to label its join `[INFERENCE]`. Reason row
therefore names the missing surface (lane labels), not a missing capture.

## Amendment

No contradicted row on this line, so no amendment paragraph is owed from this seat. The lane may
still want the positive finding recorded: for `/api/tags` ↔ `/api/ps` the digest join is confirmed
by capture, while the served-identity → source-GGUF join is not a field equality (the source digest
appears only inside `show.modelfile` text), which is exactly what justifies the `[INFERENCE]` label.
