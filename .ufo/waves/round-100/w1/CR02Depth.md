# CR02Depth — C2 depth critique (kama round 100, w1)

Axes (SCORECARD `## Axes`): operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7.
C2 works **depth** (lowest). This report attacks the C2 move only:
`tools/kama-probe.sh` `router_autoload()` at M `2e27e6f1e6b2514ec8ac5d6344998b3db61e16d6`
reads the bare `/props` body only when curl's final `%{http_code}` is exactly 200
(`[ "$pcode" = 200 ] || return 2`, probe lines 898-904).

Frozen predicate: `ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True`
(`plans/round-100-claims.md` §C2; `.ufo/waves/round-100/measured/c2.out:19`, exit 0).

## 1) Router-shaped body under non-200: real-world case or stub artefact?

Real-world case, not a stub artefact. Three independent intermediaries produce exactly this shape:

- **Reverse proxy / gateway error interception.** nginx `proxy_intercept_errors on` replaces a
  `>=300` upstream body with a locally generated error page while preserving the non-200 status
  (or normalising it, e.g. `error_page 500 502 503 504 =503 /errors/5xx.html`); without
  interception the upstream body passes through. Either way a client can receive a body that did
  not come from `get_router_props`. Sources (accessed 2026-11-08):
  <https://nginx.org/r/proxy_intercept_errors>,
  <https://nginx.org/en/docs/http/ngx_http_proxy_module.html>,
  <https://docs.nginx.com/nginx/admin-guide/content-cache/content-caching/>.
- **Cache.** nginx `proxy_cache` can store and later serve a proxied `GET` response; error
  statuses are cacheable unless explicitly disabled (`proxy_cache_valid 404 0` etc.), so a stale
  router-shaped body can be re-served under a cached error status. Same sources as above.
- **Auth gateway in front of llama-server.** llama.cpp's own auth model makes this the common
  path: `GET /props` requires `Authorization: Bearer <key>` (or `X-Api-Key`); a gateway that
  clears/replaces the header (`proxy_set_header Authorization ""`), or validates a public key
  and forwards it unchanged, yields a `401 Invalid API Key` document at `/props` even when the
  backend router is healthy, and a body that may be the gateway's own document rather than the
  router configuration. Sources (accessed 2026-11-08):
  <https://docs.keephq.dev/providers/documentation/llamacpp-provider>,
  <https://llama.app/docs/api>,
  <https://markaicode.com/integrate/nginx-with-llamacpp/>.

The probe's own comment names this class: `tools/kama-probe.sh:895-896` — "a router-shaped body
under a non-200 status (a proxy, a cache, a redirect page) is unread, never an explicit on/off
answer." The stub cells S1-S6 are therefore a faithful miniature of a documented intermediary
behaviour, not an invented shape. The pre-round-100 failure mode was severe: four of the six
cells graded `MODEL_OK` / `router-unloaded-autoload` / exit 0 at base
(`.ufo/waves/round-100/measured/c2.out:2,4,5,6` — a false cold start).

Limit disclosed honestly in the plan: `plans/round-100-claims.md:109` "(b) A 200 answer from a
non-router intermediary that returns a router-shaped body is still read." The rule is one-sided
by design (see §5).

## 2) Does reading /props only on 200 lose a legitimate configuration answer?

No legitimate loss is reachable through this probe. Passing HTTP statuses that carry a usable
body:

- **203 Non-Authoritative Information** — a transforming proxy altered the origin's `200`
  response content/metadata (RFC 9110 §15.3.4; MDN). The body is explicitly *not* guaranteed
  byte-for-byte the origin's. For a probe whose whole point is "this is the router's own
  configured value" (S624: the body is built from `params.models_autoload`), reading a proxy-
  transformed body as the configuration would repeat the round-99 false-`MODEL_OK` bug in a new
  status. Unread is correct; the reason row already tells the operator to re-probe `/props`
  (`SKILL.md` §Round-88 decision table, unread row, action column).
  Sources: <https://www.rfc-editor.org/rfc/rfc9110.html> (accessed 2026-11-08),
  <https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Status/203> (accessed 2026-11-08).
- **304 Not Modified** — carries *no body at all*; the client reuses its cached representation
  (`SKILL.md` §Round-100 table row 3: "anything, including a router document"). The probe sends
  an unconditional `GET` with no `If-None-Match`/`If-Modified-Since`, so a correct origin never
  answers 304 to it; only a broken proxy that ignores the missing conditional can. There is no
  configuration to lose.
  Sources: <https://www.rfc-editor.org/rfc/rfc9110.html>,
  <https://developer.mozilla.org/pt-BR/docs/Web/HTTP/Reference/Status/304> (accessed 2026-11-08).
