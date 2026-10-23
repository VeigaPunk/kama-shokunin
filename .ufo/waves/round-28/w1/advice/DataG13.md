# DataG13 — C1 request-field rows (round 28, wave 1)

Seat: KamaR28.DataG13-2. Live run on port 48213 only.
Binary `~/.local/opt/llama-b11755/llama-server`, model `~/.cache/kama-shokunin/models/stories260K.gguf`,
argv exactly `-m <model> --host 127.0.0.1 --port 48213`, each lifetime under `timeout 240`, process group
killed with SIGTERM (SIGKILL fallback), and `ss -ltnp` confirms 48213 has no listener and no llama-server of
mine remains. No tool installed, no pacman transaction, nothing committed, no lane-checkout file touched.

## Output

- `out/DataG13/rows.json` — **1 row draft, 3 no-rows** (fields `preserved_tokens`, and no-rows for `echo`,
  `grammar_triggers`, `reasoning_control`).
- Raw bodies cited by `rows.json` (all in `out/DataG13/`):
  `resp-r01-final.json`, `resp-r02-final.json` (repeat), `resp-p01-base.json`, `resp-p02-echo-true.json`,
  `resp-p03-echo-string.json`, `resp-p06-triggers-bare.json`, `resp-p07-trigger-word.json`,
  `resp-p08-trigger-pattern.json`, `resp-p10-reasoning-control-true.json`,
  `resp-p11-reasoning-control-int.json`, `resp-p12-reasoning-control-str.json`, plus
  `resp-m00..m13.json` (per-string tokenid map), `resp-q0*.json`, and the run records
  `probe-results.json`, `probe-results-2.json`, `probe-results-3.json`, `probe-results-4.json`.
- Harnesses retained for replay: `out/DataG13/probe.py` … `probe4.py` (scratch copies under
  `/fast/scratch/hyaku/kama-r28/w1/DataG13/`, with `server*.log`).

## Source pins verified

- Snapshot `sources/llama.cpp-704366d/server-schema.cpp` sha256 = `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`, as pinned (29572 bytes).
- My own `curl` of
  `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp`
  at `2026-10-23T08:34:35Z` → same sha256 `1f9d7b73…4050`, same size (29572 bytes).
- Mechanisms read at the pin:
  - `field_num<T>::eval` (server-schema.cpp:532-547): `set_limits` clamps silently
    (`std::max(min, std::min(max, …))`); `set_hard_limits` throws
    `"Value must be between " + std::to_string(min) + " <= value <= " + std::to_string(max) + ", but got " + std::to_string(tmp)`,
    wrapped by `handle_with_catch` (519-525) as `Field '<name>': <e.what()>`.
  - `field_bool::eval` (565-576) and `field_json::eval` (580-588) only call the custom handler; no numeric
    limits are possible on these three non-`field_num` fields, so the counted reject message cannot arise.
  - `server_grammar_trigger(const json &)` (server-common.h:76-82) reads `at("type").get<int>()`,
    `at("value").get<std::string>()`, and `at("token")` only for type `TOKEN`; `to_json()` writes
    `{type, value[, token]}`.
  - `common_sampling_add_preserved_tokens` (common/sampling.cpp:1055-1063) tokenizes each string and keeps the
    id only when it is exactly one token; `common_params_sampling::preserved_tokens` is
    `std::set<llama_token>` (common/common.h:279), so `to_json` emits ascending, unique ids. A `WORD` grammar
    trigger whose word is one token is rewritten to a `TOKEN` trigger only if that token is already preserved
    (common/sampling.cpp:1065-1098), otherwise it throws.
  - `task_params::to_json` (server-task.cpp:25-143) emits `grammar_triggers` (line 133) and
    `preserved_tokens` (line 134); it emits **neither `echo` nor `reasoning_control`**.

## Live results (all from port 48213; counter body `{"prompt": "Once upon a time", "n_predict": 1}`)

| probe | extra field | status | message / generation_settings |
|---|---|---|---|
| p01 base | — | 200 | 49 gs keys; `preserved_tokens` `[]`, `grammar_triggers` `[]`; no `echo`, no `reasoning_control` |
| p02 echo true | `echo: true` | 200 | gs parsed-equal to base (diff `{}`); no `echo` key |
| p03 echo "yes" | `echo: "yes"` | 400 | `Field 'echo': [json.exception.type_error.302] type must be boolean, but is string` |
| q05 echo false | `echo: false` | 200 | gs equal to base; no `echo` key |
| m00 | `preserved_tokens: ["Once"]` | 200 | `[403]` |
| m-map | `preserved_tokens: ["the"]` | 200 | `[265]`; `" a"` → `[261]`, `"and"` → `[269]`, `"time"` → `[378]`, `"upon"` → `[407]` |
| p05 / m-map | `preserved_tokens: [" upon"]` / `[" the"]` / `["Once upon a time"]` | 200 | `[]` (multi-token strings silently dropped) |
| **r01/r02 final** | `preserved_tokens: ["upon", "upon", "a"]` | 200 | **`[261, 407]`** (ascending, duplicate collapsed; identical across two server lifetimes) |
| p06 triggers bare | `grammar_triggers: ["Once"]` | 400 | `Field 'grammar_triggers': [json.exception.type_error.304] cannot use at() with string` |
| p07 trigger word | `grammar_triggers: [{"type": 1, "value": "Once"}]` | 400 | `Field 'grammar_triggers': Grammar trigger word should be marked as preserved token: Once` |
| p08 trigger pattern | `grammar_triggers: [{"type": 2, "value": "Once"}]` | 200 | `[{"type": 2, "value": "Once"}]` (identity) |
| q04 pattern-full | `grammar_triggers: [{"type": 3, "value": "On.*"}]` | 200 | `[{"type": 3, "value": "On.*"}]` (identity) |
| q03 token object | `grammar_triggers: [{"type": 0, "value": "Once", "token": 403}]` | 200 | `[{"type": 0, "value": "Once", "token": 403}]` (identity) |
| p09 word+preserved (two keys, evidence only) | `grammar_triggers: [{"type": 1, "value": "Once"}], preserved_tokens: ["Once"]` | 200 | `[{"type": 0, "value": "Once", "token": 403}]` — transformation needs the second field |
| p10 reasoning_control true | `reasoning_control: true` | 200 | gs parsed-equal to base (diff `{}`); no key |
| p11 / p12 | `reasoning_control: 1` / `"true"` | 400 | `Field 'reasoning_control': [json.exception.type_error.302] type must be boolean, but is number` / `… but is string` |

