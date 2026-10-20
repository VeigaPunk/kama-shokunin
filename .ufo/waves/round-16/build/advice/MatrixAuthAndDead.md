# MatrixAuthAndDead — stub-matrix family `AuthAndDead`

## Files written
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/AuthAndDead.json` — 7 tests, JSON array, parses cleanly (validated with `python3 -c json.load` + schema assertions; no probe execution).

## Design choices
All oracles derived from `tools/kama-probe.sh` classify() source order, never by running the probe:

1. **Early-return ordering** is the load-bearing fact: `fetch` rc mapping (DEAD/NOT_HTTP, lines 424–456) → status branch `case "$F_CODE"` 401/403 → `UNAUTHORIZED_SERVICE` with `return 0` (lines 458–465) → only then body inspection (`body_has_model_array`, HTML sniff, and where MODEL_LOADING will sit). So auth verdicts are body-independent.
2. `401-authentication-error-envelope` / `403-authentication-error-envelope`: llama.cpp `authentication_error` envelopes under `Server: llama.cpp` → `http-401` / `http-403`.
3. `401-carrying-loading-envelope` / `403-carrying-loading-envelope`: body is the exact `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` loading envelope at 401/403. Defeats two overbroad implementations: a body-only MODEL_LOADING matcher (fires regardless of status) and a misplaced check that precedes the auth branch.
4. `401-plain-text-body`: status-only keying; confirms a body_content requirement is not introduced on the auth path.
5. `closed-port-connection-refused` (`port_mode: closed`): no listener → curl rc=7 → DEAD `connection-refused` (lines 426–430).
6. `raw-accept-then-close` (`{"raw":"close"}` on `/v1/models`): TCP accept, zero bytes, close → curl rc=52 → NOT_HTTP `empty-reply` (lines 436–440).
7. All `expect: "*"` — auth/dead/not-http verdicts never reach `model_matches`, so `--expect` is inert for this family; exit 2 uniformly (only MODEL_OK exits 0).

## Known limitations
- No MODEL_OK positive control in this file — sibling families own those; this family is strictly negative-path coverage.
- `expect` is not varied (e.g. a concrete model id vs `*`) since it cannot influence these verdicts; varying it would be a no-op duplication.
- Harness must implement `{"raw": "close"}` and `closed` port_mode per the shared schema; if the stub binds lazily per-port these are still unambiguous.

## Installs
None. No pacman transactions (host-wide pause honored); only `python3` stdlib used for JSON validation.