- Other pass-through 2xx (206 Partial Content, 204 No Content) are likewise not answers to an
  unconditional bare `GET /props` from llama.cpp (`get_router_props` returns a full JSON body
  with 200 per S624/S631); 204 has no body and 206 requires a `Range` header the probe never
  sends.

Cost of the rule is one wasted re-probe in the 203 case, not a wrong verdict: the verdict stays
fail-closed (`MODEL_UNLOADED`, exit 2) either way, and the reason changes from a possibly-false
explicit state to an honest unread. Commands: `git show 2e27e6f1:tools/kama-probe.sh | sed -n
'898,905p'` shows the gate is status-only, no `-L`, no conditional headers.

## 3) Are S629-S631 sufficient grounding for the rule as worded?

Yes. The three rows jointly prove the exact sentence in `SKILL.md` §Round 100 ("llama.cpp answers
a refused request with its own status and an error document, never with the configuration"):

- **S629** (`corpus/SOURCES.md:384`): API-key middleware `res.status = 401` + `Invalid API Key`
  document (`server-http.cpp:291-299`); readiness middleware `res.status = 503` + `Loading model`
  (`server-http.cpp:315-321`). Snapshot `.ufo/waves/round-100/sources/S629-server-http-middleware.txt:6-17,31-41`.
- **S630** (`corpus/SOURCES.md:385`): `format_error_response` (`server-common.cpp:93-124`) maps
  handler errors to 400/401/403/404/500/501/503 — every handler error is non-200. Snapshot
  `.ufo/waves/round-100/sources/S630-server-common-error-status.txt:6-37`.
- **S631** (`corpus/SOURCES.md:386`): upstream's own router test asserts
  `res.status_code == 200` (line 20) *before* reading `res.body["models_autoload"]` (line 23).
  Snapshot `.ufo/waves/round-100/sources/S631-test-router-props.txt:11-15`.

S631 is the load-bearing row: it shows the upstream authors pair status-200 with reading the
field, so the probe's gate is not the lane's invention. The knowledge entry
(`corpus/knowledge/router-props-autoload.md:51-55`, §Round 100) cites the same three rows for
the same sentence, and §Round-99 already held the field's origin (S624 `server-models.cpp:2030`,
S625 `common.h:705`, S627 `arg.cpp:3682` — see `corpus/SOURCES.md:379-382`). No fourth row is
needed for the rule as worded; a row about intermediary behaviour (nginx) would ground the
*illustrative* proxy/cache sentence, which the entry correctly presents as the stub cells'
motivation rather than as llama.cpp evidence.

## 4) Decision row vs round-90 frozen reason-codes table

Consistent, by deliberate non-registration. Verified by command
(`git show 2e27e6f1:SKILL.md`, split at `## Probe reason codes` / `## Serving timeout`):

- The `## Probe reason codes` table has 32 rows (23 frozen population + `body-too-large` and
  siblings); there is **no `| `router-autoload-unread` |`** row among them (recount command in
  scratch run: rows=33 including one stray prose row, `has unread reason row: False`).
- The round-88 decision table's unread row (`SKILL.md:1773`) names the reason explicitly:
  "`MODEL_UNLOADED` / `router-autoload-unread`, drift, exit 2" and lists "a final HTTP status
  other than 200" among unread causes — matching the round-100 gate word for word.
- SKILL.md §Round 99 states the design: "the round-90 `## Probe reason codes` table below stays
  byte-identical... `router-autoload-unread` is documented here and in the decision row above,
  not as a row there (a row there cannot bind without editing the round-90 instrument — CN01's
  A/B/C fixtures)" (`SKILL.md:1832-1833`). The round-90 counter
  (`tools/round90-reason-rows.py`) binds rows to capture receipts; adding a row would require a
  receipt line and would edit a frozen instrument. Documenting the reason in the decision row
  instead is the consistent, non-destructive choice.
- One residual soft spot (not a falsification): the frozen `router-unloaded` reason-table row
  (`SKILL.md` reason table, last router row) still defines the trigger as "the probe could not
  confirm autoload: `GET /props` did not answer `role: router` with `models_autoload: true` (a
  no-autoload router, or a `/props` that failed, was over the 4 MiB cap, or was not JSON)". At
  the tip the probe *can* also return `router-unloaded` only via the 200-off path (probe
  `router_refine`, `tools/kama-probe.sh:985-988`: unread is chosen when `ra=2`, else `$down` which
  for an explicit off is `router-unloaded`). The table row's parenthetical therefore overstates
  `router-unloaded` slightly post-round-100, but the decision table (the operative rule) is
  exact, and the round-90 table is frozen by design. This is a known-frozen staleness, already
  disclosed by the §Round-99 paragraph, not a contradiction introduced by C2.

