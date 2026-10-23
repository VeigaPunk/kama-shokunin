# DataG14 — reasoning_budget_* request fields (C1, DATA seat)

Port 48214 · llama-server b11755 (commit 704366d76, `--version` confirmed) · model stories260K.gguf ·
snapshot `sources/llama.cpp-704366d/server-schema.cpp` sha256 `1f9d7b73…0050`, my own curl of the
704366d raw URL at 2026-10-23T08:33:42Z gave the same sha256.

## Result: 1 countable row, 3 measured no-rows

`rows.json` → `.ufo/waves/round-28/w1/out/DataG14/rows.json` (`{"rows":[…1…],"no_rows":[…3…]}`),
raw bodies under `out/DataG14/raw/`, server log `out/DataG14/server.log`.

| field | line | outcome |
|---|---|---|
| `reasoning_budget_tokens` | 335 (limits 336) | **reject 400**, bounds **-1 to 2147483647** |
| `reasoning_budget_start_tag` | 339 (handler 341–344) | no row |
| `reasoning_budget_end_tags` | 346 (handler 349–365) | no row |
| `reasoning_budget_message` | 367 (handler 369–380) | no row |

### Row (counter-ready)
- `set`: `{"reasoning_budget_tokens": -2}`; value cell canonical JSON `-2`
- canonical outcome text: `reject 400, bounds -1 to 2147483647`
- live: status 400, message exactly
  `Field 'reasoning_budget_tokens': Value must be between -1 <= value <= 2147483647, but got -2`
  (`raw/tokens_neg2.json`, sha256 `9c6ad502…6b5`)
- semantics: `field_num` + `set_hard_limits(-1, INT32_MAX)`; `server-schema.cpp:537-546` throws
  `std::invalid_argument` only when `is_hard_limit` and out of range, and `:521-522` wraps it as
  `Field '%s': %s`. Inclusive bounds, so -1 and 0 are accepted (both 200, `raw/tokens_minus1.json`,
  `raw/tokens_0.json`).
- suggested meaning (30 words): "A reasoning_budget_tokens value below -1 is rejected with HTTP 400 by
  the hard limit, so clients must send -1 to disable the budget and never rely on a silent clamp."

### Why the other three have no row (structural, not a failed probe)
`task_params::to_json` in the pinned `server-task.cpp` (lines 27-145, full and `only_metrics` paths)
serialises **no** `reasoning_budget*` key; the only reasoning keys are `reasoning_format` and
`reasoning_in_content`. Live confirmation: all 9 successful probes return `generation_settings` with
49 keys, **identical keyset and identical values to the base request** — including `start_tag`,
`end_tags`, `end_tags_alias`, `message_alone`, `message_with_end`, `tokens_minus1`, `tokens_0`. Since
the counted `effective` kind requires `generation_settings[<key>]`, no effective row can exist for any
of these fields at this commit. None of the three carries `set_limits`/`set_hard_limits`, so no bounds
reject can exist either.

Only extra 400 seen: `reasoning_budget_start_tag: 5` →
`Field 'reasoning_budget_start_tag': [json.exception.type_error.302] type must be string, but is number`
(`raw/start_tag_num.json`, sha256 `fdb4838d…823`). That is a JSON type error, **not** the counted
`Value must be between` form; do not draft a row from it.

## Evidence retained
- `out/DataG14/raw/` 11 response bodies (base, base2, tokens_neg2, tokens_minus1, tokens_0,
  start_tag, end_tags, end_tags_alias, message_alone, message_with_end, start_tag_num), sha256 printed
  per file in `rows.json`; each cited sha was re-verified against the file bytes.
- Base request `{"prompt": "Once upon a time", "n_predict": 1}` → 200, `raw/base.json` sha256
  `71563bfa…5e4`; key-for-key equal `generation_settings` in `raw/base2.json` (`ca3c2bd6…9f9`).
- server log `out/DataG14/server.log`; `ss -ltnp` shows port 48214 closed after the run (pgid killed
  with TERM then KILL). Run wrapped in `timeout 300`, server under `timeout 200`.
- Validation pass re-read the snapshot: quote verbatim, 5 words; meaning 30 words; bounds parsed from
  the live message equal `[-1, 2147483647]`; sent -2 equals the message's "got" value.

## Risks / notes for the L1
- This seat contributes **1 row**, not 4: the reasoning-budget family is invisible in
  `generation_settings` at 704366d, so any row drafted for the other three would be fabricated. Pin
  the no-row prose in the section only if the section format has room for observed no-rows; the
  counter counts only `rows`.
- `reasoning_budget_end_tags` also accepts the alias `reasoning_budget_end_tag` (line 347) — alias
  rows are voided by the duplicate-field control, so cite only line 346 if ever revisited.
- `reasoning_budget_tokens` is the only hard-limited field in this family; a positive value is
  accepted silently (no observable trace in the response), so do not claim it is clamped.
- Install record: none (no tool installed or updated).
- Blockers: none.
