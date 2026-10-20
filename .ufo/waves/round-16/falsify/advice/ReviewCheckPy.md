VERDICT: confirm — check.py's schema gate, stub, drift assertion and 0/1/2 exit contract reproduce the wave's numbers exactly (current 72/72 exit 0; frozen 55 pass/17 fail exit 1; changed set = exactly the 17 MODEL_LOADING rows), but I falsified two of the harness's own contract statements and found one latent false-pass channel plus nine lower-severity schema/fidelity gaps. None of them changes a current verdict; the 30-row off-route typo channel is the one worth closing before this harness is trusted for round 17.

Seat: falsify reviewer, leaf (no subagents). Attacked item:
`tests/probe-verdicts/check.py` — schema validation, stub fidelity (headers, Server, Content-Length),
timeouts, drift grading, exit contract 0/1/2. Read-only on the lane; the only lane file written is this
report. Scratch `/tmp/kama-r16-ReviewCheckPy/` (removed after writing).

## Axes named
1. **Calibration** — does a green row mean the probe emitted the documented verdict for the documented wire fact?
2. **Fidelity of the instrument** — can the stub produce, and can the harness distinguish, the header/body/status conditions the matrices claim to test?
3. **Exit contract** — 0/1/2 must be unambiguous and never collapse into a traceback.
4. **Failure honesty** — a fixture typo, a malformed probe, or a killed probe must never read as pass.
5. **No harm** — no registry row, receipt, score, probe byte, or matrix changed by this seat.

## What I ran (commands and exit codes)

| # | Command (cwd = lane unless noted) | Exit | Result |
|---|---|---|---|
| 1 | `python3 tests/probe-verdicts/check.py --json --selftest` | **0** | `tests=72 passes=72 failures=0 schema=kama-probe-verdicts/v1 selftest.passed=True selftest.rejected=4/4`; stdout parsed as one JSON doc, summary on stderr |
| 2 | `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` | **1** | `55/72`; all 17 failures have `expected.verdict=MODEL_LOADING`; failure-name set is exactly `{r : r.expected.verdict==MODEL_LOADING}` from run 1 |
| 3 | `sha256sum tools/kama-probe.sh` | 0 | `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50` = `probe_sha256` in run 1's doc |
| 4 | compare run 2's `probe_sha256` with `frozen/manifest.json` | 0 | both `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`; manifest source commit `20e392ea683a…` |
| 5 | raw-socket battery importing `make_handler` (`/tmp/.../stubprobe.py`) | 0 | 12 wire captures quoted below |
| 6 | 16 synthetic matrices + fake probes in `/tmp/.../s3` (schema, drift, exit cases) | mixed, tabulated below | every documented branch exercised |
| 7 | probe-hang test (`sleep 43.91`, `/tmp/.../sandbox2`) | **1** after **30 s** | `error="probe timed out after 30s"`, `passed=False`; `sleep 43.91` still live after exit |
| 8 | stalled-client test against `make_handler` | 0 | socket closed after **10.0 s** with `b''`; matches `HANDLER_TIMEOUT=10` |
| 9 | route-typo end-to-end: `/tmp/.../typo` matrix `routes={"v1/models":…503 non-loading…}` + **real** probe | **0** | row `passed=True` while evidence says `GET /v1/models -> 404` (see F1) |
| 10 | evidence↔fixture status cross-check over run 1 | 0 | 71/71 HTTP rows served the declared status; 1 closed-port row has no HTTP status by design; **0 mismatches** |

Not run (by contract): `measure.py`, `llama-server`, and any bind/probe of 8080 or 34113.
`pgrep -x llama-server` empty at end; no stray test processes or listeners remained.

Frozen failure detail (run 2): every one of the 17 is
`FOREIGN_SERVICE / non-2xx-non-model-http / exit 2 / drift true` — a specific pre-change verdict,
not a crash or parse error. That is a clean separability control: the only moved rows are the loading
envelope, and they moved from a documented verdict to the new one.

Current-run distribution (run 1): verdicts `FOREIGN_SERVICE 37, MODEL_LOADING 17, MODEL_OK 8,
UNAUTHORIZED_SERVICE 5, MODEL_MISMATCH 3, DEAD 1, NOT_HTTP 1`; families 9. Drift is `False` for
exactly the 8 MODEL_OK rows and `True` for all other 64; every `probe_exit` equals `expected.exit`.
So the "changed set == the 17 loading rows" and "72 rows / 9 families / 17 MODEL_LOADING" claims are
confirmed independently.

## Confirmed contract statements

- **Exit 0** iff every row passes (run 1; synthetic control), **1** on any failed row including probe
  timeout and unparseable output (runs 2, 7, 6), **2** on argv/schema/harness faults (run 6:
  missing probe, unknown `--only`, unknown flag, non-int status, missing key, both bodies, `raw`+extra,
  string exit, duplicate names across files, non-array matrix, unreadable matrix). `--help` exits 0.
- **`--json`**: stdout is exactly one JSON document; the human `[PASS]/[FAIL]` summary is on stderr
  (verified by piping stdout into `json.load`; stderr line count > 0).
