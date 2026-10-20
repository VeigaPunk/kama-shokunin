# VerdictHarness — round 16 build advice

Seat: KamaR16.VerdictHarness. Axes: operability + calibration. Owned file only.

## Files changed

- `tests/probe-verdicts/check.py` (new, stdlib-only, executable) — the stub-server
  matrix harness for the kama-probe verdict schema. No other files touched;
  no matrix `.json` files written (matrix seats own those).

## Post-review corrections (KamaR16.ReviewSchemaAmbiguity, all verified)

- `serve_forever` was never started: the socket listened but never accepted,
  so every stub test would have read DEAD/timeout and the `finally`
  `shutdown()` would have blocked forever. Fixed: daemon thread running
  `server.serve_forever` starts immediately after construction.
- `grade` now records an explicit error when a stub test accepts zero
  requests (serve-fault guard; the reviewer asked for a selftest/assertion —
  implemented as a recorded error, which keeps the rest of the matrix running
  while still failing loudly).
- `passed` now also asserts `drift == (verdict != "MODEL_OK")` — the probe's
  own contract, and the property C1's MODEL_LOADING relies on.
- `validate_test` rejects `expected.exit` inconsistent with the verdict
  (`MODEL_OK` requires 0, everything else 2); a `MODEL_OK`/exit-2 entry can no
  longer grade a correct probe as failing.
- `OSError` inside `grade` (bind/exec faults) is re-raised as `HarnessError`
  → exit 2 via `main`, not recorded as a test failure.
- `--selftest` now embeds 4 malformed tests (added the inconsistent
  exit/verdict pair); spec minimum was 3.

Live single-test smoke (in-process, no matrix file written): the repaired stub
answered the probe, requests were recorded (`GET /v1/models`, `GET /health`),
teardown completed in ~0.5 s. Note: the working-tree probe already returns
`MODEL_LOADING`/`llamacpp-loading` on a 503 loading body — the C1 fix appears
to have landed in `tools/kama-probe.sh`; the frozen before-probe is the red
reference.

## Behavior

- Loads sorted `*.json` siblings of itself; each must be a JSON array of tests.
  Refuses (exit 2) on: unreadable/invalid JSON, non-array doc, unknown keys on
  test/expected/route objects, missing keys, non-int `status` (bool rejected),
  headers not `str:str`, both `body_json`+`body_text`, `{"raw":...}` not exactly
  `{"raw":"close"}`, `port_mode` outside `stub|closed`, `expected.exit` outside
  `{0,2}`, and duplicate `name` across files (first-defining file is named).
- `stub` mode: `ThreadingHTTPServer` on `127.0.0.1:0` per test, fresh handler
  class per test (no shared state). Exact path match, then path-without-query
  fallback, then `default_route`, else bare 404 empty body. `body_json` is
  serialized `json.dumps(separators=(",",":"))`; `body_text` UTF-8. Route
  headers sent verbatim; a `Server` header in the route overrides
  `version_string()`; otherwise `Server: kama-stub`. Content-Length computed
  unless the route supplies one. `{"raw":"close"}` parses the request, records
  it, then closes without bytes (curl sees empty reply → NOT_HTTP/empty-reply).
  All HTTP methods route identically via `__getattr__` → `_respond`.
- `closed` mode: bind+listen+close a socket, probe the released port (curl
  refused → DEAD/connection-refused).
- Probe invocation exactly: `bash PROBE check --port P --expect E --json
  --timeout 2 --connect-timeout 1`; 30 s subprocess timeout records a failure
  (never hangs the harness); 10 s handler socket timeout so a stalled client
  cannot wedge a stub thread.
- Per test records `requests` (method+path, in order), `probe_exit`, parsed
  `verdict`/`reason`/`drift`/`served_model`/`evidence` from `rows[0]`,
  `error` (unparseable output/timeout/stub fault), and `passed` = verdict,
  reason and exit all equal `expected` plus `drift == (verdict != MODEL_OK)`.
- Output: `{"schema":"kama-probe-verdicts/v1","probe","probe_sha256",
  "matrix_sources","tests","passes","failures","records":[...]}`. `--json`
  emits the document on stdout with the human summary on stderr; default
  prints the human summary only. Exit 0 all pass / 1 any failure / 2 harness
  or schema error. `--only NAME` repeatable; unknown names exit 2.
- `--selftest` runs the matrix against the **default** probe (spec wording)
  and additionally feeds 4 embedded malformed tests (unknown key, non-int
  route status, expected.exit=1, MODEL_OK/exit-2) through the validator; any
  accepted test marks `selftest.passed=false` and forces exit 1.

## Design choices

- Fresh handler subclass per test via `make_handler` keeps route state
  isolated; `version_string()`/`send_response` overridden (not send_error's
  HTML) so the stub never emits the stock BaseHTTPRequestHandler page, which
  would itself trip html-non-model heuristics.
- `send_error` overridden to emit bare status + empty body, honoring a
  raw-close `default_route` even for malformed requests.
- Observed fields are top-level in each record (`verdict`, `reason`,
  `probe_exit`), not nested under `observed` — schema confirmed with
  KamaR16.MeasureRunner for `measure.py` consumption.

## Limitations

- `closed` mode has a TOCTOU window between socket close and probe connect
  (another process could rebind the port); probability is negligible on a
  free loopback range and a wrong verdict would record as a test failure, not
  a silent pass.
- HEAD suppresses the body but keeps Content-Length; probe only issues GET.
- Routes in `closed`-mode tests are still schema-validated but never served.
- Handler socket timeout (10 s) is a backstop; a probe that connects but never
  sends a request line is still bounded by the 30 s subprocess timeout.

## Verification

`python3 -m py_compile` is clean; an in-process smoke (no matrix file written,
since matrix files are owned by sibling seats) served the stub live, recorded
both probe requests, and tore down in ~0.5 s; `run_selftest()` rejects all 4
embedded malformed tests. Full matrix execution remains L1's measurement.

## Installs

None.
