VERDICT: confirm — the listener binds before `load_model`; a zero-503 run is a lost observation (or router mode), never a ready single-model server skipping the window.

# Scout: listener bind vs `load_model`, and when zero 503s is legitimate

Pinned commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (b11755), local copies under
`.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/`. Read-only seat; no live
server was started for this recon.

## F1. The listener is live before the model loads; `is_ready` flips only after `load_model` returns

`.ufo/waves/round-17/sources/llama.cpp-704366d76/tools/server/server.cpp:493-515`:

- `:493` `// start the HTTP server before loading the model to be able to serve /health requests`
  (15 words)
- `:494` `if (!ctx_http.start()) {`
- `:507` `if (!ctx_server.load_model(params)) {` … `:511` `return 1;`
- `:514` `routes.update_meta(ctx_server);`
- `:515` `ctx_http.is_ready.store(true);`

So the not-ready interval opens when `ctx_http.start()` returns and closes at `:515`; its
width is `load_model` wall time plus `routes.update_meta`. `start()` itself loopback-binds and
starts accepting before returning: `server-http.cpp:531-536` spawns `listen_after_bind()` then
`srv->wait_until_ready();`, and returns only if `srv->is_running()`.

`is_ready` starts false and is never stored false again: `std::atomic<bool> is_ready = false;`
(4 words) at
https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/server-http.h
line 71. `server.cpp` and `server-http.cpp` contain only the two `store(true)` sites (`:460`,
`:515`) and the middleware load (`server-http.cpp:308`); there is no reset path, so once ready,
a run cannot return to 503.

## F2. The 503 middleware covers every non-frontend path, including `/v1/models`

`server-http.cpp:307-328`: `if (!is_ready.load()) {` … `res.status = 503;` …
`{"message", "Loading model"}`. The only bypass is `frontend_paths` (`:309-311`); so during the
window both `/v1/models` and `/health` get the exact loading envelope.

Order matters: the pre-routing handler calls `middleware_server_state` (`:354`) before
`middleware_validate_api_key` (`:357`), quoted `if (!middleware_server_state(req, res)) {` …
`Handled`. Consequence: even with `--api-key` set, an unauthenticated `/v1/models` probe gets
503 during the window and 401 only after it. The middleware is installed by
`ctx_http.init(params)` (`server.cpp:226`, `server-http.cpp:111`), i.e. before `start()`, so
there is no interval in which the listener answers without the state check.

## F3. Router mode is the only genuine "ready server without a loading window"

`server.cpp:460` `ctx_http.is_ready.store(true);` executes immediately after `ctx_http.start()`
and before `:472` `models_routes->models.load_startup_models();`. Router mode is selected by
`:152-154` `params.model.path.empty() && params.model.hf_repo.empty() && params.model.docker_repo.empty()`
(11 words). In that mode startup model loads produce no 503 at all. The frozen tool always
passes `-m <model>` (`.ufo/waves/round-18/frozen/tools_kama-llamacpp-live.py:1088-1097`), so it
cannot reach router mode; for this tool the window is always structurally present.

## F4. When a client sees zero 503s, and how that compares with the poll cadence

The loop leaves the `/v1/models` phase on the first status that is not `None`/503:
`frozen/tools_kama-llamacpp-live.py:589-590` `if transitions[-1]['status'] not in (None, 503): break`
(7 words). A client therefore sees zero 503s exactly when **no request is served while
`is_ready` is false**. Two mechanisms:

