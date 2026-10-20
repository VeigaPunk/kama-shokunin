#!/usr/bin/env python3
"""Build the kama round-16 wave-1 (build) spec. L1-authored; deterministic."""
import json, pathlib

LANE = "/home/vgpnk/Projects/shokunin/kama-shokunin"
W = LANE + "/.ufo/waves/round-16"
DRAFTS = W + "/build/drafts"
GOD = pathlib.Path("/home/vgpnk/.agents/skills/godspeed/directive.md").read_text()
HEAD = "/skill:godspeed\n" + GOD.rstrip("\n") + "\n\n"

CONTEXT = f"""# Goal
kama-shokunin round 16 (hyaku phase 2), build wave. Lane domain: local model serving & endpoint health. Assigned axes: operability + calibration (calibration 7 is lowest). L1 holds the canonical planner seat; seats advise, L1 integrates and runs every measurement.
Claims:
- C1 calibration: `tools/kama-probe.sh` grades a loading llama.cpp server as FOREIGN_SERVICE / `non-2xx-non-model-http` ("non-model service") — an overreach. llama.cpp b11755 `tools/server/server-http.cpp:307-325` answers EVERY non-frontend path with HTTP 503 body {{"error":{{"message":"Loading model","type":"unavailable_error","code":503}}}} while `is_ready` is false; README @ b11755 `GET /health` documents the same body ("the model is still being loaded"). Fix: new verdict `MODEL_LOADING`, reason `llamacpp-loading`, drift true, chosen only when GET /v1/models returns 503 AND the body is a JSON object whose `error` object has message == "Loading model", type == "unavailable_error" and integer code == 503 (all exact). Anything else keeps its current verdict (e.g. "no slot available" unavailable_error stays FOREIGN_SERVICE; scope limit). Measured by a literal stub-server matrix: red against frozen `{W}/frozen/kama-probe-before.sh` (sha256 93ee4302…cd64), green against the repaired probe; positive controls defeat a reject-all/loading-all implementation.
- C2 operability (capability acquisition): `tools/kama-llamacpp-live.py` launches an ephemeral, lane-owned llama-server (official release b11755, commit 704366d76, installed at ~/.local/opt/llama-b11755, linked ~/.local/bin/llama-server; asset sha256 753bfa73…e226) with a pinned tiny GGUF (~/.cache/kama-shokunin/models/stories260K.gguf, sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d) on a free loopback port that is never a registered consumer port, captures the documented lifecycle surfaces, runs kama-probe against it, tears it down and proves teardown. No ~/.config, ~/.omp, systemd or service writes; no registered port is ever served.
L1 smoke observation (10:17 -03): during load GET /v1/models -> 503 {{"error":{{"message":"Loading model","type":"unavailable_error","code":503}}}}; ready: /health 200 {{"status":"ok"}}, /v1/models 200 with data[0].id == alias, owned_by "llamacpp", plus an Ollama-shaped models[] array; /slots 200; /metrics 501 without --metrics. Frozen probe on a stub of that loading body: FOREIGN_SERVICE non-2xx-non-model-http, exit 2.

# Contract
- Lane root {LANE}. Every `Report:` trailer path is relative to {LANE} — write it at {LANE}/<that path>. All paths absolute. Write ONLY the file(s) your item names plus your own Report. Never edit another item's file, old receipts/lessons, MANIFEST.json, fleet scripts/templates, .ufo/state, or any sibling lane repo; never write the fleet root /home/vgpnk/Projects/shokunin outside this lane directory.
- Never read `.ufo/interactive-sessions/`, ~/.omp sessions/history, or any session/transcript/credential store; bound every grep/glob to the paths your item names. Never dump environment variables.
- Measurements belong to L1: run no lane gate, harness or test against the lane except what your item explicitly allows. Your outputs are advice, never verdicts.
- Stub-matrix schema (C1, shared by harness and matrix files): each `{LANE}/tests/probe-verdicts/<Family>.json` is a JSON array of tests: {{"name": unique string, "family": "<Family>", "why": one line, "port_mode": "stub"|"closed", "routes": {{"<path>": R}}, "default_route": R or null, "expect": "<value passed as --expect>", "expected": {{"verdict": V, "reason": exact reason, "exit": 0|2}}}}. R is {{"status": int, "headers": {{name: value}}, "body_json": any}} or {{"status": int, "headers": {{...}}, "body_text": string}} or {{"raw": "close"}} (accept the TCP connection, send nothing, close). Unlisted path with default_route null -> 404, empty body. `closed` mode: no listener on the port (DEAD). Probe invocation: `bash PROBE check --port P --expect E --json --timeout 2 --connect-timeout 1`; exit 0 iff MODEL_OK else 2. Existing reasons (read classify() at {LANE}/tools/kama-probe.sh:415-525): DEAD connection-refused|timeout; NOT_HTTP empty-reply|connection-reset|no-http-response; UNAUTHORIZED_SERVICE http-401|http-403; MODEL_OK matched|expected-wildcard; MODEL_MISMATCH served-id-mismatch|unresolvable-id; FOREIGN_SERVICE html-non-model|schema-unrecognized|non-model-2xx|non-2xx-non-model-http. New: MODEL_LOADING llamacpp-loading.
- Operator tooling authorization (2026-10-19): you may install or upgrade tools that help the task — read /home/vgpnk/.omp/agent/RULES.md first (official channels, update-safety gate, record tool/version/channel/reason in your Report). pacman guard (orchestrator ruling 2026-10-20): ALL pacman transactions are PAUSED host-wide — install only via `uv tool`/`npx`/an official binary in ~/.local/bin; never -Sy/-Syu/-U/-R, never downgrade, never restart a host service. When the pause lifts, run `pacman -Sp --print-format '%n %v' <pkgs>` first and proceed only if no listed package is installed.
- Leaf seat: no subagents (an executor may spawn at most one read-only labrat). Never message agent://all. Report: concise findings with path:line or URL+quote evidence, limitations, and any install.
"""

