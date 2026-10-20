## Round-16 calibration: MODEL_LOADING (owner: kama)

llama.cpp answers HTTP 503 with a loading envelope on every non-frontend path while its model is not yet ready. Before round 16, `tools/kama-probe.sh` graded that response `FOREIGN_SERVICE` / `non-2xx-non-model-http`, which overreached: the responder is a llama.cpp server, not a non-model service. This section registers the repaired verdict. It classifies identity only. A loading server is not a readiness pass and not a model answer.

Integration precondition: the text below describes the target state after the `classify()` repair lands in `tools/kama-probe.sh` and L1 measures it. Until then `MODEL_LOADING` is absent from the shipped `VOCAB` (`tools/kama-probe.sh:55`), and the shipped probe still returns `FOREIGN_SERVICE` for the envelope.

### Verdict vocabulary

The vocabulary is seven verdicts: `MODEL_OK` | `MODEL_MISMATCH` | `MODEL_LOADING` | `FOREIGN_SERVICE` | `UNAUTHORIZED_SERVICE` | `DEAD` | `NOT_HTTP`. The list at lines 11–14 is historical and is not rewritten; this section adds `MODEL_LOADING`.

- Reason: `llamacpp-loading`.
- Drift: `true`. The registry path treats every non-`MODEL_OK` verdict as drift (`tools/kama-probe.sh:820`). A loading row therefore counts toward `drift` and yields exit `2`.
- Selection rule: chosen only when `GET /v1/models` returns HTTP 503 AND the body is a JSON object whose `error` object has `message` == `Loading model`, `type` == `unavailable_error`, and integer `code` == 503 (all exact). Any other body keeps its current verdict.
- Exit `2` is not a readiness pass. Exit `0` still requires `MODEL_OK` on every declared row.
- `/health` is not the decision surface. llama.cpp documents the same 503 body on `/health`; the probe reads `/v1/models` and records `/health` only as evidence.

### Decision table rows (append to the table in the decision section)

| Symptom | First check | Verdict | Action |
|---|---|---|---|
| `GET /v1/models` returns HTTP 503 with the llama.cpp loading envelope (signature below) | Run `bash tools/kama-probe.sh check`; confirm the row `reason` is `llamacpp-loading` and read the `GET /health` evidence on that row | `MODEL_LOADING` (`llamacpp-loading`, drift, exit 2) | The runtime is alive and still loading: neither foreign nor dead. Do not repoint the consumer or treat the 503 as a fault. Re-run `check` until the row is `MODEL_OK`. If loading does not finish, the row stays `MODEL_LOADING` and is reported as drift in progress, not as a reconciled endpoint. |
| HTTP 503 with any other body (for example `no slot available`, an `unavailable_error` with a different message, a non-JSON body, or an HTML page) | Run `check`; read the verdict and reason | Unchanged: `FOREIGN_SERVICE` (`non-2xx-non-model-http` or `html-non-model`) | Scope limit of round 16: only the exact loading envelope becomes `MODEL_LOADING`. |

### Error signature (exact envelope)

