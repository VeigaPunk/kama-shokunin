# DataG09 — round-28 C1 request-field outcomes (four fields, live on port 48209)

Seat: DATA executor, claim C1 (measured, depth). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only; nothing written inside it except this advice file and `w1/out/DataG09/`).
Port: **48209**. Binary: `~/.local/opt/llama-b11755/llama-server` (`version: 0.7.0-dev (build 11755, commit 704366d76)`). Model: `~/.cache/kama-shokunin/models/stories260K.gguf`.
argv (exactly the bounded form, wrapped in `timeout 600`, own session, process group killed):
`llama-server -m <model> --host 127.0.0.1 --port 48209`.
Port state after the run: `ss -ltnp` shows no listener on 48209 (`port_open_after: false` in `probe.json`).

Result: **1 countable row (min_keep), 3 no-row entries**. Every live fact below came from my own server run; request bodies are the counter's exact BASE_BODY (`{"prompt": "Once upon a time", "n_predict": 1}`) plus one field.

## Live probe results (raw bodies retained)

| request | status | message / relevant generation_settings | raw file | sha256 |
|---|---|---|---|---|
| base (no field) | 200 | `min_keep=0`, `post_sampling_probs=false`, `backend_sampling=false`, speculative keys `["speculative.types"]` | `raw-base.json` | e21d71f63f22e100df16df930acedc6d04933f187a376c7ad2fa870304db702b |
| `{"min_keep": -1}` | **400** | `Field 'min_keep': Value must be between 0 <= value <= 2147483647, but got -1` | `raw-min_keep.json` | bfce3536f68a4117810229d171770eddcdc26c75607f526f46313b978027b8af |
| `{"min_keep": 2147483648}` | 400 | same frame, `but got -2147483648` (int32 wraparound before the check) | `raw-min_keep_overflow.json` | 7e32979ce4b4e4dd8d6c206a67f986b7785b1fc117ca9f72de1f67f0bba13176 |
| `{"backend_sampling": true}` | 200 | `backend_sampling=true` | `raw-backend_sampling.json` | d3a231e12480bbda2bb7a720c90d851909685942c186e92f22fb5ecc5ac12ac9 |
| `{"backend_sampling": 1}` | 400 | `Field 'backend_sampling': [json.exception.type_error.302] type must be boolean, but is number` | `raw-backend_sampling_num.json` | e1e58e59720e7270006351ee70c017a1d45b4ee65a6ba78261d81f8e47c0f684 |
| `{"post_sampling_probs": true}` | 200 | `post_sampling_probs=true` | `raw-post_sampling_probs.json` | ff2691704ba602a455e6012eed4d0feff2250e2c758379e80bfa79d26f806576 |
| `{"post_sampling_probs": 1}` | 400 | `Field 'post_sampling_probs': [json.exception.type_error.302] type must be boolean, but is number` | `raw-post_sampling_probs_num.json` | 4bd718a3cf80bec9c970cd7586c69590f910f0f0d8bea8a5b200ed9f483cdc02 |
| `{"speculative.n_max": 5}` | 200 | no `speculative.n_max` key; only `speculative.types` present | `raw-speculative.n_max.json` | 13a4030faac7b5cbe08c18366cbf575d38315167a4b1fdb5ae175e62d1059cd0 |

The 400 bodies carry the counter's expected shape: `{"error": {"code": 400, "message": "Field 'min_keep': Value must be between 0 <= value <= 2147483647, but got -1", "type": "invalid_request_error"}}`; the counter's `REJECT_RE` matches it with field `min_keep`, bounds `0` and `2147483647`.

### In-range identity check (second run, same port)

To rule out an `effective` outcome for `min_keep`, a second server run sent in-range values (`probe2.json`, bodies `raw2-*.json`):

| request | status | reported `generation_settings.min_keep` |
|---|---|---|
| base (field omitted) | 200 | 0 |
| `{"min_keep": 3}` | 200 | 3 |
| `{"min_keep": 100000}` | 200 | 100000 |
| `{"min_keep": 2147483647}` | 200 | 2147483647 |

