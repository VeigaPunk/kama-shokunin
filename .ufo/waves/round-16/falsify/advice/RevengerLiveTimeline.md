VERDICT: confirm — the round-16 live receipt's timeline reconstructs coherently. Timestamps are ordered and mutually anchored, the port is identical across argv / probes / probe-declared URLs / teardown log, and teardown provably follows the probes. No divergence found; two apparent anomalies I chased dissolved under measurement.

# attacked

- `.ufo/waves/round-16/live/receipt.json` (schema `kama-llamacpp-live/v1`, port 32845, 10/10 checks, exit 0 per `live/controls.txt`).
- `.ufo/waves/round-16/live/receipt-frozen-probe.json` as the intra-session control (same tool, frozen pre-round probe).
- Harness `tools/kama-llamacpp-live.py`, probe `tools/kama-probe.sh`, pinned upstream `sources/llama.cpp-704366d/`.
- Read-only attack: no lane/fleet file edited, no llama-server started (this item does not grant that permission), nothing bound on 8080/34113.

# reconstructed timeline (2026-10-20 UTC, ms resolution)

| t (UTC) | event | receipt field / evidence |
|---|---|---|
| 13:49:38.040 | `started_utc`; set after model/install-tree/probe hashing, immediately before `Popen` | receipt.json `started_utc`; code `tools/kama-llamacpp-live.py:737` |
| 13:49:38 (exact second) | server-internal `time(NULL)` at load: `created=1792504178` | `/v1/models` body; `1792504178` = 13:49:38.000Z = floor(started_utc) |
| server +4.591 ms | `load_model: loading model '…/stories260K.gguf'` | `teardown.log_lines[0]` |
| server +8.725 ms | `llama_server: model loaded` | `teardown.log_lines[1]` |
| server +8.728 ms | `llama_server: listening on http://127.0.0.1:32845` | `teardown.log_lines[2]` |
| loop +1 ms | `/health` → ConnectionRefusedError | `transitions[0]` |
| loop +1 ms | `/v1/models` → ConnectionRefusedError | `transitions[1]` |
| loop +22 ms | `/health` → 200 `{"status":"ok"}`, and the LISTEN socket is provably the child's | `transitions[2]`, `port_listener_ownership: "child"` |
| then | captures: health 200, /v1/models 200, /props 200, /slots 200, /metrics 501 (order = `ready_captures`) | `captures`; code lines 482-530 |
| then | probe 1 `MODEL_OK` exit 0 (served `kama-stories260k`); probe 2 `MODEL_MISMATCH` exit 2 (`served-id-mismatch`) | `probes` |
| ~38.167 | SIGTERM to process group; graceful exit code 0 in 3 ms; no SIGKILL; port refuses | `teardown.term_wait_ms: 3`, `returncode: 0`, `sigkill_sent: false`, `port_refuses: true` |
| 13:49:38.170 | `ended_utc`; span 130.0 ms; 10/10 checks | receipt.json |
| 13:49:38.250 | sibling frozen-probe run starts (port 39375); ends .379 (129 ms) | receipt-frozen-probe.json |

The loop-relative clock starts at `time.monotonic()` after `Popen` returns, so the 22 ms readiness window already contains the server's 8.7 ms startup; the two clocks are not directly comparable but are mutually consistent.

# consistency results

**A. Timestamps ordered — PASS.** `started 38.040 < ended 38.170`; transitions non-decreasing (1, 1, 22); server log timestamps strictly increasing (4.591 < 8.725 < 8.728) with `model loaded` before `listening on`, exactly the source order (`server.cpp` logs "model loaded\n" then registers the signal handler, then logs listening at :544). The server's own `created` field floors to the same second as `started_utc`, tying the harness wall clock to the server clock.

**B. Port consistent — PASS.** Programmatic equality over every port-bearing surface: `receipt.port` = argv `--port` = both probe argv `--port` = both probe rows' `declared` URL = the teardown log's `127.0.0.1:32845` = **32845**. Host is `127.0.0.1` in argv, in both declared URLs and in the log line. 32845 is absent from `port_refusal_set` ([8080, 34113]), absent from the registry TSV, and `refused_ports()` re-run now returns exactly [8080, 34113] from `registry/endpoint-consumers.tsv:35-37`.