FOOT_RO = "\n# Acceptance\nRead-only seat: write nothing except your own Report. Cite path:line or URL plus a <=25-word quote for every finding; mark inferences [INFERENCE]."
FOOT_EX = "\n# Acceptance\nWrite only your owned file(s). You may run a syntax check (`python3 -m py_compile`, `bash -n`) or `--help` of your own file; L1 runs every measurement. Report exact paths, design choices and known limitations."
FOOT_SC = "\n# Acceptance\nWrite only your owned draft file plus your Report. Drafts are append-ready prose for L1 to integrate; open every source you quote this session and give URL/path:line, access date 2026-10-20 and a <=25-word located quote. No placeholders: if a fact is unknown, say what is unknown."

items = []
def add(name, role, body, foot):
    items.append({"name": name, "role": role, "prompt": HEAD + body.strip() + "\n" + foot})

# ---------------- executors (code) ----------------
add("ProbeLoadingVerdict", "executor", f"""
# Target
Own ONLY {LANE}/tools/kama-probe.sh.
# Change
Implement C1 exactly: in classify(), after the 401/403 branch and before the HTML/FOREIGN_SERVICE fallbacks, when F_CODE is 503 and the /v1/models body is a JSON object with error.message == "Loading model", error.type == "unavailable_error" and error.code == 503 (integer, exact; use the existing HAVE_PY python3 helper pattern, fail closed to the old path when python3 is absent), set C_VERDICT=MODEL_LOADING, C_REASON=llamacpp-loading, C_EVIDENCE="$base (llama.cpp loading envelope: not ready, not a foreign service); GET /health -> $(probe_short "$port" "/health")". Add MODEL_LOADING to VOCAB, the header vocabulary comment (line ~29), usage() verdict line, the diff_baseline baseline whitelist (line ~895) and the cmd_listeners per-verdict counters (count it with model servers, or add n_loading — keep existing summary keys unchanged and add one). Header comment: one line citing llama.cpp b11755 tools/server/server-http.cpp:307-325. Keep every other verdict/reason byte-for-byte; minimal diff.""", FOOT_EX)

add("VerdictHarness", "executor", f"""
# Target
Own ONLY new {LANE}/tests/probe-verdicts/check.py (stdlib only, executable).
# Change
CLI: `--probe PATH` (default {LANE}/tools/kama-probe.sh), `--only NAME` (repeatable), `--json` (default human summary + JSON when set), `--selftest` (runs the matrix against the default probe and additionally asserts the harness's own schema validation rejects 3 embedded malformed tests). Load sorted `*.json` siblings in its own directory (each a JSON array per the shared schema); refuse (exit 2) on duplicate names across files, unknown keys, or invalid R shapes. For each test start a ThreadingHTTPServer on 127.0.0.1:0 serving the routes exactly (override version_string() so the Server header equals the route's `Server` header if given, else omit-equivalent `kama-stub`; send Content-Type/other headers as given; body_json serialized with json.dumps separators (',',':'); raw close = accept and close without bytes); `closed` mode binds then closes a socket and probes that port. Record per test: requests seen (method, path), probe exit, parsed verdict/reason/drift/evidence, passed = verdict, reason and exit all equal expected. Output JSON {{"schema":"kama-probe-verdicts/v1","probe":path,"probe_sha256":hex,"tests":N,"passes":p,"failures":f,"records":[...]}}. Exit 0 all pass, 1 any failure, 2 harness/schema error. Timeouts so a hung probe cannot hang the harness (subprocess timeout 30s -> recorded failure).""", FOOT_EX)

