# DataG10 — round 28 wave 1, C1 data seat: `speculative.*` request fields

## Verdict

**0 countable rows / 4 assigned fields.** All four assigned fields — `speculative.n_min` (204),
`speculative.p_min` (208), `speculative.type` (213), `speculative.ngram_size_n` (219) — are declared
inside a compile-time-disabled `#if 0` block (line 198 … `#endif` line 227) of the pinned
`server-schema.cpp`, with the comment at line 197: "TODO: to keep things simple, we disable
speculative parameter adjustments for now". llama-server b11755 therefore never sees the keys:
every request carrying one of them returns HTTP 200 with `generation_settings` JSON-equal to the
base request and no field-specific key. Neither a hard-limit rejection nor an effective,
reported value exists to count.

## Setup (my own run, port 48210)

- argv: `/home/vgpnk/.local/opt/llama-b11755/llama-server -m /home/vgpnk/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48210`, under `timeout`
- binary sha256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`
- model sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`
- base request `{"prompt": "Once upon a time", "n_predict": 1}` → 200, `content` `,`,
  `speculative.types` = `"none"`, response sha256 `0f4e8ae6dcdf2e84c47dd1fa779649cdc6dcbf78f3736d99511b85074238a0d0`
- pinned source fetched fresh from `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76…ad/tools/server/server-schema.cpp`
  at 2026-10-23T08:33:17Z, sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`
  (equals the lane snapshot exactly)

## Source finding

```
196
197    // TODO: to keep things simple, we disable speculative parameter adjustments for now
198 #if 0
...
204    add((new field_num("speculative.n_min", params.speculative.draft.n_min))
205        ->set_hard_limits(0, INT32_MAX)
208    add((new field_num("speculative.p_min", params.speculative.draft.p_min))
209        ->set_hard_limits(0.0f, 1.0f)
213    add((new field_str("speculative.type"))
215        ->set_handler([&](field_eval_context & ctx, const json & data) {
216            ctx.params.speculative.types = { common_speculative_type_from_name(...) };
219    add((new field_num("speculative.ngram_size_n", params.speculative.ngram_simple.size_n))
227 #endif
```

`eval_llama_cmpl_schema` (line ~463) builds its schema from `make_llama_cmpl_schema` only, so the
disabled `add(...)` calls never register and unknown JSON keys are simply skipped (no unknown-key
rejection anywhere in the eval loop at 490-500). `task_params::to_json` reports only one
speculative key, `"speculative.types"` (server i.e. CLI-level `params.speculative`), never
`n_min`, `p_min` or `ngram_size_n`.

## Live results (raw bodies in `out/DataG10/raw/`)

| field | sent | status | gs vs base | `speculative.types` | response sha256 |
|---|---|---|---|---|---|
| `speculative.n_min` | `999999999` | 200 | equal | `none` | `a20e3d5ec82c61e987ac58ddfca9d2af12654aae7f7933d7e8caeeefa30fbab6` |
| `speculative.p_min` | `-1.0` | 200 | equal | `none` | `191e9a0e52ed623a0352fa7acf6b567670eb63547ce502ab9ee566ff81a7faa4` |
| `speculative.type` | `"ngram"` | 200 | equal | `none` | `fdbd4509e2d9ea29523bb6f636e988aed309ea5eeb177d93f1e3b9095a471514` |
| `speculative.ngram_size_n` | `7` | 200 | equal | `none` | `69ca4b4b9cd35dae07b3c367897961e09f9ca3f8309f6262ca4c089c80018c7a` |

("gs equal" = the whole `generation_settings` object compares equal to the base response's; only
`timings` differ between the raw bodies.)

## Falsifier probes (same server, same run)

| probe | status | result |
|---|---|---|
| `speculative.type: 7` (wrong JSON type) | 200 | ignored; gs equal to base |
| `speculative.type: "bogus-nonexistent"` | 200 | ignored; `speculative.types` still `none` |
| `speculative.n_min: "not-a-number"` | 200 | ignored; gs equal to base |
| `"speculative": {"n_min": 999999999}` (nested form) | 200 | ignored; gs equal to base |
| **contrast** `n_predict: -2` (active field, hard limits) | **400** | `Field 'n_predict': Value must be between -1 <= value <= 2147483647, but got -2` |

The contrast proves the harness and server do surface the canonical reject message when the field is
compiled in; the silence on the four assigned fields is the server ignoring unknown keys, not a
broken request path.

## Why no row exists (against the counted definition)

- `reject`: needs status 400 plus `Field '<field>': Value must be between A <= value <= B, but got`;
  the server never validates these keys, at any value or JSON type.
- `effective`: needs `generation_settings[key]` to equal a value different both from the sent value
  and from the field-omitted default. `n_min`/`p_min`/`ngram_size_n` have no `generation_settings`
  key at all; `speculative.type` would map to `speculative.types`, which stays `"none"` — the same
  as the default.

## Advisory for the L1 (no action taken in the lane)

- Do **not** draft rows for declaring lines 200 (`speculative.n_max`), 222 (`speculative.ngram_size_m`)
  or 225 (`speculative.ngram_min_hits`) either: same `#if 0` block, same 200-and-ignored live outcome.
  Any such row fails counter clause (d) as `d:not-shown`.
- Countable C1 data must come from active `add(...)` entries outside lines 198-227 (e.g. the
  `n_predict`, sampling, `reasoning_*`, `lora`, `samplers` fields, plus active handler fields).
- The treating of line 213 (`field_str`) is worth keeping in mind for the registry: it declares no
  limits, only a handler at 215-217, so even a hypothetical live row could not be a `reject` row.

## Files

- `out/DataG10/rows.json` — `{"rows": [], "no_rows": [4 entries]}`, sha256 `356d752f4161e74e25bc666a9e7753995b54d496a192eca7d50a0f0b39f2077a`
- `out/DataG10/evidence.json` — argv, binary/model/schema hashes, per-probe detail, extra probes, sha256 `aeaa827426f98ee7f94f69072c1e710f076a43c4dc5d6e5d1c5fc2074bcfe79f`
- `out/DataG10/raw/` — 10 request bodies, 10 raw response bodies, `server.log`, fetched `server-schema.cpp.github-704366d`

## Risks / blockers

- None material. Port 48210 confirmed closed with `ss -ltnp` after shutdown; server process group
  killed; no git/jj writes; no package installs (nothing installed or updated this seat); scratch
  work under `/fast/scratch/hyaku/kama-r28/w1/DataG10/`.
- Residual risk: if the L1 intended these four fields as an easy source of rows, they are dead
  weight — the 18-row target must be met entirely from the active schema, and this seat contributes
  0 counted rows.
