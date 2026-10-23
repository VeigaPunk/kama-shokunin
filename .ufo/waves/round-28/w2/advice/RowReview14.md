# RowReview14 — FALSIFY F28-27 / F28-28 (Round 28 WAVE 2)

Item: kama C1 rows F28-27 (`min_keep`, L183, S166) and F28-28 (`lora`, L229, S167).
Method: pinned server `~/.local/opt/llama-b11755/llama-server -m ~/.cache/kama-shokunin/models/stories260K.gguf --host 127.0.0.1 --port 48314` (started, killed, `ss -ltnp` confirms 48314 closed); requests exactly `POST /completion` body `{"prompt":"Once upon a time","n_predict":1}` plus the row's `set`, and the field-omitted base. Raw server-schema.cpp fetched from GitHub at 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad: sha256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050` (matches pin/snapshot). No tool installs performed.

## F28-27 min_keep (S166, L183-184) — holds

Live re-measure:
- base (no field): 200, `generation_settings.min_keep = 0`.
- set `min_keep: -1`: **400**, body sha256 `bfce3536f68a4117810229d171770eddcdc26c75607f526f46313b978027b8af` (byte-identical to receipt), message exactly `Field 'min_keep': Value must be between 0 <= value <= 2147483647, but got -1`.
- Edge probes: `2147483647` → 200, stored 2147483647; `2147483648` → 400 (message prints wrapped `-2147483648`), so the entire out-of-range claim holds above INT32_MAX too; `1.5` → 200 stored 1 (truncation, not this row).

Source: L183 `add((new field_num("min_keep", params.sampling.min_keep))`, L184 `->set_hard_limits(0, INT32_MAX)` — hard limits fully explain the 400 with named bounds. Source verdict: explains observed outcome.

Prose (SKILL.md row F28-27): "A min_keep outside 0..2147483647 is refused with HTTP 400 naming the hard bounds, so clients must send an in-range integer and treat the 400 as their own request error." Every statement verified by measurement (incl. above-INT32_MAX refusal). No correction needed. Holds.

SOURCES/Gate: S166 URL raw fetch sha256 matches pin; quote `add((new field_num("min_keep", params.sampling.min_keep)) ->set_hard_limits(0, INT32_MAX)` = whitespace-joined L183-184, occurs verbatim in normalized snapshot; Gate line L183 correct; seat DataG09 claim consistent. Holds.

Receipt: F28-27 is in `counted_ids` (why []). Right: re-measure reproduces 400 + exact bounds; REJECT_RE path would pass.

## F28-28 lora (S167, L229-237) — holds

Live re-measure:
- base: 200, `generation_settings.lora = []`.
- set `lora: [{"id":0,"scale":1.0},{"id":0,"scale":0.5}]` → **200**, `generation_settings.lora = [{"id":0,"scale":0.5}]` (single id-keyed entry, last scale 0.5 wins). Response sha256 `20b83bf1bc2df8528dd1332245dc0e8baa89abac044b025584a2a12621743bf5`; receipt recorded `e300eb9a…` — bytes differ (nondeterministic sampling fields in the body), but the stored lora effective value is identical, so this is not a data discrepancy.

Source: L229 `add((new field_json("lora"))`, handler L231-237: rejects non-array with `std::runtime_error` then `ctx.params.lora = parse_lora_request(lora);`. `parse_lora_request` at server-common.cpp:280-292 (fetched @ same commit) inserts `lora[id] = scale` into `std::map<int,float>` — a map keyed by adapter id, so duplicate ids collapse and the last assignment wins. Source fully explains the measured outcome (the dedup logic lives outside the pinned server-schema.cpp snapshot, but is confirmed both by code at the pinned commit and live behavior). Source verdict: explains.

Prose (SKILL.md row F28-28): "Duplicate adapter ids collapse to one id-keyed entry and the last scale wins, so clients must send at most one lora entry per adapter id." Exactly what measurement and `parse_lora_request` show. No correction needed. Holds.

SOURCES/Gate: S167 URL raw fetch sha256 matches pin; quote = whitespace-joined L229-230 cut at 25 words (`…Adapters not listed default to`, mid-phrase per documented convention), occurs verbatim in normalized snapshot; Gate L229 correct; the lesson's Mistakes table notes this quote was machine-corrected after seat-supplied misquote — confirmed fixed. Holds.

Receipt: F28-28 is in `counted_ids` (why []). Right: re-measure gives 200 + same effective; not identity (list != sent list), not generic conversion (list), not default (base lora []).