matrix = {
 "LoadingEnvelope": "the exact llama.cpp loading envelope on /v1/models and /health (as the middleware serves every path): variants with --expect equal to an alias, '*' and '-', with and without `Server: llama.cpp`, with `application/json; charset=utf-8` and plain `application/json`; key order permuted. All expect MODEL_LOADING llamacpp-loading exit 2.",
 "LoadingRace": "the observed race: /v1/models returns the loading envelope while /health already returns 200 {\"status\":\"ok\"} or 404 or is unlisted; and the inverse (/health loading envelope but /v1/models 200 with a model array and matching alias -> MODEL_OK matched exit 0, because /v1/models decides). Expected verdicts per case.",
 "Overbroad503": "503 responses that are NOT the exact envelope and must stay FOREIGN_SERVICE non-2xx-non-model-http (or html-non-model for HTML): nginx-style HTML 503, {\"error\":\"maintenance\"}, envelope with type unavailable_error but message \"no slot available\" (a real llama.cpp unavailable_error), message \"loading model\" lowercase, message \"Loading model\" with type server_error, code \"503\" as string, envelope at top level without the error wrapper, text/plain \"Loading model\". Read classify() to set exact reasons.",
 "NonLoadingStatuses": "the exact loading envelope body served with statuses other than 503 (200, 500, 502, 504) — 200 with no model array -> FOREIGN_SERVICE schema-unrecognized, 5xx -> FOREIGN_SERVICE non-2xx-non-model-http; proves the matcher requires status 503.",
 "ReadyControls": "ready llama.cpp b11755 /v1/models bodies (data[] with id/aliases/owned_by llamacpp plus Ollama-shaped models[]): --expect equal to id -> MODEL_OK matched exit 0; --expect '*' -> MODEL_OK expected-wildcard; --expect a different id -> MODEL_MISMATCH served-id-mismatch exit 2; --expect a path/to/model.gguf whose basename matches -> MODEL_OK matched (normalize_id). Positive controls that defeat a 'everything is MODEL_LOADING' implementation.",
 "AuthAndDead": "UNAUTHORIZED_SERVICE http-401 and http-403 JSON bodies (llama.cpp authentication_error envelope), a 401 whose body is the loading envelope (must stay UNAUTHORIZED_SERVICE http-401: auth branch precedes), closed port -> DEAD connection-refused, raw close -> NOT_HTTP empty-reply.",
 "EnvelopeShapes": "malformed or adversarial 503 bodies: invalid JSON, JSON array, error as string, error object missing code, extra fields alongside the exact triple (extra fields allowed -> still MODEL_LOADING), nested envelope one level deeper, 64 KiB padding inside an extra field, BOM-prefixed JSON. Decide expected verdicts from the exact-triple rule and classify() reasons; one line `why` each.",
 "ForeignControls": "non-model services unaffected by the change: 200 HTML page -> FOREIGN_SERVICE html-non-model, 200 openmetrics text -> FOREIGN_SERVICE non-model-2xx, 200 JSON without model array -> FOREIGN_SERVICE schema-unrecognized, 404 JSON -> FOREIGN_SERVICE non-2xx-non-model-http, 500 JSON error -> FOREIGN_SERVICE non-2xx-non-model-http.",
}
for fam, desc in matrix.items():
    add(f"Matrix{fam}", "executor", f"""
# Target
Own ONLY new {LANE}/tests/probe-verdicts/{fam}.json.
# Change
Write a literal JSON array (4-10 tests, names prefixed `{fam}.`) following the shared stub-matrix schema in the context. Family: {desc} Expected verdict/reason/exit are literal oracle values derived from the C1 rule text and classify() source — never computed by running the probe. Every test gets a one-line `why`.""", FOOT_EX + " Validate only that the file parses as JSON.")

add("LiveHarness", "executor", f"""
# Target
Own ONLY new {LANE}/tools/kama-llamacpp-live.py (stdlib only, executable).
# Change
C2 capability. Args: --server PATH (default shutil.which('llama-server'); record realpath and sha256 of that file), --model PATH and --model-sha256 HEX (required; mismatch -> exit 3 before launch), --alias (default kama-live-probe), --probe PATH (default {LANE}/tools/kama-probe.sh), --ctx 256, --threads 1, --ready-timeout 60, --out PATH (else stdout). Port: bind 127.0.0.1:0 for a free port; refuse and retry if it is 8080, 34113 or any port number appearing in {LANE}/registry/endpoint-consumers.tsv. Launch [server,-m,model,--alias,alias,--host,127.0.0.1,--port,P,-c,ctx,-t,threads,--no-webui] with start_new_session=True, stdin DEVNULL, stdout+stderr to a temp file; record argv only (never env). Lifecycle capture from t=0: tight loop alternating GET /health and GET /v1/models (urllib, 0.5s timeout, no proxy) recording every transition (path, status or connect error class, body sha256, body if <=4096 bytes, headers subset Server/Content-Type, monotonic ms) until /health is 200 or timeout; keep the first loading-503 response verbatim if one is seen (observed or not-observed is recorded, never required). Ready captures: /health, /v1/models (full body + headers), /props (only model_alias, total_slots, is_sleeping, build_info and default_generation_settings.n_ctx), /slots status + element count, /metrics status. Probe runs: `bash PROBE check --port P --expect ALIAS --json` and with --expect kama-not-this-model; store parsed JSON + exit. Teardown: SIGTERM process group, wait 10s, SIGKILL fallback; prove process exited (returncode) and port refuses connections; delete temp log after copying only lines matching build|model loaded|listening|loading. Checks array of {{id, documented_by, passed, observed}}: health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled (non-200), props_alias, probe_model_ok (MODEL_OK matched exit0), probe_mismatch (MODEL_MISMATCH served-id-mismatch exit2), teardown_exited, teardown_port_closed. Receipt schema kama-llamacpp-live/v1 with started/ended UTC, server/model identity, port, argv, transitions, captures, probes, checks, loading_observed. Exit 0 all checks pass, 1 any fail, 2 setup error, 3 digest mismatch. Always tear down (try/finally, signal handlers).
You MAY run your own tool against the installed binary/model for development (one server at a time, always torn down, confirm with `ss -ltn`); such runs are not measurements — say so in your Report.""", FOOT_EX)

