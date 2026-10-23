# DataG11 — round-28 C1 data seat (fields at server-schema.cpp:222,225,229,242)

Seat: KamaR28.DataG11-2. Port 48211. Server argv (exactly as bounded):
`~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48211`,
started under `timeout 200` from `/fast/scratch/hyaku/kama-r28/w1/DataG11/probe.py` (SIGTERM to the process group, then verified `ss -ltnp` shows 48211 closed). No installs, no pacman, no git/jj writes.

## Result: 1 row draft + 3 no-rows (rows.json)

| field | line | outcome |
|---|---|---|
| `lora` | 229 | effective: `lora = [{"id": 0, "scale": 0.5}]` for sent `[{"id":0,"scale":1.0},{"id":0,"scale":0.5}]` |
| `speculative.ngram_size_m` | 222 | no row: compiled out (`#if 0` at 198-227), silently ignored, 200 |
| `speculative.ngram_min_hits` | 225 | no row: same `#if 0` block, silently ignored, 200 |
| `dry_sequence_breakers` | 242 | no row: verbatim echo when non-empty; empty/non-array rejected with a message that carries no `Value must be between A <= value <= B` bounds |

## The lora row (countable)

- Sent (exactly the counter's base body plus the field): `{"prompt": "Once upon a time", "n_predict": 1, "lora": [{"id": 0, "scale": 1.0}, {"id": 0, "scale": 0.5}]}` -> HTTP 200, `generation_settings.lora == [{"id": 0, "scale": 0.5}]`.
- Differs from sent (two entries collapse to one) and from the field-omitted default (`generation_settings.lora == []` in `resp_base.json`).
- Why it collapses: `server-schema.cpp:236` assigns `parse_lora_request(lora)` into `params.lora`, and `server-task.cpp:37-41` serializes that member as `for (auto & it : this->lora) push_back({{"id", it.first}, {"scale", it.second}})`, i.e. an id-keyed map with last-write-wins. Live evidence: `resp_lora_dup.json`, sha256 `2786161a47665f965dce0ffeeb9a735d4a53de03f529d455f844ac24b3a52afc`.
- Countable under the counter: `same(gs_value, outcome.value)` true, `e:identity` false, `e:default` false (re-checked with the counter's own `same`/`canon` on the saved body).

Proposed integration (L1 assigns the final F28-NN id and S### token; must be new at base):
- registry `set`: `{"lora": [{"id": 0, "scale": 1.0}, {"id": 0, "scale": 0.5}]}`; `outcome`: `{"kind": "effective", "key": "lora", "value": [{"id": 0, "scale": 0.5}]}`.
- SKILL value cell: `[{"id": 0, "scale": 1.0}, {"id": 0, "scale": 0.5}]`; outcome cell: `200, lora = [{"id": 0, "scale": 0.5}]` (exact `outcome_text` output).
- SOURCES row must name `server-schema.cpp`, commit `704366d`, and a line token matching `#L229` / `L229` / `line 229`.
- Only ONE row per field is permitted; if another seat also tables `lora`, both are voided (`b:duplicate-line-or-field`).

## No-row evidence

- `speculative.ngram_size_m` (line 222) and `speculative.ngram_min_hits` (line 225): both declarations sit inside `#if 0` … `#endif` (lines 198-227, "TODO: to keep things simple, we disable speculative parameter adjustments for now"). b11755's `libllama-server-impl.so` contains no `speculative.ngram` literal. Live: values 7, -1, 2147483648 (ngram_size_m) and 9, -5 (ngram_min_hits) all return 200 with `generation_settings` lacking the key, byte-shape identical to a made-up unknown field (`resp_unknown_control.json`). No reject, no effective value, no key to cite — a row would fail the counter's own live check with `d:not-shown`.
- `dry_sequence_breakers` (line 242): `["\n", "::"]` -> 200 with `generation_settings.dry_sequence_breakers == ["\n","::"]` (echo, so `e:identity`); `["\n","\n"]` is not deduped; `[""]` is stored verbatim. `[]` and `"x"` -> 400 `Field 'dry_sequence_breakers': Error: dry_sequence_breakers must be a non-empty array of strings` (no bounds text, so the counter's `REJECT_RE` cannot match; `bounds` cannot be derived without fabricating).

## Retained evidence (all in this out dir)

`rows.json`; raw bodies `resp_base.json`, `resp_lora_dup.json`, `resp_lora_noscale.json`, `resp_lora_one.json`, `resp_lora_empty.json`, `resp_lora_str.json`, `resp_lora_negscale.json`, `resp_dry_two.json`, `resp_dry_one.json`, `resp_dry_dup.json`, `resp_dry_blank.json`, `resp_dry_empty.json`, `resp_dry_str.json`, `resp_ngram_size_m_{7,neg1,huge}.json`, `resp_ngram_min_hits_{9,neg5}.json`, `resp_unknown_control.json`; `live-probe-log.json` (status/sha/generation_settings per probe); `probe.py`; `server.log`. My own fetch of the pinned raw URL hashed `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` (accessed 2026-10-23T08:32:44Z), equal to the wave snapshot.

## Risks / notes for L1

- `parse_lora_request` itself is not in the wave snapshot (it lives in server-context), but the map shape is proven inside the snapshot by `server-task.cpp:37-41` and by the live duplicate-id collapse; a falsify seat can reproduce with any two entries sharing an id.
- A second truthful lora variant exists (`[{"id": 0}]` -> `lora = [{"id": 0, "scale": 0.0}]`, `resp_lora_noscale.json`, sha `8f68b201e5d0ad7695aaa49611bd598f6520312a86f15216e1a6372515537f4f`); only one row per field is allowed, so it is retained as alternates, not a second row.
- The two speculative fields are unreachable by design at this pin; do not let any row cite lines 222/225 — no outcome can be shown.
- No blockers; port 48211 confirmed closed.