**C. Probe declared URL port — PASS.** Both rows carry `declared: http://127.0.0.1:32845/v1`. The probe's `--port` branch synthesises that URL from the argument (`tools/kama-probe.sh:783-791,840-853`); I exercised it live against a fake surface on a different port and got `http://127.0.0.1:<passed port>/v1`, so the declared URL is a function of `--port`, and `--port` in the recorded argv is 32845.

**D. Teardown after probes — PASS.** Code order is captures → (verify, probe) ×2 → post-probe verify → checks → `finally: teardown` (lines 866-949). The receipt independently proves it: both probes returned live-HTTP verdicts (`MODEL_OK` with `served_model`, `MODEL_MISMATCH`), which is only possible while the server was up; the last liveness gate recorded `port_listener_ownership: "child"`; only then does teardown show SIGTERM, exit 0 in 3 ms, and `port_refuses: true`. The teardown temp log (`/tmp/kama-llamacpp-live-j9achou8.log`) was unlinked by the tool as designed — `ls` on it exits 2 and no `kama-llamacpp-live-*.log` remains.

**E. Identity/data integrity — PASS (recomputed now).** `install_tree` over `/home/vgpnk/.local/opt/llama-b11755` recomputes to `6c216313a88d71b141bc62f684b8f95c040710ff050801b13521861826785a2c` over 51 files, byte-identical to the receipt; `server.sha256` equals the `install_tree["llama-server"]` entry and equals `libllama-server-impl.so`'s recorded digest where applicable; `model.sha256 == model_sha256_post`; `probe.sha256 = 6edd3c4c…` equals `sha256sum tools/kama-probe.sh` today. The frozen sibling's `probe.sha256 = 93ee4302…` equals both the file and `frozen/manifest.json`.

**F. Recorded bodies match their recorded digests — PASS.** Re-hashing the retained bodies: health 15 B → `a29ee2b1…` (equal in both the capture and the readiness transition), models 682 B → `d0ed0543…`, with `Content-Length: 682` equal to the actual length. `/v1/models` has `data[0].id = kama-stories260k`, `owned_by = llamacpp`, `created = 1792504178`.

**G. Surface semantics match upstream b11755 — PASS.** `total_slots: 4` is the `--parallel` auto default (README: default −1; `server.cpp:169-173` sets 4 and `kv_unified=true`), so `default_generation_settings.n_ctx: 256` (a shared unified pool) with 4 slots is not a contradiction and `/slots` length 4 agrees; `-c 256` == props `n_ctx` 256; CORS header `Access-Control-Allow-Origin: ""` is exactly upstream's default branch `res.set_header(..., params.cors_origins)` with an empty default (`server-http.cpp:331-345`); `/metrics` 501 without `--metrics` is the documented response; SIGTERM is handled via `sigaction` (`server.cpp:533-534`), so exit code 0 in 3 ms is expected rather than −15.

**H. Checks agree with captures — PASS.** 10/10 `passed`; each `observed` equals the corresponding capture (health 200, ids, owned_by, 501, props fields, probe exits/verdicts/reasons, teardown, post-hash).

# measurements (command → exit → result)

