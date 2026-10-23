# DataG15 — round-28 C1 data seat (fields: logit_bias, ignore_eos, stop, samplers)

Seat: KamaR28.DataG15-2, leaf, port **48215**. Lane repo read-only; nothing tracked edited.
All evidence below is from my own run of the pinned binary; no row value is inferred.

## What was run

- argv (exactly the bound form, under `timeout 240`, its own session, then SIGTERM to the process group):
  `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48215`
- process identity at run: exe `/home/vgpnk/.local/opt/llama-b11755/llama-server`, sha256
  `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`; model sha256
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`; `/props` model_path was the pinned gguf.
- Requests: the counter's base body `{"prompt": "Once upon a time", "n_predict": 1}`, then the same body with
  exactly one field added (one request per value; no loops, 17 bodies total, each < 2 KB).
- Port 48215 confirmed closed after the run (`ss -ltnp`: no listener; no `llama-server.*48215` process).
- Source pin re-fetched now: `curl` of
  `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp`
  -> sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`, equal to the lane snapshot
  `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`. Accessed 2026-10-23T08:34:29Z.
- Installs/updates: none (no new tool needed; pacman not touched).

## Source reading (pinned 704366d snapshot)

All four fields are `field_json`/`field_bool` with a **handler only**: none of them calls `set_limits` (silent
clamp) or `set_hard_limits` (HTTP 400). Therefore this seat can produce **no reject rows**; every out-of-shape
value is normalized or silently dropped and answered 200. `limits_line` below is the handler-body line that
stores/transforms the value (the literal `set_handler` opener lines are 384/425/437/455 and carry no semantics).

| field | declaring line | handler store/transform line | behaviour read from source |
|---|---|---|---|
| logit_bias | 382 | 414 (object branch 407-419; array branch 394-406) | accepts array of `[token,bias]` or object token->bias; `false` -> `-INFINITY`; tokens outside `[0,n_vocab)` dropped; string keys tokenized |
| ignore_eos | 423 | 429-431 (insert) | stores the bool, then appends the precomputed `logit_bias_eog` entries to `params.sampling.logit_bias` |
| stop | 435 | 445 (string branch; array branch 440-443) | string -> one antiprompt; array keeps non-empty strings; empty result falls back to CLI defaults |
| samplers | 453 | 460 (string branch; array branch 457-458) | string chars -> sampler types; array names -> sampler types; unknown names dropped |

`generation_settings` keys come from `server-task.cpp` `task_params::to_json` (full, non-metrics branch):
`logit_bias` via `format_logit_bias` -> array of `{"bias","token"}` objects; `ignore_eos` -> bool;
`stop` -> `antiprompt`; `samplers` -> array of sampler-type strings.

## Countable rows (4) — all `effective`

Base (field omitted) values, one run: `logit_bias []`, `ignore_eos false`, `stop []`,
`samplers ["penalties","dry","top_n_sigma","top_k","typ_p","top_p","min_p","xtc","temperature"]`.

| field | set | generation_settings key | live value | line | limits_line |
|---|---|---|---|---|---|
| logit_bias | `{"12": 5}` | `logit_bias` | `[{"bias": 5.0, "token": 12}]` | 382 | 414 |
| ignore_eos | `true` | `logit_bias` | `[{"bias": null, "token": 2}]` | 423 | 429 |
| stop | `"\n"` | `stop` | `["\n"]` | 435 | 445 |
| samplers | `"kp"` | `samplers` | `["top_k", "top_p"]` | 453 | 460 |

Each value differs from the value sent **and** from the omitted-field value of the same key (checked in code
against `base.json`), so counter clause (e) holds for all four.

Canonical cells for the registry/SKILL (counter `outcome_text` rendering, copy verbatim):

- logit_bias: value cell `{"12": 5}`; outcome cell `200, logit_bias = [{"bias": 5.0, "token": 12}]`
- ignore_eos: value cell `true`; outcome cell `200, logit_bias = [{"bias": null, "token": 2}]`
- stop: value cell `"\n"`; outcome cell `200, stop = ["\n"]`
- samplers: value cell `"kp"`; outcome cell `200, samplers = ["top_k", "top_p"]`