## 5) Does the wording overreach?

The frozen counter (`tools/round100-props-status.py:4-10`) grades nine statuses/bodies; the
plan's disclosed limit `(d)` states (plans/round-100-claims.md:112-113): "The cells cover the
nine statuses/bodies listed; other non-200 statuses follow the same `[ \"$pcode\" = 200 ]` line
but are not each graded." The claim title — "the probe reads the router's bare `/props` body
only on a final HTTP 200" — is exactly what the code does: the gate is one comparison
(`tools/kama-probe.sh:904`), not a table of graded statuses. The six graded non-200 statuses
(401, 500, 503, 403, 202, 302) include the *dangerous* ones (router-shaped body that flips the
verdict, S2/S4/S5/S6) plus both middleware statuses (401, 503) and the exact llama.cpp 401
document (S7); P1/P2 are positive controls that kill a blanket refusal (mutant receipt
`controls/c2-mutant-blanket.out` fails P1+P2). The nine-cell coverage is therefore a
representative cut, honestly disclosed, and the underlying rule is total.

**Narrowing sentence (the only candidate, already in the plan):** disclosed limit `(b)` —
"A 200 answer from a non-router intermediary that returns a router-shaped body is still read"
(`plans/round-100-claims.md:109`; repeated in `SKILL.md` §Round-100 "Limits" and
`corpus/knowledge/router-props-autoload.md:70`). The wording "only on a final HTTP 200" is a
status rule, not a provenance guarantee, and the plan says so. This narrows the *claim's*
promise, not the counter's property — the counter does not claim to detect a 200-forgery, and
the plan never says it does. Under the Amendment-59 defect class (a counter green on a property
narrower than the claim's wording), this would be a narrowing only if the claim's wording
asserted intermediary-proofing. It does not: §C2's predicate is the status sentence, and the
limits list is part of the claim text.

No `falsifies-wording`, no `falsifies-number` found. One deliberate non-finding: the reason-table
`router-unloaded` trigger parenthetical (§4) is stale by one clause, but the claim's own wording
does not cite the reason table as its contract — it cites the decision row and §Round-100 rule,
both exact.

## Evidence trail (commands)

- `cat plans/round-100-claims.md` §C2; `cat .ufo/waves/round-100/claims.json` C2 block.
- `cat .ufo/waves/round-100/measured/c2.out` (tip `mismatches=0 flips=6 stable=3 met=True exit=0`,
  line 19-20; base false `MODEL_OK` lines 2,4,5,6).
- `git show 2e27e6f1:tools/kama-probe.sh | sed -n '885,930p'` — gate line 904 and the
  explanatory comment 889-897.
- `git show 2e27e6f1:SKILL.md | sed -n '1765,1800p;1830,1865p'` — decision row (line 1773),
  §Round-99 byte-identical note, §Round-100 rule + table + Limits.
- `cat corpus/knowledge/router-props-autoload.md` (§Round 100 lines 51-70); `grep -n "S629\|S630\|S631\|S624\|S625" corpus/SOURCES.md` (lines 379-386).
- `cat .ufo/waves/round-100/sources/S629-*.txt`, `S630-*.txt`, `S631-*.txt` — snapshots.
- Reason-table recount: python split of `git show 2e27e6f1:SKILL.md` at
  `## Probe reason codes` — 32 reason rows, no `router-autoload-unread` row.
- Web (access date 2026-11-08, in-text URLs): nginx proxy/cache/error-page docs; RFC 9110
  (203/304); llama.app/Keep/nginx-llama.cpp auth guides.

No tooling installed (system tools only). Scratch: `/fast/scratch/hyaku/kama-r100/CR02Depth/`
(created for the recount, no clone kept, deleted before yield). Receipts copied to
`.ufo/waves/round-100/w1/out/CR02Depth/`: `reason-table-recount.txt`.

VERDICT C2 neutral C2 is a genuine depth move: the non-200 router-shaped body is a real intermediary case (nginx proxy/cache/auth gateway), 203/304 lose nothing legitimate, S629-S631 fully ground the status-pairing sentence, and the decision row is consistent with the frozen round-90 population; the only narrowing (a 200-forgery is still read) is already disclosed in the plan's limits, so the counter is not green on a narrower property than the wording.
