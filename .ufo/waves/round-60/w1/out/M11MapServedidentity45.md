# M11 — base line 45 mapped to live Ollama evidence (round 60 w1)

Files (all under `.ufo/waves/round-60/w1/out/`): `M11MapServedidentity45/rows.tsv` (3 rows, prefix OL11), `M11MapServedidentity45/notes.md`,
`M11MapServedidentity45/corroboration-r2.json`. No lane source, registry, control or amendment file touched.

Rows on `corpus/knowledge/served-identity-crosswalk.md:45` (quotes exact, 8/4/12 words):
- OL11a `name` and `model` are both just "Model name" — confirmed; tags and ps-after both return `name == model == kama-b61c98ad5747:latest` (caller nonce), separate 64-hex digest.
- OL11b only `digest` is content-addressed — confirmed; digest `8cf91c71…c792` identical in `/api/tags` and `/api/ps` for the same name, `size` differing 1185492 vs 6312427 → the [INFERENCE] tags-to-ps join resolves on the digest, not on name or size.
- OL11c "…[INFERENCE] candidate, not a documented mapping" — not-observable (192-char reason): documentation status of S010/S011/S012 is not in any captured HTTP body.
No contradicted row: nothing on line 45 fails; no amendment paragraph is owed by this seat.

Validation (run, not asserted): `importlib` load of `tools/round60-c2-counter.py` on the committed receipt — `receipt_caps ok=True`; both predicates `safe_compile`+`evaluate`→True (matching `confirmed`) and `falsifiable`→True; `score()` over this registry alone: rows=3 covered=1 evaluated=2 sensitive=2/2 bound=2 contradicted=0 errors=0 good_rows=3; isolated `met=False` only because 1 of 14 population lines is mine.
Second look: fresh lane-owned `tools/kama-ollama-live.py --work <scratch>/run2 --nonce 3f9a11c2d7` exit 0 `MODEL_OK`, port 54911, teardown `port_closed=true`/`sigkill_needed=false`; digest identical under a different name, OL11b True on it (OL11a False only via its committed-run nonce literal).

Advisory for the frontier step, NOT a contradiction of line 45: served `digest` is the manifest sha256 (`8cf91c71…`), while `show.modelfile` names the source blob `sha256-270cba1b…` (= pinned GGUF sha256); do not join a file `sha256sum` to the served digest. It is gradeable from the committed receipt if the L1 wants it as its own row plus amendment.
Risks: predicates read one run's shape (single model, CPU, v0.40.11, fixture GGUF) — a confirmed row binds to this capture only. Scratch `/fast/scratch/hyaku/kama-r60/M11MapServedidentity45` removed; receipt copied out first. Tooling: none installed.
