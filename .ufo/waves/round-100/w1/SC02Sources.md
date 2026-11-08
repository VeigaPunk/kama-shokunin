# SC02Sources — round 100, C2 source re-opening (kama)

Seat: SC02Sources (source re-opening for C2). Scope: the three upstream b12177 files behind
S629/S630/S631, every llama.cpp path that can answer `GET /props` in router mode, and whether
S628's flip is S631. No tracked lane file was edited; nothing outside my out dir, my report and
my scratch was written.

## 0. Summary

Every one of the three C2 source rows re-fetches **byte-for-byte**: HTTP status, byte count,
sha256 and the quoted line ranges all match `corpus/SOURCES.md` and
`.ufo/waves/round-100/sources/S62*.txt` exactly. S628's flip **is** S631 — the rejected row's
flip text names the same file at the corrected path, and S631's line 23 carries the assertion
S628's flip text describes.

One defect class was hunted and one was found: the C2 counter's nine cells do **not** pin the
word **"bare"** in the claim's wording. A probe that reads `/props?model=fixture-model` instead
of bare `/props` grades **green** on the C2 counter (`mismatches=0 met=True`) and on the round-99
regression counter (`cells=8 mismatches=0 met=True`). This is a *narrowing* defect: the counter
is green on a probe that does not implement the claim's stated property.

Second, smaller narrowing: the counter's nine cells cover 401/500/503/403/202/302 but not **404**,
so a probe that additionally accepts a 404 body as configuration is also green (measured, below).

Both are narrowings of the *counter*, not of the sources. The sources themselves are sound.

## 1. Source re-opening — digests, sizes, quoted lines