add("LiveReceiptGate", "executor", f"""
# Target
Own ONLY new {LANE}/tests/llamacpp-live/check-receipt.py (stdlib only, executable).
# Change
Independent validator for a kama-llamacpp-live/v1 receipt (schema described in the context C2 bullet and the LiveHarness item: checks ids health_ready, models_alias_id, models_owned_by_llamacpp, metrics_not_enabled, props_alias, probe_model_ok, probe_mismatch, teardown_exited, teardown_port_closed). Usage `check-receipt.py RECEIPT [--expect-model-sha256 HEX] [--expect-server-sha256 HEX]`: verify schema id, every required check present exactly once and passed, probe JSON verdict/reason/exit correspond to the check claims (re-derive from stored probe output, do not trust `passed` alone), port not 8080/34113, teardown evidence present, identity hexes 64 chars and equal to the expected ones when given, ended >= started. Exit 0 valid, 1 invalid (list every problem), 2 unreadable. `--selftest`: build one minimal valid receipt literal in memory plus >=8 single-field mutations (missing check, passed flipped against stored probe output, port 8080, wrong digest, missing teardown, duplicated check id, schema id changed, MODEL_OK claimed with exit 2) and assert valid->0, each mutation->1.""", FOOT_EX)

add("SnapshotCompat", "executor", f"""
# Target
Own ONLY {LANE}/tools/test-snapshot.sh.
# Change
Read it and {LANE}/tools/kama-probe.sh diff_baseline (~lines 874-945). Add one test case proving a baseline latest.tsv row whose verdict is MODEL_LOADING is accepted (not dropped as malformed) once MODEL_LOADING is in the whitelist, and that an unknown verdict string is still dropped. Follow the file's existing fixture/assert style exactly; do not change existing cases. If the script cannot express this without running a live port, add the smallest offline case and say why.""", FOOT_EX)

add("MeasureRunner", "executor", f"""
# Target
Own ONLY new {W}/measure.py (stdlib only).
# Change
L1's counting command for C1. Runs `python3 {LANE}/tests/probe-verdicts/check.py --probe P --json` for P in (a) {W}/frozen/kama-probe-before.sh, (b) {LANE}/tools/kama-probe.sh, plus any extra `--probe NAME=PATH` pairs; writes {W}/run-<name>.json each {{"command": argv, "exit": int, "stdout_sha256": hex, "parsed": object, "stderr_tail": str}}; then prints a table name/exit/passes/failures and per-family pass counts, and the list of test names whose verdict differs between before and after. Before running, verify the frozen snapshot against {W}/frozen/manifest.json (sha256 field) and against `git -C {LANE} cat-file blob 20e392ea683a36bc223eb7cb45897acfb45456a3:tools/kama-probe.sh` byte-for-byte; mismatch -> exit 4 without running. Exit 0 when before has >=1 failure, after has 0 failures, and every test that changed verdict is a MODEL_LOADING expectation; else 1.""", FOOT_EX)

add("SourcePins", "executor", f"""
# Target
Own ONLY new {W}/sources/pin.py and the files it writes under {W}/sources/ (create the directory).
# Change
Fetch with urllib (read-only GET) these files at llama.cpp commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad from https://raw.githubusercontent.com/ggml-org/llama.cpp/<commit>/<path>: tools/server/README.md, tools/server/server-http.cpp, tools/server/server-common.cpp, tools/server/server-common.h. Save each as {W}/sources/llama.cpp-704366d/<basename>, then write {W}/sources/pins.json: per file url, sha256, bytes, and located line ranges for: README `### GET \\`/health\\`` section and the line `Body: \\`{{"error": {{"code": 503, "message": "Loading model", "type": "unavailable_error"}}}}\\``; server-http.cpp `auto middleware_server_state` block start/end; server-common.cpp `case ERROR_TYPE_UNAVAILABLE` lines; every `ERROR_TYPE_UNAVAILABLE` use. Locate by string search, never hardcode line numbers. Run it once to produce the pinned files (this fetch is your item's purpose, not a lane measurement).""", "\n# Acceptance\nWrite only the named script and its outputs; report sha256s and located line ranges.")

add("ProvenanceLedger", "executor", f"""
# Target
Own ONLY new {W}/dispatch-provenance.py (stdlib only).
# Change
Routed defect 4 from {LANE}/corpus/lessons/round-15-verifier-spotcheck.md:168 — wave validation receipts must preserve the environment bindings and refused-attempt identity. Write a script that, given `--spec PATH --out PATH`, runs `node /home/vgpnk/Projects/ufo-fsd-alpha/scripts/ufo-swarm-wave.mjs run --spec PATH` with exactly env UFO_CONFIG_PATH=/home/vgpnk/Projects/shokunin/scripts/hyaku/ufo-wave-policy-v2.json, UFO_FLEET_ALLOW_EXTERNAL_TOOLS=1, UFO_PROJECT_ROOT={LANE} added to the inherited environment, and records {{argv, cwd, env_bindings (only those three names and values), exit, stdout_sha256, taskCall_sha256 (sha256 of canonical json.dumps(sort_keys=True,separators=(',',':')) of stdout JSON taskCall), counts, started/ended UTC}} — never the rest of the environment. Also `--attempt-result PATH --label refused|spawned` appends {{label, at UTC, result_sha256, refused/spawned counts if parseable}} to the same ledger so a refused task call is tied to the same taskCall digest. Do NOT run it against a real spec; L1 runs it.""", FOOT_EX)

