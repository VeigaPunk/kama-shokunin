VERDICT: partial — all 7 AuthAndDead oracles (verdict, reason, exit) are correct by the C1 rule and the landed `classify()`; one `why` misattributes a synthetic 403 envelope to b11755, the family has no 401/403 + HTML-body cell (verified escape of a plausible mutant), and one row is mutation-redundant.

Seat: KamaR16.FamilyAuthAndDead (leaf). Attacked `tests/probe-verdicts/AuthAndDead.json`, all 7 rows, plus the design rationale in `.ufo/waves/round-16/build/advice/MatrixAuthAndDead.md`.

# Environment / identity
- landed `tools/kama-probe.sh` sha256 `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50`
- frozen `.ufo/waves/round-16/frozen/kama-probe-before.sh` sha256 `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64` = manifest sha (manifest.json:3)
- curl 8.23.0, Python 3.14.8. No servers started; `pgrep -x llama-server` exit 1 (none), `ss -ltn | grep -E ':(8080|34113)\b'` exit 1 (nothing bound).

# What I ran (all commands from `tests/probe-verdicts`)
Run template (`ONLY` = the 7 `--only AuthAndDead.<n>` flags):

```
python3 check.py --probe ../../tools/kama-probe.sh $ONLY --json   -> exit 0, 7/7 pass
python3 check.py --probe ../../.ufo/waves/round-16/frozen/kama-probe-before.sh $ONLY --json -> exit 0, 7/7 pass
```

Observed rows (landed; frozen identical on all 7):

| row | observed verdict / reason / exit | expected | source of truth |
|---|---|---|---|
| 401-authentication-error-envelope | UNAUTHORIZED_SERVICE / http-401 / 2 | same | landed:494-501 (status case before body checks); `corpus/knowledge/llamacpp-loading-lifecycle.md:57` |
| 403-authentication-error-envelope | UNAUTHORIZED_SERVICE / http-403 / 2 | same | landed:495-496 |
| 401-carrying-loading-envelope | UNAUTHORIZED_SERVICE / http-401 / 2 | same | landed:494-501 precedes 503-508; F_CODE≠503 |
| 403-carrying-loading-envelope | UNAUTHORIZED_SERVICE / http-403 / 2 | same | same |
| 401-plain-text-body | UNAUTHORIZED_SERVICE / http-401 / 2 | same | landed:494-496 (status-only) |
| closed-port-connection-refused | DEAD / connection-refused / 2, evidence `rc=7 Failed to connect ...` | same | landed:462-466 |
| raw-accept-then-close | NOT_HTTP / empty-reply / 2, evidence `rc=52 empty reply on a TCP-accepted port` | same | landed:472-476 |

`drift` was true on all 7 and `check.py` asserts `drift == (verdict != MODEL_OK)` (check.py:340-347). All `expected.exit` are 2, consistent with `validate_test` (check.py:141-146). The frozen probe passes all 7, so no row in this family discriminates C1 — consistent with the claimed changed set (the 17 `MODEL_LOADING` rows), and there is no cross-family duplicate: only AuthAndDead asserts `UNAUTHORIZED_SERVICE`, `DEAD connection-refused` and `NOT_HTTP empty-reply` among the 72 rows.

# Findings by severity