(a) *Observation hole (measured).* The poller itself issues no request spanning the whole
window. `.ufo/waves/round-17/falsify/advice/LiveUnderLoad.md` run `cpu1024b-1`: transitions are
last refusal `t_ms=27` (`repeats=56`) then `status=200 t_ms=71`; the report's words: `The
loading transition completed inside a 44 ms observation hole` (10 words). The same file records
`Passing runs captured 1-243 total 503 responses; 23 of the 59 passing runs captured exactly one.`
(16 words) and the failure captured zero.

(b) *Request straddles the flip* [INFERENCE]. A request sent during the window but accepted or
dispatched only after `:515` is answered 200 by the middleware's post-flip branch; it is the
first non-503 and ends the phase. I did not observe this directly; it follows from
`is_ready.load()` being evaluated at handling time (`server-http.cpp:308`), not at accept time.

(c) *D1 ownership scan runs inside the window (peer-measured).* On the first non-None status
the loop calls `port_owned_by(proc.pid, port)` before recording the 503 body
(`frozen/tools_kama-llamacpp-live.py:546-553`), reading both `/proc/net/tcp{,6}` (`:320-342`)
and the child's fd table. `KamaR18.ProbeZeroLoading-2` measured ~0.9 us per `/proc/net/tcp`
line and ~36 TIME_WAIT rows added per back-to-back run (IRC, 2026-10-20). The scan runs while
the window is open, so a growing table consumes the remaining cadence; the first 503 is still
recorded (row appended at `:545`, body at `:554-572` after the scan), which biases late runs
toward exactly one 503 — consistent with LiveUnderLoad's 23-of-59 single-503 passers. Treat 503
*counts* as non-comparable across runs with different table sizes; only presence/absence is
stable.

Cadence, for comparison: the loop has no sleep — `frozen/tools_kama-llamacpp-live.py:508-510`
`NO sleep, 0.5 s per-request timeout, until the first non-503 answer` (11 words). `_KeepAlive`
reuses one `http.client` connection and retries once per call (`:468-495`, `for attempt in
range(2)` at `:478`). `POLL_TIMEOUT = 0.5` (`:71`) is a per-request ceiling, not an interval:
the effective cycle is the round trip. Measured in the committed receipts
`.ufo/waves/round-17/live/receipt-{1,2,3}.json`: last refused row at `t_ms` 6 with 193/215/209
repeats, one coalesced 503 row with 41/44/44 repeats at `t_ms` 11/11/12, first 200 at
`t_ms` 11/12/12. That bounds the window at <=5-6 ms with ~0.1-0.15 ms per served request — but
a single slow cycle is 0.5 s (2x0.5 s when both `get()` attempts hang), roughly 100x the whole
window. Hence one descheduling or one hung connect erases the window; the width is not fixed:
LiveUnderLoad's idle `--threads 32 --ctx 8` controls measured `loading windows 79-927 ms, all
observed` (6 words), versus sub-millisecond windows with the tool's `-t 1 -c 256`.

The result is terminal for the run: phase `models` never revisits the server after the first
200, phase `health` runs under the same now-true `is_ready`, and `loading_observed` is
`loading_503 is not None` (`frozen/tools_kama-llamacpp-live.py:1153`). There is no path where a
later phase can recover a 503 once the models phase broke on 200.

## F5. Can a ready server skip the window?

- **Single-model (`-m`): no.** `is_ready = false` until `server.cpp:515`, i.e. strictly after
  `load_model` succeeds (`:507-511` exits 1 on failure). Every ready single-model server passed
  through the window; zero 503s says the observer missed it, not that it did not happen.
- **Router mode: yes, structurally** (F3), but unreachable with the tool's argv.
- No flag in the tool's argv (`:1088-1097`: `-m`, `--alias`, `--host`, `--port`, `-c`, `-t`,
  `--no-webui`, `--offline`) can move the flip before `load_model`; `--no-warmup` is not passed,
  and even then the load path still runs before `:515`.

## F6. Consequence for R4 / the v3 not-evaluated branch

The frozen tool hard-codes the opposite: `frozen/tools_kama-llamacpp-live.py:141-142`
`no 503 observed -> fail with {"loading_observed": false} (a real b11755 run shows dozens)`
(14 words). `_check` coerces None to false (`:832` `'passed': bool(passed)`), and exit is only
0/1 (`:1375-1378`, `0 if all(... c.get('passed') is True ...) else 1`), so a healthy run that
lost a <=5 ms window is reported as a server defect. That is exactly R4.

The frozen source binding for this check covers only the 503 body span
(`server-http.cpp` L314-325, `:886-900`); it does not bind the window boundaries
(`server.cpp:493-515`) or the `is_ready = false` default, and the "shows dozens" phrase is an
observation, not a source. A v3 `passed: null` with
`observed.not_evaluated_reason = "no-loading-503-observed"` is the honest classification **only
for this check**: every other check in the same receipt remains evaluated and can fail. Tool
exit 2, gate exit 3.

Control semantics: the frozen fake serves 503 only while `hits < LOADING.get(path, 0)` —
`.ufo/waves/round-18/frozen/tests_llamacpp-live_controls.py:202-206`, with `LOADING =
{'/v1/models': 3, '/health': 1}` at `:166`. A zero-loading control (`LOADING` = 0) is a server
whose window never existed; its receipt shape (only `loading_envelope_graded` null) is
indistinguishable from a real server whose window was missed. The control proves the exit
classification, not that the real server can skip the window — do not cite it as evidence of
the latter.

## Limitations

- No live `llama-server` run: this seat is read-only and the item is source recon. All timing
  numbers are from committed receipts and the round-17 falsify advice, not re-measured now.
- The bind/listen internals are llama.cpp's call order plus `wait_until_ready`; the vendored
  cpp-httplib copy was not re-read.
- Mechanism (b) is [INFERENCE].
- Window widths quoted from LiveUnderLoad are its own measurement; I did not re-derive its
  load-average conditions.
- Live timings: a host-wide `stress-ng --cpu 32` window was scheduled ~21:06Z for ~4 min
  (`KamaR18.ProbeZeroLoading-2`); no live run was made here and the cited receipts predate it.
  Do not mix 503 counts across CPU-load or /proc-table-size regimes (see F4c).

## Installs

None.