# ---------------- scouts ----------------
scouts = {
 "ReadmeDelta": "Compare the llama.cpp server README at commit 704366d76f8748cf9ad3df62a464bfcc8d1ae6ad (https://raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/README.md) with the S001 pin c0fd78626405c6d9b934efef0ec7291fcc20e3d6 for the GET /health, GET /v1/models, /props, /slots and /metrics sections. Report every semantic difference with line numbers in both.",
 "MiddlewareOrder": "In llama.cpp @704366d76 tools/server/server-http.cpp, determine the registration order of the API-key middleware and middleware_server_state, which paths are exempt (public endpoints, frontend_paths) and therefore what GET /v1/models and GET /health return while loading when --api-key is set. Quote the exact lines.",
 "UnavailableUses": "List every use of ERROR_TYPE_UNAVAILABLE and every literal 503 in llama.cpp @704366d76 tools/server/*.cpp and *.h (fetch from raw.githubusercontent.com), with the message string and the endpoint/condition, so C1's exact-message matcher scope is known.",
 "SleepState": "llama.cpp @704366d76: what do GET /health, GET /v1/models and GET /props return while the server is sleeping (--sleep-idle-seconds)? Read README 'Sleeping on idle' and server-context.cpp/server-http.cpp. Would kama-probe (classify() at the lane tools/kama-probe.sh:415-525) misgrade it? Frontier advice only.",
 "RouterMode": "llama.cpp @704366d76 router mode (README 'router mode', model status values loading/sleeping/downloading, GET /models): how would kama-probe's /v1/models identity check read a router? Identify misgrade risks; frontier advice only.",
 "VllmStartup": "vLLM (pinned stable docs or a tagged source file you open): what does a vLLM OpenAI server answer on /v1/models and /health before the engine is ready (connection refused, 503, or nothing)? Cite the version. Determines whether C1's llama.cpp-only scope leaves a vLLM gap.",
 "SglangStartup": "SGLang (pinned docs/source you open): /health, /health_generate and /v1/models behaviour during model load/warmup. Cite version and lines.",
 "OllamaLoading": "Ollama (docs.ollama.com and/or tagged source you open): does /v1/models or /api/tags ever answer a loading-state status? What does /api/ps show while a model is loading? Cite.",
 "TgiStartup": "Hugging Face text-generation-inference (pinned docs/source): /health and /info semantics during warmup/loading; status codes. Cite version.",
 "LocalAiStartup": "LocalAI (pinned docs/source): readiness/health endpoints (/readyz, /healthz) and /v1/models during model load. Cite version.",
 "LmStudioServer": "LM Studio local server docs (lmstudio.ai docs you open): /v1/models semantics for loaded vs downloaded models and any not-ready status. Cite page and date.",
 "KoboldCppServer": "KoboldCpp (pinned README/source): OpenAI-compatible /v1/models and its behaviour before the model is loaded. Cite version.",
 "LlmdReadiness": "Re-open https://llm-d.ai/docs/operations/readiness-probes (lane SOURCES S021, queued). Quote (<=25 words, located) the passages distinguishing process liveness on /health from model-aware readiness on /v1/models, record page version/date. Advise whether S021 can flip queued->mined as support for 'MODEL_LOADING is not-ready, not dead/foreign' in a new knowledge entry.",
 "K8sProbes": "Re-open https://kubernetes.io/docs/concepts/workloads/pods/probes/ (lane S017). Quote the readiness-vs-liveness sentences that map onto MODEL_LOADING (not ready for traffic) versus DEAD; record the page's last-modified date.",
 "ReleasePage": "Open https://github.com/ggml-org/llama.cpp/releases/tag/b11755 (and the API JSON https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11755). Record tag, commit 704366d76…, published date, the ubuntu-x64 CPU asset name, size and its sha256 digest field, and whether release notes mention server changes. Data for a new SOURCES row.",
 "ModelProvenance": "Open https://huggingface.co/ggml-org/models (observed redirect to ggml-org/models-moved) and the tinyllamas/stories260K.gguf file page/API (https://huggingface.co/api/models/ggml-org/models-moved or the redirected name). Record repo commit sha, file size, sha256/LFS oid if shown, license, and the redirect. Data for a new SOURCES row; flag any mismatch with sha256 270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d.",
 "ProbeSurfaces": f"Within {LANE}/tools/kama-probe.sh, {LANE}/tools/test-snapshot.sh, {LANE}/SKILL.md, {LANE}/corpus/knowledge/*.md and {LANE}/registry/ only: list every place that enumerates the six-verdict vocabulary or depends on it (counts, whitelists, tables, docs), with path:line, so MODEL_LOADING integration is complete.",
 "CorpusLoadingClaims": f"Within {LANE}/corpus/ and {LANE}/SKILL.md only: find every statement about 503, loading, /health readiness, or how the probe grades non-2xx responses. Classify each as consistent / stale / contradicted by the C1 facts in the context, with path:line.",
 "PortPolicy": f"Read {LANE}/registry/endpoint-consumers.tsv and {LANE}/registry/history/latest.tsv and run `ss -ltn` once (read-only). Report every port C2 must never bind (registered consumers, current listeners) and whether binding 127.0.0.1:0 can ever yield one; advise the refusal rule.",
 "HostRuntimeFacts": "Read-only: report `ldd ~/.local/opt/llama-b11755/llama-server` missing libraries (if any), `~/.local/bin/llama-server --version`, CPU flags relevant to ggml CPU backend selection (grep flags /proc/cpuinfo | head -1 | tr ' ' '\\n' | grep -E 'avx|f16c|fma'), free RAM; whether the bundled libggml-cpu-*.so variant selection could fail on this host.",
}
for name, q in scouts.items():
    add(f"Scout{name}", "scout", "# Question\n" + q, FOOT_RO)

