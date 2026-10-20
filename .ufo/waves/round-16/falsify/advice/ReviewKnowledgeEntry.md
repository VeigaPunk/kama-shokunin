VERDICT: partial — every factual line of `corpus/knowledge/llamacpp-loading-lifecycle.md` checked against the pinned b11755 copies, `tools/kama-probe.sh`, both receipts, the run controls, and the advice the entry cites. One material overclaim is refuted by the entry's own cited advice; four precision/scope defects and two provenance-ledger gaps follow; the rest confirms.

# Attack

Target: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/knowledge/llamacpp-loading-lifecycle.md` (line numbers below are that file).
Ground truth used: pinned upstream at `.ufo/waves/round-16/sources/llama.cpp-704366d/` (README.md, server.cpp, server-http.cpp, server-common.cpp, server-common.h), `.ufo/waves/round-16/sources/pins.json`, the b11755 files re-fetched from `raw.githubusercontent.com` at `704366d76f8748cf9ad3df62a464bfcc8d1ae6ad`, `.ufo/waves/round-16/live/receipt.json`, `.ufo/waves/round-16/live/receipt-frozen-probe.json`, `.ufo/waves/round-16/live/controls.txt`, `tests/probe-verdicts/*`, `tools/kama-probe.sh`, `tools/kama-llamacpp-live.py`, `corpus/SOURCES.md` S035-S041, and the cited build advice.

# What I ran (commands and exit codes)

1. `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` → **exit 0**; payload `"tests": 72, "passes": 72, "failures": 0`; 17 expected-`MODEL_LOADING` rows all returned verdict `MODEL_LOADING`, reason `llamacpp-loading`, `drift: true`.
2. `python3 tests/probe-verdicts/check.py --probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` → **exit 1**; `"tests": 72, "passes": 55, "failures": 17`; every mismatched row is an expected-`MODEL_LOADING` row; 16 returned `FOREIGN_SERVICE non-2xx-non-model-http`, 1 (`NearMissTriple.exact-envelope-labelled-html`) returned `FOREIGN_SERVICE html-non-model`.
3. Recomputed the changed set from (1)/(2) in Python → **exit 0**; names passing after but not before = exactly the 17 expected-`MODEL_LOADING` names. Frozen evidence string for the canonical row: `"GET /v1/models -> 503 ... (non-2xx HTTP from a non-model service)"`.
4. `sha256sum .ufo/waves/round-16/frozen/kama-probe-before.sh` → **exit 0**, `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`; equals `frozen/manifest.json` and `receipt-frozen-probe.json` `probe.sha256`.
5. Re-fetched the five upstream files from `raw.githubusercontent.com/ggml-org/llama.cpp/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/…` (curl `-sSfL`, each fetch succeeded), then `cmp -s` each against the lane pin → **all five IDENTICAL**, loop exit 0. `server.cpp` sha256 `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4`, matching `corpus/SOURCES.md:49` (S037).
6. Fetched `tools/server/server-models.cpp`, `common/json.h`, and `https://llm-d.ai/docs/0.10/operations/readiness-probes` into `/tmp` read-only scratch → fetches succeeded; used for the router-catalog and wire-order checks below.
7. `pgrep -x llama-server` → **exit 1** (no process). I did not run `measure.py`, did not run the live harness, did not start llama-server, and did not bind/probe 8080 or 34113.
8. Read/nl/grep over the entry, pins, receipts, controls, SOURCES, and advice files (all exit 0).

# Findings, by severity

## MEDIUM — `:82` "never a false `MODEL_OK`" is contradicted by the advice the same sentence cites

Entry `:80-83`:
> "Between roughly b6000 and b7502 llama.cpp exempted `/v1/models` from the gate, so this verdict could not fire there (missed detection, never a false `MODEL_OK`) [advice: `RevengerEnvelopeHistory.md`, `ReviewMatcherExactness.md`; sampled tags, not bisected]."

`ReviewMatcherExactness.md:81` says b6000/b6500/b6800 `/v1/models` while not ready returns **200** with a model list; `:90-91` says:
> "Honest scope limit: pre-b7600 builds may be graded `MODEL_OK` while loading (they serve a model list during load). C1 does not fix that opposite-direction gap."

`RevengerEnvelopeHistory.md:84-86` likewise says on those builds a still-loading server "can be graded `MODEL_OK` (the model list is static) or `DEAD timeout`" [its own INFERENCE].

So the exempt window has two failure modes: missed `MODEL_LOADING` **and a false-ready `MODEL_OK`**. The entry's parenthetical asserts the opposite of its cited source. The likely intent was "the new verdict cannot fire there" [INFERENCE], but as written the sentence claims a safety property the advice denies. Fix: "…so this verdict could not fire there; a loading server could instead be graded `MODEL_OK` from the static 200 list (a missed/false-ready detection, not a false `MODEL_LOADING`)." Note the two cited files sample slightly different boundaries (b7502 vs b7600), which the entry's "roughly" covers.

## LOW-MEDIUM — `:68-74` two scope overclaims in the engine paragraph

(a) "None of these emits this body" is stated after "no runtimes run". `ScoutLmStudioServer.md:87-91`:
> "absence of a 503 in docs is not proof LM Studio never returns one. [INFERENCE] `/v1/models` likely answers 200 regardless of load state"

and `:91` "LM Studio itself was not installed or run; every LM Studio claim above is docs-only." A docs-only scan cannot establish a runtime-negative for LM Studio. Fix: "none of the scanned sources documents this body on `/v1/models`" (or qualify LM Studio as docs-only).

(b) `:72-73` "Ollama and LocalAI list configured or available models with 200 whatever the load state" omits LocalAI's startup-preload phase. `ScoutLocalAiStartup.md:64`:
> "Startup preload, default CLI | no listener | no listener | connect refused -> `DEAD connection-refused`"

LocalAI's 200 config listing applies once the frontend is up (`:43-49`); during startup preload the same probe sees `DEAD`, not 200. If "load state" means backend model staging only, the clause is fine; as written it reads as "always answers 200" [INFERENCE on the intended scope]. Fix: "…with 200 after the frontend is up (LocalAI still has a pre-listener startup window that reads `DEAD`)".

## LOW — `:36-38` `id = the --alias` is overbroad

Entry `:36-38`: "`/v1/models` returns 200 with `data[]` (id = the `--alias`, `owned_by` `llamacpp`) …".
`README.md:1284`:
> "By default, model `id` field is the path to model file, specified via `-m`. You can set a custom value … via `--alias`."

The live harness sets `--alias kama-stories260k`, so the receipt correctly shows the alias; the general lifecycle statement should read "id = `--alias` when set, else the `-m` path". The entry's later line `:118-119` ("the id is the caller's alias") shows awareness, but item 4 overgeneralizes.

## LOW — `:100-101` "refusal set {8080, 34113} plus any listening port" does not match the code

`tools/kama-llamacpp-live.py:57`: `HARD_REFUSED_PORTS = {8080, 34113}`; `:192-217` `refused_ports()` adds hardcoded pins plus **every port token the registry TSV expresses** (IPv4:port, localhost:port, `--port N`, `port=N`, `host:port`), not all listening ports. A listening port is rejected only on the explicit `--port` path: `pick_port` `:239-246` raises `port-in-use:<port>`. The receipt field is exactly `"port_refusal_set": [8080, 34113]`. Fix: "refusal set {8080, 34113} ∪ registry-declared ports; an explicitly requested listening port is refused as port-in-use."

## LOW — `:104` "loads in about 8 ms" conflates launch-to-loaded with load span

Receipt `teardown.log_lines`:
> `0.00.004.591 I srv load_model: loading model …` / `0.00.008.725 I srv llama_server: model loaded`

The load span is ≈4.1 ms; 8.7 ms is time since process start. Fix: "model loaded 8.7 ms after launch (loading span ~4 ms, server log)". Toy-scale only; the entry already walls this off from real deployments.

## LOW — `:114` "the same run with the frozen pre-round probe" is a separate run

`receipt-frozen-probe.json` `started_utc`/`ended_utc` = `2026-10-20T13:49:38.250Z`–`…379Z`, port `39375`; `receipt.json` = `…040Z`–`…170Z`, port `32845`. Same harness, separate invocation. The conclusion ("also passes all 10 checks", 10/10, so the capability does not depend on `MODEL_LOADING`) stands.

## INFO — `:2` `pins.json` does not cover `server.cpp`

`pins.json` `files` keys are only `tools/server/README.md`, `server-common.cpp`, `server-common.h`, `server-http.cpp`; `pin.py:37-42` `FILES` lists the same four. `server.cpp` (the source of S037 and of lifecycle items 1 and 5) is saved in the pin directory and its digest is in `SOURCES.md:49` (`21439622…f5aef4`), but it is not in `pins.json`. I re-fetched it from the pinned commit and `cmp` says byte-identical, so this is a ledger gap, not a bad pin. Fix the parenthetical: "four files in `pins.json`; `server.cpp` digest in S037 (byte-verified at the commit)".

## INFO — `:42-44` the sleep inference is not grounded in the pinned files

The pinned directory contains no sleep code (`grep -n "is_ready\|sleep"` over the five pinned files yields only the two `is_ready.store(true)` sites, the `is_ready.load()` gate, and no `sleep`). The claim is explicitly `[INFERENCE]` and is supported by `CriticC2ToyModel.md:27` quoting unpinned `server-context.cpp:5727-5730` ("this endpoint must be accessible during sleep … `res->ok(cached_models)`") plus `README.md:2337-2345` (sleep unloads the model; `/health`, `/props`, `/models`, `/metrics` are exempt from reload). The inference itself is sound; the pointer "from code paths" should name `server-context.cpp` (unpinned) rather than implying the pinned middleware proves it.

# What confirms (spot-checked, not merely restated)

- **Lifecycle 1** — `server.cpp`: direct mode `ctx_http.start()` at `:494`, `ctx_server.load_model(params)` at `:507`, `ctx_http.is_ready.store(true)` at `:515`; `grep is_ready` across the pinned server files finds only `:460` and `:515` stores, both `true`. Entry `:24-26` matches; "no `store(false)` in the server sources read" is true for the read set.
- **Lifecycle 2** — `server-http.cpp:307-328`: `if (!is_ready.load())` `:308`; frontend exemption `:309-311` (`frontend_paths` = `/` plus embedded assets, `:242-248`); 503 + exact body `:314-325`; `res.status = 503` `:314`. `/health` and `/v1/models` are not in `frontend_paths`, so both fall to the gate. Entry `:27-32` matches.
- **Lifecycle 3** — `server-http.cpp:347-359`: OPTIONS short-circuit `:347-353`, state gate `:354-356`, API-key check `:357-359`. The `--api-key` implication (503 before 401) follows. Entry `:33-35` matches.
- **Lifecycle 4** — receipt `captures.health.body` = `{"status":"ok"}`, status 200; `captures.models` 200, body contains `"data":[{"id":"kama-stories260k",…,"owned_by":"llamacpp"…]` and the Ollama-shaped `"models":[…]`. Entry `:36-38` matches for the aliased fixture; see the id caveat above.
- **Lifecycle 5** — `server.cpp:455-460` starts the router listener then `is_ready.store(true)`; `:472` `models_routes->models.load_startup_models()` runs after. `/models` and `/v1/models` share `routes.get_models` (`server.cpp:283-284`), and the router status values are documented at `README.md:2062-2094`. Entry `:39-41` matches.
- **Lifecycle 7** — `grep -n "Loading model\|unavailable_error" README.md` finds only `:486`; the body at `:486` is `{"error": {"code": 503, "message": "Loading model", "type": "unavailable_error"}}`, i.e. README order `code, message, type`; `README.md:1258` is the exact `meta` "can be `null` … while the model is still loading" sentence. Entry `:45-48` matches. Wire order: the trigger inserts `message`, `type`, `code` (`server-http.cpp:318-320`) and `common/json.h:24` says "object keys keep the order in which they are added"; `safe_json_to_str` is `dump_safe()` (`server-common.cpp:1695-1697`), and L1's smoke records the same order (`build/make_spec.py:16`). Entry `:49-50` matches at source level (the smoke is unreceipted and the entry says so).
- **Probe mapping** — `body_is_llamacpp_loading` `:428-447` is gated on python3 `:429`, checks `error` is an object, exact `message`/`type`, rejects `bool`, requires `isinstance(code, int)` and `== 503` `:441-443`; extra keys are ignored. `classify()` checks 401/403 before any body `:494-501`, the exact envelope only at `F_CODE = 503` `:503-508`, HTML at any status `:511-518, 549-553`, generic non-2xx `:556-566`. The matrix run confirms every table row, including the 17 loading rows and the frozen 55/17 split; changed set = 17 = expected loading rows. "Fail closed without python3" is confirmed: frozen-style `FOREIGN_SERVICE non-2xx-non-model-http`, `drift: true`, exit 2 (also reproduced by sibling `falsify/advice/ExecNoPythonFallback.md` with a literal stub).
- **Live receipt** — `started_utc`/`ended_utc` `13:49:38.040Z`–`…170Z`; port `32845`; `server.sha256` `b6a31a8e…d804`; `server_impl_sha256` `e404b91a…59ed`; `install_tree` has 51 entries with digest `6c216313…5a2c`; `/props.build_info` `b11755-704366d76`; model sha256 `270cba1b…3bd256d` pre and post; alias `kama-stories260k`; `child_env_keys` `["HOME","LANG","PATH"]`; argv includes `--offline`; transitions are `/health` refused, `/v1/models` refused, `/health` 200 at 22 ms; `loading_observed: false`; `/metrics` 501; `/slots` 200 with 4 elements; probe rows `MODEL_OK matched exit 0` and `MODEL_MISMATCH served-id-mismatch exit 2`; teardown `sigterm_sent: true`, `returncode: 0`, `port_refuses: true`. Ownership is checked before the ready captures and again before **each** probe (`tools/kama-llamacpp-live.py:861-864, 902-907`). `controls.txt`: `post_pgrep_llama_server=0`, `post_ss_8080_34113=0`. `registry/history/latest.tsv` rows for 8080/34113 remain `DEAD connection-refused`.
- **Frozen control** — `receipt-frozen-probe.json` has 10/10 checks passed, probe sha `93ee43…cd64`, matching the frozen file and manifest; the frozen script has zero `MODEL_LOADING` occurrences and grades the canonical loading body `FOREIGN_SERVICE non-2xx-non-model-http` with evidence "non-2xx HTTP from a non-model service" (entry `:10-12` correct).
- **Engine claims** — vLLM v0.32.0 binds before the engine but does not listen until ready (`ScoutVllmStartup.md:9-13`: "the TCP connection is refused"); TGI v3.3.7 binds no HTTP port during load/warmup (`ScoutTgiStartup.md:23-25`); KoboldCpp 1.123.1 default mode does not listen before load (`ScoutKoboldCppServer.md:53-63`); SGLang v0.5.22 answers `/v1/models` 200 while `/health` is 503 during `Starting` (`ScoutSglangStartup.md:23-28`); Ollama lists 200 regardless of load state (`ScoutOllamaLoading.md:7-9`). S040 is vLLM-scoped: the fetched page is titled "vLLM Model-Aware Readiness Probes | llm-d" and discusses vLLM only, so "does not support the llama.cpp body" is correct. S017's readiness/liveness vocabulary matches `runtime-health-surface-matrix.md:18`.
- **Prior ground** — `runtime-health-surface-matrix.md:14` does record the `/health` 503 `unavailable_error` "Loading model" body (README @ c0fd7862), as the entry says.

# Limitations / residual risk

- I did not run `measure.py` (forbidden: it rewrites L1 receipts); I reproduced its 55/17 vs 72/72 claim with `check.py` into `/tmp` only.
- I did not run the live harness or start llama-server (this item does not authorize it). The receipt's `loading_observed: false` means the live `MODEL_LOADING` branch is still not exercised against a live server; the only live loading-body observation is L1's 10:17 smoke, carried in `build/make_spec.py:16` and not receipted. The entry discloses this at `:118-120`.
- I did not re-fetch the b6000–b7502 tags myself; the older-build finding rests on the two cited advice files, which the entry itself names.
- The S040 check verified title/scope, not every sentence of the page.
- The receipt is one sampled instant on a toy model; it does not show concurrency, auth, router, sleep, GPU, or generation. The entry's "what the receipt does not show" covers these.
- [INFERENCE] where marked above (likely intent of the `:82` parenthetical; intended scope of "load state" for LocalAI; severity judgments).

# Installs

None. `pgrep -x llama-server` returned exit 1 (empty) after the review; no server was started. Scratch under `/tmp/kama-r16-ReviewKnowledgeEntry/` was used read-only and removed after writing this report.