Every in-range value is stored and echoed verbatim, and the upper hard bound is inclusive (no clamp, no error), so `min_keep` has **no** countable `effective` row — the out-of-range reject is its only countable outcome. `min_keep` 2147483648 wraps to `-2147483648` (int32 overflow in `get<int32_t>`) and is then rejected with the same bounds, which is why that spelling is not usable as the row value.

## Countable row draft (1) — `rows.json`

```json
{"field": "min_keep", "set": {"min_keep": -1},
 "outcome": {"kind": "reject", "bounds": [0, 2147483647]},
 "line": 183, "limits_line": 184,
 "meaning": "A min_keep outside 0..2147483647 is refused with HTTP 400 naming the hard bounds, so clients must send an in-range integer and treat the 400 as their own request error.",
 "source": {"url": "https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp",
            "fetched_sha256": "1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050",
            "accessed": "2026-10-23T08:33:23Z",
            "quote": "add((new field_num(\"min_keep\", params.sampling.min_keep)) ->set_hard_limits(0, INT32_MAX)"},
 "live": {"status": 400,
          "message": "Field 'min_keep': Value must be between 0 <= value <= 2147483647, but got -1",
          "effective": null, "base_effective": null,
          "response_sha256": "bfce3536f68a4117810229d171770eddcdc26c75607f526f46313b978027b8af"}}
```

`fetched_sha256` is my own `curl` of that URL into `schema-704366d.cpp` (29572 bytes), equal to the pinned snapshot `1f9d7b73…4050`, so the source is the same bytes the server was built from.

### Integration snippets for the L1

