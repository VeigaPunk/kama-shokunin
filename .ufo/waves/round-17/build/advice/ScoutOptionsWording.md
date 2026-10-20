VERDICT: confirm — the lane's loading-gate wording overstates by one method; `OPTIONS` is answered before the state gate, so "every non-frontend path" needs an explicit carve-out in six editable files, while one matrix row and one SOURCES cell are frozen by contract.

# Scope, authority, method

Read-only scout. No edits outside this Report; no runtime, probe, gate, or measurement was run.

- Pinned authority: `.ufo/waves/round-16/sources/llama.cpp-704366d/server-http.cpp`, 940 lines, sha256 `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` — byte-identical to the digest S036 records (`corpus/SOURCES.md:48` "raw file sha256 24ede172…"). The pinned copy is what I read; I did not fetch the GitHub URL.
- Search (recursive, exclusions `--exclude-dir=interactive-sessions --exclude-dir=.git --exclude-dir=.jj`, `.ufo/waves` outputs skipped per the item): `non-frontend|frontend_paths|frontend path|loading gate|no endpoints are allowed|every request|all requests|any request|every path|all paths|any path|all endpoints|any endpoint|every endpoint|whole server|every route|all routes|before the API.?key`. The only loading-gate universal claims are the seven editable statements plus the frozen matrix fields (X1-X2) and the S036 cell (X3) listed below.
- Checked clean (no universal gate claim, no correction needed): `corpus/knowledge/consumer-registry.md:409`, `corpus/knowledge/listener-census.md:393`, `corpus/knowledge/served-identity-crosswalk.md:141-143` (single-route claims about `GET /v1/models` only); `LOG.md`, `SCORECARD.md`, `AGENTS.md`, `MINT.md`, `SHONEN.md`, `PROVINCE.md`, `README.md`, `registry/`, `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/*` contain no such claim.
- Behavioral neutrality: no probe, stub, check, live-tool, or receipt file sends `OPTIONS` (`grep -n OPTIONS tools/kama-probe.sh tests/probe-verdicts/check.py tools/kama-llamacpp-live.py tests/llamacpp-live/check-receipt.py` → no matches), and the stub serves every method through one route table (`tests/probe-verdicts/check.py:253-257` "Serve every HTTP method through the same route table."). The defect is documentary; no graded row outcome changes.

# Observed facts in the pinned copy (server-http.cpp)

