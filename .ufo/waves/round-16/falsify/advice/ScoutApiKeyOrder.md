VERDICT: confirm — llama.cpp @704366d76 `server-http.cpp` runs OPTIONS → state gate → API-key check in that order (state gate does precede auth), and `AuthAndDead.json`'s 401/403-carrying-loading rows are probe-precedence guards, not claims about llama.cpp; one collateral defect found (their `why` line citations are 36 lines stale).

# Two propositions attacked

- **P1 (source ordering).** In `tools/server/server-http.cpp` @ `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (= release b11755, S036) the pre-routing handler short-circuits `OPTIONS`, then runs `middleware_server_state`, then `middleware_validate_api_key`.
- **P2 (row semantics).** `AuthAndDead.{401,403}-carrying-loading-envelope` in `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/AuthAndDead.json` test *probe* branch precedence; they are not statements about what llama.cpp emits.

# P1 — confirmed at source, pinned copy re-verified against upstream

Pinned tree: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-16/sources/llama.cpp-704366d/`. Re-fetched the raw blob and compared digests (`curl` exit 0):

| file | sha256 (pinned copy == fresh fetch) |
|---|---|
| `server-http.cpp` | `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb` |

`server-http.cpp:331` registers one pre-routing handler; inside it, in order:

```
346|        // If this is OPTIONS request, skip validation because browsers don't include Authorization header
347|        if (req.method == "OPTIONS") {
...
351|            res.set_content("", "text/html"); // blank response, no data
352|            return httplib::Server::HandlerResponse::Handled; // skip further processing
353|        }
354|        if (!middleware_server_state(req, res)) {
355|            return httplib::Server::HandlerResponse::Handled;
356|        }
357|        if (!middleware_validate_api_key(req, res)) {
358|            return httplib::Server::HandlerResponse::Handled;
359|        }
```

- State gate body (`middleware_server_state`, declared `307-328`): `308 if (!is_ready.load())`, `314 res.status = 503`, `318 {"message", "Loading model"}`, `319 {"type", "unavailable_error"}`, `320 {"code", 503}`. Its only exemption is frontend assets: `309 if (frontend_paths.count(req.path))`.
- Auth (`middleware_validate_api_key`, `260-305`): exempts `get_public_endpoints` = `{"/health","/v1/health"}` + frontend paths (`251-258`), so `/v1/models` is *not* public; failure is `290 res.status = 401`, `294 {"message", "Invalid API Key"}`, `295 {"type", "authentication_error"}`, `296 {"code", 401}`.

So `354` (state) precedes `357` (auth) unconditionally, and `347-353` (OPTIONS) precedes both. Consequence: a 401 is only reachable when `is_ready` was true at `354`, therefore a real server's 401 body is always the `authentication_error` envelope, never the loading envelope. Confirms knowledge entry `corpus/knowledge/llamacpp-loading-lifecycle.md:33-35`, whose citation `server-http.cpp:347-359` is accurate.

`is_ready` is only ever stored `true` in the pinned set (`server.cpp:460` router mode, `server.cpp:515` direct mode); no `store(false)` exists, so there is no ready→loading flip race inside one request. [INFERENCE] status for an OPTIONS reply is 200: llama.cpp sets no status and leaves it to cpp-httplib's default; httplib is not pinned, so this is not observed here and nothing in the probe depends on it.

# P2 — confirmed: the rows test probe precedence, and they are not upstream behaviour

Three independent lines of evidence.

1. **The probe's own order.** `/home/vgpnk/Projects/shokunin/kama-shokunin/tools/kama-probe.sh:494-497` is the status case (`401) UNAUTHORIZED_SERVICE; http-401`, `403) … http-403`) with `return 0` at `498-501`; the loading branch is later, at `503-508` (`[ "$F_CODE" = "503" ] && … body_is_llamacpp_loading`). `body_is_llamacpp_loading` has exactly one call site (`503`). A 401/403 therefore exits before the body is consulted — matching each row's `why` text.
2. **The rows do not discriminate round 16.** `check.py` against the frozen pre-round probe passes all 7 AuthAndDead rows (7/7), including both carrying-loading rows — the 401/403 arms are byte-identical in frozen (`458-461`) and current (`494-497`) probes. These rows are invariant guards, not new-behaviour rows.
3. **Decisive counterfactual.** I built a scratch variant that moves the exact same loading test ahead of the status case (`/tmp/…/probe-bodyfirst.sh`, only `[ "$F_CODE" = "503" ]` dropped and the block moved; `bash -n` exit 0). Under it the two carrying-loading rows flip to `MODEL_LOADING llamacpp-loading` and fail, while the ordinary 401 row still passes → the pair has exactly the discriminating power the `why` claims ("a body-only MODEL_LOADING matcher would false-pass here").

Empirical runs (`tests/probe-verdicts/check.py`, JSON to /tmp):

| probe | rows | pass/fail | check.py exit |
|---|---|---|---|
| `tools/kama-probe.sh` (sha256 `6edd3c4c…`) | all 7 AuthAndDead | 7 / 0 | 0 |
| frozen `kama-probe-before.sh` (sha256 `93ee4302…`, == `frozen/manifest.json`) | both carrying-loading | 2 / 0 | 0 |
| frozen | all 7 AuthAndDead | 7 / 0 | 0 |
| body-first scratch variant | 401-carrying, 403-carrying, plain 401 | 1 / 2 | 1 |

