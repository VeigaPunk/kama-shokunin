# Scout: llama.cpp `--sleep-idle-seconds` wire state vs kama-probe

Seat: read-only scout (leaf). Question: what do `GET /health`, `GET /v1/models`,
`GET /props` return while sleeping; would `classify()` misgrade it?

Source basis: official tarball `codeload.github.com/ggml-org/llama.cpp/tar.gz/704366d76`
(extracted to `/tmp/lcpp-sleep/llama.cpp-704366d76`; no repo checkout existed). Installed
binary confirms the same build: `llama-server --version` -> `0.7.0-dev (build 11755, commit
704366d76)`, and `--help` lists `--sleep-idle-seconds`. All `path:line` cites below are
relative to that tarball unless prefixed `lane/` (kama-shokunin).

## 1. Observed: the three endpoints while sleeping

Sleep is opt-in: `--sleep-idle-seconds SECONDS` default `-1` = disabled
(`tools/server/README.md:247`, `common/arg.cpp:3852-3858`; `0` and `< -1` throw).

| Request | Status | Body | Evidence |
|---|---|---|---|
| `GET /v1/models` | 200 | cached `{"object":"list","models":[...],"data":[{...}]}` — same bytes as ready | `server-context.cpp:5725-5733` serves `cached_models`; snapshot built at `6306` |
| `GET /health` | 200 | `{"status":"ok"}` | `server-context.cpp:5288-5299`: "this endpoint can be accessed during sleeping"; `5297` `res->ok({{"status", "ok"}});` |
| `GET /props` | 200 | full props with `"is_sleeping": true` | `server-context.cpp:5438-5446` serves `cached_props`; field at `5264`; snapshot `6307` `cached_props = get_res_props(*meta, params, true);` |

Docs agree: "When the server enters sleep mode, the model and its associated memory … are
unloaded from RAM" and "The sleeping status can be retrieved from the `GET /props` endpoint"
(`tools/server/README.md:2337,2339`). "Endpoints created with `create_response(true)`
(`/health`, `/props`, `/models`, `/metrics`) skip `wait_until_no_sleep`, so they answer from
the cached responses instead of waking the server" (`tools/server/README-dev.md:322`).

