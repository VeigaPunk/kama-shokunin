# Options corrections — llama.cpp loading-gate scope (draft, not applied)

Owner: ScribeOptionsCorrections (round 17, build wave). Status: draft for L1 to integrate. No lane document has been edited.
Access date for every source below: 2026-10-20.

Pinned source: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp` (940 lines; sha256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`, matching the digest recorded in `corpus/SOURCES.md` S036). Upstream: https://github.com/ggml-org/llama.cpp/blob/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.cpp

Located facts (all read in the pinned copy this session):
- `:242-248` `frontend_paths` = `"/"` plus each embedded UI asset.
- `:251-258` `get_public_endpoints` = `"/health"`, `"/v1/health"`, plus frontend paths. It is consulted only by the API-key check at `:267-268`, not by the loading gate.
- `:307-328` `middleware_server_state`: when `!is_ready.load()`, only `frontend_paths` (`:309-311`) return early; everything else gets `res.status = 503` (`:314`) and the envelope.
- `:318` `{"message", "Loading model"}`; `:319` `{"type", "unavailable_error"}`; `:320` `{"code", 503}`.
- `:346-353` the OPTIONS branch in the pre-routing handler; `:352` `return ... Handled` skips all later checks. Quote at `:347`: `if (req.method == "OPTIONS") {`.
- `:354` `middleware_server_state` is called before `:357` `middleware_validate_api_key`.

Unknown, stated plainly: this draft does not check the router-mode path (`server-models.cpp`) or whether a proxy in front of a child relays the envelope. Not in scope.

---

## Append A — `corpus/README.md` (append at end of file, after line 228 `Line 119's ... §Correction — round 16.`)

§Correction — round 16 (loading-gate scope, OPTIONS).

Line 206's row says the llama.cpp loading gate answers "every non-frontend path 503 before the API key". At b11755 (704366d76) the gate exempts only the frontend set (`/` and embedded UI assets, `server-http.cpp:309-311`). OPTIONS requests return earlier, in the pre-routing handler at `server-http.cpp:347-352`, and are not 503'd. Every other path, including `/health` and `/v1/models`, gets the envelope while `is_ready` is false; the state gate (`:354`) runs before the API-key gate (`:357`). Envelope fields: message `:318`, type `:319`, code `:320`. Source: llama.cpp 704366d76 `tools/server/server-http.cpp`, accessed 2026-10-20.

---

## Append B — `corpus/knowledge/endpoint-identity.md` (append at end of file, after line 216)

Correction to line 202 (2026-10-20, source accessed 2026-10-20). "Every non-frontend path" narrows to every path except the frontend set (`/` and embedded UI assets, `server-http.cpp:309-311`) and `OPTIONS` requests, which return before the gate at `server-http.cpp:347-352`. The envelope's type and code are at `:319-320`, beside the message at `:318`. `/health` and `/v1/health` are not exempt from the loading gate: the public-endpoint set at `:251-258` is consulted only by the API-key check (`:267`).

---

## Append C — `corpus/knowledge/runtime-health-surface-matrix.md` (append at end of file, after line 75)

Correction to line 65 (2026-10-20, source accessed 2026-10-20). "On every non-frontend path" narrows to every path except the frontend set (`server-http.cpp:309-311`) and `OPTIONS` (answered at `:347-352`, before the state gate at `:354`). `/v1/models` and `/health` remain inside the gate; the exempt set at `:251-258` is used only by the API-key check (`:267`). Envelope message, type and code: `:318-320`.

---

## Append D — `SKILL.md` (append at end of file, after line 553)

Correction to line 519 (2026-10-20, source accessed 2026-10-20). "Every non-frontend path ... before the API-key check" excludes `OPTIONS` requests, which the pre-routing handler answers at `server-http.cpp:347-352` before the state gate (`:354`). Exempt set is the frontend set only (`:309-311`); `/health` is gated. Type and code are at `:319-320` alongside the message at `:318`. The match rule in this section is unchanged.

---

## Append E (extra, same statement, not in the four named targets) — `corpus/SOURCES.md`, S036 cell

`corpus/SOURCES.md:48` (S036 "scope/teaches" cell) reads "Every non-frontend path, `/v1/models` and `/health` included, answers 503 ... before the API-key check while not ready." The registry contract (rule 2) allows only status/recheck/used-by to change in place, so do not edit the cell. Suggested append-only note at the end of `corpus/SOURCES.md` (after the Leads section): S036 correction (2026-10-20, source accessed 2026-10-20): the gate exempts `OPTIONS` (answered at `server-http.cpp:347-352`, before `:354`) as well as the frontend set (`:309-311`); envelope fields at `:318-320`. Named in `corpus/lessons/round-16-verifier-spotcheck.md:185` (item 4). L1 decides placement.

---

## Other located statements (not drafted; for L1 routing)

- `tools/kama-probe.sh:422-424` comment "every non-frontend path returns 503". Code comment in a tool owned by another seat; it needs the same OPTIONS note in its own change.
- `tests/probe-verdicts/LoadingEnvelope.json:143-145` test name `every-non-frontend-path`. Matrix fixture; the round-16 pin (`measure.py`) fixes these bytes, so do not edit. Route the name question to C1.
- `corpus/lessons/round-16-verifier-spotcheck.md:131` already records the OPTIONS nit; `corpus/lessons/` is not in this draft's scope.
- `.ufo/waves/round-16/build/advice/*` (for example `ConnectKengaku.md:45`) and round-17 advice carry the same phrase; they are wave artifacts, not lane docs, and are not drafted.
