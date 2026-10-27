# M12MapServedidentity51 — base line 51 mapping notes

Base coordinate: `corpus/knowledge/served-identity-crosswalk.md:51` at base
`ec3b0d583ed4eb05c7ae935dc59f560e86b0a80b` (frozen population line, "No
inference-readiness guarantee from inventory"). Evidence: the committed live
receipt `.ufo/waves/round-60/live/receipt.json` (schema `kama-ollama-live/v1`,
`receipt_caps` ok=True) and one fresh independent run of
`tools/kama-ollama-live.py` (`--work` in my scratch, nonce 7f2aa13df1cb, port
48997, exit 0, verdict MODEL_OK); the fresh receipt is copied here as
`fresh-r.json`. Both runs agree on every value quoted below, so no row depends on
one sample. All values below are from Ollama v0.40.11 on the 260K fixture GGUF.

## OL12a — "Ollama `/api/ps` entries bounded by `expires_at`"

Documented statement in my words: a loaded-residency observation from Ollama
consists of an `/api/ps` entry that carries an expiry field, i.e. the surface
states when the entry stops being true.

Observed: `/api/ps` after the generation returns exactly one entry
(`kama-…:latest`, digest `8cf91c71…c792`, `runner: "llamacpp"`,
`size_vram: 0`) with `expires_at = 2026-10-27T18:34:10.425205706-03:00`, about
five minutes after the `created_at` of the same run's generation
(`2026-10-27T21:29:10.424782727Z`). Predicate verdict: confirmed (evaluates true
on the committed captures; flips false if `expires_at` is removed, emptied, or
the entry list changes length).

Scope: confirmed for this version, this fixture model, this one-shot run. It says
nothing about whether a vendor keeps `expires_at` across versions.

## OL12b — "Neither is a durable readiness guarantee"

Documented statement in my words: even where a residency witness exists, it is a
dated, bounded observation and not a standing readiness guarantee — so inventory
presence must not be read as residency, and a hit must not be read as lasting.

Observed: the run imported the model and already listed it in `/api/tags`
(one entry, no `expires_at` field anywhere on the tags entry), then sampled
`/api/ps` before any generation: `{"models": []}`. Only after the one
`/api/generate` does `/api/ps` carry the entry, and that entry is the only place
the expiry appears. Predicate verdict: confirmed (evaluates true; it would flip
false if the pre-generation `/api/ps` sample had already held the model, if the
post-generation entry had no `expires_at`, or if the tags entry itself carried
one).

Calibration caveat, stated on purpose: this row tests the observable core —
residency is absent before the load and bounded after it. It does not prove the
modal claim over all future time; "durable" in general is not something a receipt
of two `/api/ps` samples can settle, and the row does not assert it.

## OL12c — "Ollama's compatibility documentation does not specify equivalent residency fields"

Documented statement in my words: the compatibility page does not document
residency fields equivalent to `/api/ps`.

Not-observable: this is a statement about page text. No captured HTTP body can
show what the documentation omits; deciding it means re-reading the S010
(`/api/openai-compatibility`) and S012 (`/api/ps`) rows and the pages behind
them, not sampling a server. For completeness the captured OpenAI-compatible
bodies were inspected: `/v1/models` returns `id`, `object`, `created`,
`owned_by` only (and `data: null` on an empty store), and `/v1/models/<id>` the
same four fields — no residency field on the served surface. That is a fact about
the served payload, not about the page, and the crosswalk already carries it as a
separate statement at line 50 (`/v1/models` documents metadata only); folding it
into this row would grade a documentation claim with a runtime capture, so it is
left as a not-observable row with the served-payload note recorded here instead.

## Corrections to append

None. No row is contradicted, so no amendment paragraph is proposed and
`corpus/knowledge/ollama-live-amendment-r60.md` needs nothing from this line.

## Fodder for the round's knowledge entry (not written by me; lane source is read-only for this seat)

If the knowledge entry needs one live-sourced datum, the sharpest one from this
line is: `ollama create` does not load the model — the tag is listed in
`/api/tags` while `/api/ps` is empty, and the entry appears only after the first
generation request, with `expires_at` roughly five minutes out. That is the
concrete observation behind "inventory is not residency" and it is reproducible
from the committed receipt alone (`tags`, `ps-before`, `ps-after`, `generate`).