Current-probe records: 401-carrying → `UNAUTHORIZED_SERVICE http-401`, `probe_exit 2`, evidence `GET /v1/models -> 401 application/json (Server: llama.cpp); 404| @ /` — the evidence string contains nothing body-derived, i.e. the body was never read. Same for 403-carrying.

Why the rows cannot be upstream behaviour: (a) upstream ordering above forbids it; (b) the stub bodies are not upstream bytes — the 401 stub says `"Invalid API key"` while `server-http.cpp:294` says `"Invalid API Key"`; (c) upstream's only 403 emitter is `server.cpp:343-353` (`res_403`, `{"message","this feature is disabled"},{"type","feature_disabled"}`, no `code`) wired only to `/cors-proxy` (`374-375`) and `/tools` (`404-405`), never `/v1/models`, so a 403 on `/v1/models` is unproducible at this build; (d) `ERROR_TYPE_AUTHENTICATION` / `ERROR_TYPE_PERMISSION` are declared and switched (`server-common.cpp:99-102,111-114`) but **never invoked** anywhere in the pinned set, so there is no second permission-shaped 401/403 path. The rows' own `why` text cites probe lines, not server lines.

# Findings for L1 (actionable, outside my write scope)

1. **Stale citations in `AuthAndDead.json` (defect introduced by round 16).** Every `why` line reference is pre-round numbering, uniformly **+36** off after `body_is_llamacpp_loading` (`428-447`) and the `503-508` branch were inserted: `426-430`→`462-466`, `436-440`→`472-476`, `459`→`495`, `460`→`496`. The claims stay true; the pointers now land on unrelated lines (e.g. current `460` is `case "$F_RC" in`). No other family is affected: the other eight JSONs either cite no probe lines or cite current ones (`ForeignControls.json` `506-511/514-519/520-522` resolve correctly today). Fix = add 36 to those four references, or drop line numbers in favour of symbol names (`middleware`→`classify`/status case).
2. **Probe comment overstates the gate.** `tools/kama-probe.sh:421` says "while is_ready is false every non-frontend path returns 503"; upstream also short-circuits `OPTIONS` before the gate (`server-http.cpp:347-353`), so an OPTIONS during loading is not a 503 [INFERENCE on the 200 status]. Harmless to the probe (it only issues `GET /v1/models`), but the comment is not literally true. Suggest "every non-frontend non-OPTIONS path".
3. **Fidelity nit.** `AuthAndDead.401-authentication-error-envelope` claims a "llama.cpp authentication_error envelope" but its message casing differs from `server-http.cpp:294` (`key` vs `Key`). Since the probe never parses auth bodies this is cosmetic; relabel the row "shaped like" or fix the casing so a future body-aware matcher is not misled.
4. **Cross-report note (sibling, not mine to resolve):** `ExecApiKeyLiveOrder.md` independently confirmed P1 live (5/5 launches, unkeyed 503 `Loading model` during the ~8 ms window). Its table column is headed "unkeyed 401 pre-ready" while its prose says every unkeyed 401 came strictly after the last 503 and after ready. If the column label were literal it would refute the gate-first claim; the prose (and the source, and my counterfactual) say it is a label error. Flagging only so L1 does not read the table as a contradiction.

# Commands run (all exits stated)

- `sha256sum` over the four pinned files; `curl -sS -m 20` of the raw `server-http.cpp` at the commit → exit 0, digest identical to the pinned copy and to `pins.json`.
- `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json --only <7 AuthAndDead names>` → exit 0, 7/7.
- same with `--probe .ufo/waves/round-16/frozen/kama-probe-before.sh` → exit 0, 2/2 (carrying rows) and exit 0, 7/7 (full family).
- `bash -n /tmp/kama-r16-ScoutApiKeyOrder/probe-bodyfirst.sh` → exit 0; `check.py --probe /tmp/.../probe-bodyfirst.sh --only <3 names>` → exit 1, 1 pass / 2 fail (`MODEL_LOADING`).
- `pgrep -x llama-server`: one transient match (PID 39645) during the run that vanished before `/proc/39645` could be read; it was a sibling seat's live-harness server, not mine — I started no server. No listener on 8080 or 34113 (`ss -ltnp` empty for both). I did not run `measure.py`.

# Limitations

- Only static evidence establishes P1 here; the live receipt `…/.ufo/waves/round-16/live/receipt.json` has `loading_observed: false` and its argv carries no `--api-key`, so it cannot speak to auth ordering at all. Live corroboration exists only in the sibling `ExecApiKeyLiveOrder` report.
- `is_ready` declaration/default lives in `server-http.h`, which is not in the pinned set; I verified all reads/writes in the four pinned files only.
- httplib's OPTIONS status default is [INFERENCE]; nothing depends on it.
- I did not start a server (not authorised for this seat), so I add no new live measurement for P1.

# Files

Report only. Scratch `/tmp/kama-r16-ScoutApiKeyOrder/` (four check.py JSONs, `upstream-server-http.cpp`, `probe-bodyfirst.sh`) removed after capture; every result above is reproducible from the named commands.

# Installs

None. No tool installed, upgraded or removed; no pacman transaction attempted.
