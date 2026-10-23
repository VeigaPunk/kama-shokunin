# DataG02 — round-28 C1 data seat (4 fields, port 48202)

Assignment: `n_discard` (server-schema.cpp:58), `n_cmpl` (:62), `t_max_predict_ms` (:74), `response_fields` (:78).
Outcome: **3 countable reject rows + 1 no-row**. All live evidence from my own pinned server run on 127.0.0.1:48202
(argv exactly `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48202`,
under `timeout`, stopped by process-group SIGTERM; `ss -ltn` shows no listener on 48202 afterwards).

## Source facts (pinned snapshot, my own curl fetch)

- Snapshot `server-schema.cpp` sha256 `1f9d7b73…7904050`; my curl of
  `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp`
  returned the same sha256 at 2026-10-23T08:33:00Z.
- `field_num::eval` (server-schema.cpp:532-550): `set_hard_limits` throws
  `Value must be between <min> <= value <= <max>, but got <tmp>` wrapped as `Field '<name>': …`;
  `set_limits` alone silently clamps (`std::max(min, std::min(max, …))`).
- generation_settings comes from `task_params::to_json` (server-task.cpp:25-140): it reports
  `n_discard` (and `n_predict`/`max_tokens`) but has **no** `n_cmpl`, `t_max_predict_ms` or
  `response_fields` key.
- Types from server-task.h @704366d (fetched for reference only): `int32_t n_discard = 0`,
  `int32_t n_cmpl = 1`, `int64_t t_max_predict_ms = -1`, `std::vector<std::string> response_fields`.

## Rows (in `rows.json`)

| field | line / limits_line | set | live |
|---|---|---|---|
| n_discard | 58 / 59 | `-1` | 400 `Field 'n_discard': Value must be between 0 <= value <= 2147483647, but got -1` |
| n_cmpl | 62 / 63 | `0` | 400 `Field 'n_cmpl': Value must be between 1 <= value <= 4, but got 0` |
| t_max_predict_ms | 74 / 75 | `-2` | 400 `Field 't_max_predict_ms': Value must be between -1 <= value <= 9223372036854775807, but got -2` |

Bounds equal the observed message bounds exactly. Raw bodies are the cited `live_*.json` files
(sha256 in each row's `live.response_sha256`). Base request
`{"prompt":"Once upon a time","n_predict":1}` → 200, `generation_settings.n_discard = 0`,
`generation_settings.n_predict = 1` (`live_00_base.json`, sha256 `2eaabba6…ed7bf3c`).

## No-row: `response_fields` (:78, handler :80-81)

`field_json` with only a handler; it writes `ctx.params.response_fields`, has no limits and no
generation_settings key, so it can satisfy neither countable kind. Live proof:
`{"prompt":"Once upon a time","n_predict":1,"response_fields":["generation_settings/n_predict"]}`
→ 200 `{"generation_settings/n_predict":1}` (literal root key; sha256 `a9d12ea2…4c6367b8`).
`["content"]` → 200 `{"content":","}`. A string value `"content"` → 200 with the default projection
and server log `Wrong type supplied for parameter 'response_fields', using default value: … type must be array, but is string`.
Note for reviewers: the field's own description says slashes unnest (`generation_settings/n_predict`
"moves n_predict to the root"), but on `/completion` the literal slash key was returned; that mismatch
is an observation, not a row (no generation_settings outcome).

## Secondary live observations (not rows)

- `n_discard: 5` → 200, `generation_settings.n_discard = 5`: identity, so not an effective row (echo rule).
- `n_discard: 2147483648` → 400 but the message prints `but got -2147483648` (nlohmann int32 conversion
  wrap), so the clean below-min probe `-1` is the row value.
- `t_max_predict_ms: 1000` → 200, no such key under generation_settings (only `max_tokens`), so no effective row.
- `n_cmpl: 2` → 200 with a JSON **array** of two completion objects (3345 bytes); `n_cmpl: 5` → 400 with
  the same `1 <= value <= 4` bounds.
- `n_cmpl`'s upper hard bound is `params_base.n_parallel`, observed as 4 (server log `n_slots = 4`) for the
  default launch argv the counter uses; a server started with a different `--parallel` would print different bounds.
  The row records the bounds this launch (and therefore the counter's own replay) produces.

## Files (under `.ufo/waves/round-28/w1/out/DataG02/`)

- `rows.json` — 3 rows + 1 no_row (validated: parses; every `live.message` re-read from its cited body;
  message bounds equal `outcome.bounds`).
- `live_00_base.json`, `live_01_n_discard=-1.json`, `live_02_n_discard=5.json`,
  `live_03_n_discard=2147483648.json`, `live_04_n_cmpl=0.json`, `live_05_n_cmpl=2.json`,
  `live_06_n_cmpl=5.json`, `live_07_t_max_predict_ms=-2.json`, `live_08_t_max_predict_ms=1000.json`,
  `live_09_response_fields=[content].json`, `live_10_response_fields=[generation_settings_n_predict].json`,
  `live_11_response_fields=content.json` — raw response bodies.
- `probe_results.json` — compact matrix (field, set, status, sha256, message, gs extracts).

## Risks / notes for the L1

- Registry mapping: rows use distinct declaring lines (58/62/74), so the counter's duplicate-line and
  duplicate-field clauses are not tripped; each row needs one new SOURCES S### citing
  `tools/server/server-schema.cpp`, commit 704366d and its line, plus the SKILL row cells.
- `n_cmpl` bounds `[1, 4]` are dynamic (`n_parallel`); they reproduce under the counter's own launch argv,
  but the meaning text should not promise 4 on other deployments.
- No installs or updates were made (nothing needed); no git/jj writes; scratch probe lives under
  `/fast/scratch/hyaku/kama-r28/w1/DataG02/`.
