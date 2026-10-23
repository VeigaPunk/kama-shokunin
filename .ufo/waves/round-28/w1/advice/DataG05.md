# DataG05 — round-28 C1 DATA seat (port 48205)

Item: 4 assigned request fields (`dynatemp_exponent`, `repeat_last_n`, `repeat_penalty`,
`frequency_penalty`) against pinned llama-server b11755 / stories260K, pinned source
`server-schema.cpp` @704366d76.

## What ran

- Server argv (exactly, under `timeout 1200`, own session):
  `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48205`
  - startup banner captured in `out/DataG05/server-startup.log` (`listening on http://127.0.0.1:48205`)
  - killed with SIGTERM/SIGKILL on its process group after the probes; `ss -ltnp` then reported no
    listener on 48205 (`PORT_CLOSED`), `pgrep` found no llama-server process. Port never overlapped
    the counter range 47600-47619.
- Every POST body is the counter's base `{"prompt": "Once upon a time", "n_predict": 1}` plus exactly
  one field key. Base request repeated 3x: `generation_settings` for the four keys was identical each
  time — `dynatemp_exponent` 1.0, `repeat_last_n` 64, `repeat_penalty` 1.0, `frequency_penalty` 0.0.
- Raw response bodies for every request are in `out/DataG05/resp-*.json`; `probe-log.json` and
  `probe-log-extra.json` hold the per-probe status/sha/effective dumps.

## Source reading (pinned snapshot, sha256 1f9d7b73…4050, also re-fetched by curl now: same sha)

`server-schema.h:50-52`: `T min = std::numeric_limits<T>::lowest(); T max = std::numeric_limits<T>::max();
bool is_hard_limit = false;` — a numeric field without `set_limits`/`set_hard_limits` is bounded only by
the C++ type's full range and clamps silently.

`server-schema.cpp:536-546` (`field_num<T>::eval`): if `!is_hard_limit` ->
`val = std::max(min, std::min(max, data.at(n).get<T>()))` (line 539, silent clamp); else
`T tmp = …get<T>()` (541), `if (tmp < min || tmp > max)` (542) throw
`"Value must be between … <= value <= …, but got …"` (543), wrapped by `handle_with_catch` (518-522)
into `Field '<name>': …` -> HTTP 400.

Consequence for the four fields: only `repeat_last_n` (line 126, `set_hard_limits(0, INT32_MAX)` at
line 127) can reject. The other three declare no limits, so the observable non-trivial behaviour is the
classification boundary of `get<float>()`: a JSON number whose double value is outside the float range
is cast to ±inf and then clamped by line 539 to ±FLT_MAX (= 3.4028234663852886e+38), and that clamped
number is what `generation_settings` echoes. In-range values (including negative ones) are identity.

## Rows (4 counted candidates, 0 no-rows) — canonical cell text the registry/SKILL need

| field | set (canon) | outcome text | line | limits_line |
|---|---|---|---|---|
| dynatemp_exponent | `1e+39` | `200, dynatemp_exponent = 3.4028234663852886e+38` | 123 | null |
| repeat_last_n | `-1` | `reject 400, bounds 0 to 2147483647` | 126 | 127 |
| repeat_penalty | `1e+39` | `200, repeat_penalty = 3.4028234663852886e+38` | 130 | null |
| frequency_penalty | `1e+39` | `200, frequency_penalty = 3.4028234663852886e+38` | 133 | null |

Live evidence (all from this seat's run on 48205; sha = sha256 of the raw body saved in the out dir):

1. `dynatemp_exponent: 1e39` -> 200, `generation_settings.dynatemp_exponent` = 3.4028234663852886e+38
   (base 1.0), sha `0de2b7ad…9a0`. Symmetric check: `-1e39` -> -3.4028234663852886e+38 (sha `0d7cd981…f95`);
   `-1.0` -> -1.0 (identity, sha `a3df165f…fbc`); `3.5e38` -> same FLT_MAX clamp (sha `988ffaed…b46`).
2. `repeat_last_n: -1` -> 400
   `Field 'repeat_last_n': Value must be between 0 <= value <= 2147483647, but got -1`,
   sha `8a193415…7c0` (repeat probe byte-identical). `2147483648` -> 400 same bounds
   `…but got -2147483648` (the number is read through int32 first, wraps, then fails the hard check),
   sha `92955e58…fa7`.
3. `repeat_penalty: 1e39` -> 200, `generation_settings.repeat_penalty` = 3.4028234663852886e+38
   (base 1.0), sha `0f0dae56…e79`.
4. `frequency_penalty: 1e39` -> 200, `generation_settings.frequency_penalty` = 3.4028234663852886e+38
   (base 0.0), sha `7c6c63e4…8d1`. Negative check: `-1e39` -> -3.4028234663852886e+38 (sha `ee475061…8b2`);
   `-3.0` -> -3.0 identity (sha `47a8a7c8…e49`); `0.0` -> 0.0 identity (sha `cbd4e078…0e7`).

`rows.json` holds these four rows in the seat schema (field/set/outcome/line/limits_line/meaning/source/live);
`no_rows` is empty because every assigned field produced a countable outcome. Every row was re-validated
against its saved raw body: status, message/effective value, effective != sent, effective != base default,
and the source quote is a verbatim substring of the cited snapshot lines.

## Extra live evidence that is NOT a row (do not turn these into rows)

- `repeat_penalty: 0.0` and `repeat_penalty: -1e39` both return 400
  `Failed to initialize samplers: penalty_repeat must be finite and greater than 0` — byte-identical body,
  sha `7a14b892…318`. It carries no `Value must be between …` bounds, so the counter's reject regex does
  not match it; it is a post-schema sampler-init guard, not a request-field bound. The countable row for
  the field is therefore the saturation row above.
- In-range values for all four fields are identity in `generation_settings` (no clamping, no rounding
  beyond float32), so an effective row had to use a value outside the float range.

## Risks / notes for the L1 and falsify seats

- Three rows share one mechanism (float-range saturation, schema.h:50-51 + schema.cpp:539). Each is live-true
  and cites a distinct field/declaring line, so the counter's duplicate-field/line and echo checks pass, but
  a falsify seat may call the mechanism repetitive; if that matters, keep all three only with the mechanism
  named in the section prose, and do not add a second row per field.
- Each row needs its own new SOURCES S### for `server-schema.cpp` @704366d with the exact line
  (`line 123`, `line 126`, `line 130`, `line 133`); reusing one S### across rows is refused by
  `source-misuse`.
- SKILL value cells must contain `1e+39` / `-1` exactly as `json.dumps` renders them, and outcome cells the
  canonical text above; the `row` token (S###) must appear in the source cell.
- The `response_sha256` values are of my raw 200 bodies, which embed generated content and timings; a counter
  re-run will hash different bytes. Only the status/message/effective values are reproducible, and those are
  stable across the three base runs and repeated probes.
- `repeat_last_n` default is 64, not 0; do not claim "0 disables" as the omitted default in prose.

## Files written

- `out/DataG05/rows.json` (4 rows, 0 no_rows)
- `out/DataG05/resp-*.json` (17 raw bodies), `probe-log.json`, `probe-log-extra.json`, `server-startup.log`
- this advice file. No lane-tracked file touched, no git/jj write, no package install, no subagent.

Scratch (not evidence): `/fast/scratch/hyaku/kama-r28/w1/DataG05/{probe.py,server.log}`. Port 48205 closed.