Observed on the loading state of llama.cpp b11755 (commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`):

```text
status:       503
Content-Type: application/json; charset=utf-8
Server:       llama.cpp
body:         {"error":{"message":"Loading model","type":"unavailable_error","code":503}}
```

The body is produced by `safe_json_to_str` (`dump_safe()`, compact). Key order is insertion order in the server (message, type, code), per the `common_json` header. The README documents the same envelope with a different key order. The `Server` header comes from `set_default_headers` and applies to every response from that server; the L1 smoke run did not record headers for the 503 response. The reason phrase of the status line was not observed in this seat.

| Verbatim string | Where | Meaning | Next action |
|---|---|---|---|
| `{"error":{"message":"Loading model","type":"unavailable_error","code":503}}` with `application/json; charset=utf-8` and status 503 | `GET /v1/models`; also `/health` and every other non-frontend path while the model is not ready | llama.cpp is loading; not ready | `MODEL_LOADING` / `llamacpp-loading`; re-run `check` after loading |
| `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}` | llama.cpp README `GET /health` section (documentation, not a live capture) | Same envelope; different key order and spacing | Parsers compare fields, never key order or whitespace |
| `{"error":{"message":"no slot available","type":"unavailable_error",…}}` (the `code` value was not inspected) | `?fail_on_no_slot` path, `server-context.cpp:5396` | Busy, not loading | Stays `FOREIGN_SERVICE`; the exact-message rule excludes it |

Scope facts from the server source, not runtime-observed in this seat:
- Frontend paths (`/` and embedded UI assets) are exempt while loading and serve normally, so `GET /` is not a loading signal.
- The loading-state middleware runs before the API-key middleware, so a keyed server that is still loading answers the 503 envelope rather than a 401 (`server-http.cpp:354` before `:357`).

### Local gate and capability registry (owner: kama)

Round-16 rows follow the round-13/14 seven-column format. Registration is not a verdict: a green check certifies only its finite fixture matrix, a live receipt certifies only its captured run, and neither is serving readiness or routing authority. Exit meanings do not transfer across tools (see the round-14 note above). Nothing in these rows is run by the author seat; L1 runs every measurement.

| Name | Kind / entry command | Verdict map | Self-test | Pinned values | Write scope | Owner |
|---|---|---|---|---|---|---|
| Stub-matrix verdict harness | gate: `python3 tests/probe-verdicts/check.py [--probe PATH] [--only NAME]... [--json]`; default probe `tools/kama-probe.sh` | 0 all matrix tests pass; 1 any test fails (verdict, reason and exit must all equal expected); 2 harness or schema error (duplicate names across files, unknown keys, invalid response shape); probe runs are capped at 30 s each | `python3 tests/probe-verdicts/check.py --selftest`: runs the matrix against the default probe and asserts that three embedded malformed tests are rejected | `tests/probe-verdicts/*.json` (planned families: LoadingEnvelope, LoadingRace, Overbroad503, NonLoadingStatuses, ReadyControls, AuthAndDead, EnvelopeShapes, ForeignControls). Not present in the repo on 2026-10-20; expected values are literal oracles, not computed from the probe | stdout only; test servers bind `127.0.0.1:0` and are closed after each test; closed-mode tests bind and close a socket. No registry, history or consumer file is written | kama |
| Live llama.cpp capture | capability (not a gate): `python3 tools/kama-llamacpp-live.py --model PATH --model-sha256 HEX [--server PATH] [--alias ALIAS] [--probe PATH] [--ctx 256] [--threads 1] [--ready-timeout 60] [--out PATH]` | 0 all checks pass; 1 any check fails; 2 setup error; 3 model digest mismatch (before launch). A receipt is evidence, not a verdict | None specified in the round-16 build contract; none is claimed | llama-server b11755, tag commit `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad` (verified via GitHub API on 2026-10-20). Asset sha256 `753bfa73…e226` and model sha256 `270cba1b…d256` are from the build contract and were not verified in this seat | Receipt to `--out` or stdout; temporary server log is copied (matching lines only) and removed. Writes nothing under `~/.config`, `~/.omp` or systemd. Binds `127.0.0.1` on a free port refused if it is 8080, 34113 or any port in `registry/endpoint-consumers.tsv`. Tears the server down and records proof | kama |
| Live receipt validator | gate: `python3 tests/llamacpp-live/check-receipt.py RECEIPT [--expect-model-sha256 HEX] [--expect-server-sha256 HEX]` | 0 valid; 1 invalid (every problem listed); 2 unreadable. Exit 1 here is a receipt-invalid result, not a probe error | `python3 tests/llamacpp-live/check-receipt.py --selftest`: one minimal valid receipt in memory plus at least eight single-field mutations; valid must exit 0 and each mutation must exit 1 | Schema `kama-llamacpp-live/v1`; required check IDs: health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_exited, teardown_port_closed | Reads the receipt only; self-test uses in-memory fixtures. Writes nothing | kama |

Known gaps for the integrating seat: the `listeners` summary counts verdicts in a `case` with no `MODEL_LOADING` arm (`tools/kama-probe.sh:684-690`), so a loading endpoint would be uncounted there until the repair adds one. The `usage()` vocabulary line (`tools/kama-probe.sh:110`) and the header comment (`:29`) also need the new verdict.

### Sources (accessed 2026-10-20)

- llama.cpp b11755 `tools/server/server-http.cpp:308–323` (raw: `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/tools/server/server-http.cpp`): `res.status = 503;` at 314; body `{"message", "Loading model"}` at 318; `Content-Type` `application/json; charset=utf-8` at 323; the state middleware is called before the API-key middleware at lines 354 and 357. The frontend exemption at 309–310 reads "frontend asset, allow it to load and show "loading"".
- llama.cpp b11755 `tools/server/README.md:479–487` (raw URL as above): "Explanation: the model is still being loaded." (line 487; body at 486 has code-first key order).
- llama.cpp b11755 `common/json.h:24` (raw: `https://raw.githubusercontent.com/ggml-org/llama.cpp/b11755/common/json.h`): "object keys keep the order in which they are added".
- llama.cpp b11755 `tools/server/server-common.cpp:1695–1697`: `return data.dump_safe();`.
- llama.cpp b11755 `tools/server/server-context.cpp:5396`: `res->error(format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE));`.
- llama.cpp tag `b11755` (GitHub API: `https://api.github.com/repos/ggml-org/llama.cpp/git/refs/tags/b11755`): `"sha": "704366d76f8748cf9ad3df62a464bfcc8d1ae6ad"`.
- Lane: `tools/kama-probe.sh:20`, `:29`, `:55`, `:110`, `:520–522` (`C_REASON=non-2xx-non-model-http`), `:684–690`, `:820`; `SKILL.md:11–14`, `:127–140`, `:169–182`, `:294–306`, `:463–466`.
- Round-16 build contract: `.ufo/waves/round-16/build/make_spec.py:46` (harness exit map), `:69` (live capture exit map), `:76` (receipt validator exit map).