Fetch method (each of the three, and S628's rejected path):

```
curl -sL -o fetch_<name> https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/<path>
```

| row | path | HTTP | bytes | sha256 (recomputed) | matches SOURCES.md |
|---|---|---|---|---|---|
| S629 | `tools/server/server-http.cpp` | 200 | 39157 | `aad15b757323f36b81235182c4a0a35d448399012ae3ef4fed9902b716fa17ea` | yes |
| S630 | `tools/server/server-common.cpp` | 200 | 79532 | `b686729ed7d098e2f0c3da1ba28325d0e6d30721dab09f71cb9b53f342710ddb` | yes |
| S631 | `tools/server/tests/unit/test_router.py` | 200 | 33103 | `fed2ff448c55422d64c4667aa40a8922e2f3fab01420ea35ccbfa875dfacd1ef` | yes |
| S628 | `tests/unit/test_router.py` | **404** | 14 (`404: Not Found`) | `d5558cd419c8d46bdc958064cb97f963d1ea793866414c025906ec15033512ed` | yes (rejection stands) |

Digests of all fetched files (including the supporting ones read for the path map) are in
`.ufo/waves/round-100/w1/out/SC02Sources/b12177-digests.txt`.

**Quoted-line verification** — I extracted each quoted range from the committed
`.ufo/waves/round-100/sources/S62*.txt` and compared it byte-for-byte with the same line range
of the freshly fetched upstream file:

```
S629: declared 290-325  match=True
S630: declared 93-124   match=True
S631: declared 14-25    match=True
```

Per-line spot checks against the fetched bytes (all exact):

- **S629** quotes `res.status = 401;` — upstream `server-http.cpp:291`; `{"message", "Invalid API Key"},`
  — `:295`; `res.status = 503;` — `:315`; `{"message", "Loading model"},` — `:319`. The row's stated
  ranges "291-299 and 315-321" and "lines 291, 295 / 315, 319" are all correct.
- **S630** quotes `json format_error_response(const std::string & message, const enum error_type type) {`
  — upstream `server-common.cpp:93`; `int code = 500;` — `:95`. The row's case list
  "400/401/404/500/403/501/503" matches the switch bodies at `:99,103,107,111,115,119,123`.
  (Upstream also has `ERROR_TYPE_EXCEED_CONTEXT_SIZE → 400` at `:125-128`, i.e. **outside** the row's
  cited 93-124 range; the row does not claim it, and 400 is already in the row's list, so the
  teaches-cell statement "error documents carry 400/401/403/404/500/501/503" remains true. Worth
  flagging as a precision nit for the L1: the *cited range* stops one case short of the switch.)
- **S631** quotes `assert res.status_code == 200` — upstream `test_router.py:20`; and
  `assert res.body["models_autoload"] is False` — `:23`. Both exact, and the order (200 first, field
  second) is exactly what S631's teaches cell claims.

**Counter's S7 cell body.** `tools/round100-props-status.py:74` embeds the "exact llama.cpp 401
`Invalid API Key` document". I rebuilt it from upstream `server-http.cpp:292-300` and from
`vendor/nlohmann/json.hpp` (default `object_t` is `std::map` with `std::less` comparator →
keys serialize **alphabetically**; `dump_safe()` is compact) and got byte-identical output:

```
reconstructed: b'{"error":{"code":401,"message":"Invalid API Key","type":"authentication_error"}}'
counter S7   : b'{"error":{"code":401,"message":"Invalid API Key","type":"authentication_error"}}'
equal: True
```

So S7's embedded document is genuinely the upstream bytes, not a paraphrase.

## 2. S628's flip — confirmed to be S631

S628 (`corpus/SOURCES.md:383`) is **rejected**, on `tests/unit/test_router.py`, HTTP 404, with the
flip text: *"the file exists at b12177 and line 23 carries that assertion"*. Its rejected-source file
`.ufo/waves/round-99/sources/s628-test-router.md` records the same flip and the same 404 digest.

- The 404 re-fetches exactly (14 bytes, `404: Not Found`, digest `d5558cd4…`), so the rejection is
  stable at the pinned tag.
- The whole b12177 tree has **exactly one** `test_router.py`, at `tools/server/tests/unit/test_router.py`
  (GitHub tree API, `b12177`, recursive). There is no `tests/unit/` directory at that tag at all, and
  no other `test_router.py` anywhere in the repo — so S628's path was the only thing wrong about it.
- At that path, upstream line 23 **is** `assert res.body["models_autoload"] is False` — the assertion
  S628's flip text names.

**Conclusion: S628's flip is discharged by S631.** S631 (`corpus/SOURCES.md:386`) is the same file at
the corrected path, cites lines 17-23 and the 200-before-the-field order, and its teaches cell already
says "the path S628 missed (tests live under tools/server/)". The round-99 spot-check
(`corpus/lessons/round-99-verifier-spotcheck.md:100,121`) asked for exactly this re-filing. Confirmed.

One **defect in the plan's prose**, not in the sources: `plans/round-100-claims.md:97` grounds C2 on
"S631 (`tests/unit/test_router.py:20` asserts 200 before reading the field)" — that is **S628's
rejected path**, the one that 404s. The counter's own docstring
(`tools/round100-props-status.py:39`) and `SKILL.md:1844` and `corpus/knowledge/router-props-autoload.md:54`
all cite the correct `tools/server/tests/unit/test_router.py`. So the plan line contradicts the
artifact it names, and points a reader at a URL that returns 404. Same file, same line 20, but the
path is S628's. This is the one place the round-100 sources chain is internally inconsistent.

## 3. Every llama.cpp path that can answer `GET /props` in router mode

Router mode is `server_run_router` (`tools/server/server.cpp:470`). Route registration is
`server.cpp:174` `ctx_http.get("/props", ex_wrapper(routes.get_props))`; the router replaces the
handler at `server.cpp:526` `routes.get_props = models_routes->get_router_props`. Complete list of
answer paths, in httplib dispatch order (`vendor/cpp-httplib/httplib.cpp:9841-9854`: pre-routing
handler → file handler → custom route):

1. **API-key middleware** — `server-http.cpp:291` `res.status = 401;` + `Invalid API Key` document
   (`:292-301`). Reached before any handler; applies to `/props` because `/props` is *not* in
   `get_public_endpoints` (`server-http.cpp:253-259` = `/health`, `/v1/health` + frontend assets).
   → **401, error document.**
2. **Readiness middleware** — `server-http.cpp:315` `res.status = 503;` + `Loading model` document
   (`:316-325`). Skips only `frontend_paths` (`:310`); `/props` is not one, so `/props` **is**
   refused with 503 while not ready. Note ordering: readiness (`:355`) is checked **before** the API
   key (`:358`), so a not-ready server with a bad key answers **503, not 401**.
   → **503, error document.**
3. **Static file handler** — only if `--path`/`public_path` is set (`server-http.cpp:380`
   `set_mount_point`), mounted at `api_prefix + "/"`. A file literally named `props` there would
   answer GET /props with **200** and file bytes. (Requires operator misconfiguration; the default
   `public_path` is empty — `common/common.h:651`.)
4. **Custom route → `get_router_props`** (`server-models.cpp:2021-2050`):
   - **`name` empty (bare `/props`)** → `:2023-2046` builds the router props JSON
     (`role`=`"router"` `:2028`, `models_autoload`=`params.models_autoload` `:2030`) and
     `res_ok(res, props)` (`:2046`) → **status 200** (`res_ok` sets `res->status = 200`,
     `server-models.cpp:1939-1941`).
   - **`?model=<id>` present** → `:2049` `return proxy_get(req);` → `proxy_get` (`:2052-2063`):
     `router_validate_model` (`:1949-1965`) may `res_err` **400** (`:1945`, code from
     `format_error_response` → 400 for INVALID_REQUEST, `server-common.cpp:99`); otherwise
     `models.proxy_request` → the child instance's own `/props` (a *single-model* instance,
     `server-context.cpp:5894` `this->get_props`), whose body has **no `role` field at all**
     (`server-context.cpp:5695-5719` `get_res_props` — no `"role"` key anywhere in that object;
     `grep '"role"' tools/server` returns only `server-models.cpp:2028`).
     → **200 with a non-router body, or 400.**
