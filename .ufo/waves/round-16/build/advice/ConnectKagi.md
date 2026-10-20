# ConnectKagi — secrets overlap scan for C1 / C2 (round 16)

- **Seat:** connector, read-only (leaf; no subagent). Lane: `kama-shokunin`.
- **Verified-at:** `2026-10-20T13:33:11Z` (`date -u`). Upstream citations are the pinned
  release commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (b11755), opened via
  `raw.githubusercontent.com` this session. `tools/kama-llamacpp-live.py` was re-read after
  it landed at 10:31 -03 (13:31Z), after the first pass.
- **Tooling record:** zero packages/tools installed or updated. One bounded local
  measurement (a throwaway `python3` stub on `127.0.0.1:0` + `curl`) is recorded in E12;
  it is not a lane gate or harness.

## 1. Axes named

- **Operability** — C2's launch must be a function of its declared inputs, not of the
  operator's ambient shell; no registered consumer port may ever be served.
- **Calibration** — the probe's verdict must not absorb authentication state, and the
  C1 record must not generalise the loading envelope past what the source shows.
- Non-harm surfaces checked: **contract** (no new verdict, no credential support in the
  probe), **verification** (receipts stay value-free), **consistency** (kagi's `/health`
  rule must agree with the new loading state).

## 2. Evidence

**E1 — llama.cpp checks readiness before the API key.** `tools/server/server-http.cpp:354`
`if (!middleware_server_state(req, res)) {` precedes `:357`
`if (!middleware_validate_api_key(req, res)) {`. Both run in one `set_pre_routing_handler`
(`:331`). Consequence: while loading, an **unauthenticated** request gets the 503 loading
body even when `--api-key` is configured.

**E2 — the loading body is exact and path-wide.** `server-http.cpp:307-325` answers every
non-frontend path while `!is_ready.load()` with
`{"message", "Loading model"}, {"type", "unavailable_error"}, {"code", 503}` (`:318-320`).
Frontend assets are the only exemption (`:309-311`).

**E3 — the auth envelope is a different triple.** `server-http.cpp:294-296`
`{"message", "Invalid API Key"}, {"type", "authentication_error"}, {"code", 401}`. Public
endpoints are only `/health`, `/v1/health` and frontend assets (`:251-258`, tested at
`:267`), so a ready keyed server returns 401 on `/v1/models` and 200 on `/health`.

