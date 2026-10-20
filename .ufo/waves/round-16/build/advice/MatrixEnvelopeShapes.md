# KamaR16.MatrixEnvelopeShapes — advice (round 16, build wave)

## Files changed
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/EnvelopeShapes.json` (new; only file written). JSON array, 9 tests, all `EnvelopeShapes.*`, all `port_mode: "stub"`, `default_route: null`, `--expect "*"`. Validated only by `json.load` round-trip (72,036 bytes); no probe invocation.

## Family coverage — malformed/adversarial 503 `/v1/models` bodies
| test | body | expected |
|---|---|---|
| InvalidJsonBody | truncated JSON text containing all triple tokens (body_text) | FOREIGN_SERVICE / non-2xx-non-model-http / 2 |
| TopLevelArray | `[{"error":{exact triple}}]` | FOREIGN_SERVICE / non-2xx-non-model-http / 2 |
| ErrorAsString | `{"error":"Loading model"}` | FOREIGN_SERVICE / non-2xx-non-model-http / 2 |
| MissingCode | error object with exact message+type, no code | FOREIGN_SERVICE / non-2xx-non-model-http / 2 |
| CodeAsString | `code:"503"` (string, not integer) | FOREIGN_SERVICE / non-2xx-non-model-http / 2 |
| ExtraFieldsAllowed | exact `error` triple + extra top-level siblings | MODEL_LOADING / llamacpp-loading / 2 |
| NestedEnvelope | `{"outer":{"error":{exact triple}}}` — one level deeper | FOREIGN_SERVICE / non-2xx-non-model-http / 2 |
| Padding64KiB | exact triple + 65,536-char extra `pad` field | MODEL_LOADING / llamacpp-loading / 2 |
| BomPrefixedJson | U+FEFF + exact-triple JSON (body_text) | FOREIGN_SERVICE / non-2xx-non-model-http / 2 |

## Oracle derivation (never ran the probe)
- Exact-triple rule from C1 text: 503 AND JSON object whose `error` object has message == "Loading model", type == "unavailable_error", integer code == 503 — all exact, else keep current verdict. Every non-2xx non-HTML body without a model array currently lands at classify() `kama-probe.sh:520-522` → FOREIGN_SERVICE / non-2xx-non-model-http. Exit 0 iff MODEL_OK else 2 per the shared schema, so MODEL_LOADING exits 2.
- Two positive controls (ExtraFieldsAllowed, Padding64KiB) defeat a reject-all implementation; seven negatives defeat a loading-all/signature-grep implementation (truncated body containing all tokens, nested triple, string code).
- `CodeAsString` added beyond the named list: same family, cheap extra axis of strictness on `code`.

## Design choices / ambiguities
- NestedEnvelope uses `{"outer":{"error":{...}}}` rather than `{"data":{"error":{...}}}`: the nested `data` variant would hit `body_has_model_array`? No — `body_has_model_array` requires `data`/`models` to be a **list** (kama-probe.sh:403-405), and `served_ids` on an object `data` would be fragile. `outer` is unambiguous: no top-level `error` object.
- ExtraFieldsAllowed keeps `error` exactly the triple; "extra fields alongside" is read as top-level siblings only, not extra members inside `error`. If L1 wants permissive-extras-inside-error coverage too, that is a separate future test.
- BomPrefixedJson assumes strict JSON parsing (python `json.loads` rejects a leading U+FEFF; a grep fallback would match the tokens — flagged as an implementation-sensitive edge). If the repaired probe strips BOM, expectation must flip to MODEL_LOADING.
- All stub responses carry `Content-Type: application/json` (llama.cpp's actual loading response CT); status 503 keeps every case in the non-2xx branch, so Content-Type only matters for the 2xx schema-unrecognized fork, which none of these reach.
- `expect: "*"` throughout: expectation is irrelevant on non-2xx paths (model_matches is only consulted on the 2xx+model-array branch).

## Known limitations
- Oracles derived from C1 rule text + classify() source only; if the implemented loading check inspects members *inside* `error` differently (e.g., tolerates string code), MissingCode/CodeAsString expectations must be revisited.
- No `closed`-mode case — not in this family.
- BOM case is the most implementation-sensitive expectation (see above).
- No installs; no measurements run (L1 owns the matrix harness).