5. **Proxy relay** (`server-models.cpp:1686` `proxy_request` → `server_http_proxy` `:2616-2795`):
   the child's status is relayed verbatim (`:2783` `this->status = header.status;`); a client-side
   failure becomes **500** with a plain-text body (`:2767-2768` `"proxy error: …"`).
   → **child's status verbatim, or 500.**
6. **httplib error handler** (`server-http.cpp:200-214`): a 404 gets a JSON `File Not Found` document
   (status stays 404); any other status keeps its own body.
7. **httplib exception handler** (`server-http.cpp:183-198`): **500** with `text/plain` body.
8. **`ex_wrapper`** (`server.cpp:61-96`): an exception inside a handler becomes **400** (invalid_argument /
   common_json_error) or **500**, JSON `{"error": …}` document (`:87-89`).

**Does the router's bare `/props` ever answer 200 with something other than the router configuration?**
No — for the bare form the only 200 producer is `get_router_props`' main-instance branch
(`server-models.cpp:2023-2046`), which always emits `"role":"router"` + `models_autoload`. The
`"role":"router"` marker exists in exactly one place in the whole server
(`grep '"role"' tools/server` → `server-models.cpp:2028` only), so a 200 body carrying `role:router`
plus `models_autoload` can only come from that branch. Every other 200 that reaches the probe is
either the instance-mode body (no `role` → probe reads `unread`, probe `kama-probe.sh:913`) or a
static file (no `role` → `unread`).

**Does a router proxy a child's non-200 status?** Yes, on the `?model=` form:
`server-models.cpp:2783` relays the child's status unchanged, so a child 401/503 becomes the
router's answer. This is the one place where a non-200 status can carry a *child's* answer — but
the child's `/props` body has no `role` field, so the probe still reads `unread`, never a
configuration.

So the claim's premise — *"a non-200 answer is never the router configuration"* — **holds upstream
for the bare path**: every non-200 answer is an error document (401/503/400/404/500), and the router
configuration body is emitted only at 200. The sources (S629, S630, S631) say exactly this and
verify byte-for-byte.

## 4. The narrowing defect found (measured, not asserted)

The wave's defect class is *a frozen counter that goes green on a property NARROWER than the claim's
stated wording*. The claim's wording has two components; the counter grades them differently.

### 4.1 The counter cannot see "bare" — measured

Claim C2 wording (`plans/round-100-claims.md:88`): *"the probe reads the router's **bare** `/props`
body only on a final HTTP 200"*; counter docstring (`tools/round100-props-status.py:8`): *"the probe
reads the **bare** `/props` body only when the final HTTP status is exactly 200"*.

The C2 stub routes on `path = self.path.split("?")[0]` (`tools/round100-props-status.py:103`) — it
**strips the query string**, so `/props` and `/props?model=anything` are the same stub route. The
probe's own bare-only rule is real and load-bearing: `kama-probe.sh:57` *"read bare only
(`/props?model=` would route to, and may load, an instance)"*, and upstream
`get_router_props` `:2022` branches on `req.get_param("model")` precisely to route a modelled
request to a child instance.

Measured: I built a candidate probe that reads `http://127.0.0.1:$port/props?model=fixture-model`
instead of bare `/props`, and graded it with the **public** `--probe-file` path:

```
ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True
  rev=2e27e6f1… probe_sha256=d8449b29… candidate=yes        exit=0
```

and with the round-99 regression counter:

```
AUTOLOAD_STATES99 cells=8 mismatches=0 base_mismatches=7 flips=7 stable=1 met=True
  rev=2e27e6f1… probe_sha256=d8449b29… candidate=yes        exit=0
```