Response sha256 of the cited bodies: r01 `addb5f7b40ef278b5d0d7d2d4c3ee6bfd44612d8d6db64c14d0bfb1b098239c6`,
r02 `e7cae56977bed9a1eb762a1eb3d305c9d78766d77a024cabe4d507e314008e4c`,
base `55aee8bf9e8fb7b24eb28b134b896a5e94a3c716cfe6a501465905857f01d595`,
echo-true `cf291a98addfeb9a39613e56d48f2e253ca49ee7751b8a761345accc85234612`,
trigger-word `9ff9739e5b5a41d3e521ec5bd3c47dc1b369136f861a539c5b902d7ad9c039fb`,
reasoning-true `e6587e3ba98de4826e1c82a5bb8fcaf998d6505de6e221d410caf545d59f5844`.

## Countable outcome

One row, verified three times on port 48213 (probe run 3 and both repeats in run 4):

- field `preserved_tokens`, declaring line **316**, handler line **319** (no `set_limits`/`set_hard_limits`).
- sent `["upon", "upon", "a"]` → stored `[261, 407]`; differs from the sent value **and** from the
  field-omitted default `[]`. It is also not a mere re-encoding of the first element: order is ascending
  (sent order was 407 then 261) and the duplicate is collapsed, which only a `std::set<llama_token>` explains.

The other three fields have **no** countable one-key outcome at b11755:

- `echo` (306): `field_json` handler at 309 evaluates `data.at("echo").get<bool>()` and discards it; no
  `generation_settings` key exists (`to_json` has none), so neither `effective` nor a bounds-style `reject` is
  possible. Live: 200 with gs equal to base; non-boolean 400 is a `type_error.302`, not the counted message.
- `grammar_triggers` (322): one-key values are either non-bounds 400s (bare string → `at()` type_error.304;
  word trigger not preserved → `Grammar trigger word should be marked as preserved token`) or stored verbatim
  (types 0, 2, 3). The only transformation observed (word → `{type: 0, value, token: 403}`) required
  `preserved_tokens` in the same request, which the one-key row predicate forbids — so it stays a no-row.
- `reasoning_control` (332): `field_bool` stores `params.sampling.reasoning_control`, but `to_json` never
  emits it and the live gs diff for `true` is `{}`; non-booleans are `type_error.302` 400s. No counted outcome.

## Integration notes for L1 (counter shape)

`count-c1.py` `static_checks` needs, for the one row: `source.file == "server-schema.cpp"`, `source.line = 316`,
a **new** `source.row` S### token (unused at base) whose SOURCES.md text contains `server-schema.cpp`,
`704366d` and an `L316`-style reference; `id` matching `^F28-\d{2}$`; registry `set` with exactly one key
`preserved_tokens`. Canonical cells for the SKILL table:

```
| <F28-XX> | preserved_tokens | ["upon", "upon", "a"] | 200, preserved_tokens = [261, 407] | Only strings that tokenize to exactly one token are kept, as ascending llama_token ids de-duplicated in a set, so send one-token strings and read preserved_tokens back to see what was kept. | <S###> |
```

Registry entry (my `rows.json` uses the url/sha/quote source shape from the item; the counter wants row/file/line):

```json
{"id": "<F28-XX>", "field": "preserved_tokens",
 "set": {"preserved_tokens": ["upon", "upon", "a"]},
 "outcome": {"kind": "effective", "key": "preserved_tokens", "value": [261, 407]},
 "meaning": "<the meaning cell above>",
 "source": {"row": "<S###>", "file": "server-schema.cpp", "line": 316}}
```

Outcome text must be exactly `200, preserved_tokens = [261, 407]` (`canon` of the value, spaces after commas);
value cell `["upon", "upon", "a"]`; meaning cell has 32 words (≥ 6 required). Do **not** turn the three
no-rows into rows: `echo`/`reasoning_control` rows would be the `source-blind`/`echo` control's fabrication,
and a `grammar_triggers` row would need a two-key request.

## Risks / limits on this evidence

- The stored ids come from the pinned `stories260K.gguf` vocab; a different model changes them. They were
  stable across three separate server lifetimes on 48213.
- `base_effective` is `[]` for the row (measured, p01/q02); the no-rows have `null` because no key exists to
  compare.
- Identical requests produce different response bytes (seed/timings), so the two repeat bodies differ in sha;
  the `generation_settings.preserved_tokens` value is what is claimed and it was identical.
- `preserved_tokens` drops strings that tokenize to more than one token **silently** (200, no error), and
  leading-space forms (`" the"`, `" upon"`) are multi-token in this vocab; clients must read the key back.
- No installs/updates were needed this seat; no blockers.
