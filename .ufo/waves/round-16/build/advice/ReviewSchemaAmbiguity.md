# ReviewSchemaAmbiguity — shared stub-matrix schema

Read-only seat. I ran no lane gate, harness, or probe. The only executions were isolated
`curl`/`http.server` controls in `/tmp` (framing and header semantics). No installs or upgrades.

Snapshot at write time (both files changed several times mid-review; line numbers are for these
shas):
- `tools/kama-probe.sh` sha256 `6edd3c4cfdf3f86c98202cef58859c29406d4a9cec17495454c514ac5972fa50` (1137 lines)
- `tests/probe-verdicts/check.py` sha256 `fd49ff7c0621bf3799c835b8e2baffbac61c35ce8e2c6e91b92fc495ce376140` (510 lines)
- 9 family files / **72 tests** (`AuthAndDead` 7, `EnvelopeShapes` 9, `ForeignControls` 8,
  `LoadingEnvelope` 8, `LoadingRace` 9, `NearMissTriple` 8, `NonLoadingStatuses` 7,
  `Overbroad503` 8, `ReadyControls` 8). All parse; a strict reading of the contract (keys, types,
  family/name, exit⇔verdict, one body key, header charset, framing headers, closed-mode shape,
  filenames) finds **0 violations**.

---

## 0. Blockers found during review — now fixed in the harness

These were real defects, not ambiguities, and the fixes landed while I reviewed. They stay here
as regression checks for L1's run.

### H1 (was fatal; fixed at `check.py:312-315`)
At `check.py` sha `0e395623…` the stub was constructed but never served (`serve_forever` absent,
`threading` not imported). Verified in isolation with stock `http.server` on this host (Python
3.14.8): `curl rc=28 elapsed=2.00s "Operation timed out after 2001 milliseconds with 0 bytes
received"`; `classify()` maps rc 28 to `DEAD timeout` (`kama-probe.sh:467-471`), so every stub
test would have read DEAD/timeout. In the pre-fix file the `finally` called
`server.shutdown()` (the call is now at `check.py:354-355`), which blocks forever when
`serve_forever` never ran — the shutdown event is only set by `serve_forever`'s `finally`
(verified: shutdown thread still alive after 3 s).
Current file: `threading.Thread(target=server.serve_forever, daemon=True).start()` at
`check.py:312-315`, plus a guard at `:326-328` (`"stub accepted no requests; probe never reached
a listening socket"`). Keep the guard: it distinguishes a serve fault from a verdict.

### H2 (was high; fixed at `check.py:349-351`)
`except OSError: record["error"] = "stub failure"` used to grade bind/exec faults as test
failures (harness exit 1). Now `raise HarnessError(f"stub failure in {test['name']}: {exc}")`
→ exit 2. Correct separation.

### B2 drift (was unasserted; fixed at `check.py:344-346`)
`passed` now includes `record["drift"] == (record["verdict"] != "MODEL_OK")`, so the C1 claim
"drift true" is measured. The shared schema text should state this invariant (see B2 below).

---

## 1. The six asked ambiguities

### A1. Header casing (names and media-type values) — OPEN
Harness sends authored keys/values verbatim (`check.py:229-240`); the probe matches the **value**
case-sensitively: `kama-probe.sh:513` `case "$F_CT" in *html*) ishtml=1 ;;` and
`kama-probe.sh:559` `*json*) C_REASON=schema-unrecognized ;;`.
Verified: curl reports `%{content_type}` verbatim (`W=200|TEXT/HTML` for `Content-Type:
TEXT/HTML`). So a 200 fixture authoring `Application/JSON` yields `FOREIGN_SERVICE
non-model-2xx`, not `schema-unrecognized`; `Text/HTML` still reaches `html-non-model` only via
the lowercasing body sniff (`kama-probe.sh:514-517`). Header **names** are case-insensitive on
the probe side only for `Server` (`grep -i '^server:'`, `:303`).
Resolution: (a) matrix header names MUST be canonical (`Content-Type`, `Server`) and media-type
values lowercase as sent on the wire; (b) probe SHOULD lowercase `F_CT` before matching (HTTP
media types are case-insensitive) — probe owner; (c) harness MUST reject case-insensitively
duplicate header names, which it currently forwards as two headers (`check.py:95` only checks
string:string).