Both **green**. A probe that fetches the *routed* `/props?model=` — which upstream loads an instance
rather than reading the router's own configuration — passes both counters. Neither counter's cells
can distinguish it, because both stubs strip the query string before routing.

> **Corroboration / do-not-double-file.** While this seat was measuring, the L1 filed the same
> narrowing independently in `plans/round-100-amendment-1.md` §"C2 — narrowed (filed) wording",
> whose *Not claimed* paragraph already names this exact gap ("requests the bare path … the stub
> ignores any query string") and routes the killer cells (a stub that keeps the query string, a 302
> whose target answers 200, seeded 204/304, a closed port with a pre-seeded body file) to round 101
> (`SCORECARD.md` §Planned (round 101)). This seat's finding is an **independent reproduction with
> the mutation measurements attached** (`mutant-model.sh` grades green on both counters). My verdict
> line below is therefore *corroborating* the already-filed narrowing, not a new one — the L1's
> round-101 killer cells are the correct remedy and need no further filing from this seat.
> My §4.2 (404 untested) is a **strictly smaller** instance of the same ungraded-status gap and is
> also within amendment-1's *Not claimed* list ("rejects every other non-200 status (204, 304, …)"),
> so it needs no separate filing either.

This is the amendment-59 shape: the counter is green on a property narrower than the wording. The
**narrowing sentence** is `plans/round-100-claims.md:88` — *"the probe reads the router's **bare**
`/props` body only on a final HTTP 200"* — and the counter at `tools/round100-props-status.py:8`
repeats it while grading a property that omits "bare".

Mitigation that exists but does not close it: `kama-probe.sh:56-57` documents the bare-only rule in
the probe's own header, and `SKILL.md:1778` states *"`/props` bare only; `/props?model=<id>` routes to
an instance"*. So the *lane* knows the rule; it is simply not *graded* by either counter. The
C2 claim's own disclosed limits list `(a)` stub-fed answers, `(d)` "other non-200 statuses … not
each graded" — but **nowhere** does any limit disclose that the counter does not grade "bare".

### 4.2 The counter does not grade 404 — measured

The nine cells cover 401/500/503/403/202/302 plus the 200 pair. A candidate probe whose guard is
`[ "$pcode" = 200 ] || [ "$pcode" = 404 ]` (i.e. also treating a 404 body as a configuration
answer) grades **green**:

```
ROUTER_PROPS_STATUS100 cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True
  rev=2e27e6f1… probe_sha256=7ada1df9… candidate=yes        exit=0
```