# ---------------- reviewers ----------------
reviewers = {
 "MatcherExactness": "Review C1's exact-triple matcher against llama.cpp @704366d76 tools/server/server-http.cpp middleware_server_state (fetch raw). Is serialization stable (key order, code integer)? Any version where the envelope differs? Recommend accept/narrow/widen with evidence.",
 "SchemaAmbiguity": "Review the shared stub-matrix schema in the context for ambiguities that would let the harness and matrix authors disagree (header casing, Server header, body_text encoding, default_route, closed mode, exit expectation). List each and a resolution.",
 "ClaimSeparability": "Review C1 (stub matrix, probe change) and C2 (live harness) for causal separability per /home/vgpnk/Projects/shokunin/AXES.md §Working the axes: can each verify without the other? Which C2 checks would change if C1 had not landed? Advise.",
 "Kq19Interplay": f"Read {LANE}/corpus/QUALITY.md (KQ1-KQ18). Draft-review a new KQ19 for C1 ('a probe verdict must not grade a documented not-ready model-server state as a foreign/non-model service; admission requires a discriminating literal matrix red against the frozen probe, green after, with exact-envelope negatives and ready positives'). Name overlaps/conflicts with KQ4, KQ13, KQ17, KQ18 with line numbers.",
 "ReplayProsePrecision": f"Routed defect 5 of {LANE}/corpus/lessons/round-15-verifier-spotcheck.md:169. Read {LANE}/corpus/knowledge/ollama-evidence-replay.md:325-345 and {LANE}/.ufo/waves/round-14/measure.py corpus_problems. Propose the exact append-only correction sentence (do not edit).",
 "S012Wording": f"Routed defect 6 of {LANE}/corpus/lessons/round-15-verifier-spotcheck.md:170 and the SOURCES contract in /home/vgpnk/Projects/shokunin/CORPUS.md §SOURCES.md. Should S012's teaches cell be superseded by an appended row, or is an appended registry note marking cross-source synthesis sufficient? Re-open https://docs.ollama.com/api/ps and quote. Propose exact text.",
 "ShonenEvidence": f"Read {LANE}/SHONEN.md and /home/vgpnk/Projects/kimi-shokunin/skills/shokunin/protocol/PROTOCOL.md (promotion/SHONEN rules). What would a C2 live receipt let box 2 ('end-to-end domain task executed and logged') honestly claim, and what must remain [~]? Propose the replacement pointer text.",
 "ScorecardCurrency": f"Read {LANE}/SCORECARD.md lines 1-60 and 120-135. List each current-tense statement that is stale versus the latest supersession sections (round 11-15) and observed repo state (e.g. sources-registry row counts, live axes, planned). Recommend an append-only 'Current state (round 16)' block content.",
 "SnapshotCoupling": f"Read {LANE}/tools/test-snapshot.sh and {LANE}/tools/kama-probe.sh cmd_snapshot/diff_baseline. Would adding MODEL_LOADING break any existing test or history row parse (registry/history/latest.tsv, DELTA.md)? List exact risks.",
 "SkillPlacement": f"Read {LANE}/SKILL.md (all). Identify where verdict vocabulary, decision table, error signatures and gate registry live (line numbers) and propose append-only text registering MODEL_LOADING, the stub matrix gate and the live harness capability, following the file's established gate-registration format (e.g. lines ~493-505).",
 "ProvinceBoundary": f"Read {LANE}/PROVINCE.md and {LANE}/corpus/QUALITY.md KQ5. Does an ephemeral lane-owned llama-server on an unregistered loopback port, launched from an operator-authorized ~/.local install and torn down, stay inside the province write boundary? Propose append-only PROVINCE note text, or argue it needs an L0 ruling.",
 "FrontierAdvance": f"Read {LANE}/corpus/README.md §Frontier and later frontier dispositions. Which frontier items does C1/C2 advance (e.g. served-model reconciliation against a real runtime) and which remain open? Propose append-only README text.",
 "LogConvention": f"Read the last 120 lines of {LANE}/LOG.md. Describe the round-entry convention (headings, evidence binding, measured commit wording) so L1 appends a conforming round-16 entry; give a skeleton with exact headings.",
 "HarnessDesignRisk": "Review the LiveHarness design in the context (port choice by bind-then-release, process-group teardown, urllib polling). Name race windows (port reuse between bind and launch, zombie, orphan), and the minimal mitigations.",
}
for name, q in reviewers.items():
    add(f"Review{name}", "reviewer", "# Review\n" + q, FOOT_RO)

# ---------------- critics (m_opus, <=10 incl sentinels) ----------------
critics = {
 "C1Honesty": "Attack C1: is replacing FOREIGN_SERVICE with MODEL_LOADING for one exact llama.cpp envelope a calibration move (overreach caught, confidence graded) or merely an operability patch? Is the score honestly 7->7 or does it earn more? What evidence would falsify C1?",
 "C1Overfit": "Attack C1's scope: exact-message matching may miss localized/future llama.cpp messages and other engines; widening may misgrade foreign services. Which is the honest limit statement, and which matrix negatives must exist so the claim cannot pass vacuously?",
 "C2ServiceBoundary": "Attack C2 against KQ5 ('A training admission requires enabling services ... -> reject') and the PROVINCE write boundary: is an ephemeral lane-owned llama-server an 'enabled service'? What conditions make it admissible, and what must the report say?",
 "C2ToyModel": "Attack C2's evidentiary weight: a 1.2 MB F32 stories260K model on CPU. What does a passing live receipt establish about llama.cpp serving surfaces, and what must it never be used to claim (performance, quality, the registered consumers' health, model readiness of real deployments)?",
 "SourcedClaim": "Attack the sourced-claim requirement: C1 rests on new SOURCES rows for the llama.cpp README and server-http.cpp at b11755. Is a version-pinned source-code row tier A for 'what this binary returns while loading'? Is S001 (master README) sufficient alone? What must the Gate quotes contain?",
 "ScoreDeltas": "Attack the planned SCORECARD deltas: calibration 7->7 (C1), operability 8->8 plus a capability row (C2). Argue for or against any numeric change with AXES.md §Capabilities and the lane saturation line 8; identify any axis that could be harmed (e.g. adjacency by running a runtime, freshness claims).",
}
for name, q in critics.items():
    add(f"Critic{name}", "critic", "# Attack\n" + q, FOOT_RO)

