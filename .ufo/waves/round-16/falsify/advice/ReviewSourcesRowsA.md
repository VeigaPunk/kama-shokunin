VERDICT: partial — S035/S036/S037 (corpus/SOURCES.md:47-49) and corpus/lessons/round-16.md §Gate: every line number and every sha256 confirms from the pinned commit, and every Gate quote is present; two absolute-word claims in the rows' `teaches` cells are falsified by code paths the rows did not scope out.

Seat: KamaR16.ReviewSourcesRowsA (reviewer, falsify wave). Leaf: no subagents. I wrote only this report and scratch under `/tmp/kama-r16-ReviewSourcesRowsA/`, deleted at the end. I did not start llama-server, did not touch 8080/34113, did not run `measure.py`, and did not read any session/credential store. No installs.

Incident (M4 class, disclosed): my first `write` used a lane-relative path that resolved against the fleet root, creating `/home/vgpnk/Projects/shokunin/.ufo/waves/round-16/falsify/advice/ReviewSourcesRowsA.md` outside the lane. I copied it into the lane unchanged and deleted the outside copy, so the lane file is the only copy. A sibling's `RevengerRunReceipts.md` (11:00, 14874 bytes) remains at that fleet-root path; I left it alone because it is not my Report.

## Axes

Line-number fidelity, raw-file sha256 reproducibility, quote presence and word limit, scope consistency of each claim with the cited range, and whether the §Gate decisions still hold after re-opening every cited location.

## What I ran (commands and exit codes)

1. `curl -sSL …/704366d76f8748cf9ad3df62a464bfcc8d1ae6ad/tools/server/{README.md,server-http.cpp,server.cpp}` → HTTP 200 each, 119661 / 37318 / 24572 bytes. `sha256sum` on the downloads: `714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37`, `24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb`, `2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4` — byte-equal to the rows, and to `.ufo/waves/round-16/sources/llama.cpp-704366d/` (same `sha256sum`, exit 0).
2. `awk` line dumps of every cited range in the pinned copies (exit 0).
3. `gh api repos/ggml-org/llama.cpp/releases/tags/b11755` → exit 0.
4. `curl` HF model card, model API and tree API → 200 each.
5. `curl` kubernetes.io probes page → 200; `curl` `kubernetes/website/main/content/en/docs/concepts/workloads/pods/probes.md` → 200; `sed -n '70p'` → exact sentence.
6. `curl https://llm-d.ai/docs/operations/readiness-probes` → 404; `/docs/0.10/operations/readiness-probes` → 200.
7. `python3 tests/probe-verdicts/check.py --probe tools/kama-probe.sh --json` → exit 0, 72 tests / 72 passes / 0 failures. `--probe .ufo/waves/round-16/frozen/kama-probe-before.sh --json` → exit 1, 72 tests / 55 passes / 17 failures; the 17 failure names are exactly the 17 `MODEL_LOADING` rows (set equality, symmetric difference empty).
8. `sha256sum` frozen probe = `93ee4302718f97862135472411ecf7aa6d5a0dc5cf778cce2c8deefe97a2cd64`; `git cat-file blob 20e392e…:tools/kama-probe.sh | sha256sum` gives the same (exit 0).
9. `git diff 20e392e..b8e485c -- corpus/SOURCES.md` → 35 insertions, 1 deletion; the single deleted/modified line is S017's used-by cell.
10. Fetched all 29 `tools/server/*.{cpp,h}` at the commit and grepped (`Loading model`, `unavailable_error`, `ERROR_TYPE_UNAVAILABLE`) plus read `common/common.h` and `common/arg.cpp`.

## Confirmed (row by row)

**S035** — `corpus/SOURCES.md:47`.
- Lines 479-490 are the `### GET /health` block: 479 heading, 481 "This endpoint is public (no API key check). `/v1/health` also works.", 485 503 status, 486 body literal, 487 "- Explanation: the model is still being loaded.", 488-490 the 200 branch.
- Line 1258 is exactly "The returned list always has one single element. The `meta` field can be `null` (for example, while the model is still loading)."
- README contains only two 503 mentions: 485-486 (`/health`) and 987 (`?fail_on_no_slot=1` on the slots route). There is no `/v1/models` 503 documentation, so "README alone supports the `/v1/models` 503 = reject" is correct.
- Raw sha256 is the claimed one; the scope sentence ("at commit 704366d76 only; not `/v1/models` loading behaviour, which the code row S036 decides") is consistent with the file.