**E4 — documented surface.** `tools/server/README.md:481` "This endpoint is public (no API
key check). `/v1/health` also works."; `:486` documents the 503 loading body for `GET
/health` ("the model is still being loaded"). `:215-216` document `--api-key KEY` with
`(env: LLAMA_API_KEY)` and `--api-key-file FNAME` with `(env: LLAMA_ARG_API_KEY_FILE)`.

**E5 — those env names are real defaults, not prose.** `common/arg.cpp:3542`
`.set_env("LLAMA_API_KEY")` and `:3559` `.set_env("LLAMA_ARG_API_KEY_FILE")`. Env is
applied in the parser (`:790`) before CLI arguments, so an ambient `LLAMA_API_KEY`
enables auth when the launcher passes no `--api-key`.

**E6 — a second ambient switch overrides `--port`.** `server-http.cpp:92-95` reads
`AIP_MODE`, `AIP_HTTP_PORT`, `AIP_HEALTH_ROUTE`, `AIP_PREDICT_ROUTE` directly from the
environment (`:95` default port `8080`); `:117-121` then logs and applies
`"overriding server port %d with AIP_HTTP_PORT %d"`. This `getenv` runs at server init,
**after** arg parsing, so an explicit `--port` cannot prevent the bind. With
`AIP_MODE=PREDICTION` in the parent environment, the C2 launcher's pre-launch port guard
is bypassed and the child binds `8080` — a registered consumer port the C2 contract says
is never served. Presence-only check this session: `AIP_MODE`, `AIP_HTTP_PORT`,
`AIP_HEALTH_ROUTE`, `LLAMA_API_KEY`, `LLAMA_ARG_API_KEY_FILE` are all **absent** from this
shell (names tested with `${!v+x}`; no values read or printed), so this is latent, not a
live defect.

**E7 — a keyed server can log a key prefix.** `server-http.cpp:232`
`SRV_TRC("api_keys: ****%s\n", substr.c_str());` logs the last four bytes at trace
verbosity. The landed argv (`tools/kama-llamacpp-live.py:558-568`) sets neither a key nor
a verbosity flag, so this is conditional on a future keyed run.

**E8 — the probe is credential-free by construction.** `tools/kama-probe.sh:290-293` and
`:322-324` call `curl` with no `-H`/`--user`; there is no `--api-key` option in the parser
(`:119-137`). The 401/403 branch (`:493-498`) runs before the loading branch (`:501-506`),
so a 401 carrying the loading triple stays `UNAUTHORIZED_SERVICE`. The exact-triple helper
is `:426-445`; the repaired probe already lists `MODEL_LOADING` in `VOCAB` (`:60`) and has
the branch at `:501-506`, so this report does not re-propose the verdict.

**E9 — kama's own boundary.** `PROVINCE.md:40` "credential material & auth flows (kagi)";
`SKILL.md:133` "do not supply a credential ... Escalate auth handling to kagi.";
`SKILL.md:181` "The runtime could enforce keys; the historical unit did not pass
`--api-key`."; `corpus/knowledge/cross-lane-scope.md:32` assigns any change caused only by
credentials/auth to kagi.

**E10 — kagi states the reciprocal boundary.** `PROVINCE.md:63` "kama refuses to hold
credentials for authenticated health checks and would route that need here through L0";
`SKILL.md:14-16` "never print, copy, or exfiltrate a secret value ... Ref *paths* are
internal metadata"; `corpus/QUALITY.md:24` (QA5) "No credential material, ever: no secret
value, token, session id".

**E11 — one shared read surface, currently dormant.** kagi `SKILL.md:446` "the *global*
`~/.config/opencode/opencode.json` also reaches the handler"; kama `PROVINCE.md:11` lists
the same file as a historical baseURL pin (provider block since removed). The current
registry has only three rows (`registry/endpoint-consumers.tsv:35-37`: omp, thetick,
local-helper) and none reads that file.

**E12 — kagi's `/health` verification rule is incomplete for loading.** kagi `SKILL.md:43`
"`curl -fsS <endpoint-minus-/v1>/health` → `{"status":"ok"}`". Measured on a local
throwaway stub returning E2's body: `curl -fsS` exits **22**, writes **0** stdout bytes,
stderr `curl: (22) The requested URL returned error: 503`. A loading llama.cpp therefore
looks like a failed endpoint to that rule.

**E13 — existing redaction conventions in kama's resolver.**
`tools/kama-probe.sh:650-651` "never surface credentials: strip userinfo and query/fragment";
the raw branch prints the matched string verbatim (`:672`), and the JSON-pointer printer
prints the node value (`:613`, `:625`). Registry specs must stay URL/port-shaped; a
`json:` pointer into a provider block could print an `apiKey`.

**E14 — the landed C2 launcher inherits the parent environment.** `tools/kama-llamacpp-live.py:23-24`
"Only argv is recorded from the launch environment — never env." The server `Popen`
(`:585-591`) passes no `env=`, so it inherits everything; the assigned argv (`:558-568`)
sets no key and no verbosity flag. The probe subprocess does pass an explicit env dict
(`:366-373`), but only to force `NO_PROXY`; the probe itself sends no credential (E8).

## 3. Contested scope and boundary rulings

| Surface | kama's claim | kagi's claim | Ruling for this round |
|---|---|---|---|
| `llama-server --api-key` / `LLAMA_API_KEY` **value** | may document status/envelope shape only (`SKILL.md:133`) | runtime auth and credential custody (`PROVINCE.md:63`) | **Hand off.** kama never supplies, generates, stores, or validates a key; the probe stays credential-free (E8). |
| Loading while keyed | records the 503 body and the ordering fact (E1) | no claim; kagi does not own endpoint internals | **kama owns the code fact**; kagi owns whether a keyed deployment is acceptable. |
| Pre-auth loading disclosure | records that unauthenticated callers see `Loading model` before the key check | security significance is kagi's judgment | **Report, do not adjudicate.** Named here as a kagi/L0 question, not a kama finding. |
| `~/.config/opencode/opencode.json` | historical baseURL pin (`PROVINCE.md:11`) | global config reaches the handler; "attack/drift surface" (`SKILL.md:446`) | **Shared read surface, dormant** (E11). If re-added, read only the `baseURL` node; never dump the provider block. |
| Vault-resolved environment (`op run`) | `file_match=inherited`; "not proof of the effective environment-selected endpoint" (`registry/endpoint-consumers.tsv:35`) | owns `op`/env-ref resolution | **Hand off.** Establishing the *effective* `LLAMA_CPP_BASE_URL` requires kagi; kama reports the file-level pin only. |
| kagi `/health` endpoint check | supplies the loading envelope and status contract | owns the decision-table row | **Hand off** the correction: add a 503-loading branch; `-f` alone cannot distinguish it (E12). |

## 4. What kama must hand off rather than absorb

1. Any authenticated health check or keyed-endpoint test — route through kagi via L0
   (`kagi/PROVINCE.md:63`). C2 must remain an unkeyed ephemeral server.
2. Any provider `apiKey`, `headers`, or credential-shaped value in a consumer config.
   kama may cite the pin's path/shape, never the block body (`SKILL.md:139`).
3. Effective environment resolution where the value may be vault-delivered (`op run`).
   kama keeps `file_match=inherited` as an unresolvable-by-kama state.
4. The pre-auth state disclosure in E1 — endpoint fact here, risk judgment in kagi.
5. kagi's `/health` row: kama reports the envelope; kagi edits its own table.

## 5. Reusable conventions

- **Shape evidence, not values.** kagi QA5 (`kagi-shokunin/corpus/QUALITY.md:24`) and kama
  KQ5 (`kama-shokunin/corpus/QUALITY.md:13`, "nonsecret shape evidence only") already agree;
  cite both when a receipt or report touches a credential-adjacent surface.
- **Redact at the boundary, not at the reader.** kama's sentinel (`tools/kama-probe.sh:650-651`)
  is the implementation pattern: strip URL userinfo/query before output. C2 receipts should
  apply it to every recorded URL and must never record env values.
- **Name the object, not the value.** Upstream envelope constants (`"Invalid API Key"`,
  `"authentication_error"`) are message/type literals, not credentials; they are safe in
  the stub matrix. Never add an `Authorization`/`X-Api-Key` header carrying a key-shaped
  literal to a matrix case — the stubs ignore headers anyway.
- **One fact, one owner.** kama's falsifiable arbitration rule
  (`corpus/knowledge/cross-lane-scope.md:32`) and kagi's "report, don't absorb"
  (`PROVINCE.md:63`) are the same rule; no new convention is needed.

## 6. Proposed move (one bounded)

**M1 — make C2's child environment a declared, scrubbed surface, and write C1's
credential-free precondition into the round record.**

Concretely, in `tools/kama-llamacpp-live.py` (landed at 10:31; its server `Popen` at
`:585-591` passes no `env=`, see E14), build the child environment subtractively and pass
it explicitly:

```python
SCRUB = {
    "LLAMA_API_KEY", "LLAMA_ARG_API_KEY_FILE",          # credential-bearing
    "AIP_MODE", "AIP_HTTP_PORT",                        # can override --port to 8080
    "AIP_HEALTH_ROUTE", "AIP_PREDICT_ROUTE",
}
child_env = {k: v for k, v in os.environ.items() if k not in SCRUB}
subprocess.Popen(argv, env=child_env, start_new_session=True, ...)
```

- Keep argv exactly as assigned; assert `--api-key`/`--api-key-file` are absent.
- Record only the **names** scrubbed (e.g. a receipt metadata field `env_unset`, or the
  launcher's stdout summary if the receipt schema is closed — item 11's checker requires
  fixed check ids). Never record values.
- Scrub only the server child. Keep the probe subprocess environment (`:366-373`): it sets
  `NO_PROXY` and may legitimately read `UFO_SRC` for registry rows
  (`tools/kama-probe.sh:578-592`), so scrubbing it would break pin resolution.
- Add one sentence to the C1/SKILL record: *MODEL_LOADING is detected pre-auth — readiness
  is checked before the API key (`server-http.cpp:354` vs `:357`) and the probe sends no
  credential (`tools/kama-probe.sh:290-293`); a ready keyed server therefore yields
  `UNAUTHORIZED_SERVICE` http-401, and adding key support to the probe is out of scope
  (kagi).*

**Why non-obvious.** The two halves come from different lanes' failure modes: the
credential half is kagi's "no secret material" rule applied to a child process that
inherits the whole environment; the AIP half is a serving-runtime `getenv` that bypasses
C2's pre-launch port guard. Both are invisible in a clean shell (the checked names are
absent today), so a green C2 run proves nothing about them. The fix is three lines and
touches no verdict.

**Affected axes.** Operability: removes two ambient switches that silently change the
launch (auth enabled; bind 8080). Calibration: keeps the ready/loading verdict a function
of the server, not the operator shell, and fixes the auth/loading ordering in the record.
Non-harm: no new vocabulary, no credential handling, no write outside the lane; the C1
matrix and the frozen probe comparison are unchanged.

## 7. Risks

- `env=` starvation: a subtractive filter is safe; a minimal allowlist could break dynamic
  loading. Use subtraction, keep `PATH`/`HOME`/`TMPDIR`/loader variables.
- Scrubbing `LLAMA_API_KEY` deliberately removes any in-lane authenticated coverage. That
  is the ratified boundary (kagi `PROVINCE.md:63`), but it must be stated as a limitation.
- Receipt schema churn: if item 11's checker rejects extra fields, put the scrub names in
  the launcher's stdout report instead of the receipt.
- The AIP scrub is defensive only; absent today. It costs nothing and prevents a
  hard-constraint violation if the operator shell ever exports `AIP_MODE=PREDICTION`.
- The landed `Popen` passes the default inherited environment (E14), so the patch is
  exactly the three lines above; no other call site needs editing.

## 8. Verification (L1 runs these)

1. Static: `grep -nE 'LLAMA_API_KEY|LLAMA_ARG_API_KEY_FILE|AIP_MODE|AIP_HTTP_PORT|--api-key' tools/kama-llamacpp-live.py`
   shows only the scrub-list constants and no argv use; the server `Popen` at `:585-591`
   passes `env=child_env`.
2. Behavioural falsifier (optional, one server): launch with the parent environment
   carrying `AIP_MODE=PREDICTION AIP_HTTP_PORT=8080` and a non-secret sentinel
   `LLAMA_API_KEY=TEST_CONSTANT_NOT_A_SECRET`; assert the ready `/v1/models` probe is
   `MODEL_OK` (not `UNAUTHORIZED_SERVICE`) and `ss -ltn` shows the chosen `P`, never `8080`.
   The AIP half needs no credential-shaped literal and can run alone.
3. Receipt: zero occurrences of the sentinel string; scrub names present.
4. Unchanged: frozen probe red / repaired probe green on the C1 matrix.

## 9. Adjacent calibration note (not a kagi handoff)

`tools/kama-probe.sh:426-427` returns 1 immediately when `python3` is absent
(`[ "$HAVE_PY" -eq 1 ] || return 1`), while the header calls python3 optional
(`:55-56`). This is deliberate, not a defect: `:424-425` says "a grep approximation cannot
prove the exact envelope", so the body keeps `FOREIGN_SERVICE` — fail closed. The matrix is
green because this host has python3. The round record should carry that precondition
("exact triple requires python3") so the vocabulary is not read as host-independent.

## 10. Limitations

- Read-only seat: no lane gate, matrix, harness, or live launcher was run.
- `~/.config`, `~/.omp`, `op.env`, and all credential stores were not read. The shape of
  `~/.config/opencode/opencode.json` is cited from `PROVINCE.md:11`, not re-verified.
- Environment inspection was presence-only for five named variables; no values printed.
- Local `tools/kama-probe.sh` line numbers are from the 10:27 revision; the file was being
  edited by another seat during this scan, so a later re-read may shift them.
- Upstream line numbers are the pinned commit's; README, `common/arg.cpp`, and
  `tools/server/server-http.cpp` were the only files opened.
- kagi's substrate is declared historical (`kagi/PROVINCE.md:10`, round-18 erratum), so
  the `/health` handoff is a documentation correction, not a live gate.
- `tests/probe-verdicts/AuthAndDead.json` was observed while a sibling was writing it; its
  authorization cases (401/403, loading-body-under-401) are assigned at `spec.json:44` and
  are not re-specified here.