- **Drift grading bites both ways**: `MODEL_OK`+`drift=true` → exit 1; `MODEL_LOADING`+`drift=false`
  → exit 1; `MODEL_LOADING`+`drift=true`+exit 2 → pass. This is the right invariant for the only mode
  check.py uses (`--port`), and it matches `tools/kama-probe.sh:848-849`.
- **Stub wire facts** (captures, abbreviated):
  - default: `HTTP/1.0 200 OK\r\nServer: kama-stub\r\nContent-Type: application/json\r\nContent-Length: 31\r\n\r\n{"data":[{"id":"stories260K"}]}`
  - route `Server: llama.cpp` and lowercase `server:` each emit **exactly one** `Server:` header with
    the route value, and suppress the default.
  - `HEAD` emits `Content-Length` of the would-be body and no body; unknown path → `404 Not Found`
    with `Content-Length: 0`; malformed request line → `400 Bad Request` with `Server` +
    `Content-Length: 0` (not the stock HTML); `{"raw":"close"}` sends 0 bytes and closes for both a
    routed path and a malformed request, while still recording the parsed request.
  - auto `Content-Length` equals the exact body length when the route does not supply one.
- **Handler timeout** is real: a client that sends `GET /v1/models HTTP/1.1\r\n` and stalls is closed
  after 10.0 s, with no stderr noise (`log_message` is silenced).

## Findings, by severity

### F1 (medium, latent) — no route-match assertion; an off-route fixture can pass green
`grade` only requires `requests` to be non-empty (check.py:320-328) and records method+path
(check.py:214). It never asserts that `/v1/models` matched a declared route, nor that the status the
probe saw equals `routes["/v1/models"].status`. Demonstrated with the **real probe**: a matrix whose
key is `"v1/models"` (no leading slash) declaring a 503 non-loading body, expected
`FOREIGN_SERVICE/non-2xx-non-model-http/2`, **passes (exit 0)** while the probe reports
`GET /v1/models -> 404 ... (non-2xx HTTP from a non-model service)`. Blast radius: **30 of 72** current
rows expect exactly that default-404 outcome (`FOREIGN_SERVICE`/`non-2xx-non-model-http`), so the same
typo in any of those would be silently green. Not active today: my evidence↔fixture cross-check shows
all 71 HTTP rows were served their declared status (the 72nd is closed-port). Cheap hardening: record
the matched route in `_respond`, and grade a row failed (or harness error) when `/v1/models` fell
through to `default_route`/404.

### F2 (medium) — malformed probe output crashes the harness and emits no machine document
Two reachable probe shapes escape the `except` at check.py:332 and produce a traceback with **exit 1
and empty stdout** under `--json`, instead of the documented exit 2 or a graded record:
1. `{"rows":["not-an-object"]}` → `AttributeError: 'str' object has no attribute 'get'` at
   check.py:338 (`record[key] = row.get(key)`); `AttributeError` is not in the caught tuple.
2. non-UTF-8 stdout → `UnicodeDecodeError` inside `subprocess.run(..., text=True)` (check.py:277-
   278), before any grading.
This contradicts the module docstring's "2 on a harness/schema error" and the `--json` machine-document
promise; a CI consumer gets a traceback on stderr and nothing on stdout. The real probe emits validated
UTF-8 dict rows, so the 72/72 result is unaffected.