**S036** — `corpus/SOURCES.md:48`.
- 307 `auto middleware_server_state = …`, 308 `if (!is_ready.load())`, 309-311 frontend exemption, 312 the quoted comment, 314-325 status/content/`return false`, 328 close. All match.
- Body at 317-321: `{"error", {` / `{"message", "Loading model"},` / `{"type", "unavailable_error"},` / `{"code", 503}` — message, type, integer 503 exactly as the row writes.
- Pre-routing order: 331 registers the handler; 347-353 is the OPTIONS branch; 354 `middleware_server_state`; 357 `middleware_validate_api_key`. State gate precedes the API-key check, so "before the API-key check" holds.
- `/health` and `/v1/health` are in `get_public_endpoints` (`server-http.cpp:251-258`) but that only bypasses the key check; the pre-routing state gate still runs first, and README:485-487 documents the same body for `/health`. "`/health` included" holds.
- Raw sha256 is the claimed one.

**S037** — `corpus/SOURCES.md:49`.
- Router: 440 `if (is_router_server)`; 455 `ctx_http.start()`; 460 `ctx_http.is_ready.store(true)`; 462 next block. 472 `models_routes->models.load_startup_models()` runs after ready, so "ready before any model" holds.
- Single-model: 493 comment, 494 `ctx_http.start()`, 507 `ctx_http.load_model(params)`, 515 `ctx_http.is_ready.store(true)`. `server-http.h:71` initialises `std::atomic<bool> is_ready = false;`, so the window 494→515 is real.
- `grep -n is_ready server.cpp` returns only 460 and 515; `server-http.cpp` only reads it at 308. No other writer exists, so the "when is_ready is set" scope is complete.
- Raw sha256 is the claimed one.
- "Never emits that body" is true for the router's own middleware (and across the 29 top-level `tools/server` C++ sources at the commit the literal exists only at `server-http.cpp:318`). It is not true for every router-mode **response**; see F2.

**§Gate (corpus/lessons/round-16.md:36-58)** — all quotes and citations present:
- `server-http.cpp:312` → "no endpoints are allowed to be accessed when the server is not ready" (12 words).
- `server.cpp:493` → "start the HTTP server before loading the model to be able to serve /health requests" (16 words).
- `server-context.cpp:5396` → `format_error_response("no slot available", ERROR_TYPE_UNAVAILABLE)`; `server-models.cpp:2585` → `format_error_response("Stream owner model is loading, retry later", ERROR_TYPE_UNAVAILABLE)`. `server-common.cpp:119-122` maps `ERROR_TYPE_UNAVAILABLE` to type `unavailable_error`, code 503, so "share type and code" holds; `res_err` (`server-models.cpp:2158-2161`) also sets `status = code` (503).
- `README:1258` and `README:487` as quoted.
- `probes.md:70` → "Readiness probes determine when a container is ready to accept traffic." (11 words); rendered page footer "Last modified June 30, 2026".
- S040 quote appears verbatim under §Problem Statement on the v0.10 page ("Version: v0.10"); S021's recorded URL is 404, v0.10 is 200.
- S038: tag `b11755`, `prerelease: true`, `published_at 2026-10-20T11:18:44Z`, `target_commitish 704366d76…`, asset `llama-b11755-bin-ubuntu-x64.tar.gz` size 22240468, digest `sha256:753bfa7327a75b477d4d14cde71e0e46a40acc3a1408c5504530b78c33a6e226`. Every cell matches.
- S039 model card is one line: "Various models to be used in llama.cpp CI workflow."
- S041: receipt `schema kama-llamacpp-live/v1`, `port 32845`, `port_refusal_set [8080, 34113]`, `started_utc 2026-10-20T13:49:38.040Z`, `ended_utc …170Z`, exactly 10 checks, all passed; `probe_model_ok.observed` = `{"exit": 0, "reason": "matched", "verdict": "MODEL_OK"}`. `registry/history/latest.tsv` still lists three rows, all `DEAD connection-refused`.
- "No status or recheck cell of an existing row changed": the only modified existing line is S017's used-by cell, which gained `corpus/knowledge/llamacpp-loading-lifecycle.md`; S021 is untouched and `queued`.
- The stub-matrix claim in the Gate ("a stub that is not llama.cpp is graded MODEL_LOADING") holds: `body_is_llamacpp_loading` (`tools/kama-probe.sh:428-446`) parses only status-coded JSON and never inspects `Server`; rows `LoadingEnvelope.no-server-header`, `NearMissTriple.readme-key-order-positive`, `EnvelopeShapes.ExtraFieldsAllowed` and `EnvelopeShapes.Padding64KiB` expect `MODEL_LOADING` with no `Server: llama.cpp` identity. My frozen/current rerun reproduced the exact expected change set.

## Findings

**F1 — medium-low, S036 `teaches` (corpus/SOURCES.md:48).** "Every non-frontend path … answers 503" is false for `OPTIONS`. The row's own anchor includes `347-359`, and 347-353 handles `OPTIONS` before the state gate at 354: it sets CORS headers, `res.set_content("", "text/html")`, and returns `Handled` without touching `res.status` (the response default is 200, `server-http.h:23`). So `OPTIONS /v1/models` on a loading server answers 200 blank, not the envelope. GET/HEAD probes are unaffected, so the C1 claim and the Gate decisions stand. [INFERENCE] from code; not executed.
*Smallest correction:* scope the sentence to "every non-frontend, non-OPTIONS request" in an appended note or a correction row.

