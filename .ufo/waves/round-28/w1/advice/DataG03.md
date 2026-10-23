# DataG03 — round 28 wave 1, C1 data seat (four sampling fields, port 48203)

Seat: `KamaR28.DataG03-2`. Claim served: C1 (measured, depth). Assigned target: `top_k` (server-schema.cpp:89), `top_p` (:93), `min_p` (:97), `top_n_sigma` (:101) of the pinned 704366d snapshot.
Verdict: **4 row drafts (3 A1-clean), 1 no-row note** — one `effective` row per field, all measured on my own server on port 48203. `min_p` was re-probed after counter amendment A1 (revision: sent `-1.5`, not `-0.25`); `top_n_sigma` is expected to be refused under A1 and is left as-is per the L1.

## Row drafts (deliverable: `w1/out/DataG03/rows.json`)

| field | set | outcome | declaring line | limits line |
|---|---|---|---|---|
| top_k | `{"top_k": -5}` | `effective top_k = 0` (base 40) | 89 | 90 (`set_limits(0, INT32_MAX)`) |
| top_p | `{"top_p": 2.5}` | `effective top_p = 1.0` (base 0.949999988079071) | 93 | 94 (`set_limits(0.0f, 1.0f)`) |
| min_p | `{"min_p": -1.5}` | `effective min_p = 0.0` (base 0.05000000074505806) | 97 | 98 (`set_limits(0.0f, 1.0f)`) |
| top_n_sigma | `{"top_n_sigma": 3.5e+38}` | `effective top_n_sigma = 3.4028234663852886e+38` (base -1.0) | 101 | null (no `set_limits`, no handler) |

Canonical cell texts the counter will require verbatim (computed with its `canon()`/`outcome_text()`):

| field | value cell | outcome cell |
|---|---|---|
| top_k | `-5` | `200, top_k = 0` |
| top_p | `2.5` | `200, top_p = 1.0` |
| min_p | `-1.5` | `200, min_p = 0.0` |
| top_n_sigma | `3.5e+38` | `200, top_n_sigma = 3.4028234663852886e+38` |