## Medium — no 401/403 + HTML-body cell; the family's "auth is body-independent" claim is untested against the HTML sniff
`classify()` sniffs HTML at any status (landed:510-518) and emits `FOREIGN_SERVICE html-non-model` at 549-554, i.e. below the auth branch. No row anywhere puts `text/html` on a 401/403 (`grep '"status": 401|403|text/html' *.json`: AuthAndDead has only 401/403 with JSON/text bodies; ForeignControls' HTML rows are 200, NearMissTriple/Overbroad503 HTML rows are 503). I hoisted the HTML sniff + branch above the auth case (mutant `M_hoist_html`, scratch copy, full-file text surgery in /tmp):

```
python3 check.py --probe M_hoist_html.sh $ONLY --json   -> exit 0, 0 failures (all 7 rows pass)
```
A hypothetical row `401 + Content-Type: text/html` in a /tmp copy of the harness:
```
vs landed        -> exit 0, UNAUTHORIZED_SERVICE/http-401, passed True
vs M_hoist_html  -> exit 1, FOREIGN_SERVICE/html-non-model, passed False
```
So the mutant is invisible to the current family and a one-row addition kills it. Suggested row (not written — outside my write scope):

```json
{
  "name": "AuthAndDead.401-html-body",
  "family": "AuthAndDead",
  "why": "401 with a text/html body: the auth branch (kama-probe.sh:494-501) precedes the any-status HTML sniff (kama-probe.sh:549-554) -> UNAUTHORIZED_SERVICE http-401, never FOREIGN_SERVICE html-non-model.",
  "port_mode": "stub",
  "routes": {"/v1/models": {"status": 401,
    "headers": {"Content-Type": "text/html; charset=utf-8"},
    "body_text": "<html><body>Unauthorized</body></html>"}},
  "default_route": null,
  "expect": "*",
  "expected": {"verdict": "UNAUTHORIZED_SERVICE", "reason": "http-401", "exit": 2}
}
```
(Same shape at 403 is optional; the 401 cell is enough to kill the preemption mutant.)

## Minor — `403-authentication-error-envelope`'s `why` misattributes a synthetic envelope to llama.cpp
`AuthAndDead.json:24` says: "403 with llama.cpp authentication_error envelope: status branch ... -> UNAUTHORIZED_SERVICE http-403." The oracle is right, the engine attribution is not:
- b11755 API-key failure is **401** `{"error":{"message":"Invalid API Key","type":"authentication_error","code":401}}` — `server-http.cpp:290-298`.
- Every 403 in the pinned tree is `feature_disabled` / "this feature is disabled" — `server.cpp:343-352` (only `/cors-proxy`, `/tools`), or `permission_error` — `server-common.cpp:111-114`. `authentication_error` is hard-wired to code 401 (`server-common.cpp:99-102`).
- `GET /v1/models` 403 is not producible at this build in single-model mode.
Fix: drop "llama.cpp" (e.g. "403 with an authentication_error-shaped envelope (synthetic; b11755 403 is feature_disabled)"). Note the row intentionally omits `Server: llama.cpp` (evidence shows `Server: kama-stub`), unlike row 3 — keep that asymmetry deliberate or align it.

## Minor — the rationale in `MatrixAuthAndDead.md` overstates what rows 3/4 defeat (oracle unaffected)
`build/advice/MatrixAuthAndDead.md` item 3 claims the loading-body rows defeat "a misplaced check that precedes the auth branch". They cannot: the loading check requires `F_CODE = 503` (landed:503), and a 401/403 is never 503, so ordering between the two branches is unobservable. Mutants:
```
M_reorder          (loading block hoisted above auth, 503 gate intact)      -> exit 0, all 7 pass
M_bodyonly         (503 conjunct dropped, block left after auth)            -> exit 0, all 7 pass
M_reorder_bodyonly (hoisted AND body-only)                                  -> exit 1, rows 401/403-carrying-loading fail with MODEL_LOADING
```
So rows 3/4 are the sole killers of the composite mutant and are still worth keeping; only the mechanism wording is wrong. The `why` texts themselves are defensible ("... and the status is not 503" / "a body-only MODEL_LOADING matcher would false-pass here") — they describe a body-only matcher in place of the whole verdict, not a mere reorder.

## Nit — row 1's message casing and the frozen numbering
- `AuthAndDead.json:8` body message is `"Invalid API key"`; upstream emits `"Invalid API Key"` (`server-http.cpp:294`; `README.md:2327`). The probe never reads the body, so this is fixture realism only.
- All four `why` citations are exact **frozen** line numbers and stale against landed by +36: `459→495`, `460→496`, `426-430→462-466`, `436-440→472-476` (verified: `diff <(sed -n '458,465p' frozen) <(sed -n '494,501p' landed)` and the rc block at frozen 424-440 vs landed 460-476 are identical). This is the whole matrix's convention (ForeignControls cites the same base), but nothing declares it; landed `kama-probe.sh:459` is blank and `:460` is `case "$F_RC" in`. L1 should pick one global rule: label "frozen numbering" in a header or re-base citations.

# Redundancy / discrimination (mutation evidence, each run against the 7 rows)
| mutant | exit | rows failed |
|---|---|---|
| `M_drop401` (remove 401 mapping) | 1 | 1, 3, 5 |
| `M_drop403` (remove 403 mapping) | 1 | 2, 4 |
| `M_jsonauth` (auth only if body contains `authentication_error`) | 1 | 3, 5 |
| `M_parseauth` (auth only if body parses as JSON) | 1 | 5 |
| `M_reorder`, `M_bodyonly` | 0 | none |
| `M_reorder_bodyonly` | 1 | 3, 4 (`MODEL_LOADING`) |
| `M_hoist_html` | 0 | none |
| `M_rc7_dns` (rc 7 → dns-failure) | 1 | 6 |
| `M_rc52_reset` (rc 52 → connection-reset) | 1 | 7 |

Reading: rows 3/4, 5, 6, 7 each uniquely kill a mutant no other row kills; row 2 shares `M_drop403` with row 4 but is the only row carrying an auth-envelope body at 403; **row 1 is near-dominated by row 5** — every mutant that killed row 1 also killed row 5 (`M_drop401` kills 1,3,5; `M_parseauth` kills only 5), and the only way to kill row 1 alone is an absurd "auth only for text/plain" probe. [INFERENCE] Row 1 remains the canonical documented wire shape and costs one row; keep it unless the wave enforces minimality, in which case it is the first candidate. No row is a literal duplicate of another.

# Residual risk / verification gaps
- I ran only the 7 AuthAndDead rows (plus a hypothetical 8th in /tmp); not the full 72, not `--selftest`, and I did not invoke `measure.py` (prohibited).
- Rows 3/4 are wire shapes b11755 cannot emit (`llamacpp-loading-lifecycle.md:35`: a loading server with `--api-key` answers 503, not 401), so they are probe-logic guards, not runtime fixtures. That is acceptable for a stub matrix but should not be cited as observed engine behavior.
- `closed` mode has the documented bind-close TOCTOU (VerdictHarness.md Limitations); observed rc=7 every run here, and a wrong verdict would fail loudly, not pass silently.
- `/tmp/kama-r16-FamilyAuthAndDead` scratch (mutant scripts + receipts) was removed after writing this report; mutants are reproducible by the text surgery described above.

# Installs
None. No pacman/uv/npx/cargo transactions; host-wide pacman pause untouched.