**F2 — medium, S037 `teaches` (corpus/SOURCES.md:49).** "The router … never emits that body" is overbroad as an absolute about router-mode responses. The router's own middleware cannot emit it (is_ready is stored true at 460), and router `/v1/models` is served locally by `get_router_models` (`server.cpp:269`), `/health` by the shared `get_health` (`server.cpp:241,278`; `server-context.cpp:5288-5299`). But with autoload off, `proxy_post` skips `ensure_model_ready` (`server-models.cpp:2297`) and forwards; `proxy_request` accepts `SERVER_MODEL_STATUS_LOADING` because `is_running()` includes LOADING (`server-models.h:98-100`); the child is a single-model server in the S037 494-515 window, so the client receives the child's exact 503 envelope (`server-http.cpp:314-325`) through the router. Autoload off is supported: `--no-models-autoload` (`common/arg.cpp:3704-3708`, default `models_autoload = true` in `common/common.h:702`) and per-request `?autoload=false` (`server-models.cpp:2182-2188`). [INFERENCE] static read of an unexecuted path; the probed `/v1/models` surface is unaffected, so neither C1 nor the Gate's "503 window" decision is harmed.
*Smallest correction:* "the router's own state middleware never emits that body; with models autoload disabled a proxied request to a still-loading child can relay it, though `/v1/models` and `/health` on the router are served locally."

**F3 — low, §Gate S017 citation (corpus/lessons/round-16.md:47).** The citation is written "S017 probes.md:70", but S017's recorded anchor is the rendered URL plus section names, and no `probes.md` copy is pinned under `.ufo/waves/round-16/sources/` (that directory pins only llama.cpp files). The line number is therefore reproducible only against mutable upstream `main`; it matches today, and `ScoutK8sProbes.md:5-7` records commit `751b927b5a68…` as the checked revision, but that commit is not in the Gate or the row. S035-S037 set the opposite standard by carrying a raw sha256.
*Smallest correction:* append the `kubernetes/website` commit sha and raw sha256 (or pin the file) next to the quote.

**F4 — low, §Gate preamble "Quotes are verbatim" (corpus/lessons/round-16.md:38).** The S041 quote `{"exit": 0, "reason": "matched", "verdict": "MODEL_OK"}` is not a byte-verbatim substring of `receipt.json`: the receipt stores those fields pretty-printed at lines 150-154 (`"exit": 0,` newline `"reason": "matched",` newline `"verdict": "MODEL_OK"`). Values are identical; only the serialization differs.
*Smallest correction:* cite `receipt.json:150-154 (compact re-serialization)` or quote one field per line.

**F5 — nit, S035 `teaches` (corpus/SOURCES.md:47).** The prose writes the ready body as `{"status": "ok"}`; README:489 has `{"status": "ok" }` (trailing space inside braces). It is not presented as a quote, so no action is required.

**F6 — nit, §Gate row 1 (corpus/lessons/round-16.md:42).** "body literal at 318-320 `{"message", "Loading model"},`" — the quoted text is line 318 only; 319 is `{"type", "unavailable_error"},` and 320 is `{"code", 503}`. The range is correct for the triple; the quotation covers one of the three lines.

No sha256 defect, no wrong line number, and no missing quote was found in S035-S037 or in the Gate.

## Residual risk and verification gaps

- Both code-path findings (F1, F2) are static reads; this seat was not authorised to start llama-server, so no wire-level `OPTIONS` or `--no-models-autoload` router run was performed. The exact `OPTIONS` status (200 vs another default) is [INFERENCE] from `server_http_res.status = 200` plus the branch order.
- S035-S037 are fully reproducible (raw sha256 pinned twice: row + local copy). The Gate's S017, S040, S038 and S039 citations depend on mutable web/GitHub surfaces; S017 has no digest, the others are dated but not content-hashed. The release API is rate-limited unauthenticated (my first `curl` got 403); `gh api`, authenticated, is the reproducible channel.
- Running the permitted `check.py` leaves `tests/probe-verdicts/__pycache__/check.cpython-314.pyc` untracked in the lane; I left it in place because sibling seats were running the same command concurrently and deleting a `.pyc` mid-run is not my call. L1's misroot sweep should expect it.
- `pins.json` lists four files and omits `server.cpp` although the file is present and its hash matches S037; this is a manifest gap, recorded by the sibling CriticSourceRows too, outside this seat's claims audit but worth fixing alongside F3.
- The Gate's "found no such body" rejection for vLLM should be read as "no such *exact* body": S021/llm-d (per `ScoutVllmStartup.md:83-86`) does document vLLM `/v1/models` as "503 or connection refused during model loading", and `ScoutVllmStartup.md` reconciles that to connection-refused in practice. The exact-envelope rejection itself is unaffected.