This is the narrower half of the disclosed limit `(d)` ("other non-200 statuses … are not each
graded") — 404 is upstream-reachable for `/props` when `--api-prefix` is set
(`server-http.cpp:691` `full_path = path_prefix + path` ⇒ `/props` no longer matches) or via the
httplib 404 handler (`server-http.cpp:200-213`). It is disclosed in spirit by `(d)`, but the
concrete number of *untested* statuses is not stated.

### 4.3 The counter does grade "exactly 200" against 2xx — measured

Worth recording as a positive: a candidate probe accepting **any** 2xx
(`[ "$pcode" -ge 200 ] && [ "$pcode" -lt 300 ]`) is correctly **killed** by cell S5 (202):

```
ROUTER_PROPS_STATUS100_MISMATCH S5-202-router-on want=MODEL_UNLOADED/router-autoload-unread/2
                                got=MODEL_OK/router-unloaded-autoload/0
ROUTER_PROPS_STATUS100 cells=9 mismatches=1 … met=False   exit=1
```

So the "exactly 200" half of the wording is genuinely graded (S5 and S6 pin it); only "bare" and
the unlisted non-200 statuses are ungraded.

### 4.4 A positive control on the counter's own kill power

The committed blanket-refusal mutant (`controls/c2-mutant-blanket.out`) is reproduced by the
frozen bytes: `mismatches=2` (P1 and P2), `exit=1`. And the round-99 regression control
(`controls/c2-regression-r99.out`) is `cells=8 mismatches=0` at M. Both re-verified here by
re-running the counter at M: `cells=9 mismatches=0 base_mismatches=6 flips=6 stable=3 met=True`,
`exit=0`, matching `measured/c2.out` byte-for-byte in its summary fields.

## 5. What I checked and did not find

- **No quote, line-number, digest, or byte-size mismatch** in S629/S630/S631 (section 1). The only
  source-level defects are (a) the plan's own C2 grounding line citing S628's dead path
  (§2), and (b) S630's cited range stopping one switch case short of the full
  `format_error_response` body (§1). Neither changes a teaches-cell truth.
- **No upstream path contradicts the claim's premise.** Every non-200 answer to bare `GET /props`
  is an error document; the router configuration body is emitted only at 200
  (`server-models.cpp:2046`); `"role":"router"` occurs exactly once in the server tree
  (`server-models.cpp:2028`), so a 200 carrying that marker can only be the router configuration.
- **Byte-stability M→HEAD**: `git diff 2e27e6f1 HEAD` is empty for
  `tools/round100-props-status.py`, `tools/kama-probe.sh`, `corpus/SOURCES.md` and
  `.ufo/waves/round-100/sources/` — kill rule **K1** (counter/probe bytes change after the freeze
  commit without an amendment) is **not** tripped. Probe sha256 at M and at HEAD are both
  `23b26d76…`, matching the frozen receipt.

## 6. Commands (all reproducible)

```
# upstream re-fetch + digests
cd /fast/scratch/hyaku/kama-r100/SC02Sources
for p in tools/server/server-http.cpp tools/server/server-common.cpp \
         tools/server/tests/unit/test_router.py tests/unit/test_router.py \
         tools/server/server-models.cpp tools/server/server.cpp \
         common/common.h common/arg.cpp vendor/cpp-httplib/httplib.{h,cpp} \
         vendor/nlohmann/json.hpp tools/server/server-context.cpp tools/server/tests/utils.py ; do
  n=$(echo "$p" | tr '/' '_'); curl -sL -o "fetch_$n" "https://raw.githubusercontent.com/ggml-org/llama.cpp/b12177/$p"
  sha256sum "fetch_$n"; stat -c%s "fetch_$n"
done

# quoted-range check (byte compare of each declared range vs upstream)
python3 - <<'PY'   # extract "line A-B:" from each S62*.txt, slice the same range from the fetch, compare
PY

# upstream path map greps
grep -n 'res.status = 401\|res.status = 503' fetch_tools_server_server-http.cpp
grep -n 'res.status = 200\|res->status = json_value\|res_ok\|res_err' fetch_tools_server_server-models.cpp
grep -n 'get_router_props\|proxy_get\|proxy_request\|ensure_model_ready' fetch_tools_server_server-models.cpp
grep -n 'set_mount_point\|full_path = path_prefix' fetch_tools_server_server-http.cpp
grep -n '"role"' all/                       # only server-models.cpp:2028
grep -n 'set_follow_location\|this->status  = header.status' fetch_tools_server_server-models.cpp

# counter reproduction at M and the narrowing measurements
cd /home/vgpnk/Projects/shokunin/kama-shokunin
python3 tools/round100-props-status.py --repo . --rev 2e27e6f1… --work <scratch>
python3 tools/round100-props-status.py --repo . --rev 2e27e6f1… --work <scratch> --probe-file <mutant-404.sh>
python3 tools/round100-props-status.py --repo . --rev 2e27e6f1… --work <scratch> --probe-file <mutant-2xx.sh>
python3 tools/round100-props-status.py --repo . --rev 2e27e6f1… --work <scratch> --probe-file <mutant-model.sh>
python3 tools/round99-autoload-states.py  --repo . --rev 2e27e6f1… --work <scratch> --probe-file <mutant-model.sh>
```

## 7. Verdict

**C2 — falsifies-wording.** The C2 counter is green on a probe that reads the *routed*
`/props?model=<id>` instead of bare `/props` (measured: `mismatches=0 met=True` on both
`round100-props-status.py` and the `round99-autoload-states.py` regression control), because both
stubs strip the query string (`tools/round100-props-status.py:103`) — so the **"bare"** in the
claim's wording (`plans/round-100-claims.md:88`; counter docstring
`tools/round100-props-status.py:8`) is not graded by any counter, while upstream
`get_router_props` (`server-models.cpp:2022`) routes `?model=` to a child instance and
`kama-probe.sh:57` forbids that read. Secondary: 404 is upstream-reachable for `/props` and is not
among the nine cells, so a probe accepting 404 bodies as configuration is also green (limit `(d)`
covers this in spirit). The upstream sources themselves (S629/S630/S631) re-fetch byte-for-byte and
S628's flip is confirmed discharged by S631; the sources are not the defect — the counter's
coverage of the wording is.

*(This narrowing is already filed by the L1 in `plans/round-100-amendment-1.md` §"C2 — narrowed
(filed) wording"; this seat's contribution is the independent reproduction plus the mutation
measurements. The L1's round-101 killer cells — a stub that keeps the query string, a 302 whose
target answers 200, seeded 204/304, a closed port with a pre-seeded body file — are the correct
remedy; no new filing is needed from this seat.)*