### A2. Server header — OPEN (implementation-defined; schema silent)
`check.py:191` `return self._server_header or STUB_SERVER_HEADER`; `:229-236` select the authored
`Server` (case-insensitively) and skip it in the send loop, so exactly one header is emitted:
the authored value, else `kama-stub`. The probe takes the first `^server:` (`kama-probe.sh:303`)
and compares **exactly** to `llama.cpp` (`:529`), only for evidence `runtime=` — never a verdict.
Resolution to state: (i) `Server` in `headers` replaces (never duplicates) the stub marker;
absent → `Server: kama-stub`; (ii) comparison is case-sensitive, evidence-only, and no matrix
assertion may read `evidence`; (iii) an authored empty `Server` is inexpressible — it degrades to
`kama-stub` through the `or` at `:191`; forbid empty values.

### A3. body_text encoding and framing — OPEN
Contract silent. Harness (`check.py:243-248`): `body_json` → `json.dumps(..., separators=(",",":"))`
(compact, `ensure_ascii` default), `body_text` → `.encode("utf-8")`, `Content-Length` =
`len(body)` bytes. **Authored `Content-Length` is honored, not overridden** (`check.py:234-239`,
`sent_length = True`), so a wrong authored length yields curl rc 18 / hang instead of a measured
verdict.
Resolution: (i) body bytes are exactly the authored string as UTF-8, no strip/newline
augmentation (the pretty fixture at `LoadingEnvelope.json:127-140` depends on its trailing
newline); (ii) at most one body key (`check.py:97-98`), absent = zero-length body, `body_json:
null` = the four bytes `null`; (iii) forbid `Content-Length`, `Transfer-Encoding`, `Connection`
in matrix `headers` and have the harness reject/override them; (iv) note non-ASCII `body_text`
is legal and length is bytes, not characters (unpinned).

### A4. default_route — OPEN
Contract says only "Unlisted path with default_route null -> 404, empty body". Harness
(`check.py:216-221`): exact request path, then query-stripped path (`:216`), then `default_route`
(`:219`), then implicit `{"status": 404, "headers": {}}` (`:221`) with `Content-Length: 0`, no
Content-Type, empty body. Malformed requests go through an overridden `send_error`
(`:198-208`) that also refuses the stock HTML body. `default_route` is validated with the same R
rules (`check.py:127-128`) and answers every unlisted path **including `/v1/models`**.
Now verdict-bearing: `LoadingEnvelope.every-non-frontend-path` has `routes: {}` and relies on
`default_route` for `/v1/models` (`LoadingEnvelope.json:143-156`); `LoadingRace.HealthUnlisted`
relies on the implicit 404 for `/health` (`LoadingRace.json:45`).
Resolution to state: explicit routes win; match is path-only (query stripped), method-agnostic;
`default_route` applies to any unlisted path; the implicit 404 is exactly 404 + CL:0 + no
Content-Type + no body, never a framework error page; `default_route` may be any R including
`raw: close`.

### A5. closed mode — OPEN (reason implied, not specified)
`check.py:262-267` binds+listens an ephemeral loopback port, closes it, then probes; the probe
sees curl rc 7 → `DEAD connection-refused` (`kama-probe.sh:462-466`). Contract says "closed" →
DEAD but never names the reason; `AuthAndDead.json:90` pins `connection-refused`.
Resolution: `closed` ⇒ exactly `DEAD`/`connection-refused` (timeout is the blackhole outcome and
must not be conflated); `routes` MUST be `{}` and `default_route` null (silently ignored today —
a fixture could believe it serves something); harness MUST verify no listener remains and must
not select a registered consumer port (B4).

### A6. Exit expectation — PARTIALLY CLOSED
`check --port` exits 0 iff `MODEL_OK`, else 2 (`kama-probe.sh:881`; summary at `:889`). The
harness now enforces the mapping at load (`check.py:143-146`: exit ≠ (0 if verdict=="MODEL_OK"
else 2) is a schema error) and grades exit too (`:340-346`). Still unenforced: `expected.verdict`
membership in the probe's `verdict_vocabulary`, and probe exit 1 / other is not classified as
`probe_error` (it lands as a generic failure). The probe can exit 1 from `emit_json` failures
(`kama-probe.sh:180-188`), missing deps, or bad argv.
Resolution: assert vocabulary membership at load; treat probe exit ∉ {0,2} as `probe_error` with
stderr captured; never compare it to a verdict.

