# DataG16 — C1 request-field rows (round 28, wave 1)

Seat: `KamaR28.DataG16-2`. Claim C1, DATA seat. Live run on port **48216 only**, two short
lifetimes of the pinned binary, argv exactly
`~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48216`,
under `timeout`; each process group killed and `ss -ltnp` confirms 48216 closed.
No tool installed, no pacman transaction, no write in the lane checkout; nothing committed.

## Output

- `out/DataG16/rows.json` — **0 row drafts, 4 no-row entries** (`{"rows": [], "no_rows": [...]}`).
- Raw bodies cited, same dir: `base.json`, `verbose_true.json`, `verbose_num.json`,
  `tpt_true.json`, `tpt_num.json`, `stream_false.json`, `stream_num.json`, `stream_true.sse`,
  `stream_true.headers`, `usage_true.json`, `usage_num.json`, `so_num.out`, `cu_toplevel.out`,
  `oai_verbose.out`, `native_stream_verbose.sse`, `chat_usage.sse`, `chat_nousage.sse`,
  `server.log`, `server2.log` (92 KB total).
- Scratch: `/fast/scratch/hyaku/kama-r28/w1/DataG16/`.

## Source pins verified

- Snapshot `sources/llama.cpp-704366d/server-schema.cpp` sha256 = `1f9d7b73…c7904050`, as pinned.
- Own `curl` of `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp`
  at 2026-10-23T08:34Z → same sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`.
- Supporting defaults from the pin (not in the snapshot): own curl of `tools/server/server-task.h`
  at the same commit → sha256 `ffd0ac6e1d0f0af63c35d1fd07347e3ec6b3746769667e55742521c7d0c5904f`;
  lines 52/53/76/83 give `stream`, `include_usage`, `timings_per_token`, `verbose` all default
  `false`, which the live base request confirmed.
- Mechanism read at the pin: all four assigned fields are plain `field_bool`
  (`server-schema.cpp:17,20,23,27`), and `field_bool::eval` (`server-schema.cpp:565-578`) assigns
  `val = data.at(n).get<bool>();` (line 572) with no bounds and no custom handler.

## Live results (all from port 48216)

Base (counter body `{"prompt": "Once upon a time", "n_predict": 1}`): 200, sha `55b11fdd…`,
`generation_settings.stream = false`, `generation_settings.timings_per_token = false`,
**no** `verbose` key, **no** `include_usage` key.

| probe | request extra | status | message / generation_settings |
|---|---|---|---|
| verbose | `true` | 200 | no `generation_settings.verbose`; no `__verbose` in body |
| verbose | `1` | 400 | `Field 'verbose': [json.exception.type_error.302] type must be boolean, but is number` |
| timings_per_token | `true` | 200 | `timings_per_token = true` (equal to sent; base false) |
| timings_per_token | `1` | 400 | `Field 'timings_per_token': … type must be boolean, but is number` |
| stream | `false` | 200 | `stream = false` (equal to base) |
| stream | `true` | 200 | `Content-Type: text/event-stream`; final `data:` chunk has `stream = true` |
| stream | `1` | 400 | `Field 'stream': … type must be boolean, but is number` |
| stream_options.include_usage | `true` | 200 | no `generation_settings.include_usage`, body unchanged |
| stream_options.include_usage | `1` | 400 | `Field 'include_usage': … type must be boolean, but is number` |
| stream_options = 5 | — | 200 | silently ignored (non-object nested value) |
| top-level include_usage | `true` | 200 | silently ignored (unknown top-level field) |
| /v1/completions verbose | `true` | 200 | `__verbose` present (OpenAI-compat path only) |
| /completion stream+verbose | `true,true` | 200 | SSE, 0 occurrences of `__verbose` |
| /v1/chat/completions stream + include_usage | — | 200 | 1 `usage` chunk; without it, 0 |

## Why none of the four can produce a countable row

1. **Reject is structurally impossible.** These fields declare no `set_hard_limits`, so there is no
   bounds check; `server-schema.cpp:518-523` would still wrap a thrown message as `Field '<name>': …`,
   but the only throw here is nlohmann's `type must be boolean, but is number`. That text contains no
   `Value must be between A <= value <= B`, so the counter's `REJECT_RE` never matches and a `reject`
   row cannot be shown live.
2. **Effective is structurally impossible for booleans.** `task_params::to_json` reports `stream`
   (`server-task.cpp:73` and `:127`) and `timings_per_token` (`:82` and `:141`) with exactly the
   parsed bool, and the live runs confirm identity (`true` → `true`). C1 requires the effective value
   to differ from the sent value **and** from the field-omitted default (both `false` at the pin);
   a two-valued identity assignment can satisfy neither branch. `verbose` and `include_usage` have no
   `generation_settings` key at all, so `lookup()` returns absent.
3. **Type errors are a different validation class.** `{"field": 1}` yields a 400, but it is a JSON
   type error, not a bounds rejection; it cannot be expressed as `{"kind": "reject", "bounds": [A, B]}`
   without fabricating bounds.

So each field gets a `no_row` entry with the live status and response sha; `rows.json` has `rows: []`.

## Operational facts for prose (not rows)

- `verbose` is **inert on native `/completion`**: with `{"verbose": true}` the non-stream body has no
  `__verbose`, and even `stream: true` + `verbose: true` yields 0 `__verbose` occurrences
  (`native_stream_verbose.sse`). `__verbose` appears only on `/v1/completions`
  (`oai_verbose.out`) and `/v1/chat/completions`; `params.verbose` is consumed solely by the
  OAI-compat serializers (`server-task.cpp:396,444,513,1090`).
- `include_usage` only appends the empty-`choices` usage chunk to OpenAI **chat streaming**
  (`server-task.cpp:494`): `/v1/chat/completions` with `stream_options.include_usage` emitted one
  `"usage"` chunk, without it zero. On native `/completion` it is a no-op.
- `stream: true` switches `/completion` to `text/event-stream`; the final data chunk carries
  `generation_settings`, but the body as a whole is not a JSON document, so it cannot be read as one.
- A non-object `stream_options` (e.g. `5`) is silently ignored — `field_nested::eval`
  (`server-schema.cpp:592-601`) only recurses when the value is an object; an unknown top-level
  `include_usage` is also silently ignored. A client sending `0/1` instead of `true/false` gets a 400
  type error naming the field, so use JSON booleans.

## Counter interplay notes for L1

- These four fields contribute nothing to the 18-row target; the registry must draw its rows from
  numeric fields (`set_hard_limits` → reject; `set_limits` → clamp).
- `verbose` and `include_usage` cannot be counted even by a future claim built on
  `generation_settings`; their observables are response shape (`__verbose` presence, usage chunk),
  which the current C1 predicate does not read.
- My `stream` live sha is the SSE body `ac3e4b46…`; if anyone tries to register an effective row from
  that body, the counter's `parse_json` returns `None` (body starts `data: `) and marks it `d:not-shown`.

## Evidence sha256

| file | sha256 |
|---|---|
| base.json | `55b11fdd7ae4449f06b422446e986f0ec175d5045b0550cb2e8839608897c856` |
| verbose_true.json | `87191e9f776fb58081276c20cf078ada8ede5cf01758fd814a5c326e6c2e5d5a` |
| verbose_num.json | `7b6e156ee2d149731ea1a791483c60a14e4f09d6bf256b86e813fab2e8ab63fb` |
| tpt_true.json | `dc5df906fd06cf003d2f57c7c2f04bde09ca081b1ee4243b588a453123441b9a` |
| tpt_num.json | `28d4cc69784d56f715d7b5e8ed581c45bbd70198c5acc97a4c85c38484d9e50d` |
| stream_false.json | `199d02173d29d9465ad2e8dec108229c3c4f6194f39d3cf6db0ec0ddbffbdb77` |
| stream_true.sse | `ac3e4b46d9330d82c28e88f102ecc2bb44dee5ddccb4827323ee6cf9d464d509` |
| stream_num.json | `16efcef7ec45d0976a582632c08834966baedafe68447bdb1fa3bce7b1e645b0` |
| usage_true.json | `fa9739deaf2f8ff58a16b7cbda9f6bad0be4b89fa23b3927ff69f96a7e762fd6` |
| usage_num.json | `a1098a15715eacd4c36c1d871f8b7ab58add3ca1cf8626ed6f52a0d4bb57970d` |
| so_num.out | `dd87658a4bc855d821af8c8f40311b5e6132049a71bb6309da9739b6072ecb9e` |
| cu_toplevel.out | `8aca03c49e38426cd5a112a73c44857aedb40415165b51e0f2d7ad609a11a019` |
| oai_verbose.out | `2dcde335bffd3e7ef9f1a07bafd5e0f1d16e8aad8deae868782449f6e34f0e6d` |
| native_stream_verbose.sse | `8225afb6e22fcfad82f67abd08ed2fdc6bfc2762dbe8e55a334acbb5349e1687` |
| chat_usage.sse | `cfcfafb2efebca42f85e1e40ee22550293bfcebbc34e4b517f78d7e7b9622db2` |
| chat_nousage.sse | `c0ec410a48a961322ac430a2828d79103ab395b68323365e36c8fe905c702e4d` |

## Risks / limits on this evidence

- The four assigned fields are booleans with no bounds; this seat's measured result is **no change**
  (`rows: []`). If the wave needs rows from them, the claim rule (not the data) would have to change —
  not attempted here.
- 400 type-error wording was recorded verbatim from this build; it depends on nlohmann's
  `type_error.302` text and is not a stable bounds contract.
- SSE bodies (`stream_true.sse`, `native_stream_verbose.sse`, `chat_*.sse`) are non-JSON by
  construction; they are cited only as behaviour evidence, never as a JSON document.
- Two server lifetimes (~1 s model load each); `server.log`/`server2.log` retained for replay.
- `report_issue`: no tool output contradicted documented behaviour during this seat.