add("SentinelLiveSafety", "sentinel", f"""
# Audit
Security/safety review of the C2 design (context) and, if present when you run, {LANE}/tools/kama-llamacpp-live.py: loopback-only bind, refusal of registered ports, process-group teardown on every exit path, no env/secret leakage into receipts, model digest gate before launch, temp-file cleanup, no writes to ~/.config/~/.omp/systemd, no network listener left behind. Read only; list concrete defects with line numbers.""", FOOT_RO)
add("SentinelInstallChain", "sentinel", """
# Audit
Review the operator-authorized install performed by L1: ~/.local/opt/llama-b11755 extracted from the official GitHub release asset llama-b11755-bin-ubuntu-x64.tar.gz (sha256 753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226, matching the API digest), symlink ~/.local/bin/llama-server; model from huggingface ggml-org/models (redirected to models-moved) tinyllamas/stories260K.gguf. Check: channel order compliance with /home/vgpnk/.omp/agent/RULES.md, RPATH/library resolution (readelf -d), no setuid, file ownership, whether the symlink shadows any existing binary. Read-only.""", FOOT_RO)

# ---------------- connectors ----------------
for sib, focus in [
 ("kengaku", "model evaluation: does running a toy model and recording completions risk absorbing eval/quality ground?"),
 ("kagi", "secrets: --api-key behaviour while loading, authentication_error envelopes, and any credential-bearing config"),
 ("kumitate", "orchestration/tooling: llama.cpp router mode, dispatch/route mechanisms, ~/.local/bin tool installs"),
 ("tsukuroi", "host operability/repair: ~/.local/opt installs, binaries, pacman pause, service restarts"),
 ("mori", "fleet/host observability: transient listeners and processes a live harness creates; detection overlap"),
 ("tameshi", "verification-fixture craft: stub-server matrices, red/green controls, mutation gates — reuse their conventions?"),
 ("souji", "workspace hygiene: ~/.cache/kama-shokunin model cache and ~/.local/opt install as preserved artifacts"),
 ("kake", "web properties: any HTTP surface conventions overlapping kama's local HTTP probing"),
]:
    add(f"Connect{sib.capitalize()}", "connector", f"""
# Overlap scan
Read /home/vgpnk/Projects/shokunin/{sib}-shokunin/SKILL.md and PROVINCE.md (if present; read-only, bounded to those files and its corpus/QUALITY.md) and compare with kama's C1/C2 (context) and {LANE}/PROVINCE.md. Focus: {focus}. Report contested scope, what kama must hand off rather than absorb, and any reusable convention, with path:line.""", FOOT_RO)

# ---------------- revengers ----------------
add("RevengerPlannerWalk", "revenger", f"""
# Reconstruct (bounded planning data-walk for the L1 planner seat)
Using `git -C {LANE} log -p --follow tools/kama-probe.sh` (bounded to that file) and {LANE}/LOG.md, reconstruct why the probe's v3 rules route every non-2xx non-model response to FOREIGN_SERVICE non-2xx-non-model-http, which round introduced it, and whether any lane record ever observed a loading llama.cpp. Output a dated timeline and the original intent.""", FOOT_RO)
add("RevengerEnvelopeHistory", "revenger", """
# Reconstruct
Reconstruct the history of llama.cpp's 'Loading model' 503 envelope: when the middleware/README form was introduced (lane S028 references issue #4746 closed via PR #5548), whether the message/type/code changed across releases (inspect a few tagged versions of tools/server/server-http.cpp or older examples/server/server.cpp via raw.githubusercontent.com). Output: version table and stability judgment for an exact-match rule.""", FOOT_RO)
add("RevengerRound1Live", "revenger", f"""
# Reconstruct
From {LANE}/LOG.md rounds 1-3 and {LANE}/corpus/knowledge/endpoint-identity.md, served-model-identity.md, runtime-health-surface-matrix.md only: what did kama observe from the real llama.cpp (qwen-coder) runtime before it was deleted — endpoints, ids, alias behaviour? Which of those observations can C2's live run re-verify on b11755, and which differ by version?""", FOOT_RO)
add("RevengerListenersPath", "revenger", f"""
# Reconstruct
Trace {LANE}/tools/kama-probe.sh cmd_listeners and cmd_consumers (lines ~667-780): how does a loading server flow through listeners classification and the summary counters today, and what would MODEL_LOADING change in their output keys? Report exact lines and the minimal compatible change.""", FOOT_RO)