| span | observed | quote / code |
|---|---|---|
| 307-328 | gate lambda | `auto middleware_server_state = [this](const httplib::Request & req, httplib::Response & res) {` |
| 308 | gate condition | `if (!is_ready.load()) {` |
| 309-311 | only path exemption | `if (frontend_paths.count(req.path)) {` → `return true; // frontend asset, allow it to load and show "loading"` |
| 312-313 | intent comment | "no endpoints are allowed to be accessed when the server is not ready" (14 words) |
| 314 | status | `res.status = 503;` |
| 318 | message literal | `{"message", "Loading model"},` |
| 319 | type literal | `{"type", "unavailable_error"},` |
| 320 | code literal (integer) | `{"code", 503}` |
| 323 | content type | `"application/json; charset=utf-8"` |
| 331 | pre-routing handler | `srv->set_pre_routing_handler([&params, middleware_validate_api_key, middleware_server_state](const httplib::Request & req, httplib::Response & res) {` |
| 346 | OPTIONS comment | "If this is OPTIONS request, skip validation because browsers don't include Authorization header" (13 words) |
| 347 | OPTIONS condition | `if (req.method == "OPTIONS") {` |
| 351 | OPTIONS body | `res.set_content("", "text/html"); // blank response, no data` |
| 352 | OPTIONS return | `return httplib::Server::HandlerResponse::Handled; // skip further processing` |
| 353 | block close | `}` |
| 354 | state gate runs after OPTIONS | `if (!middleware_server_state(req, res)) {` |
| 357 | API-key check after state gate | `if (!middleware_validate_api_key(req, res)) {` |
| 242-248 | `frontend_paths` definition | `std::unordered_set<std::string> paths { "/" };` plus `paths.insert("/" + a.name);` |
| 251-255 | API-key public set (not the gate's set) | `"/health",` `"/v1/health",` plus frontend paths |

Derived truth (the wording every correction below must carry): while `is_ready` is false, **every non-frontend request whose method is not `OPTIONS`** answers the 503 envelope (status 314; `message`/`type`/`code` at 318/319/320) **before** the API-key check (354 before 357). `OPTIONS` never reaches either middleware: the pre-routing handler answers it with CORS headers and a blank `text/html` body at 346-353 and returns `Handled` at 352. Frontend paths (242-248) are the only *path* exemption; `/health` is public to the *API-key* middleware (253) but is still gated while loading because 354 precedes 357.

# Statements found, and the correction each needs

Editable (correction appended at end of file, per `corpus/QUALITY.md` KQ7 "every correction appended at the end of its file"; the existing files already use this pattern):

| # | path:line | quote (≤25 words) | defect | correction |
|---|---|---|---|---|
| S1 | `corpus/knowledge/llamacpp-loading-lifecycle.md:9` | "A single-model llama-server answers almost every request with HTTP 503" | vague universal; excludes the very OPTIONS case the same entry records at line 33 | A |
| S2 | `corpus/knowledge/llamacpp-loading-lifecycle.md:29` | "answers every other path, `/health` and `/v1/models` included, with status 503" | path-true, method-false; contradicts line 33 ("The pre-routing handler short-circuits `OPTIONS`, then runs the state gate") | A |
| S3 | `corpus/knowledge/endpoint-identity.md:202` | "middleware answers every non-frontend path with that 503 body while not ready" | overstates by the OPTIONS method | B |
| S4 | `corpus/knowledge/runtime-health-surface-matrix.md:64-65` | "the loading window is served by the 503 middleware on every non-frontend path" | overstates by the OPTIONS method | C |
| S5 | `corpus/README.md:206` | "every non-frontend path 503 before the API key" | overstates by the OPTIONS method (the outside check's named case) | D |
| S6 | `SKILL.md:519-520` | "every non-frontend path while loading, before the API-key check" | overstates by the OPTIONS method; body quote already cites no per-field lines | E |
| S7 | `tools/kama-probe.sh:422-423` | "while is_ready is false every non-frontend path returns 503 with the exact envelope" | code comment overstates by the OPTIONS method | F |

Frozen / excluded (no edit; reason and residual record):

| # | path:line | quote (≤25 words) | why no change |
|---|---|---|---|
| X1 | `tests/probe-verdicts/LoadingEnvelope.json:143` | `"name": "LoadingEnvelope.every-non-frontend-path"` | hard constraint: the nine matrix files stay byte-identical; current sha256 `12bc261c595115446dbf592d1ff479c1351229f504a0016f5ef8c0ab05306f03`; `.ufo/waves/round-16/measure.py:281` pins `EXPECTED_MATRIX_SHA256 = "bf9068d8…"` |
| X2 | `tests/probe-verdicts/LoadingEnvelope.json:145` | "returns the envelope for EVERY non-frontend path while !is_ready" | same freeze; also not graded: `check.py:341-343` compares `record["verdict"] == expected["verdict"]`, reason and exit, and `:346` asserts drift; `why`/`name` are carried into records (`:288` `"why": test["why"]`) but never compared |
| X3 | `corpus/SOURCES.md:48` (S036 `teaches`) | "Every non-frontend path, `/v1/models` and `/health` included, answers 503" | contract rule 2 (`SOURCES-CONTRACT-v1.md`): "Only `status`, `recheck` and `used-by` change in place" — the cell cannot be edited; the carve-out is already appended at `corpus/SOURCES.md:135-136`: "S036: \"every non-frontend path\" excludes `OPTIONS`, which is answered at server-http.cpp:347-353 before the state gate" |
| X4 | `corpus/lessons/round-16-verifier-spotcheck.md:131,185` | "\"every non-frontend path\" overstates by one method" / "to exclude OPTIONS, which bypasses the gate" | old lesson; contract forbids editing old lessons; it already states the defect (this is defect 4's source) |
| X5 | `corpus/lessons/round-16.md:46` | "no endpoints are allowed to be accessed when the server is not ready" | verbatim upstream comment quote, not a lane scope claim; historical lesson |

# Exact appended-correction text

## A — end of `corpus/knowledge/llamacpp-loading-lifecycle.md` (after line 148)

```markdown
## Correction — round 17 (2026-10-20): the gate is path-scoped and method-scoped

Line 9's "almost every request" and line 29's "answers every other path" overstate
by one method; line 33's ordering bullet is the correct statement. At
`server-http.cpp:307-328` the gate exempts only the exact `frontend_paths` set
(`/` plus embedded UI assets, 242-248) at 309-311, and sets status 503 at 314 with
`message`/`type`/`code` at 318/319/320. `OPTIONS` never reaches it: the pre-routing
handler answers `OPTIONS` with CORS headers and a blank `text/html` body at
346-353 (condition 347, `return ... Handled // skip further processing` 352),
before the state gate at 354 and the API-key check at 357. Precise claim: while
`is_ready` is false, every non-frontend request whose method is not `OPTIONS`
answers the 503 envelope ahead of the API-key check; `/health` and `/v1/models`
are both on that side. The body-shape match, the router/sleep limits and the
probe mapping are unchanged.
```

## B — end of `corpus/knowledge/endpoint-identity.md` (after line 216)

```markdown
## Correction — round 17 (2026-10-20): "every non-frontend path" is not every method

Line 202's "every non-frontend path" is exact for paths, not for methods.
`OPTIONS` is answered before the state gate: CORS headers, a blank `text/html`
body and `return ... Handled // skip further processing` at `server-http.cpp:346-353`
(condition 347, return 352), ahead of the state gate at 354 and the API-key check
at 357. The 503 envelope reaches every non-frontend request except `OPTIONS`;
status at 314, `message`/`type`/`code` at 318/319/320
(`Loading model`, `unavailable_error`, integer `503`), content type at 323.
Frontend paths remain the only path exemption (242-248, 309-311). The verdict
table and its rule order are unchanged.
```

## C — end of `corpus/knowledge/runtime-health-surface-matrix.md` (after line 75)

```markdown
## Correction — round 17 (2026-10-20): the round-16 scope sentence is method-blind

The round-16 text above at lines 64-65 ("the 503 middleware on every non-frontend
path") holds for requests, not for `OPTIONS`. `OPTIONS` is answered by the
pre-routing handler before the state gate (CORS headers, blank `text/html`,
`return ... Handled`, `server-http.cpp:346-353`, condition 347, return 352), so
the 503 envelope (status 314; `message` 318, `type` 319, `code` 320) reaches every
non-frontend request except `OPTIONS`, ahead of the API-key check at 357.
`/v1/models` and `/health` are both gated: `/health` is public to the API-key
middleware (251-255) but the state gate runs first (354 before 357).
```

## D — end of `corpus/README.md` (after line 228)

```markdown
Round-16 coverage-map correction (round 17, 2026-10-20). The
`knowledge/llamacpp-loading-lifecycle.md` row above says "every non-frontend path
503 before the API key". Narrow to requests: every non-frontend request except
`OPTIONS` gets the 503 envelope while not ready. The gate exempts `frontend_paths`
(242-248, 309-311) and 503s every other path (status 314; `message`/`type`/`code`
318/319/320), but `OPTIONS` is answered blank `text/html` with CORS headers before
the state gate at `server-http.cpp:346-353` (condition 347, return 352), ahead of
the API-key check at 357.
```

## E — end of `SKILL.md` (after line 552)

```markdown
Correction — round 17 (2026-10-20): line 519's error signature is path-scoped and
method-scoped. Every non-frontend request except `OPTIONS` answers that 503 body
while loading, before the API-key check; `OPTIONS` is answered before the state
gate with CORS headers and a blank `text/html` body (`server-http.cpp:346-353`,
condition 347, return 352) and never reaches it. Envelope literals: status 314;
`message` 318 `Loading model`, `type` 319 `unavailable_error`, integer `code` 320
`503`; content type `application/json; charset=utf-8` at 323.
```

## F — `tools/kama-probe.sh:422-423` (same-line-count replacement; no downstream shift)

The comment is code, not corpus, so it is corrected in place, but **the replacement must keep exactly two lines**: `corpus/knowledge/snapshot-history.md` cites probe lines 555-572, 833-903, 911-928 and 932-1003, and `endpoint-identity.md` cites 418, 516 and 723-733. Line 424 and everything after stay byte-identical.

Old:

```sh
# llama.cpp loading gate (b11755 tools/server/server-http.cpp:307-325): while
# is_ready is false every non-frontend path returns 503 with the exact envelope
```

New:

```sh
# llama.cpp loading gate (b11755 server-http.cpp:307-325, OPTIONS bypass 346-353): while
# is_ready is false every non-frontend request except OPTIONS returns 503 with that envelope
```

`# {"error":{"message":"Loading model","type":"unavailable_error","code":503}}.` on line 424 is unchanged.

## G — `corpus/SOURCES.md` (no cell edit; the cell is append-only)

The S036 `teaches` cell cannot change (`SOURCES-CONTRACT-v1.md` rule 2: "Only `status`, `recheck` and `used-by` change in place"). Two contract-compliant records are available. G1 is the minimum and follows the file's existing appended-note pattern (the round-11 to round-16 notes at lines 77-150 already sit after the Leads list); G2 is only if L1 wants a registry-level correction row.

Option G1 (recommended; append at end of file after line 150; no row, no cell change). It completes both halves of defect 4 — the OPTIONS carve-out and the 318/319/320 per-field anchors, which the round-16 note at lines 135-136 does not name.

```markdown
**Round-17 note on S036 (outside routed defect 4; no cell changes).** The
round-16 falsify note above already records that S036's "every non-frontend
path" excludes `OPTIONS`, answered at `server-http.cpp:347-353`. It does not name
the 503 body's per-field anchors: status 314, `message` 318, `type` 319, integer
`code` 320, content type 323; frontend paths are exempted at 309-311 from the set
defined at 242-248; the state gate at 354 runs before the API-key check at 357.
Precise claim: every non-frontend request except `OPTIONS` answers the 503
envelope before the API-key check. S036's cells stay byte-identical.
```

Option G2 (if L1 wants a formal contract-rule-2 correction row): mint the next free id (S042 unless another item claims it) with the next two cells as follows; all other cells follow the S036 shape (`code | A | ... | mined | 2026-10-20 | on-release | corpus/knowledge/llamacpp-loading-lifecycle.md`).

```text
anchor: lines 307-328 (gate and 503 body 314-325; 318 message, 319 type, 320 code;
        frontend exemption 309-311) and 346-353 (OPTIONS short-circuit; condition
        347, return 352), with the state gate at 354 before the API key at 357;
        same raw file sha256 24ede172…; at commit 704366d76 (single-model mode)
teaches: supersedes S036 — while `is_ready` is false every non-frontend request
         except `OPTIONS` answers 503 with `{"error":{"message":"Loading model",
         "type":"unavailable_error","code":503}}` before the API-key check;
         `OPTIONS` is answered by the pre-routing handler before the state gate.
```

Contract flags for G2: rule 1 requires the source to be opened in the round that writes the row — re-reading the lane's pinned copy is not a URL open, so a same-round pinned-URL re-open (or an explicit L1 ruling that the frozen copy counts) is required. [INFERENCE] Adding a registry row also changes registry census counts; verify against the round's own pins before minting.

# Limitations

- Read-only static reading; the `OPTIONS` response status is not asserted. `res.set_content("", "text/html")` leaves httplib's default status, so "blank `text/html` with CORS headers, not the 503 envelope" is observed; "HTTP 200" is [INFERENCE] and is deliberately not written into any correction text.
- I did not execute the probe, the stub matrix, the live harness, or any lane gate, and did not fetch the GitHub blob; source correspondence rests on the pinned copy's sha256 matching S036's recorded digest.
- `tests/probe-verdicts/LoadingEnvelope.json` is left untouched by design; its `why` and row name keep the older wording and are not graded (`check.py:341-346`). Any future prose that describes the matrix should state that the row's wording is descriptive, not an expectation of OPTIONS behaviour.
- `.ufo/waves/` outputs were skipped as sources of statements per the item; the only `.ufo` path read was the pinned `server-http.cpp` and `measure.py:281` for the digest pin.
- Installs/updates: none.