Sleeping is NOT the loading state. Loading is a middleware gate:
`server-http.cpp:308` `if (!is_ready.load()) {` … `318-320` message `"Loading model"`, type
`"unavailable_error"`, code `503`, applied to every non-frontend path (`312`: "no endpoints
are allowed to be accessed when the server is not ready"). `is_ready` is stored true once,
after the model loads — `server.cpp:515` `ctx_http.is_ready.store(true);` (direct server;
`460` is the router-mode equivalent) — and nothing clears it on sleep. Entering sleep calls
`destroy()` (`server-context.cpp:1064-1072`), not an `is_ready` reset. So a sleeping server
never emits the loading envelope.

Cache readiness at the moment sleep becomes observable: the queue sets `sleeping = true`,
runs `cb(true)` callbacks, then `condition_tasks.wait` — all under `mutex_tasks`
(`server-queue.cpp:327-338`), and `is_sleeping()` locks that same mutex
(`server-queue.h:72-75`). The cache snapshot callback is registered before `load_model()`
registers the destroy callback (`server-context.cpp:5161-5165`: "this must be registered
before `load_model()`"), giving the documented order "cb0 -> cb1" (`README-dev.md:303-309`).
[INFERENCE] Therefore no handler can observe `is_sleeping()==true` with an unpopulated
`cached_models`.

## 2. Would kama-probe misgrade it?

**No — for the steady sleeping state, neither frozen nor repaired probe misgrades it.**

- `classify()` decides on `GET /v1/models` only (`lane/tools/kama-probe.sh:452`).
- A sleeping server answers 200 with the model array (above), so control reaches the
  `MODEL_OK` block (`lane/tools/kama-probe.sh:525-545`): `matched` or `expected-wildcard`,
  exit 0. `/health` is consulted only for the evidence string (`541-542`), never the verdict.
- The new `MODEL_LOADING` branch is unreachable here: `lane/tools/kama-probe.sh:501`
  requires `"$F_CODE" = "503"` plus `body_is_llamacpp_loading` (`426-444`: `error.message ==
  "Loading model"`, `error.type == "unavailable_error"`, integer `code == 503`).
- Frozen probe (`sha256 93ee430271…a2cd64`) lacks only that branch (diff vs working tree),
  so its sleeping result is the same `MODEL_OK` path. Both agree; the C1 fix changes nothing
  about sleep.

Edge windows checked:
- **Wake reload:** `sleeping` stays true until `load_model()` returns
  (`server-context.cpp:1074-1079`; queue clears at `server-queue.cpp:344-350`), so
  `/v1/models` keeps serving the cached 200 across the whole reload. No 503 window, hence no
  false `MODEL_LOADING`. [INFERENCE from the callback ordering above]
- **Reload failure:** `GGML_ABORT("failed to reload model after sleeping")`
  (`server-context.cpp:1076`) kills the process; probe then reports DEAD. Genuine failure,
  not a misgrade.
- **`/health` cannot discriminate:** it is `{"status":"ok"}` both ready and sleeping
  (`5288-5299`), and `503` loading during first load. Probe evidence `GET /health ->
  200|application/json` is true but does not mean "loaded".
- **Router mode (scope note):** router `/v1/models` advertises models with
  `"status": {"value": "sleeping"}` (`tools/server/README.md:2080-2095,2236`), i.e. a
  sleeping model is still listed and grades `MODEL_OK`. That is advertised identity, which
  is what the probe's contract asks; not a misgrade.

## 3. Probe is sleep-safe / non-disruptive

`classify()` touches only `/v1/models`, `/health`, `/`, `/metrics`
(`lane/tools/kama-probe.sh:452,497,504,541,550,560,563`; `metrics_trap` `311-318`). The docs
list exactly those as exempt: they "do not trigger model reloading and do not reset the idle
timer" (`tools/server/README.md:2341-2345`). `/` is the static frontend. The idle timer is
reset only by posted tasks (`server-queue.cpp:24-26`, all types except
`SERVER_TASK_TYPE_METRICS`), and these GETs post none. So monitoring a sleeping llama.cpp
never wakes it and never postpones sleep.

## 4. Frontier advice (ranked)

1. **Do not add a sleep verdict or a sleep branch.** Sleeping is wire-identical to ready on
   `/v1/models`; keeping `MODEL_LOADING` gated on `503` (`lane/tools/kama-probe.sh:501`) is
   what protects it. Any broaden-to-`/health` change would start misgrading at the loading
   boundary and still cannot see sleep.
2. **Do not add a "Sleep" stub family to `tests/probe-verdicts/`.** A stub cannot express
   sleep: the observable `/v1/models` response is a plain 200 model array, already covered
   by the `MODEL_OK` controls. The only sleep-specific assertion that matters — a loading
   envelope on `/health` must not decide the verdict — already exists as
   `LoadingRace.InverseHealthLoadingModelsOk`.
3. **Optional, defer out of round 16:** evidence-only sleep visibility via `/props`
   `is_sleeping` (`README.md:933`). It costs a 4th request, ties the probe to a non-frontend
   endpoint, and changes evidence bytes; it buys operator insight, not calibration. If ever
   added, it must never touch `C_VERDICT`.
4. **C2 harness (`tools/kama-llamacpp-live.py`): do not pass `--sleep-idle-seconds`.** If a
   sleep observation is ever wanted, `/v1/models|/health|/props|/metrics` stay cheap and do
   not wake, but `/slots` (and any inference route) creates a response without
   `bypass_sleep` (`server-context.cpp:4857-4869`) and will wake the server and block until
   reload. Sleep is reachable ~1 s after start with `--sleep-idle-seconds 1` plus a quiet
   window, so a live capture is feasible — but that is L1's measurement, not this seat's.
5. **Verifier counter-argument ready:** if a reviewer asks "what about sleeping?", the answer
   with cites is: `is_ready` never clears (`server.cpp:515`), cache is snapshotted before
   destroy (`server-context.cpp:6301-6307`), verdict endpoint is cached-200
   (`5725-5733`) — therefore MODEL_OK, unchanged by C1.

## 5. Remaining unknowns / limits

- No live sleeping server was exercised (measurements belong to L1); §1 is source- and
  doc-derived. The binary was only queried for `--version`/`--help`.
- [INFERENCE] The "no empty-cache window" and "no 503 during wake reload" conclusions follow
  from mutex/callback ordering read in source, not from runtime observation.
- Router-mode sleeping listing is read from README docs, not run.
- Timing numbers (`--sleep-idle-seconds 1`) are from the flag's semantics (`>= idle_sleep_ms`
  check at `server-queue.cpp:290-296`), not measured.

## 6. Installs

None. No pacman/uv/npm/cargo transaction. Only a read-only source tarball download to
`/tmp/lcpp-sleep` (38 MB, commit `704366d76`); the pre-installed b11755 binary was used as-is.