### F3 (low) — `expected.exit` accepts floats
check.py:141 tests `expected["exit"] not in VALID_EXITS or isinstance(..., bool)`. Python's `0.0 in
(0, 2)` is true, so `"exit": 0.0` (and 2.0) pass schema and later compare equal to the integer exit.
Demonstrated: a fixture with `"exit": 0.0` loads and grades a passing row, `EXIT=0`. `type(...) is int`
would close it.

### F4 (low) — drift is compared with `==`, so JSON integers 0/1 are accepted for booleans
check.py:346 uses `record["drift"] == (verdict != "MODEL_OK")`. `0 == False` / `1 == True`, so a probe
emitting `"drift": 0` for MODEL_OK, or `"drift": 1` for MODEL_LOADING, passes. Demonstrated both.
Missing drift (`None`) and string `"false"` do fail, so the strictness is only one-directional. An
`isinstance(record["drift"], bool)` guard would make the assertion exact.

### F5 (low) — an empty matrix directory is a green run
With no `*.json` siblings, `load_matrix` returns `tests=[]`, `failures=0`, `EXIT=0` (observed:
`tests=0 passes=0 failures=0`). If the directory is renamed, emptied, or the files fail to land, the
gate says success with zero coverage. A `if not tests: fail(...)` (exit 2) or a minimum-count
assertion would keep a vacuous run from reading as evidence.

### F6 (low) — three schema/range checks are looser than the instrument's contract
- Route keys are only checked to be strings (check.py:121-124); no leading-`/` requirement, so an
  unreachable route is accepted (feeds F1).
- `route.status` allows 100..999 (check.py:88-89, message "out of HTTP range"). HTTP statuses are
  100..599; 1xx is unusable as a final response — status 100 produced curl rc 8 "Invalid status line",
  while 999 was transmitted and reported as `999`. A matrix could encode an impossible status and the
  stub would send it.
- `expected.verdict`/`reason` are any strings (check.py:138-143). A synthetic probe emitting
  `MODEL_OKK` plus an expectation for `MODEL_OKK` graded **green, exit 0**. The probe defines
  `VOCAB` (kama-probe.sh:62) and check.py never consults it, so a typo'd expectation can co-sign a
  typo'd probe verdict. Cross-checking the documented 7-value vocabulary (and
  `MODEL_LOADING`→`llamacpp-loading`) is a two-line guard.

### F7 (low) — probe timeout kills only bash; grandchildren survive
`subprocess.run(..., timeout=30)` at check.py:277-278 kills the direct child. In my hang test the
runner returned after 30 s with the correct record error and exit 1, but `sleep 43.91` was still
running (PID observed with `pgrep -af`). The real probe's curls are bounded by `--max-time 2`, so the
practical exposure is small; `start_new_session=True` + `os.killpg` would make the 30 s cap a real cap.

### F8 (low, fidelity) — the stub cannot omit `Server`, and its default is not the real runtime's
`version_string` is `self._server_header or STUB_SERVER_HEADER` (check.py:188-191): there is no way to
send **no** Server header, and a route `Server: ""` silently becomes `kama-stub`. Consequently
`LoadingEnvelope.no-server-header` (LoadingEnvelope.json:69-71, why text "No Server header: …") does
not test that condition: the captured probe evidence is
`(Server: kama-stub) (body matches the llama.cpp loading envelope …)`. The row's *conclusion*
(body-driven detection, not header-driven) still holds because `kama-stub != llama.cpp`; only the
fixture's stated condition is false. Rename it (e.g. `non-llamacpp-server-header`) or add an explicit
`omit_server` capability. Related fidelity notes, none consulted by the probe today: responses are
`HTTP/1.0` with no `Date` header (real llama.cpp/cpp-httplib answers HTTP/1.1 with `Date`), so
keep-alive and date-sensitive semantics cannot be tested.

### F9 (low, fidelity) — Content-Length and Transfer-Encoding are only half-modelled
A route-supplied `Content-Length` is honored and suppresses the auto header (check.py:239-250), but the
full body is still written. Observed: `CL=5` + 10-byte body → curl downloads 5 bytes, rc 0, while the
socket carries 10 (trailing bytes); `CL=20` + 10-byte body → curl rc 18, which the probe maps to
`NOT_HTTP/no-http-response`. Short-CL truncation therefore "works" at the client while being
wire-inexact. `Transfer-Encoding: chunked` is passed through as a header but the body is not
chunk-framed and an auto `Content-Length` is added too —
`HTTP/1.0 200 OK … Transfer-Encoding: chunked\r\nContent-Length: 5\r\n\r\nhello` — an invalid dual
framing. No matrix file uses CL/TE (0/9 match `Content-Length|Transfer-Encoding`), so this is latent;
either implement chunking or reject TE in `validate_route`.

### F10 (low, documentation/diagnostics) — three statements in check.py do not match the code
- Docstring check.py:29 and help check.py:447-449 say `--selftest` feeds **3** embedded malformed
  tests; `SELFTEST_MALFORMED` has **4** (check.py:359-380) and the JSON reports
  `malformed_tests=4, rejected=4`.
- The comment at check.py:325 calls a no-request stub "a harness serve fault, not a probe verdict",
  but the branch returns a failed record (`passed=False`, exit **1**, observed), not a harness error.
- The drift comment at check.py:343-346 states the universal "probe contract: drift ==
  (verdict != MODEL_OK)". That is true only for the CLI-override path (kama-probe.sh:848-849);
  registry mode sets drift for a **MODEL_OK** row when `file_match ∉ {yes,inherited}`
  (kama-probe.sh:864-865). check.py never runs registry mode, so the assertion is safe here, but the
  comment overclaims and would mislead anyone reusing the predicate.

## Residual risk and verification gaps
- **HTTP/1.0 and no Date** are harmless for the current probe because every surface is fetched with a
  fresh `curl` invocation [INFERENCE]; a future probe that reuses a connection or asserts
  `Connection`/keep-alive semantics would be testing the stub, not llama.cpp.
- `bind_closed_port` binds/listens/closes and then the probe connects (check.py:262-268); a theoretical
  race could let another process take the port in between. Not observed across 72 rows and re-runs.
- Handler threads are daemons and `shutdown()` only stops the accept loop; a probe killed mid-response
  may leave a handler thread blocked until its 10 s socket timeout. Process exit is unaffected.
- I did not exercise concurrency (multiple check.py runs at once) or a live llama.cpp server; the
  live-server fidelity belongs to the C2 seats. [INFERENCE] Live-server behavior is out of my item.
- My route-typo demonstration used a synthetic matrix; the 30-row exposure is measured from run 1's
  expectation distribution, not from an existing typo. Today's matrices are off-route clean (run 10).

## Installs / updates
None. No pacman/uv/npx/cargo action; scratch used only `/tmp/kama-r16-ReviewCheckPy/` and was removed.