---

## 2. Additional ambiguities with material effect

### B1 (high) — `raw: "close"` must define whether the request is drained — OPEN
Contract: "accept the TCP connection, send nothing, close"; harness prompt repeats "accept and
close without bytes". `AuthAndDead.json:95,98,102` expects `NOT_HTTP empty-reply` (rc 52).
Verified framing fact: closing immediately after `accept()` without reading yields **rc 56
`connection-reset`**; reading the request head first yields **rc 52 `empty-reply`**
(`kama-probe.sh:474,479` are different reasons). It works today only because
`BaseHTTPRequestHandler` parses the request head before `_respond` (`check.py:213-226`), so the
close happens after the drain — incidental, not specified.
Resolution: schema must say "read the request head (bounded), then FIN; no SO_LINGER reset; no
response bytes", keeping the fixture at `empty-reply`.

### B2 — drift invariant (fixed in harness; schema text missing)
`check.py:344-346` now asserts `drift == (verdict != "MODEL_OK")`. The shared schema's
`expected` object has no `drift` field and its text never says drift is graded. Resolution:
document the invariant (all non-`MODEL_OK` verdicts, including `MODEL_LOADING`, must report
drift true) or add optional `expected.drift`.

### B3 (medium) — probe JSON envelope is under-checked — OPEN
Harness reads only `doc["rows"][0]` (`check.py:331`) and ignores `schema`, `subcommand`,
`verdict_vocabulary`, and `summary.exit`. A probe whose process exit disagreed with its own
summary, or whose vocabulary regressed, would not be caught. Resolution: assert `len(rows)==1`,
`summary.exit == process exit`, `schema=="kama-probe/v1"`, and `expected.verdict in
verdict_vocabulary.split()` (`kama-probe.sh:62,850,889`).

### B4 (medium; C2 claim) — ephemeral stub port can be a registered consumer port — OPEN
`check.py:266` and `:309` bind `127.0.0.1:0`. `/proc/sys/net/ipv4/ip_local_port_range` is
`32768 60999`, which includes registered consumer port `34113`
(`registry/endpoint-consumers.tsv:36-37`, `grep:http://127\.0\.0\.1:34113...`). C2 promises "no
registered port is ever served", and `check.py:6` only says the stubs write no registry/config
state — it does not exclude registry ports. Resolution: after bind, if the assigned port appears
in the registry's declared ports (and not just 8080/34113 — parse the TSV), close and rebind
(bounded), surfacing refusals; or allocate from a lane-owned, registry-checked range.

### B5 (low) — extra keys and integer-token policy — OPEN
The matcher compares only the three named fields (`kama-probe.sh:440-443`) and
`EnvelopeShapes.ExtraFieldsAllowed` pins top-level extras (`EnvelopeShapes.json:134`), but no
fixture pins extra keys **inside** `error`, and none pins `"code": 503.0`. A float token is
rejected by `isinstance(code, int)` (`:443`) even though `503.0 == 503` numerically.
Resolution: state extras are ignored at both levels; `error` must be an object; `code` must be a
JSON integer token (fraction/exponent, string, bool all negative); add both fixtures.

### B6 (low) — header character set / injection — OPEN
`validate_route` only type-checks header keys/values (`check.py:90-96`). A value containing CR/LF
would inject headers or split the response; any other C0 control reaches evidence and makes
`jstr` emit invalid JSON (`kama-probe.sh:170-177` escapes only `\t\n\r`), turning the probe into
exit 1. Resolution: reject CR/LF/NUL and non-printables in names/values; require RFC-token names
and printable-ASCII single-line values.

### B7 (low) — uniqueness and family binding — OPEN
The harness enforces global duplicate-name refusal (`check.py:169`) but never checks
`family == <file stem>` or the `name` prefix (`:114-117` checks only non-empty strings). The
contract says only "unique string" / "`<Family>`". Resolution: declare global uniqueness across
the directory, file stem == family, `name` prefixed `Family.` (all current files comply).