# ---------------- scribes (drafts) ----------------
scribes = {
 "KnowledgeEntry": ("llamacpp-loading-lifecycle.md", "Draft a new knowledge entry for corpus/knowledge/llamacpp-loading-lifecycle.md: provenance trio header (as other kama entries; read one, e.g. ollama-evidence-replay.md head), the documented loading->ready lifecycle at b11755 (README /health; server-http.cpp middleware applies to every non-frontend path), the probe verdict mapping (MODEL_LOADING vs FOREIGN_SERVICE vs DEAD vs MODEL_OK), the exact-envelope scope limits (no slot available, sleeping, router mode, other engines), and a 'Live observation' section L1 will fill from the receipt (write it as a clearly titled section listing which receipt fields go there — no fabricated numbers)."),
 "Kq19": ("kq19.md", "Draft the QUALITY.md append block for KQ19 in the file's exact table format (read corpus/QUALITY.md), including 'No earlier criterion is superseded' preamble and the motivating lesson pointer lessons/round-16.md."),
 "SourcesRows": ("sources-rows.md", "Draft new SOURCES.md registry rows S035+ in the exact 11-column format (read corpus/SOURCES.md and /home/vgpnk/Projects/shokunin/CORPUS.md §SOURCES.md): llama.cpp server README @704366d76 (/health loading semantics), llama.cpp tools/server/server-http.cpp @704366d76 (middleware_server_state), llama.cpp release b11755 page (binary identity), Hugging Face ggml-org/models stories260K.gguf (model identity). Open each; give tier, scope, anchor, teaches, status mined, opened 2026-10-20, recheck, used-by (corpus/knowledge/llamacpp-loading-lifecycle.md and/or corpus/lessons/round-16.md). Also a dated search-log supplement paragraph."),
 "LessonGate": ("lesson-gate.md", "Draft corpus/lessons/round-16.md `## Gate` section: for each candidate decision (admit MODEL_LOADING exact rule; reject widening to any 503/unavailable_error; reject 'live toy run proves registered consumers healthy'; admit live capability scoped; S021 flip if supported), author decision, source with URL/access date/<=25-word located quote. Read lessons/round-15.md for the format."),
 "LessonMistakes": ("lesson-mistakes.md", f"Draft `## Mistakes` for round 16: mined mistake 'loading model server graded FOREIGN_SERVICE (non-model service) since the v3 rules' — class, evidence pointer ({LANE}/.ufo/waves/round-16/frozen/kama-probe-before.sh classify non-2xx branch line numbers you read), captured-by (none), fix (KQ19 + stub matrix shown red against the frozen probe). Also a second entry template for the round-15 spotcheck process incidents (session-dir grep; seats verifying against instructions) with captured-by and this round's fix (context bounding clauses). Read lessons/round-15.md Mistakes format."),
 "SkillSection": ("skill-section.md", "Draft the append-only SKILL.md round-16 section: verdict vocabulary update (MODEL_LOADING), decision-table row, error signature (the exact envelope), gate registration for tests/probe-verdicts/check.py and tools/kama-llamacpp-live.py + tests/llamacpp-live/check-receipt.py (commands, exits, owner, write scope), following SKILL.md's existing registration format (read it)."),
 "ReadmeFrontier": ("readme-frontier.md", "Draft the append-only corpus/README.md round-16 section: coverage-map row for the new knowledge entry and lesson, frontier disposition (what C1/C2 advance, what remains: sleeping, router mode, other engines, registered consumers still DEAD)."),
 "ProvinceNote": ("province-note.md", "Draft an append-only PROVINCE.md note: the ephemeral lane-owned llama.cpp runtime used for C2 (official release b11755 under ~/.local/opt, tiny pinned GGUF in ~/.cache/kama-shokunin, unregistered loopback port, torn down) — what it is and is not (not service restoration; registered consumers stay DEAD; no ~/.config/systemd writes)."),
 "RoutedDefects": ("routed-defects.md", f"Draft the round-16 dispositions of every routed defect in {LANE}/corpus/lessons/round-15-verifier-spotcheck.md:163-172 (items 1-6): for each, the fix/lesson this round or the reason not, in append-only wording for lessons/round-16.md."),
 "LogEntry": ("log-entry.md", f"Draft the LOG.md round-16 entry body following the convention in the last entries of {LANE}/LOG.md: motivating evidence (frozen-probe FOREIGN_SERVICE on the loading envelope; smoke observation in the context), planned claims, and clearly marked slots for L1-measured results (named slots, not invented values)."),
}
for name, (fname, task) in scribes.items():
    add(f"Scribe{name}", "scribe", f"# Draft\nOwn ONLY {DRAFTS}/{fname}.\n{task}", FOOT_SC)

add("SimplifierHarness", "simplifier", """
# Simplify
Review the stub-matrix schema and the LiveHarness/LiveReceiptGate/MeasureRunner designs in the context for unnecessary parts (YAGNI) that add failure surface without serving C1/C2 measurement. Recommend deletions or merges with reasons; read-only.""", FOOT_RO)

spec = {
    "context": CONTEXT,
    "reportDir": ".ufo/waves/round-16/build/advice",
    "maxLanes": 100,
    "items": items,
}
names = [i["name"] for i in items]
assert len(names) == len(set(names))
out = pathlib.Path(W) / "build" / "spec.json"
out.write_text(json.dumps(spec, indent=1, ensure_ascii=False) + "\n")
from collections import Counter
print(len(items), dict(Counter(i["role"] for i in items)))
