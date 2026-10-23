# DataG06 -- C1 DATA seat, wave 1 (port 48206)

Claim: C1 (measured, depth). Assigned fields: `presence_penalty` (line 136), `dry_multiplier` (139),
`dry_base` (142), `dry_allowed_length` (149) from `tools/server/server-schema.cpp` @ `704366d76`.
Result: **1 countable row** (`dry_allowed_length`, reject) and **3 no-row entries**; rows.json has
`{"rows": [1], "no_rows": [3]}`.

## Method

- Pinned snapshot `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp`,
  sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`.
- Own `curl` of the same raw GitHub URL at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` on
  2026-10-23T08:33:00Z returned HTTP 200 and the same sha256; kept as
  `out/DataG06/server-schema-704366d.cpp`.
- Server: exactly `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf
  --host 127.0.0.1 --port 48206`, wrapped in `timeout 180`, readiness via `GET /health` = 200,
  process group TERM then KILL; `ss -ltnp` confirmed port 48206 closed after the run.
- Requests: counter base body `{"prompt": "Once upon a time", "n_predict": 1}` plus one key per probe.
  All bodies were POSTed to `/completion`; status and raw body files kept in the out dir.

## Live results (own run, port 48206)

| field | line | limits/handler in schema | probe | status | generation_settings | verdict |
|---|---|---|---|---|---|---|
| presence_penalty | 136 | none (`set_desc` only) | 1000000000.0 | 200 | presence_penalty = 1000000000.0 (base 0.0) | identity -> no row |
| dry_multiplier | 139 | none (`set_desc` only) | -7.5 | 200 | dry_multiplier = -7.5 (base 0.0) | identity -> no row |
| dry_base | 142 | handler, v < 1.0 -> `params_base.sampling.dry_base` (142-146) | 0.5 then 2.5 | 200, 200 | dry_base = 1.75 (base 1.75); 2.5 -> 2.5 | substituted value equals default -> no row |
| dry_allowed_length | 149 | `set_hard_limits(0, INT32_MAX)` (line 150) | -1 | 400 | n/a | **countable reject, bounds [0, 2147483647]** |

Reject message observed verbatim:

    Field 'dry_allowed_length': Value must be between 0 <= value <= 2147483647, but got -1

This matches the counter `REJECT_RE`, and `set_hard_limits` is the reject path (line 543 of the
snapshot: `Value must be between ...` inside `field_num::eval`), whereas `set_limits` clamps silently.

## Row draft (for integration)

- id/field `dry_allowed_length`, line 149, limits_line 150, `set {"dry_allowed_length": -1}`,
  outcome `{"kind": "reject", "bounds": [0, 2147483647]}`.
- Meaning text: "llama-server rejects a negative dry_allowed_length with HTTP 400 and the exact
  integer bounds, so clients must clamp the DRY window length to 0..2147483647 before sending."
- Integration caution: the counter voids duplicate rows sharing a field or a cited line; line 150 is
  the limits line for this same field, so no second row may cite it. Source quote spans 149-150.

## No-row evidence

- `presence_penalty`: no limits, no handler; extreme value is echoed verbatim, so no transformed or
  rejected outcome exists at b11755.
- `dry_multiplier`: same; negative value echoed verbatim.
- `dry_base`: the handler replaces values below 1.0 with `params_base.sampling.dry_base`, observed as
  the omitted-field default 1.75; acceptance voids effective outcomes equal to the default, and 2.5
  is identity. No countable outcome.

## Evidence files (out dir `.../w1/out/DataG06/`)

`rows.json`, `req-{base,pp,dm,db-low,db-hi,dal}.json`, `resp-{base,pp,dm,db-low,db-hi,dal}.json`,
`server.log`, `server-schema-704366d.cpp`. Response sha256 (also in rows.json):
base `1c59828d...906`, pp `dc42c4aa...621`, dm `ae179600...04ee`, db-low `735b9636...b2c3`,
db-hi `932a81b6...7611`, dal `7bfa1668...bb97`.

## Risks / blockers

- `dry_base` and the two identity fields cannot contribute rows to C1; only one of the four assigned
  fields yields a countable outcome. The reject row replays deterministically (hard limits are
  source constants), but the counter will re-verify it on its own ports 47600-47619.
- Values 1000000000.0 and -7.5 are exactly representable in float32, so no rounding could fake an
  effective outcome; the identity readings are not serialization artifacts.
- No tools installed; no tracked lane files touched; no git/jj writes. Scratch work in
  `/fast/scratch/hyaku/kama-r28/w1/DataG06/` only.
