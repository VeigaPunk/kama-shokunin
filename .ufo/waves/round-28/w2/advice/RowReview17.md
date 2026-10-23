# RowReview17 — F28-33 (stop), F28-34 (samplers)

Seat: KamaR28.RowReview17, wave 2 FALSIFY, port 48317. Fixture per assignment:
`~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48317`
(binary self-reports `build 11755, commit 704366d76`; sha256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`, matching SKILL.md; `git ls-remote` shows tag `b11755` → `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`. Identity pin verified independently.)
Raw probe results: `.ufo/waves/round-28/w2/out/RowReview17/remeasure.json`; server log `…/server.log` (server killed, `ss` confirms port free).

## F28-33 — `stop` (SKILL.md line 1192, S172, snapshot L435)

**Live re-measure.** Counter-exact body `{"prompt": "Once upon a time", "n_predict": 1, "stop": "\n"}` → HTTP 200, `generation_settings.stop = ["\n"]`, response sha256 `bbbbb4b7bb4f3ea0e90d97baf810c7a2c6c9be2350960d47dbc3069d7b54da4d`. Field-omitted base (same prompt, `n_predict` 1) → 200, `stop = []`, sha `1fd734bb6553b57f777dcb70ab4f92aec2ebc5b5ec217d79dd9f0bf6f629aa40`. Outcome and delta match the registry and the seat's record (byte-level sha differs because `timings` differ; the recorded invariant — status + stored value — holds).

**Source verdict.** Snapshot L435-450 declares `field_json("stop")` whose handler clears `params.antiprompt`, pushes every array element `word` where `!word.empty()`, or pushes a bare string verbatim, then falls back to `params_base.antiprompt` (CLI defaults) if empty. `server-task.cpp:121` serializes `{"stop", antiprompt}` into `generation_settings`, so the echo is the antiprompt vector — the source explains the observed wrap `"\n" → ["\n"]`. Decisive edge check: `word.empty()` is nlohmann `json::empty()`, which is false for strings (only null/array/object can be empty), so an array `""` element is NOT skipped — my live probes confirm: `[""]→[""]` and `["", " upon"]→["", " upon"]`. `[null]→[]` (skipped, falls back to CLI defaults, empty here) and `5→[]` (neither branch, silent no-op). `[1]→400 "Field 'stop': type must be string"`.

**Prose verdict (meaning cell).** All stated clauses verified live:
- `"\n"` wrapped to one-element array — holds.
- "an empty string is echoed as a `[""]` stopping entry" — holds and is stronger than stated: `stop:""` with `n_predict:8` produced `content:""`, i.e. the `[""]` entry is a real immediate stopper (`find_stopping_strings` at server-context.cpp:615 finds `""` at position 0).
- "an empty array clears it" — holds under this fixture but is over-general as client advice: the pinned handler (L448-449) falls back to the CLI `--reverse-prompt`/antiprompt defaults, so "clears" is only true because the fixture's default argv sets none; with CLI antiprompts the array input restores them.
- Corrected sentence (if touched): `An empty array clears the request's stop strings and falls back to the server's CLI defaults (empty under the fixture's default argv, so the echo is []); an empty string inside an array is kept verbatim and stops generation immediately.`

**SOURCES/Gate.** `corpus/SOURCES.md` S172: URL `…/server-schema.cpp#L435` — raw fetch re-hashed `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`, equal to the pin; quote is L435+L436 whitespace-joined, verbatim ✓ (verified mechanically, 20 words). `limits/handler line 445` names the string-branch store line actually exercised by `"stop":"\n"` — consistent. Gate row in `corpus/lessons/round-28.md` matches (DataG15, 08:34:29Z, same quote/hash).

**Counted verdict.** `c1-e49b4cf7-receipt.json` lists F28-33 in `counted_ids` (`why: []`, live status 200, effective `["\n"]`, base `[]`). Correct per the frozen A1 predicate: `set` = `{"stop": "\n"}` is one key equal to the field; L435 has `new field_json("stop")`; S172 unique to this row; the wrap is not a numeric generic conversion (`conversions()` returns `[]` for string input, count-c1.py:283-301), and the sent value `"\n"` ≠ stored `["\n"]` ≠ base `[]` — so it is genuine field knowledge. Counted stands.

## F28-34 — `samplers` (SKILL.md line 1193, S173, snapshot L453)

**Live re-measure.** `{"prompt": "Once upon a time", "n_predict": 1, "samplers": "kp"}` → HTTP 200, `generation_settings.samplers = ["top_k", "top_p"]`, response sha256 `55e624454bd6fc4c2b331e14cd14d895f9ea84e1523bf4a8d8013b3454dc2219`. Base → 200, `samplers = ["penalties","dry","top_n_sigma","top_k","typ_p","top_p","min_p","xtc","temperature"]` (matches registry `base_effective` exactly). Outcome verified.

**Source verdict.** L453-461 declares `field_json("samplers")`; the handler resolves an array via `common_sampler_types_from_names` and a string via `common_sampler_types_from_chars`. In `common/sampling.cpp:1025` (`common_sampler_types_from_chars`) each char maps via `common_sampler_type_to_chr`; `'k'→top_k`, `'p'→top_p` ⇒ `"kp"→["top_k","top_p"]` — source fully explains the observation. Edge probes confirm the mechanism: `["bogus"]→[]`, `"zz"→[]` (unknowns dropped), `""→[]`, `[]→[]`, `42`→full default chain (handler silently skips non-array/non-string), `["TOP_K","nucleus","top-k"]→["top_k","top_p","top_k"]` (lowercased, aliases accepted, no dedup).

**Prose verdict (meaning cell).**
- `["top_k","top_p"]` resolution — holds, measured.
- "unknown sampler names are silently dropped" — HTTP-true but log-false: `common_sampler_types_from_names`/`from_chars` emit `LOG_WRN` per unmatched name/char; my server.log lines 79/90-91 show `unable to match sampler by name 'bogus'` / `by char 'z'`. Over HTTP the drop produces no error and status stays 200, so "silently" is defensible only from the client side; an operator-side reader will see the warnings. Minor wording defect.
- "(an all-unknown array becomes [])" — holds, measured (`["bogus"]→[]`).
- "a client must read back the array and cannot assume the requested chain applied" — holds; moreover `samplers=[]`/`["bogus"]` still generate text with the empty chain, so the failure is silent at output level too.
- Corrected sentence (if touched): `…, while unknown sampler names are dropped without an HTTP error (a LOG_WRN appears in the server log) — an all-unknown array becomes [] — …`.

**SOURCES/Gate.** `corpus/SOURCES.md` S173: URL `…/server-schema.cpp#L453`, same raw fetch sha `1f9d7b73…4050` ✓; quote = L453+L454 whitespace-joined, verbatim ✓ (22 words); `limits/handler line 460` is the `is_string` branch exercised by `"kp"`. Gate row in the lesson matches.

**Counted verdict.** F28-34 is in `counted_ids` (`why: []`, live 200, `["top_k","top_p"]` vs the 9-element default chain). Correct per the predicate: single-key `set`, L453 declares `new field_json("samplers")`, S173 unique; the char-alphabet resolution is field knowledge (A1 `conversions()` returns `[]` for a string), stored value ≠ sent, ≠ base. Counted stands.

## Residual risk / gaps

- Row-level numbers and meanings reproduce on an independent port and run; both counts are predicate-correct. The only findings are wording: F28-33 "clears it" omits the CLI-defaults fallback (fixture-dependent), and F28-34 "silently" ignores server-side LOG_WRN. Neither invalidates the row or the claim.
- `body_sha256`/`response_sha256` values in the registry/receipt are per-run artifacts (timings embedded); my hashes differ but semantics match. Not a defect.
- No installs/updates performed (existing `curl`, `python3`, `git`, `ss` sufficed).
