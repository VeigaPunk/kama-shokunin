# DataG12 — Round-28 C1 data seat report

- Seat: `KamaR28.DataG12-2` (data, W1). Assigned port **48212** (only; never 47600-47619).
- Server: `~/.local/opt/llama-b11755/llama-server` → `version: 0.7.0-dev (build 11755, commit 704366d76)` — exactly the pinned snapshot commit.
- Model: `~/.cache/kama-shokunin/models/stories260K.gguf`. Server launched with the exact required argv under `timeout 900`, process group killed afterwards; port 48212 verified closed (`ss -ltnp`).
- Pinned source read: `.ufo/waves/round-28/sources/llama.cpp-704366d/server-schema.cpp` (sha256 `1f9d7b73...7904050` matches the snapshot) and `server-task.cpp` (generation_settings keys).
- Raw fetch: `curl` of `https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-schema.cpp` → status 200, 29572 bytes, sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` (identical), accessed `2026-10-23T08:34:25Z`.

## Outcome: 0 countable rows, 4 no-rows

`rows.json` = `{"rows": [], "no_rows": [4]}`. Live evidence for every entry was produced by my own runs on port 48212; raw response bodies are in `out/DataG12/raw/` (12 files, each < 2 KiB).

| Field | Decl line | Handler/limits line | generation_settings key | Live observed | Verdict |
|---|---|---|---|---|---|
| `json_schema` | 252 | 255 (handler; no set_limits/set_hard_limits) | `grammar` (server-task.cpp:131) | 200; grammar = `root ::= ("true" \| "false")\nspace ::= \| " " \| "\n"{1,2} [ \t]{0,20}\n`; base grammar `` | Transform real, row **not representable** (see blocker) |
| `grammar_lazy` | 287 | null | `grammar_lazy` (server-task.cpp:132) | 200; true stored as true, base false | Identity → not countable; non-boolean → 400 type_error, not bounds |
| `reasoning_format` | 294 | 296 (handler) | `reasoning_format` (server-task.cpp:136/77) | 200; accepted names `none/auto/deepseek/deepseek-legacy` echoed verbatim; default `deepseek`; unknown → 400 `Unknown reasoning format: X` | Identity → not countable |
| `continue_final_message` | 300 | 302 (handler) | none | 200 for `true`/`"content"`/`"reasoning_content"`; no generation_settings key appears; invalid → 400 `Invalid continue_final_message: expected a boolean, "content" or "reasoning_content"` | Parsed and discarded → not countable |

### json_schema blocker (important for L1)

The field has genuine non-trivial behaviour — a JSON schema is compiled to a GBNF grammar stored under `generation_settings.grammar`, which differs both from the value sent and from the default `""`. However, **no countable row can be written for it**: `json_schema_to_grammar` always appends a `space` rule containing literal `|` characters (`space ::= | " " | "\n"{1,2} [ \t]{0,20}`) — observed on all 8 probed schemas (boolean, const string, const 42, enum, string/maxLength 0, null, integer, empty-object handling). The counter's `count-c1.py` parses SKILL table rows by naive `.split("|")` (`static_checks`), so the canonical outcome text `200, grammar = "…|…"` can never occupy one of the six cells; the row is skipped as unparseable. Escaping as `\|` fails the verbatim substring check. `json_schema` therefore cannot contribute a counted row under the frozen counter; L1 should exclude it from the table (or document it in prose outside the counted table). Invalid schemas (e.g. `true`) reject with `Field 'json_schema': "json_schema": JSON schema conversion failed: …`, not the bounds message.

### Notes for L1 integration

- For any *other* field whose effective value is a GBNF string (e.g. `grammar` itself), the same pipe limitation applies — only pipe-free effective values can be counted.
- All four assigned fields have **no** `set_limits`/`set_hard_limits`, so no reject-with-bounds row can come from this seat.
- The would-be json_schema row (blocked): field `json_schema`, set `{"json_schema": {"type": "boolean"}}`, outcome `{"kind": "effective", "key": "grammar", "value": "root ::= (\"true\" | \"false\")\nspace ::= | \" \" | \"\\n\"{1,2} [ \\t]{0,20}\n"}` — delivered only as evidence, since it cannot be placed in the counted table.
- No tools installed, no pacman transactions (pacman paused host-wide). No lane/fleet files modified; only the two output files listed below were written.

## Evidence files (all in `out/DataG12/raw/`)

| File | sha256 | What it is |
|---|---|---|
| `base_200.json` | `4e96beeb…e886ea14` | Base request (no field): `generation_settings` |
| `json_schema_boolean_200.json` | `0936155731…ba1927` | `json_schema: {"type":"boolean"}` → 200, grammar transformed |
| `grammar_lazy_true_200.json` | `94851b4324…e899c` | `grammar_lazy: true` → 200, stored true |
| `grammar_lazy_string_400.json` | `43a706424f…3f2b5` | `grammar_lazy: "true"` → 400 type_error |
| `grammar_lazy_number_400.json` | `c01a006bcd…66038dd` | `grammar_lazy: 1` → 400 type_error |
| `reasoning_format_none_200.json` | `3a4710a85f…e87562` | `reasoning_format: "none"` → 200, stored `none` |
| `reasoning_format_auto_200.json` | `6191db6c4f…1f1f52` | `auto` → 200, stored `auto` |
| `reasoning_format_deepseek-legacy_200.json` | `baa39db266…4e974d` | `deepseek-legacy` → 200, stored `deepseek-legacy` |
| `reasoning_format_bogus_400.json` | `4d5b131a07…63670` | `bogus` → 400 `Unknown reasoning format: bogus` |
| `continue_final_message_true_200.json` | `fd3e18721e…253e0` | `continue_final_message: true` → 200, key absent |
| `continue_final_message_content_200.json` | `4b5d0dd61e…870aea` | `"content"` → 200, key absent |
| `continue_final_message_42_400.json` | `8e33dfa2e6…cc2aba` | `42` → 400 invalid-value message |

## Verification summary

- `rows.json` parses; exactly `{"rows": [], "no_rows": [4]}`; every `no_rows[].live` is from my runs on 48212 (effective values match the raw bodies above; base_effective values come from `base_200.json`).
- No row met the countable predicate: no reject-with-bounds (no hard limits on these fields), no effective value differing from both sent and default that is table-representable.
- Determinism check: json_schema grammar identical across two runs (`stable: True`).

## Risks / blockers

1. **json_schema countable-row blocker** (counter table parser cannot hold `|`-bearing canonical text) — the only field in this seat with non-trivial behaviour. Other seats must supply the 18 counted rows.
2. None otherwise: no crashes, no 500s, no other-server-flag requirements observed.