Evidence bodies (raw bytes, sha256 recorded in `rows.json`):
`logit_bias_object.json`, `ignore_eos_true.json`, `stop_string.json`, `samplers_string.json`, plus `base.json`.

## Non-countable variants measured (do NOT register as rows)

| variant | live | why no row |
|---|---|---|
| `ignore_eos: false` | 200, `ignore_eos false`, `logit_bias []` | identical to base (identity) |
| `stop: ["\n"]` | 200, `stop ["\n"]` | effective equals sent value (identity) |
| `samplers: ["top_k","top_p"]` | 200, `samplers ["top_k","top_p"]` | effective equals sent value (identity) |
| `logit_bias: [[12,5]]` | 200, `[{"bias": 5.0, "token": 12}]` | array-of-pairs form is accepted as sent shape; transformation is only bias/object normalization, and one row per field is allowed |
| `logit_bias: "12:5"` | 200, `logit_bias []` | wrong type silently ignored -> equals base default |
| `stop: ""` | 200, `stop [""]` | differs from default but the cleaner row is the string->array wrap; also documents that an empty string is kept as a literal stop |
| `stop: []` / `stop: 7` | 200, `stop []` | equals base default (empty array / wrong type falls back to CLI defaults) |
| `samplers: ["bogus"]` / `"zz"` | 200, `samplers []` | all-unknown names dropped to empty chain; differs from sent and default, but the `"kp"` row is the canonical char-form mapping (mention the drop in that row's meaning) |
| `samplers: 5` | 200, default sampler list | wrong type silently ignored -> equals base default |
| `logit_bias: {"hello": false}` | 200, `[{"bias": null, "token": 281}, ...]` | string key tokenizes to several tokens; `bias` is null because `-INFINITY` serializes as JSON null — a viable alternate logit_bias row, but the numeric object row is simpler and unambiguous |

## Integration notes / risks

1. **ignore_eos row key is `logit_bias`, not the field name.** The measured effect is a cross-field coupling:
   `ignore_eos: true` leaves `generation_settings.ignore_eos` at `true` (identity) and injects EOG token 2 with
   `null` (= `-INFINITY`, `parse_bias` line 391 and the EOG bias vector) into `generation_settings.logit_bias`.
   The registry row still satisfies C1: field `ignore_eos`, one-key `set`, and clause (e) differs from both the
   sent `true` and the omitted-field `[]`. Falsify review should judge the meaning sentence, which states both
   the identity and the injection.
2. **`bias: null` must stay `null`.** JSON has no infinity; do not "fix" it to `-Infinity` or a number, or the
   counter's exact comparison fails.
3. **limits_line is the handler storage line**, because these fields have no `set_*_limits` call anywhere;
   citing the `set_handler` opener (384/425/437/455) would satisfy the letter but carry no semantics. Quotes
   keep every fragment byte-verbatim against the pinned snapshot; each quote splits into <= 3 fragments
   separated by ` ... ` and is <= 25 whitespace tokens excluding the ellipses.
4. **No reject rows exist for these four fields** under b11755: malformed/wrong-type values are silently
   ignored, not 400. A future row must not invent bounds for them.
5. Counter reproduction was not run from this seat (its server uses ports 47600-47619, which my bounds forbid
   me to start). I replayed its predicate offline instead: status 200, parsed `generation_settings[key]`
   equals the row value, differs from sent and from `base.json`; hashes of every cited body are recorded.
6. The two sampler/stop rows are request-determined, and the EOG token id is vocab-determined by the pinned
   model, so the counter's own fresh-server replay should reproduce them exactly.

## Files

- `rows.json` — `{"rows": [4 effective rows], "no_rows": []}`.
- 17 raw response bodies (`base.json`, `*.json`) cited above.
- `/fast/scratch/hyaku/kama-r28/w1/DataG15/probe.py` and `build_rows.py` (scratch, outside the lane), plus
  `probe-results.json` and `schema-live.cpp` (fetched pin).