Integration needs, per row: a distinct `F28-##` id, its own new `S###` row in `corpus/SOURCES.md` naming `server-schema.cpp`, `L<line>` (89/93/97/101) and `704366d` (counter refuses one S### cited by two rows), and the exact six-column SKILL table. One row per field and per line — do not add a second row for any of these four.

## A1 status (counter amendment)

A1 refuses an `effective` value equal to a generic conversion of the value sent (truncation toward zero, float32 rounding/saturation, 2^32/2^64 wrap, truthiness). Checked numerically against each retained row:

| field | sent | effective | trunc | float32 | wrap | truthiness | A1 collision |
|---|---|---|---|---|---|---|---|
| top_k | -5 | 0 | -5 | -5 | -5 | 1 | none |
| top_p | 2.5 | 1.0 | 2 | 2.5 | — | 1 | **truthiness, if that conversion is numeric 1** |
| min_p | -1.5 | 0.0 | -1 | -1.5 | — | 1 | none |
| top_n_sigma | 3.5e+38 | 3.4028234663852886e+38 | — | FLT_MAX saturation | — | 1 | refused by A1 (L1 ruled: leave as is) |

`min_p` `-0.25 -> 0.0` was superseded because `trunc(-0.25) = 0`; the old probe is kept in `rows.json` as the `min_p` no-row note (`sha fb794db1…`, body `min_p.json`).

If A1 flags `top_p` (1.0 vs truthiness 1.0), a measured alternative is already on disk: `{"top_p": -1.0}` -> 200, `top_p = 0.0` (base 0.949999988079071), raw body `probe2-02-top_p.json`, sha256 `f8aa31fbf3ed22604081e6eea88510423fc2768afda10e56094e27f676b564e2`; `trunc(-1) = -1`, truthiness 1, so no A1 collision. Swapping is a one-row edit; I did not change `top_p` because the L1 named only `min_p`.

## What the source says

`field_num<T>::eval` (pinned snapshot, lines 532-549): absent `set_hard_limits`, `val = std::max(min, std::min(max, data.at(n).get<T>()))` — silent clamp, HTTP 200. With `is_hard_limit`, a value outside `[min,max]` throws `Value must be between A <= value <= B, but got X` (400). All four assigned fields use only `set_limits` or nothing, so **none of them can produce a `reject` row**; the reject shape belongs to `set_hard_limits` fields (e.g. `n_discard`:40, `repeat_last_n`:127).

`field_num` defaults are the type's own range (`server-schema.h:42-43`, `lowest()`/`max()`), which is why `top_n_sigma` (a `float`) still saturates even though the declaration attaches no limits: `1e39`, `3.5e38` -> `3.4028234663852886e+38` (`FLT_MAX`); `-3.5e38` -> `-3.4028234663852886e+38`.

Generation settings keys (pinned `server-task.cpp:100-103`, `task_params::to_json`): `top_k`, `top_p`, `min_p`, `top_n_sigma` — flat keys, no dotted path needed.

## Live evidence (all from my run, port 48203)

Server: `timeout --kill-after=10 300 ~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48203`; binary sha256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`, model sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches the counter's model pin). Request = counter body `{"prompt": "Once upon a time", "n_predict": 1}` plus one key.

| probe | status | effective | raw body sha256 |
|---|---|---|---|
| base (no field) | 200 | top_k 40, top_p 0.949999988079071, min_p 0.05000000074505806, top_n_sigma -1.0 | `ead2ae1906ec…fff310f0` (`base.json`) |
| top_k -5 | 200 | 0 | `3f929f125af0…fcc703` (`top_k.json`) |
| top_p 2.5 | 200 | 1.0 | `11a63f6d5132…ddc73` (`top_p.json`) |
| min_p -1.5 (retained) | 200 | 0.0 | `ad72bbe31213…31bd99e` (`probe5-00-min_p.json`) |
| min_p -0.25 (superseded, no-row note) | 200 | 0.0 | `fb794db107cd…74f0a3` (`min_p.json`) |
| top_n_sigma 3.5e38 | 200 | 3.4028234663852886e+38 | `27b80f7f7cb6…665d46` (`top_n_sigma-3.5e38.json`) |
| top_k 4294967296 | 200 | 0 (2^32 wraps into int32 as 0, then clamps) | `8edcfae95a00…b003ac3` (`probe2-04-top_k.json`) |
| top_p -1.0 | 200 | 0.0 | `f8aa31fbf3ed…b564e2` (`probe2-02-top_p.json`) |
| min_p 2.0 | 200 | 1.0 | `e81fca244dc3…c52684f` (`probe2-03-min_p.json`) |
| top_n_sigma 1e39 | 200 | 3.4028234663852886e+38 | `d14f2780680b…64574574e` (`top_n_sigma-1e39.json`) |
| top_n_sigma -3.5e38 | 200 | -3.4028234663852886e+38 | `3a76a2f2a847…026fab6` (`top_n_sigma-neg3.5e38.json`) |
| top_n_sigma 3.4e38 | 200 | 3.3999999521443642e+38 (float32 round-trip, identity) | `35de4aba0caf…3b3e3b587` (`probe4-00-top_n_sigma.json`) |
| top_n_sigma 3.4028234663852886e38 | 200 | 3.4028234663852886e+38 (identity) | `92a043ee2108…32502ffedc` (`probe4-01-top_n_sigma.json`) |

Full shas in `rows.json` and `live-index.json`; bodies are in `w1/out/DataG03/`.

Provenance note: my second-round harness reused the filename template `probe2-##`, so the third probe run (the 3.5e38 / -3.5e38 pair) overwrote the `-3.5` and `1e30` response files. The overwritten files were copied to their descriptive names above and the run records survive in `/fast/scratch/hyaku/kama-r28/w1/DataG03/result3.json` / `result4.json`. Nothing cited by `rows.json` is affected: every cited file's sha256 was recomputed from disk in `build_rows.py`, and each cited file's `generation_settings` was re-read at build time.

## Judgement call handed to the L1 — `top_n_sigma`

Its row is mechanically valid (line 101 declares the field; 200; effective 3.4028234663852886e+38 differs from sent 3.5e+38 and from the omitted-field value -1.0) and the behaviour is reproducible, but the threshold is the `float` type maximum inherited from `field_num`'s defaults, **not** an explicit `set_limits` on the declaration; A1 will refuse it as float32 saturation. The L1 has ruled: leave it as is. If it is dropped instead, register this no-row (measured, same run):

```json
{"field": "top_n_sigma", "line": 101,
 "reason": "No set_limits/set_hard_limits/handler on the declaration; representable values are stored verbatim (sent 12345 -> 12345.0, base -1.0), so no out-of-range rejection or non-identity transform inside float32 exists; values beyond float32 only saturate to FLT_MAX, which is the type maximum, not a declared field limit.",
 "live": {"status": 200, "message": null, "effective": 12345.0, "base_effective": -1.0,
          "response_sha256": "960c12ddcceb9f147d57aa58ff5e55ffa4bc393e3f09a22d09ac039974040b3b"}}
```

That `live` block is the `top_n_sigma: 12345` probe (`top_n_sigma.json`), which showed identity.

## Bounds compliance

- Port 48203 only; argv exactly the assigned one, wrapped in `timeout --kill-after=10 300`; every run killed its process group in a `finally`; `ss -ltnp` after the last run showed `48203` closed and no `llama-server.*48203` process.
- Read-only in the lane: writes only under `.ufo/waves/round-28/w1/out/DataG03/` and this report. No git/jj, no tracked-file edits, no MANIFEST/.ufo state touched.
- Source sha256 of my own `curl` of the pinned raw URL (`2026-10-23T08:32:44Z`) is `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`, identical to the pinned snapshot; saved as `server-schema-704366d.cpp.fetched`.
- No tool installs or updates (nothing needed; python3/curl/sha256sum present). No pacman transactions.
- Scratch: `/fast/scratch/hyaku/kama-r28/w1/DataG03/` (probe.py, probe2.py, probe3.py, probe4.py, probe5.py, build_rows.py, result*.json, server*.log); free space checked before running.

## Risks

- `top_n_sigma` row rests on float32 saturation and is expected to be refused under A1 (L1 ruled to leave it).
- `top_p` collides with truthiness only if A1 maps `2.5` to numeric `1`; the measured `-1.0 -> 0.0` alternative is ready (`probe2-02-top_p.json`, `f8aa31fb…`).
- Do not pick `3.4e38` for a top_n_sigma row: 3.4e38 -> 3.3999999521e38 is within the counter's float32 tolerance, so `same()` treats it as identity (`e:identity`).
- The base response hash varies per run (timings/id_slot are in the body), so `base_response_sha256` is run-local evidence only, not a cross-seat constant.
- The three clamp rows' `limits_line` are the literal `->set_limits(...)` continuation lines; the counter never reads them, but keep them honest if the SKILL prose cites them.