### B8 (low) — status range — OPEN
`validate_route` accepts 100–999 (`check.py:88`). A 1xx final response makes curl wait for a
final response, producing `DEAD timeout` instead of the fixture's intent [INFERENCE].
Resolution: restrict to 200–599 (or explicitly forbid 1xx and 600+).

### B9 (low) — timeout is unmeasurable by this schema — OPEN
No delay/hang primitive exists in R, so `DEAD timeout` (`kama-probe.sh:467-471`) can never be
pinned; no fixture attempts it. Resolution: declare it out of scope, or add a bounded `delay_ms`
route key with documented `--timeout` interaction.

### B10 (low) — wildcard `expect` tokens and empty string — OPEN
`classify()` treats `''`, `'*'`, `'-'` as wildcards with reason `expected-wildcard`
(`kama-probe.sh:530-532`); `ReadyControls.json:71,95` pin `*` and `-`. The harness accepts an
empty `expect` string (`check.py:114-117`), which silently becomes a wildcard. Resolution:
document the three tokens as the only no-id forms and reject `""` in matrix files.

### B11 (low) — harness output/exit contract absent from the shared schema — OPEN
The harness exits 0 (all pass) / 1 (any failure) / 2 (schema or harness error)
(`check.py:458-493`); the probe itself uses 2 for drift. L1's runner must not conflate them.
Resolution: publish these semantics; the runner treats harness 2 as infrastructure, 1 as failed
tests, and never as a probe verdict.

---

## 3. Verified non-findings (checked because they would otherwise be ambiguous)
- MODEL_LOADING vocabulary plumbing is consistent: `VOCAB` (`:62`), usage (`:117`), listeners
  counters/summary (`:723,733,743,748`), and the baseline validator (`:939`) all include it;
  snapshots of a loading server will not be dropped as malformed.
- Precedence is defined in code: 401/403 (`:495-496`) before the 503 envelope (`:503-506`),
  which precedes HTML/2xx classification (`:513`). A 503 with `text/html` CT carrying the exact
  JSON envelope currently yields MODEL_LOADING (body-first); no fixture pins that boundary.
  The shared schema should state the ladder.
- Calibration honesty: the verdict is a **body-shape** claim, and the probe says so —
  `kama-probe.sh:423` "the body shape does not prove the runtime", and the evidence string at
  `:506` says "runtime identity and served model unverified". C1 prose should therefore say the
  probe recognises llama.cpp's documented loading envelope, not that it identified the runtime.
- The harness honors the contract invocation (`check.py:274-276`: `check --port P --expect E
  --json --timeout 2 --connect-timeout 1`), omits `--id` (rows label `cli-override`), starts the
  stub before the probe, and fails unknown `--only` names as a schema error (exit 2).
- `bind_closed_port` releases the listener before the probe and `ThreadingHTTPServer` binds
  before `run_probe`, so there is no startup race in the current shape.

## 4. Residual risk / gaps
- I did not execute the probe or the harness (measurements belong to L1). The two fixed
  blockers are verified by source reading plus isolated stdlib/curl controls; L1 must still
  observe one real stub round-trip and a `--selftest` run.
- Both files changed repeatedly during review (harness: 484 → 506 → 510 lines). Line numbers are
  tied to the sha256 values above; re-derive them if the files move again.
- `[INFERENCE]`: 1xx behavior with curl (B8) and the kernel choosing a registered ephemeral port
  (B4 is a possibility, not a guarantee).
- The MODEL_LOADING matcher is python3-gated (`kama-probe.sh:429` `[ "$HAVE_PY" -eq 1 ] ||
  return 1`); with `python3` absent the probe fails closed to FOREIGN_SERVICE. The harness should
  record `python3` availability as an environment fact so a red matrix can be attributed.
- Fixture `why` strings cite drifted probe line numbers (e.g. `AuthAndDead.json:95` cites
  `kama-probe.sh:436-440`; rc-52 handling is now `:473-475`). Cosmetic, but the matrix should not
  be treated as line-accurate evidence.
