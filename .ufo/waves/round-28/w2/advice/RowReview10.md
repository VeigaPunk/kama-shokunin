# RowReview10 — F28-19 / F28-20

Axes checked: live request outcomes, schema explanation, meaning prose scope, source URL/quote integrity, and frozen-counter verdict.

## Shared verification

- Started the pinned `~/.local/opt/llama-b11755/llama-server` with the assigned port 48310 and exact requested argv; SHA-256 `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`. Pinned implementation library SHA-256 `e404b91a81c9ab65756b6a57b97b42115a5f429c5060c4b7f0d717ca595b59ed`; model SHA-256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`.
- Used the counter's exact JSON request bytes (same property order and spacing), `POST /completion`, with the field omitted for each base and with only the row's `set` added for its tested request. Both base requests returned 200.
- Fetched the Gate raw URL at commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`; fetched-file SHA-256 `1f9d7b73b4363b90b08de0360b0a5ce0b3d152750bfb8d587a367e90c7904050`, equal to the pinned snapshot and the full hash recorded in the Gate. The Gate quotations below match the fetched lines verbatim after its stated whitespace-join rule.
- Stopped the server process group after requests; `ss -ltnp 'sport = :48310'` showed no listener. LSP was unavailable (`read xd://lsp` reported no such device; only `ast_edit` and `debug` are mounted). Literal grep located table/source rows only; findings below rely on file reads and live responses, not grep as semantic proof.

## F28-19 — `dry_penalty_last_n = -1`

- **Live:** field-omitted base: HTTP 200, `generation_settings.dry_penalty_last_n = 64`, response SHA-256 `f7d1fa4f5331b9bbc221ea3c60393c4655e7265ae30eedf25bb485c5c4f1690b`. With `dry_penalty_last_n: -1`: HTTP 400, message `Field 'dry_penalty_last_n': Value must be between 0 <= value <= 2147483647, but got -1`, response SHA-256 `fb708366138df18698b3ddc500807c88f64887e9474dfd40698e647e7187188a` (matches registry live evidence).
- **Source:** pinned `server-schema.cpp:153-155` declares the field, applies `set_hard_limits(0, INT32_MAX)`, and describes its function. This directly explains the observed lower-bound rejection and exact bounds.
- **Meaning verdict: partly holds.** The rejection claim and bounds are supported for the measured `-1` and by the hard-limit declaration. “Clients must clamp” and “operators should treat the 400 as final” are operational prescriptions not established by this measurement or cited schema; clamp is one possible response, not a requirement shown here. Suggested replacement: “In this b11755 `/completion` fixture, `dry_penalty_last_n = -1` returns HTTP 400 with bounds 0..2147483647; the schema declares those hard limits.”
- **SOURCES/Gate:** S158 links the correct commit and declaring line (SOURCES.md:170); Gate line 96 gives the correct raw URL, line and quote: `add((new field_num("dry_penalty_last_n", params.sampling.dry_penalty_last_n)) ->set_hard_limits(0, INT32_MAX)` (5 words). The raw fetch hash matches the pinned source; URL/quote hold.
- **Count:** counted. The fresh-clone receipt lists F28-19 in `counted_ids` with `why: []`; this verdict is right: static row/source checks pass and the measured 400 bounds match the registered outcome.

## F28-20 — `mirostat = 5`

- **Live:** field-omitted base: HTTP 200, `generation_settings.mirostat = 0`, response SHA-256 `7db819e36c3aa480df4013c8ca74757938ea5cc9b3eaedbe51b5351365c3ae48`. With `mirostat: 5`: HTTP 200, `generation_settings.mirostat = 2`, response SHA-256 `0d60023a21883e5fc4ce08f0868fae1969ffc3c09a82c8e8621f43c1f0bcccfa`.
- **Source:** pinned `server-schema.cpp:157-159` declares `mirostat`, specifies soft limits `0..2`, and labels 0/1/2; there is no custom handler on this declaration. This range plus the live 5→2 result explains the observed clamp in this build; it does not establish sampling quality or outcomes on other builds/endpoints.
- **Meaning verdict: mostly holds, with an overstrong directive.** The measured `5 → 2`/HTTP 200 and source range agree. The section preface scopes this to the b11755 fixture and says one row is one observed point, so the row is not an unqualified cross-build claim. However, “must read generation_settings” states necessity not shown by the measurement/source (it is a sensible way to verify the effective value). Suggested replacement: “On this b11755 `/completion` fixture, sending `mirostat = 5` returns HTTP 200 and `generation_settings.mirostat = 2`; the schema declares soft limits 0..2, so read back settings when you need to confirm the effective mode.”
- **SOURCES/Gate:** S159 links the correct commit and declaring line (SOURCES.md:171); Gate line 97 gives the correct raw URL, line and quote: `add((new field_num("mirostat", params.sampling.mirostat)) ->set_limits(0, 2)` (5 words). The raw fetch hash matches the pinned source; URL/quote hold.
- **Count:** counted. The fresh-clone receipt lists F28-20 in `counted_ids` with `why: []`; correct because its source/table structure passes, the observed effective value is 2 (not sent 5 and not omitted-base 0), and no A1 generic-conversion exclusion applies.
