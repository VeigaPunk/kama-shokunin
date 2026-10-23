# ScoutSkillContradictions — round-28 vs earlier SKILL and corpus/knowledge

Verdict: **partly**. The new section does not contradict earlier statements about temperature, stop, logit_bias, or sampling. It restates one already-admitted fixture fact (`n_parallel` / slots = 4). Its HTTP 400 field-bounds story does not deny older 400 classes, but those classes make a general reading of "the 400" false.

Searched: `SKILL.md` headings through line 1134 (round-28 section starts at 1135) and every file under `corpus/knowledge/`. No installs.

## Duplicate

1. **Default parallel / slot count is 4.** Already admitted for this build when `-np` is omitted.
   - Prior: `corpus/knowledge/context-capacity.md:63-65` — "Leaving `-np` unset makes the server use 4 slots and a unified cache (S108, server.cpp 169-174)." Cell K1 (`context-capacity.md:25`) observes `total_slots` 4 on the same fixture model.
   - New: `SKILL.md:1141` ("default argv … so `n_parallel` is 4"), `SKILL.md:1150` (n_cmpl upper bound is `n_parallel`), `SKILL.md:1165` (F28-06 "bounds 1 to 4" / "four here" / "server slots").
   - The n_cmpl *rejection* is new. The "four" is not. F28-06 does not repeat the unified-cache half of line 63, so it is a partial duplicate, not a second rule.

## Not contradictions (checked pairs)

2. **`generation_settings` is two objects.** Prior text is `GET /props` `default_generation_settings` (serving config / per-slot `n_ctx`): `SKILL.md:174`, `SKILL.md:687`, `corpus/knowledge/context-capacity.md:48-49`, `corpus/knowledge/gguf-declared-identity.md:28-29`, `corpus/knowledge/served-model-identity.md:10` and `:18-19`. New text is the completion *response* field (`SKILL.md:1147-1148`). Different names, different endpoints. No shared claim about sampling params inside `/props`.

3. **`n_predict`.** Prior use is in-range length on `/completion`: `context-capacity.md:122` (`n_predict` 600), `:127-129` (L2 "600 tokens each"), `:159-160` (25 passes, 26 fails), summarized without the field name at `SKILL.md:689` ("1000 + 600 token requests" → HTTP 500 on a shared pool). New: `SKILL.md:1142` (base body `n_predict` 1), `SKILL.md:1161` (F28-02 rejects -2, bounds -1..2147483647), `SKILL.md:1204-1205` (in-range value is echoed). Compatible: positive values the capacity cells sent are inside the F28-02 bounds. Not the same proposition (tokens generated vs value stored). F28-02's "send -1 for unbounded" does not say that generation then succeeds; `SKILL.md:689` / `context-capacity.md:127` still say pool overflow is HTTP 500.

4. **`ignore_eos` / `logit_bias`.** Prior only *sends* `ignore_eos` true (`context-capacity.md:122-123`). No prior sentence about `logit_bias`, temperature, stop strings, or sampler order exists in pre-1135 `SKILL.md` or `corpus/knowledge/`. F28-13 (`SKILL.md:1172`), F28-31 (`:1190`), F28-32 (`:1191`), F28-33 (`:1192`) do not collide with an earlier claim. F28-32 (ignore_eos injects token 2 into `logit_bias`) is additive to the capacity use of the flag.

5. **`cache_prompt`.** `context-capacity.md:169-170` says the server default is true and the L cells sent false. `SKILL.md:1197-1199` says the bool field stores the value sent (or is not reported). Compatible.

6. **`lora`.** `SKILL.md:1112` (E26-11) is `POST /lora-adapters`: non-array body is HTTP 400; `{id, scale}` entries are not validated; unknown ids ignored; omitted loaded adapters go to scale 0. `SKILL.md:1187` (F28-28) is the per-request `lora` field on `/completion`: duplicate ids collapse, last scale wins. Different route. "Not validated" does not assert that duplicate request-field ids are stored as sent.

7. **`--parallel 2` is a different server.** `SKILL.md:188-191` and `context-capacity.md:236-237` describe production `:34113` (`--parallel 2`, other build, explicit flag). `SKILL.md:1141` is the lane fixture with `-np` omitted. F28-06 already marks the upper bound launch-dependent (`SKILL.md:1150`, `:1165`). Not a contradiction. Applying "1 to 4" to that production process would be wrong; the section does not do that.

8. **`json_schema`.** `corpus/knowledge/echo-discriminating-counters.md:53-56` says a response_format type *other than* `text`, `json_object`, or `json_schema` is returned as HTTP 400. `SKILL.md:1206-1207` says `json_schema` is compiled into `generation_settings.grammar`. Complementary, not the same sentence.

9. **`reasoning_format` understatement (not a literal contradiction).** `echo-discriminating-counters.md:49-66` says b11755 splices decoded request values into error text and lists `chat.cpp:874` `reasoning_format` among those frames. The HTTP 400 status in that paragraph is stated for the response_format throw (`:54-56`), not restated per frame. `SKILL.md:1207-1210` says `reasoning_format` has "no bounds message and no stored transform." That denies the numeric-bounds template and a stored rewrite; it does not deny the echo-frame throw. Reading it as "a bad reasoning_format is ignored" would be wrong. The words on the page do not say that.

## HTTP 400 — adjacent, harmful only if generalized

`SKILL.md:1145-1146` states what `set_hard_limits` does: HTTP 400 `Field '<name>': Value must be between …`. It does not say every HTTP 400 is that template. Older 400s on the same fixture/build are different faults:

| Prior | Lines | 400 means |
|---|---|---|
| E26-03 slot restore | `SKILL.md:1104` | same body for missing file, bad slot file, and KV too small; log distinguishes. Not final from the body. |
| E26-06 pooling | `SKILL.md:1107` | launch pooling, not a request-field bound |
| E26-07 embeddings body | `SKILL.md:1108` | missing `input`/`content` |
| E26-11 lora route | `SKILL.md:1112` | body must be an array |
| E26-14 prompt shape | `SKILL.md:1115` | prompt element type |
| context overflow vs per-slot ceiling | `context-capacity.md:163-165` | `exceed_context_size_error` (1000 tokens > 512) |
| pool overflow while generating | `SKILL.md:689`, `context-capacity.md:127` | HTTP **500**, not 400 |
| response_format echo | `echo-discriminating-counters.md:54-61` | 400 body contains the caller's decoded string |

F28 reject rows (`SKILL.md:1160-1166`, `:1174`, `:1177-1178`, `:1183`, `:1186`, `:1189`) are a seventh class. F28-19 (`SKILL.md:1178`) "treat the 400 as final" and F28-27 (`SKILL.md:1186`) "treat the 400 as their own request error" are true only for that row's bounds message. Lifted to HTTP 400 in general they contradict E26-03 (`SKILL.md:1104`) and the capacity 400 (`context-capacity.md:164`).

`SKILL.md:1126-1128` says 26 request-validation messages were seen and not registered. It does not quote bounds or name these fields, so the F28 table does not duplicate that paragraph.

## Absent

No pre-1135 `SKILL.md` sentence and no `corpus/knowledge/` sentence states a temperature range, a stop-sequence shape, a logit_bias encoding, or that sampling used a stored `generation_settings` value. Nothing there to contradict F28-08..F28-13 or F28-31..F28-34 except the ignore_eos *use* in item 4.

Confidence: high on the duplicate and on the absent temperature/stop/logit_bias claims (string search of both trees). Medium on item 9 (echo entry does not pin reasoning_format's status code).
