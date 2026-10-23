# DataG04 — round 28, wave 1, C1 data seat (four schema fields)

Item: DataG04, port 48204. Lane repo READ-ONLY; no lane files touched.
Output dir: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-28/w1/out/DataG04/`
(rows.json; resp-base.json, resp-xtc_probability.json, resp-typical_p.json,
resp-temperature.json, resp-dynatemp_range.json). Scratch: `/fast/scratch/hyaku/kama-r28/w1/DataG04/`
(server.log).

## Run

- argv (exactly): `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48204`, under `timeout 420`, started with `setsid`.
- Binary sha256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`, model sha256
  `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` — both equal the counter's pins.
- Source snapshot sha256 `1f9d7b73…4050`; my own curl of the pinned raw URL today produced the same hash
  (`/fast/scratch/hyaku/kama-r28/w1/DataG04/server-schema-704366d.cpp`), accessed 2026-10-23T08:33:00Z.
- Base request `{"prompt": "Once upon a time", "n_predict": 1}` -> 200; generation_settings defaults:
  temperature 0.800000011920929, dynatemp_range 0.0, xtc_probability 0.0, typical_p 1.0
  (resp-base.json, sha256 8d4febb3…a840).
- Server process group (pgid 2235526) SIGTERM'd after the probes; `ss -ltnp` shows port 48204 closed and
  the process group is gone.

## Result: 2 countable rows, 2 no-rows

| field | decl line | limits line | sent | outcome |
|---|---|---|---|---|
| xtc_probability | 104 | 105 `set_limits(0.0f, 1.0f)` | 5.0 | 200, generation_settings.xtc_probability = 1.0 (soft clamp) |
| temperature | 116 | 117 `set_limits(0.0f, +inf)` | -1.0 | 200, generation_settings.temperature = 0.0 (soft clamp) |
| typical_p | 112 | null (only set_limits is commented out at 113) | 2.0 | 200, typical_p = 2.0 == sent: identity |
| dynatemp_range | 120 | null (no limits, no handler) | -2.5 | 200, dynatemp_range = -2.5 == sent: identity |

No field among these four uses `set_hard_limits`, so no reject row exists here: schema.cpp's
`field_num<T>::eval` (lines 531-547) clamps when `!is_hard_limit`, and only throws
`Value must be between …` for hard limits. `handle_with_catch` wraps any throw as `Field '<name>': …`.

## Integration notes for the L1 (measured, not applied)

- SKILL value cell must contain `canon(set[field])`: `5.0` for xtc_probability, `-1.0` for temperature.
- Counter `outcome_text` renders: `200, xtc_probability = 1.0` and `200, temperature = 0.0`.
- Registry entry `source` must be `{"row": "S###", "file": "server-schema.cpp", "line": <n>}`; each S###
  must be new (absent at base 4179301f) and its SOURCES.md row must name `server-schema.cpp`, `L<line>`,
  and commit `704366d`. One S### per row; fields and lines must be unique across the registry.
- Live hashes for the two rows: xtc_probability 73649880…7efc, temperature 6e7ed205…d079; no-row hashes
  typical_p 3de5e581…4b, dynatemp_range 058740c5…c93 (full 64-hex values in rows.json).
- rows.json `source.quote` concatenates the declaring line and the limits line verbatim (5 words each).

## Risks / caveats

- The two no-rows are honest identities; do not convert them into clamp rows — sending values inside a
  non-existent limit cannot produce an effective outcome (live evidence in rows.json).
- The clamp rows are of the kind the `echo` control targets: both effective values (1.0, 0.0) differ from
  the sent value and from the base default (0.0, 0.8), so they survive that control per the counter's
  own rule (e) checked on its own base request.
- `typical_p`'s commented-out `set_limits` at line 113 is dead code in the pin; if the L1 cites it, cite
  it only as a null/limits commentary, never as an active limit (it would be a source-misuse signal).
- Tool installs: none. No pacman, no uv, no downloads beyond the single curl of the pinned source.

## Files returned

- `.ufo/waves/round-28/w1/out/DataG04/rows.json` (2 rows, 2 no_rows)
- `.ufo/waves/round-28/w1/out/DataG04/resp-{base,xtc_probability,typical_p,temperature,dynatemp_range}.json`
- this report
