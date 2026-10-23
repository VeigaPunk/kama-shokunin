# DataG07 — round 28 / wave 1, C1 data seat (ports 48207)

Lane: /home/vgpnk/Projects/shokunin/kama-shokunin (read-only; no tracked file touched)
Outputs: `.ufo/waves/round-28/w1/out/DataG07/` (rows.json + raw bodies), this advice file.

## What I ran
Pinned server, my assigned port only, exact argv:
`~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48207` (under `timeout`, TERM'd; `ss -ltnp` shows 48207 closed, no leftover process).

Every request: `POST /completion` with `{"prompt":"Once upon a time","n_predict":1}` plus exactly one field, matching the counter's request construction. Base (field omitted) ran first, body `base.body.json`, sha256 `93f0d85bfaa8d3fae30d86b7b095d0d06050af8987a11e8d642b647583068745`; its `generation_settings` defaults: `dry_penalty_last_n=64`, `mirostat=0`, `mirostat_tau=5.0`, `mirostat_eta=0.10000000149011612`.

## Live results (raw bodies kept in the out dir)
| field | sent | status | observed |
|---|---|---|---|
| dry_penalty_last_n | -1 | 400 | `Field 'dry_penalty_last_n': Value must be between 0 <= value <= 2147483647, but got -1` (`drypen_neg.body.json`) |
| mirostat | 5 | 200 | `generation_settings.mirostat = 2` (default 0) (`mirostat_5.body.json`) |
| mirostat | -3 | 200 | `generation_settings.mirostat = 0` — confirms two-sided clamp (`mirostat_neg3.body.json`) |
| mirostat_tau | 0.1 | 200 | `0.10000000149011612` — float32 rounding, treated as identity/echo, NOT a row (`mirostat_tau_0p1.body.json`) |
| mirostat_tau | 1e39 | 200 | `3.4028234663852886e+38` (FLT_MAX), default 5.0 (`mirostat_tau_1e39.body.json`) |
| mirostat_eta | 0.5 | 200 | `0.5` — identity, NOT a row (`mirostat_eta_0p5.body.json`) |
| mirostat_eta | 1e39 | 200 | `3.4028234663852886e+38` (FLT_MAX), default 0.10000000149 (`mirostat_eta_1e39.body.json`) |

## Mechanism (pinned source, sha256 1f9d7b73…4050, my own fetch at 704366d matches the pin)
- `server-schema.h:47-64`: `field_num` defaults `min=lowest`, `max=max`; `set_limits` (soft, inclusive) and `set_hard_limits` (soft + `is_hard_limit=true`).
- `server-schema.cpp:532-551`: null/absent leaves the default; `!is_hard_limit` does `val = max(min, min(max, get<T>()))` (silent clamp); hard limit throws `Value must be between <min> <= value <= <max>, but got <tmp>`, wrapped by `handle_with_catch` into `Field '<name>': …` (HTTP 400).
- Declaring/limit lines: 153/154 (dry_penalty_last_n, hard), 157/158 (mirostat, soft 0..2), 161 (mirostat_tau, no limits), 164 (mirostat_eta, no limits).
- tau/eta have no `set_limits`, so their only bounds are the implicit `numeric_limits<float>` defaults in the header; an out-of-float-range value clamps to ±FLT_MAX, which is what the live rows record. In-range values are plain identity.

## Row drafts (rows.json)
4 rows, 0 no_rows. Each `live.response_sha256` was re-verified against the saved body with hashlib (a first transcription of the reject hash was 62 hex chars; corrected and re-checked).

Canonical cell text for integration (`json.dumps` form used by the counter):
- value cells: `-1`, `5`, `1e+39`, `1e+39`
- outcome cells: `reject 400, bounds 0 to 2147483647`, `200, mirostat = 2`, `200, mirostat_tau = 3.4028234663852886e+38`, `200, mirostat_eta = 3.4028234663852886e+38`

Registry `source` still needs the S### `row`, `file: "tools/server/server-schema.cpp"`, `line` 153/157/161/164. The SOURCES row must be new this round and contain the line marker the counter greps (`#L153`/`L153`/`line 153`); suggest `…/server-schema.cpp#L153-L154 @704366d`, `#L157-L158`, `#L161`, `#L164`.

## Risks / decision for the L1
1. **tau and eta rows rest on implicit float-range clamping**, not a declared `set_limits`. They satisfy the counter's literal predicate (200, key equals, differs from sent and from default) and are reproducible on the counter's own port, but a falsify seat may read them as probe-overflow rather than a schema decision. If the L1 judges implicit `numeric_limits<float>` bounds out of scope, demote both to no_rows with reason "in-range values are identity; only implicit float-range clamp (1e39 -> FLT_MAX) observed; no declared limits".
2. `mirostat_tau: 0.1` returns `0.10000000149011612`: a float32 echo the counter's 1e-6 tolerance calls identity — do not use it as an effective row.
3. Reject row is unambiguous: 400, field named, bounds exactly `0` and `2147483647`.

## Housekeeping
No installs/updates (curl, jq, ss, sha256sum, python3 already present). No git/jj write, no sibling files touched, no llama-server left running. Scratch under `/fast/scratch/hyaku/kama-r28/w1/DataG07/`.
