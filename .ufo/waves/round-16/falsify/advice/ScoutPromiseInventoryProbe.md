VERDICT: partial — round-16 `tools/kama-probe.sh` promise inventory. Every value-level rejection, status gate, and precedence promise introduced by b8e485c is paired by a passing matrix row, but 5 claims are unpaired, 3 of them materially: "Router mode never emits it" has no router-mode test, the no-python3 fallback is untested in-repo (I verified it manually), and the live capability never observed `MODEL_LOADING` at all (`loading_observed=false` in both receipts, and the receipt gate accepts that).

# What I ran (all command output in /tmp/kama-r16-ScoutPromiseInventoryProbe/)

| # | command | exit | result |
|---|---|---|---|
| 1 | `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` | 0 | `tests=72 passes=72 failures=0`; 9 families; **17** records with verdict `MODEL_LOADING` |
| 2 | `bash tools/test-snapshot.sh` | 0 | `RESULT pass=30 fail=0`; lines 24-26 `PASS MODEL_LOADING baseline row accepted and diffed / never audited as malformed / never warns` |
| 3 | stub serving the canonical envelope on every path; probe, normal PATH | 2 | `{"verdict":"MODEL_LOADING","reason":"llamacpp-loading","served_model":"-","drift":true}` |
| 4 | same stub; `env -i PATH=<symlink dir with every /usr/bin binary except python*>`; `command -v python3`→absent | 2 | stderr `[kama-probe] python3 not found — using grep fallbacks…`; `{"verdict":"FOREIGN_SERVICE","reason":"non-2xx-non-model-http","drift":true}` |
| 5 | stub with exact triple **plus** `"detail"` inside `error` and a top-level sibling | 2 | `{"verdict":"MODEL_LOADING","reason":"llamacpp-loading"}` |
| 6 | `jq` over `.ufo/waves/round-16/live/receipt.json` and `receipt-frozen-probe.json` | 0 | `loading_observed:false`, `loading_503:null`, `loading_envelope_exact:null` in both; transitions are refuse@1ms → `/health` 200@22ms, no 503 |
| 7 | `grep -rln "listeners" tests/ tools/test-snapshot.sh` | 1 | no matches |
| 8 | reads of pinned `sources/llama.cpp-704366d/server-http.cpp:307-328`, `server.cpp:452-460,493`, `server-http.cpp:493` (start) | 0 | envelope middleware registered in `init()`, `start()` only binds/listens, router stores `is_ready=true` after `start()` |

No installs. No llama-server started (this item does not authorize it); `listeners` not run (it would probe 8080/34113); `measure.py` not run.

# Inventory of round-16 promises (all line refs current file)

Status: **P** = paired and passing, **W** = paired but weak/ungraded, **U** = unpaired.