Registry entry (`registry/request-field-outcomes-r28.json`; `source` here is the counter's `{row,file,line}` shape, not the `rows.json` source block):

```json
{"id": "F28-XX", "field": "min_keep", "set": {"min_keep": -1},
 "outcome": {"kind": "reject", "bounds": [0, 2147483647]},
 "meaning": "A min_keep outside 0..2147483647 is refused with HTTP 400 naming the hard bounds, so clients must send an in-range integer and treat the 400 as their own request error.",
 "source": {"row": "S1XX", "file": "server-schema.cpp", "line": 183}}
```

SKILL row (header must be exactly `| id | field | value | outcome | meaning | source |`):

```
| F28-XX | min_keep | -1 | reject 400, bounds 0 to 2147483647 | A min_keep outside 0..2147483647 is refused with HTTP 400 naming the hard bounds, so clients must send an in-range integer and treat the 400 as their own request error. | S1XX |
```

The four cells must be verbatim: field `min_keep`, value canonical JSON `-1`, outcome `reject 400, bounds 0 to 2147483647` (counter builds that text from `outcome_text()`), source token `S1XX`.

New SOURCES row proposed (must be absent from base; must contain `server-schema.cpp`, `704366d` and a line reference matching `L183`/`line 183`):

```
| S1XX | llama.cpp server-schema.cpp @ 704366d (b11755) — https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp#L183 | code | A | the min_keep request field: declaring line, hard limits and the HTTP-visible reject text at commit 704366d76 only; not the sampler-level effect of an accepted min_keep | min_keep declared line 183, set_hard_limits(0, INT32_MAX) line 184; hard-limit throw line 543; raw sha256 1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050 | An out-of-range min_keep is refused before sampling: the error names the field and both hard bounds, so a client can distinguish a bad request from a server fault; values above INT32_MAX wrap to negative and are rejected the same way. | new | 2026-10-23 | unset | C1 F28-XX |
```

## No-row entries (3)

1. **`backend_sampling`** (declared line 187, `field_bool`, no limits/handler). Live: `true` → 200, `generation_settings.backend_sampling = true`, base (omitted) `false`. It is stored and echoed verbatim, i.e. identity against the sent value, so the counter's `e:identity` clause cannot be satisfied. Sending `1` gives 400 but with a `json.exception.type_error.302` message that has no `Value must be between …` text, so it cannot be a reject row either. No limits line exists.
2. **`post_sampling_probs`** (line 190, `field_bool`, no limits/handler). Same shape: `true` → 200 and reported `true`; base `false`; identity; `1` → type_error 400 without bounds text.
3. **`speculative.n_max`** (line 200, `field_num` with `set_hard_limits(0, INT32_MAX)`): the declaration sits inside `#if 0` (line 198) … `#endif` (line 227), so it is **not compiled into the schema**. Live: request with `5` → 200, and `generation_settings` has no `speculative.n_max` key (only `speculative.types`); the key is silently ignored, no clamp, no reject, no reported value.

## Pinned-code reading that explains the live results

* `field_num<T>::eval` (server-schema.cpp:532-551): with `is_hard_limit` false it clamps `val = max(min, min(max, got))` (line 538-539 — silent clamp, the `set_limits` path); with hard limits it throws `Value must be between <min> <= value <= <max>, but got <got>` (line 543). `handle_with_catch` (518-523) prefixes `Field '<name>': `, which is what produced the observed 400 text.
* `field_bool::eval` (565-576) only does `val = data.at(n).get<bool>()`; a non-bool throws nlohmann `type_error.302`, captured by the same wrapper, hence the 400 without bounds.
* `has_value` (527-529) treats JSON `null` as absent, so `null` would fall back to the default (not probed for rows; it would be `e:default`).
* `task_params::to_json` reports `min_keep` at server-task.cpp:75 (metrics) and :130 (full), `post_sampling_probs` at :83/:142, `backend_sampling` at :84/:143; there is no `n_max` key, only `speculative.types` at :81/:140. So the bool values observed are the stored `task_params` members, unmodified after schema eval.

## Risks / blockers / notes

* Only `min_keep` of my four fields can contribute to the counted target; the two bools are identity-only by construction (no handler, no limits) and `speculative.n_max` is inert (`#if 0`). No fabrication was used to force rows.
* **Adjacent hazard for other seats (source inference, not my live evidence):** every other speculative field in the same `#if 0` block (lines 204-225: `speculative.n_min`, `speculative.p_min`, `speculative.type`, `speculative.ngram_size_n/_m`, `speculative.ngram_min_hits`) is equally uncompiled, so drafting them would only produce dead rows; my live run covers only `speculative.n_max`.
* Duplicate rule: `min_keep` is cited only here (checked `w1/out/DataG*/rows.json`; no other seat drafts it). If another seat also drafts `min_keep` or line 183, the counter voids both, so the L1 must land one only.
* The counter's static check needs the SOURCES row to name the file, the commit and the line; the snippet above carries all three.
* No tool installs or updates were made. No git/jj writes in the lane or fleet repo. Only `/fast/scratch/hyaku/kama-r28/w1/DataG09/` (probe script and server log) and this seat's out/advice dirs were written.
* Raw response bodies cited above are small (142-1685 bytes) and live next to `rows.json`; `probe.json` contains the request bodies, statuses, shas and `port_open_after: false`; `probe2.json` does the same for the in-range run.
* Two separate server runs were used (each killed, port 48209 re-verified closed); every status/message/value cited comes from one of them, never from the counter's own ports.

## Files

* `kama-shokunin/.ufo/waves/round-28/w1/out/DataG09/rows.json` (3a666555e742ddc005423f73241b516d614fea88966471e7043e8e0240c00340)
* `…/out/DataG09/probe.json` (57427918ac110f823f63863e877a88bbac1453cde09f41cb73153272805bd7c2)
* `…/out/DataG09/probe2.json` (474e4895a888130e222bb5dc25fa21a4492c714cd977a8822803ae4f3c651f80)
* `…/out/DataG09/raw-base.json`, `raw-min_keep.json`, `raw-min_keep_overflow.json`, `raw-backend_sampling.json`, `raw-backend_sampling_num.json`, `raw-post_sampling_probs.json`, `raw-post_sampling_probs_num.json`, `raw-speculative.n_max.json`
* `…/out/DataG09/raw2-base2.json`, `raw2-min_keep_3.json`, `raw2-min_keep_100000.json`, `raw2-min_keep_max.json`
* `…/out/DataG09/schema-704366d.cpp` (my curl of the cited URL, sha256 1f9d7b73…4050)
* `kama-shokunin/.ufo/waves/round-28/w1/advice/DataG09.md` (this file)
* Scratch (not evidence): `/fast/scratch/hyaku/kama-r28/w1/DataG09/probe.py`, `probe2.py`, `server.log`, `server2.log`
