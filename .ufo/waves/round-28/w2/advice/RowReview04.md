# RowReview04 — F28-07 (`t_max_predict_ms`), F28-08 (`top_k`)

Seat: KamaR28.RowReview04. Port 48304 (pinned `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48304`, under `timeout 900`, process group killed, `ss -ltnp` clean). No tools installed (curl/python3/git preexisting). Artifacts: `.ufo/waves/round-28/w2/out/RowReview04/` (response bodies `base.json`, `f28_07.json`, `f28_08.json`, probes `probe_t_float|t_zero|t_minus1|k_big|k_float.json`, `fetch-server-schema.cpp`, `fetch-server*.cpp`, `server-context.h`, `common.h`, `sampling.*`, `server-common.h`).

## F28-07 `t_max_predict_ms` — registry `set`: `{"t_max_predict_ms": -2}`

- **Live re-measure**: POST /completion `{"prompt":"Once upon a time","n_predict":1,"t_max_predict_ms":-2}` → **400**, `{"code":400,"message":"Field 't_max_predict_ms': Value must be between -1 <= value <= 9223372036854775807, but got -2","type":"invalid_request_error"}`, body sha256 `01eea5c0a81900bb3b8087c3ef06e79b1ec23e672ab8fb483802df320a0f220e` — byte-identical to registry `live_by_seat` and receipt `live.body_sha256`. Base request (field omitted) → 200.
- **Source verdict**: pinned `server-schema.cpp` L74-75 declares `field_num("t_max_predict_ms", params.t_max_predict_ms)->set_hard_limits(-1, int64_t::max)`; eval L541-544 throws the exact message for `tmp < -1` (int64 domain). Source explains the observed outcome.
- **Prose verdict: meaning cell DOES NOT HOLD** — two false/over-general claims:
  1. "The server rejects **any** t_max_predict_ms below minus one with HTTP 400": falsified — `t_max_predict_ms: -1.5` → **200** (`probe_t_float.json`, gs shows no error). `data.at(n).get<int64_t>()` (L541) truncates toward zero before the bound check, so every JSON value in (-2,-1) is accepted. The universal is false as a client-facing statement.
  2. "clients **must** send -1 when they want no prediction time limit": false — the timeout fires only when the value is positive (`server-task.h:69` `int64_t t_max_predict_ms = -1; // if positive, limit the generation phase…`; `server-context.cpp:2085` `if (…t_max_predict_ms > 0 && …)`). `t_max_predict_ms: 0` accepted (200, `probe_t_zero.json`) and also disables the limit; -1 is a sentinel, not the only way. Also the stored value is never echoed: `t_max_predict_ms` is absent from `generation_settings`.
  Corrected cell: "The server rejects integer t_max_predict_ms below -1 with HTTP 400 (bounds -1 to 9223372036854775807); the bound check truncates first, so a JSON float like -1.5 is accepted as -1, and since the time limit fires only for positive values, any value <= 0 disables it (-1 is the documented default)."
- **SOURCES/Gate**: fresh fetch of the S146 URL → sha256 `1f9d7b73…0050` = pin; Gate quote = L74+L75 whitespace-joined verbatim; SOURCES.md S146 (line 74 decl / line 75 limits, commit-scoped) holds.
- **Receipt**: counted (`why: []`) — verdict right: cells match registry, single `set` key, correct declaring line, live outcome reproduced; A1 generic-conversion exemption not triggered (reject row). The prose defect is a falsify-seat finding, not a counter defect.

## F28-08 `top_k` — registry `set`: `{"top_k": -5}`

- **Live re-measure**: `{"prompt":"Once upon a time","n_predict":1,"top_k":-5}` → **200**, `generation_settings.top_k = 0` (sha256 `68dbf058…a08`; 200-bodies carry timings so body sha varies per run — registry seat sha `3f929f1…`, receipt `168400e…` — the counted claim, effective 0, reproduces). Base → `top_k = 40`.
- **Source verdict**: L89-90 `field_num("top_k", params.sampling.top_k)->set_limits(0, INT32_MAX)`; eval L539 `val = max(0, min(INT32_MAX, get<int32_t>()))` clamps -5 → 0; `llama_sampler_init_top_k` treats `k <= 0` as an empty `"?top-k"` sampler (`src/llama-sampler.cpp:1525-1530`), so "(top-k disabled)" is source-backed. Source explains the outcome.
- **Prose verdict: HOLDS** — "only soft limits" (set_limits, no set_hard_limits), "silently clamps a negative request to 0 (top-k disabled)" (measured), "clients must validate 0..INT32_MAX themselves" (sound, reinforced). One completeness gap, not a falsehood: the soft-clamp claim does not cover out-of-int32 sends — `top_k: 5000000000` → 200 with `gs.top_k = 705032704` (the `get<int32_t>` on L539 wraps `mod 2^32` before the clamp sees it), and `top_k: -0.5` → 0. A sharper cell could append: "note a JSON value above INT32_MAX wraps mod 2^32 (e.g. 5e9 stores as 705032704) rather than clamping to 2147483647."
- **SOURCES/Gate**: S147 URL fetches to the same pinned sha256; Gate quote = L89+L90 whitespace-joined verbatim; SOURCES.md S147 (line 89 decl / line 90 limits) holds.
- **Receipt**: counted (`why: []`) — verdict right: effective 0 differs from sent -5 and every generic conversion of it, so it is genuine field knowledge (clamp to soft min), not e:generic-conversion.

## Verdict

**Partly holds.** C1's counted verdict is right for both rows (26 counted, meets 18). F28-08 meaning holds (minor out-of-int32 wrap gap). F28-07 meaning cell is wrong: its "any … below minus one" is falsified by `t_max_predict_ms: -1.5 → 200` and its "must send -1" by `0` disabling equally; correction proposed above.