| ID | Promise (quote, line) | Pairing | Status |
|---|---|---|---|
| P1 | "GET /v1/models answered 503 with the exact … envelope" :32-34 | 17 `MODEL_LOADING` rows: 8 `LoadingEnvelope.*`, 5 `LoadingRace.*`, 2 `NearMissTriple.*`, 2 `EnvelopeShapes.*`; source verified `server-http.cpp:307-328` | P (stub); see U5 for real runtime |
| P2 | "Drift (exit 2): not ready" :35 | all 17 rows expect exit 2; `check.py:346` asserts `drift == (verdict != "MODEL_OK")` | P |
| P3 | "body-shape match only — runtime identity and served model are unverified" :35-36 | `LoadingEnvelope.no-server-header` (no Server header) and `NearMissTriple.exact-envelope-labelled-html` (text/html label) prove runtime identity markers are ignored; `.plain-json-content-type` varies only Content-Type; code resets `C_SERVED='-'` at :453 and my run observed `served_model:"-"` | W: `check.py` grades only verdict/reason/exit/drift — no row asserts `served_model=="-"` |
| P4 | "Router mode never emits it" :35-36 | only `NearMissTriple.router-stream-owner-loading`, which is the **different** message `"Stream owner model is loading, retry later"`; probe has no router branch (`grep -n router` → only the comment at :35) | **U1** |
| P5 | "requires python3 (without it the body keeps FOREIGN_SERVICE)" :36 | no repo test manipulates PATH; run 4 confirms behavior | **U2** |
| P6 | "while is_ready is false every non-frontend path returns 503" :420-422 | source `server-http.cpp:308-325`; `LoadingEnvelope.every-non-frontend-path` serves the same 503 default for `/health` and `/v1/models` | P at source; the probe only classifies `/v1/models` (`/health` is evidence via `probe_short`), so "every path" is not test-enforced |
| P7 | "Exact match only — any deviation … falls through" :423-425 | 31 explicit near-miss rows: `EnvelopeShapes` 7, `NearMissTriple` 6, `Overbroad503` 8, `NonLoadingStatuses` 7, `ForeignControls` 2 (`busy-unavailable-error`, `loading-message-wrong-type`), `LoadingRace.HealthOkNonLoading503` 1 | P for value deviations; see U3 for key-set deviation |
| P8 | 401/403 win over the loading branch :494-501 before :503 | `AuthAndDead.401-carrying-loading-envelope`, `.403-carrying-loading-envelope` → `UNAUTHORIZED_SERVICE` | P |
| P9 | Empty 503 body is not loading (`[ -s "$FBODY" ]`) :503 | `NearMissTriple.empty-503` | P |
| P10 | Top-level must be an object; `error` must be an object; body must parse :432-440 | `EnvelopeShapes.InvalidJsonBody`, `.TopLevelArray`, `.ErrorAsString`, `.NestedEnvelope`, `.BomPrefixedJson`, `.MissingCode`; `Overbroad503.error-string`, `.no-error-wrapper` | P |
| P11 | `code` must be int, not bool, ==503 :441-443 | `NearMissTriple.code-float-503.0`, `.code-boolean-true`; `EnvelopeShapes.CodeAsString`; `Overbroad503.code-string` | P |
| P12 | `message` must equal `"Loading model"` exactly :442 | `NearMissTriple.message-trailing-period`, `.message-surrounding-space`; `Overbroad503.lowercase-loading`, `.plaintext-loading`; `ForeignControls.loading-message-wrong-type` | P |
| P13 | `type` must equal `"unavailable_error"` exactly :442 | `Overbroad503.server-error-type`, `ForeignControls.loading-message-wrong-type` | P |
| P14 | `"no slot available" unavailable_error does not match :424 | `Overbroad503.no-slot-available`, `LoadingRace.HealthOkNonLoading503` | P |
| P15 | non-503 status does not match :424-426 | `NonLoadingStatuses.*` (200,200,500,502,504,404,429); `Overbroad503.nginx-html-503` | P |
| P16 | extra top-level keys allowed (`EnvelopeShapes.ExtraFieldsAllowed.why`) | same row | P; extra keys **inside `error`** also match (run 5) — see U3 |
| P17 | `diff_baseline` accepts a prior `MODEL_LOADING` verdict and still drops an unknown one :939 | `tools/test-snapshot.sh:162-187` seeds `MODEL_LOADING` + `MODEL_LOADED`; run 2 passes 3/3 assertions plus kwargs | P |
| P18 | `listeners` summary gains `model_loading` counter :723-749 | no test references `listeners` at all (run 7) | **U4** |
| P19 | `VOCAB` / usage text carry `MODEL_LOADING` :62,:117 | no test asserts `verdict_vocabulary` content; `check.py` never compares the probe's vocabulary field | U5-minor |

# Unpaired promises, with evidence and smallest closing test

**U1 — "Router mode never emits it" (:35-36). Material.**
- No test starts llama-server in router mode. The one row with "router" in its name (`NearMissTriple.router-stream-owner-loading`) exercises a *different* message, so it proves message exactness, not router-mode behavior.
- The row's provenance cites `server-models.cpp:2585`, and that file is **not** in the pinned source set (`find .ufo/waves/round-16/sources -name 'server-models*'` → empty). The claim is not reproducible from the pinned evidence.
- The probe cannot enforce it: zero router references in code (only the comment); if a router-mode server returned the canonical envelope, the probe would label `MODEL_LOADING`.
- Pinned source nuance: the envelope middleware is registered in `server_http_context::init()` (`server-http.cpp:301-328`), while router mode calls `ctx_http.start()` and then `ctx_http.is_ready.store(true)` (`server.cpp:452-460`). `start()` only binds/listens (`server-http.cpp:493-540`). So the absolute "never" has a startup window between the listener accepting and `is_ready=true`; that window is real in router mode (microseconds). [INFERENCE: `is_ready` defaults to false — the declaration lives in an unpinned header, but single-model mode's whole gate depends on that default.]
- Smallest closing test: a router-mode smoke (`llama-server` with no `-m`) polling `/v1/models` from the instant `/proc/<pid>/net/tcp` shows LISTEN until first 200; assert no canonical envelope after the first accepted connection. At minimum, correct the wording to "router mode does not enter the loading state" and pin `server-models.cpp`.

**U2 — no-python3 fallback (:36, :425-427). Material but promise is true.**
- No matrix row touches PATH, and `check.py:run_probe` passes only `["bash", probe, check, --port, …, --json, …]`; `tools/test-snapshot.sh` likewise runs with ambient PATH. `grep -rn "python3 not found\|HAVE_PY\|PATH=" tests/ tools/test-snapshot.sh` → nothing.
- Run 4 is the missing pair: restricted PATH (no `python3`) + canonical envelope → exit 2, `FOREIGN_SERVICE/non-2xx-non-model-http`, i.e. fail-closed exactly as documented. So the claim is **confirmed behaviorally, unpaired in-repo**.
- Smallest closing test: a harness option (`probe_env`/`PATH` override) plus one row `EnvelopeShapes.NoPythonFailsClosed` expecting `FOREIGN_SERVICE`; or a shell test in `tools/` that symlinks a python-free PATH.

**U3 — "Exact match only / any deviation" overstates the matcher (:423-425). Material only as wording.**
- The matcher is a required-triple subset test: `err.get("message")`, `err.get("type")`, `err.get("code")`; extra keys are never rejected anywhere in the object tree. Run 5: canonical triple + `"detail"` inside `error` + top-level sibling → `MODEL_LOADING`.
- The matrix covers extra **top-level** keys and expects acceptance (`EnvelopeShapes.ExtraFieldsAllowed`), but has no row for extra keys inside `error`; "any deviation falls through" is therefore literally false for key-set deviations.
- Risk to the claim is low (real b11755 envelope has exactly three fields; `tests/llamacpp-live/check-receipt.py:67-75` mirrors the same subset semantics, so probe and receipt gate agree). Still, the word "exact" invites a stricter reading than the code implements.
- Smallest fix: either (a) add `EnvelopeShapes.ExtraFieldInsideError` expecting `MODEL_LOADING` and document "required triple, extras ignored", or (b) enforce `set(err) == {"message","type","code"}` and add the negative row.

**U4 — `listeners` `model_loading` counter (:723-749). Unpaired, zero coverage.**
- `grep -rln "listeners" tests/ tools/test-snapshot.sh` → no matches. The added counter (`n_loading`, JSON `summary.model_loading`, human tail) has no test; a typo in either branch would pass every existing gate (matrix only uses `check --port`).
- Also untested: `exit_codes` claims `listeners` never gates (exit 0) while `classify` can return `MODEL_LOADING` — unchanged from other drift verdicts, but the new counter is the round-16 delta.
- Smallest closing test: a stub loading listener + `listeners --json` and assert `summary.model_loading==1` and exit 0. Caveat: `listeners` probes *all* loopback ports, so the fixture must tolerate a noisy host (or the counting should be factored so it can be tested without enumeration).

**U5 — the live capability never observed `MODEL_LOADING`. Material to the claimed end-to-end evidence.**
- `.ufo/waves/round-16/live/receipt.json`: `loading_observed:false`, `loading_503:null`, `loading_envelope_exact:null`; the 10 check ids are `health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_exited, teardown_port_closed, model_unchanged` — none is a loading check. Same fields false/null in `receipt-frozen-probe.json`.
- `tests/llamacpp-live/check-receipt.py:337-360` only enforces *consistency* (`loading_503` present ⇔ `loading_observed` true) and re-derives `loading_envelope_exact`; a receipt with no observation is VALID. So "receipt 10/10 VALID" does **not** mean the new verdict was exercised against a real llama-server.
- Cause is visible in `transitions`: `/health` and `/v1/models` refused at t=1ms, then `/health` 200 at t=22ms; the loop returns on the health 200 before re-probing `/v1/models` (`tools/kama-llamacpp-live.py:429-446`), and `POLL_INTERVAL=0.02` is longer than this tiny model's load. The 503 window is missed deterministically for stories260K, not by chance.
- Consequence for this wave: P1's positive half rests on synthetic stubs + pinned source only. The live capability validates `MODEL_OK`/`MODEL_MISMATCH` against the real server, not `MODEL_LOADING`.
- Smallest closing test: make the loading window exceed the poll cadence in one capture (cold page cache / `--no-mmap`, a larger pinned GGUF, or force-load latency) **and** have `check-receipt.py` require at least one receipt to carry `loading_observed:true` + `loading_envelope_exact:true` (or mark the capability's live-loading check red while false).

**U6 (minor) — "served model unverified" is ungraded.** No row asserts `served_model=="-"`; `check.py` ignores that field. My runs 3-5 observed `"-"`; a future refactor that extracted an id from a 503 body would not fail the matrix. Add `expected.served_model` to the row schema or one explicit assertion.

**U7 (minor) — vocabulary strings ungraded.** `VOCAB` (:62) and the usage line (:117) are asserted by nothing; `check.py` never reads `verdict_vocabulary`. A one-line check in the harness (`assert "MODEL_LOADING" in doc["verdict_vocabulary"]`) would pin it.

# Confirmed strengths (not flags)

- Negative-case density is genuinely high: 31 explicit near-miss rows, all 72 pass (run 1). The closest real-world confusions are covered — `"no slot available"` unavailable_error (`Overbroad503.no-slot-available`, `LoadingRace.HealthOkNonLoading503`), code as string/float/bool, non-503 statuses, HTML/plaintext/openmetrics 503s, BOM, invalid JSON, missing/nested `error`, empty body.
- Precedence is tested where it matters: 401/403 with a canonical envelope still yields `UNAUTHORIZED_SERVICE` (2 rows), and an exact envelope labelled `text/html` still yields `MODEL_LOADING` (`NearMissTriple.exact-envelope-labelled-html`) — both match the code order at :495-509.
- Snapshot vocabulary growth is properly paired in `tools/test-snapshot.sh` (run 2: 30/0), including the near-miss `MODEL_LOADED` still being dropped — a good positive/negative pair around the new whitelist entry at :939.
- Header citation `server-http.cpp:307-328` is accurate against the pinned copy: the middleware emits exactly `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` with `Content-Type: application/json; charset=utf-8` for every non-frontend path while `!is_ready`.

# Limitations

- I did not run `listeners` (would probe host ports 8080/34113, which this item forbids) and did not start `llama-server` (the item authorizes only the C2-capability lanes); U1/U4/U5 are therefore pairing gaps established by reading tests/receipts/source, not by new live runs. My two stub experiments in /tmp are the only added executions.
- `.ufo/waves/round-16/measure.py` was not run (it rewrites L1 receipts); the matrix was invoked via `tests/probe-verdicts/check.py` as required.
- `is_ready`'s declared initializer is in an unpinned header; the router startup-window argument is marked [INFERENCE] and does not change the pairing verdict (no router test exists either way).

Scratch: `/tmp/kama-r16-ScoutPromiseInventoryProbe/` (matrix.json, normal.json, nopy.json, nopy.err, extraerr.json, snapshot.out, stub scripts + python-free PATH dir) — removed after report.