- `jq`/`python3` receipt inspection and equality script → exit 0 → `all equal: True`; span 130.0 ms; `floor matches created: True`.
- `python3` replay of the harness's exact body (4 `verify_live`, `ready_captures`, 2 `run_probe`, `teardown`, re-hash) against a fake surface serving the receipt's own bodies → exit 0 → at load 1-min 2.98: total non-readiness 99.8–102.6 ms (probes 44.7–47.8 ms; gates 1.05–1.55 ms; captures 1.4–2.1 ms; teardown 1.2 ms; rehash 0.7 ms). +22 ms readiness + ~2 ms spawn = **121.8–124.6 ms ≤ the recorded 130 ms**.
- The same replay earlier at load 1-min 12.29 → exit 0 → 120.8–145 ms (over budget). Load sensitivity is real: probe CPU 50.8 ms at load 12 vs 47.0 ms at load 3.6, and `port_owned_by` 4.38 ms vs 1.1 ms. My first reading of a ~20 ms shortfall was a load artifact, not a receipt defect.
- `python3` probe CPU stability (6 runs) → probe wall 45.8–48.5 ms, CPU 47.0–49.6 ms, spread 5.5%.
- Transition-row arithmetic: fresh-process first refused GET 0.862–0.882 ms, second cumulative 0.94–0.99 ms, `time.sleep(0.02)` returns 20.039–20.067 ms; a script that hashes the same 54 MB immediately before polling reproduces `t_ms = 1, 1, 21` (4/4 runs). The receipt's `1, 1, 22` is one rounding millisecond away and is identical in the sibling receipt. [INFERENCE] the extra millisecond is first-poll cost under a just-forked server + cold caches.
- `ss -ltn | grep -E ':32845|:8080|:34113'` → exit 1 (nothing listening); `pgrep -x llama-server` and `pgrep -af llama-server` → exit 1 (none), consistent with `controls.txt` `post_pgrep_llama_server=0`.
- Probe against the now-closed port 32845, 5 runs → exit 2 each, `DEAD connection-refused`, wall 25.3–28.3 ms (calibration that a probe invocation costs tens of ms, not single ms).
- `strings`/`grep` on `llama-server` and `libllama-server-impl.so` → log formats `srv  %12.*s: loading model '%s'`, `listening on %s`, `model loaded` all present; no startup `build:` format string exists, so the 3-line kept log is complete under `LOG_KEEP = build|model loaded|listening|loading`.
- `sha256sum` on `tools/kama-probe.sh` → `6edd3c4c…`; on `frozen/kama-probe-before.sh` → `93ee4302…`; `manifest.json` sha256 → `93ee4302…`.

# hypotheses I formed and refuted (kept as evidence)

1. "`total_slots: 4` contradicts `-c 256`" — refuted: slots auto-default to 4 with unified KV, so 256 is the shared pool.
2. "The log is missing the customary `build` line" — refuted: b11755's server libs contain no startup build-log format (only `--version`'s `version: %s (build %d, commit %s)`).
3. "130 ms is too short to contain two probes" — refuted at the run's load level; the apparent shortfall was a measurement-load artifact (CPU-time of the same probe inflated 7.5% at load 12 vs load 3.6).

# residual risk

- The 130 ms span leaves roughly 5–8 ms of slack in my reconstruction; it is consistent, not comfortable. Any future slower probe path (e.g., python3 missing → different branch) would change the budget, so the span is not itself a strong liveness proof — the semantic evidence (live probes, captures, ownership) is.
- The two receipts' near-identical `(1, 1, 22)` transitions are expected from the fixed 20 ms poll sleep, not duplication: ports (32845 vs 39375), log paths (`j9achou8` vs `rby6ftf3`), and probe digests (6edd3c vs 93ee43) all differ.

# limitations

- I did not start llama-server (not permitted by this item), so costs were replayed against a Python surface serving the receipt's verbatim captured bodies; probe cost is client-side and unaffected, but capture and teardown wall costs during the real run can differ by a few ms (measured captures 1.4–3.2 ms; teardown 3 ms real vs 1.2 ms fake).
- `teardown.log_lines` cannot be re-hashed: the tool unlinks the temp log (verified in code and by its absence). Only format, ordering, and port are checkable from the receipt.
- `/props` and `/slots` bodies are not retained (`keep_body=False`), so `0b2770e1…` and `6d345b40…` are unverifiable; their extracted fields (`n_ctx 256`, `total_slots 4`, alias, build_info, 4 slots) are internally consistent with argv and each other.
- Timestamps are millisecond-resolution; all sub-millisecond statements above are [INFERENCE] from measurement, not from the receipt.
- The wall-budget conclusion depends on the load at 13:49Z, inferred from the host's 15-min average (3.33 at 10:56 local, 7 min after the run) rather than measured then. [INFERENCE]

# installs

None. No package manager or tool installation was performed; no host service touched.
