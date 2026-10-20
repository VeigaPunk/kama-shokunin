VERDICT: partial — the round-16 engine contrasts in `corpus/knowledge/runtime-health-surface-matrix.md` §Correction. All four behavior claims match the cited advice (and the pinned upstream), but the correction drops material scope qualifiers, omits Ollama's pinned revision, and leaves the entry's own KQ6 clearance false as written.

# What I attacked

`corpus/knowledge/runtime-health-surface-matrix.md:60-72`, the §Correction — round 16 block, line 66-72 in particular:

> Engine contrasts gathered this round from source and kept as advice, not as rows: vLLM v0.32.0 and TGI v3.3.7 do not listen until ready (connection refused); SGLang v0.5.22 answers `/v1/models` 200 while `/health` is 503; Ollama `/v1/models` lists available models whatever the load state.

checked line by line against the four cited files under `.ufo/waves/round-16/build/advice/`, plus the adjacent llama.cpp claim at lines 62-66, the entry's QUALITY clearance at lines 28-36, and the SOURCES registry. No runtime was started; this is a source/advice fidelity review.

# What I ran (all exit 0 unless stated)

1. Pinned-source identity — `sha256sum .ufo/waves/round-16/sources/llama.cpp-704366d/{README.md,server-http.cpp,server.cpp}` → exit 0; all three equal `pins.json` and the S035/S036/S037 cells:
```
714c067bdbc49bde2735810fbff83eb2933b12c57d50f0012b61fcecb75a6a37  README.md
24ede172e526763567dbe929da5b16250693d7a2e44334ef0126649b6d3f5fdb  server-http.cpp
2143962217e9d6275f28c42d599139bb702e2f880dccbad01ab9d8b094f5aef4  server.cpp
```
2. Row census — `grep -c '^| S03[5-9]\|^| S04[01]' corpus/SOURCES.md` → `7`, exit 0. `grep -n 'TGI\|text-generation-inference' corpus/SOURCES.md | grep -c '| S'` → `0`, pipeline exit 1. There is no vLLM/TGI/SGLang/Ollama source row.
3. Raw GET at each pinned revision — `HTTP 200`, `rc=0` for all four:
   - `vllm-project/vllm/v0.32.0/.../launchers/launcher.py`
   - `huggingface/text-generation-inference/dfb3fbe78e0d1d69251bd33065591c61bafdfaa8/router/src/server.rs`
   - `sgl-project/sglang/v0.5.22/python/sglang/srt/entrypoints/http_server.py`
   - `ollama/ollama/v0.40.6/server/routes.go`
4. Anchor reads (`nl -ba`/`sed`/`grep -n`) on the pinned llama.cpp tree, the matrix, the four advice files, and the four upstream files. Scratch (`/tmp/kama-r16-ReviewHealthMatrixCorrection/`, removed after writing).
5. Probe/gate runs: none (not in this item's scope; the matrix makes no probe claim). No llama-server started.

# Line-by-line check of the four contrasts

| # | Correction claim (lines 66-70) | Cited advice — actual words | Verdict |
|---|---|---|---|
| 1 | "vLLM v0.32.0 … do not listen until ready (connection refused)" | `ScoutVllmStartup.md:7-9`: "Answer (v0.32.0, the current stable release) … **Neither endpoint answers: the TCP connection is refused.**" Bind-before-engine at §1; same ordering at v0.10.2/v0.6.4 (§2); all listed topologies refuse pre-ready (§4). | **Matches.** Upstream re-check: `launcher.py:348 sock.bind(addr)` with no `listen()`; comment `:391` "workaround to make sure that we bind the port before the engine is set up." |
| 2 | "TGI v3.3.7 … do not listen until ready (connection refused)" | `ScoutTgiStartup.md:23-26`: "During both weight loading and router warmup, a **launcher-managed** TGI v3.3.7 binds no HTTP port at all. A client gets TCP connection refused." | **Matches on behavior; scope qualifier dropped.** The advice's evidence is the launcher-managed deployment (`F5` step 5: bind only in `server::run`). Upstream re-check: `router/src/server.rs:2322 TcpListener::bind` after `connect_backend` + warmup (`:151,199` per advice). The generalized claim is probably true [INFERENCE], but the advice did not establish it for a standalone router. |
| 3 | "SGLang v0.5.22 answers `/v1/models` 200 while `/health` is 503" | `ScoutSglangStartup.md:21`: "HTTP up, `server_status == Starting` (warmup in flight) … **503, empty body** … **200** with `data[0].id = served_model_name`." | **Matches.** Upstream re-check: `http_server.py:705-706` (one handler, two routes), `:719-720` Starting → 503, `:1926` `/v1/models`; `tokenizer_manager.py:703` initial `ServerStatus.Starting`. The advice's phase/default qualifier is dropped (see F4). |
| 4 | "Ollama `/v1/models` lists available models whatever the load state" | `ScoutOllamaLoading.md:8-10`: "Both always describe installed on-disk models (200) or fail with 500; there is no 503/loading branch." `:40`: "a probe pointed at `/v1/models` gets 200 whether the model is cold, loading, or ready." | **Matches on behavior; revision dropped** (advice pins v0.40.6 at `:16`). Upstream re-check: `routes.go:2120-2128` (`ListHandler` 200/500 only), `:2370-2371` `/api/tags`, `:2406` `/v1/models`, `:2778` `PsHandler` 200. |

The correction's "kept as advice, not as rows" is itself accurate: `SOURCES.md:111-112` says the engine scans "are kept as wave advice, not rows", and rows S035-S041 contain no vLLM/TGI/SGLang/Ollama entry (census above).

# Findings

## F1 — medium: the entry's KQ6 clearance no longer describes the file

`runtime-health-surface-matrix.md:35` states KQ6 as "every engine statement names engine + documented revision … and section and cites an opened `SOURCES.md` row". The authors knew how to scope this to the table when they meant the table: `:30` (KQ1) says "every **row** is a documentation statement pinned to revision and section". KQ6 says **statement**, and the appended contrasts are engine statements:

- **No section anchor** for any of the four (no file:line, no route section, no page section).
- **No opened `SOURCES.md` row** for any of the four; the only citations are four advice file paths at `:70-72`.
- **No revision at all for Ollama** — the only engine of the four without one; `ScoutOllamaLoading.md:16` pins v0.40.6.
- TGI is not merely row-less: `ScoutTgiStartup.md:13-15` says the registry "has **no TGI row**" and the pin "cannot be cited as a lane source until a row is admitted".

"net as advice, not as rows" acknowledges the gap but does not amend `:35`. A reader checking the clearance sees a claim that four statements in the same file do not meet. KQ6's text has no advice exemption.

**Smallest fix:** either (a) append rows for the four pinned engines (cheap anchors already in the advice files: vLLM v0.32.0 `launcher.py:348,391` + `health.py:23-33`; TGI v3.3.7 `router/src/server.rs:230-241,2322`; SGLang v0.5.22 `http_server.py:705-720,1926-1955`; Ollama v0.40.6 `server/routes.go:2120-2128,2370-2371,2406`), or (b) append one sentence scoping KQ6 to the crosswalk rows and declaring the round-16 contrasts unadmitted advice — and name Ollama v0.40.6 in either case.

## F2 — medium: SGLang `/health` cost is omitted and now contradicts the entry

The correction cites `ScoutSglangStartup.md`, whose table row for the state after warmup reads: "200; **runs one-token generation** by default (up to 20 s)" (`:21`), and whose advice `A5` says: "Do not use SGLang `/health` as a cheap liveness probe." (`:103`). `/ready` (`:698-702`) is the cheap 200/503 route.

The matrix still says `:16` "Liveness route | `GET /health`" and `:26` "`/health` remains a lightweight liveness signal", with the row-16 caveat naming only `/health_generate` as a generation request. After this correction the file cites the source that says the opposite for `/health` post-`Up`, without reconciling the row. The four-word contrast sentence is not itself false, but the entry is now internally inconsistent on the one property the matrix exists to record (what a health route costs).

**Smallest fix (append-only, per KQ7):** one sentence in the round-16 block noting SGLang `/health` is generation-based by default after warmup (20 s ceiling) and `/ready` is the cheap route; scope `:26`'s "lightweight liveness" phrasing to llama.cpp.

## F3 — low: TGI "launcher-managed" qualifier dropped

`ScoutTgiStartup.md:23` restricts the finding to "a launcher-managed TGI v3.3.7". The correction generalizes to TGI. The advice traced only the launcher-managed chain (`F5`); the standalone router is not covered. The upstream bind site (`server.rs:2322`) suggests the generalization holds [INFERENCE], but it is not what the cited file established. Add "launcher-managed" or cite the broader trace.

## F4 — low: SGLang phase/default qualifier dropped

`ScoutSglangStartup.md:111` records "`--skip-server-warmup` skips the 503 window entirely". The correction states the `/v1/models` 200 vs `/health` 503 conjunction unconditionally. It is true at any instant `/health` answers 503, but the unstated scope is the default warmup path; with the flag the 503 window does not exist. Name the window ("during startup warmup") in the sentence.

## F5 — low: "None of these is a local runtime observation" is narrower than it reads

True for engine runtimes: no engine was started in any of the four advice files. But two of them do record local non-engine checks — `ScoutVllmStartup.md` §"Kernel control (run locally 2026-10-20 … no vLLM)" and `ScoutOllamaLoading.md:17` ("nothing listening on 127.0.0.1:11434", `command -v ollama` empty). If the intended claim is "no engine runtime was contacted", say that; the current sentence can be read as denying all local measurement.

## F6 — low: "gathered this round from source"

TGI, SGLang and Ollama also rest on docs pages (`ScoutTgiStartup.md` F6; `ScoutSglangStartup.md` F11; `ScoutOllamaLoading.md` docs scope). Pinned source is the primary evidence, so this is a provenance compression, not a behavior error. "From pinned source and docs" would be exact.

# What checked out (the llama.cpp half of the correction is sound)

- **README:1258 quote is exact.** `README.md:1258`: "The `meta` field can be `null` (for example, while the model is still loading)." S035's row anchor names the same line.
- **The 503 middleware covers `/v1/models`.** `server-http.cpp:307-328` gates on `is_ready`; the only exemption is `frontend_paths` (`:242-248` = `"/"` plus embedded UI asset names, not API routes). Quote `:312`: "no endpoints are allowed to be accessed when the server is not ready". Body at `:316-322` is the exact `message`/`type`/integer `code` envelope.
- **Order vs API key.** Pre-routing handler runs the state gate at `:354` before `middleware_validate_api_key` at `:357`; the S036 "before the API-key check" cell is correct.
- **Single-model ordering.** `server.cpp:493` comment "start the HTTP server before loading the model to be able to serve /health requests"; `:507 load_model`; `:515 is_ready.store(true)`. Router mode flips `is_ready` at `:460` before `load_startup_models` at `:472`, so the 503 window is single-model-only, exactly as S037 and the correction say.
- **Row 14 remains consistent.** `README.md:479-490` documents the 503 loading body and the 200 `{"status": "ok"}` ready body; the code's gate matches.
- **All four behavior contrasts match the advice and the advice matches upstream at the sampled anchors** (raw GETs above; vLLM bind-only, TGI health 200/503 `healthcheck`, SGLang Starting→503 + `/v1/models` unguarded 200, Ollama list 200/500 only).

# Residual risk / verification gaps

- No engine runtime was started (nor should be, per this item); every status statement remains source-derived, as the correction itself says. `pgrep -x llama-server` was not run because nothing was started.
- GitHub REST release queries returned **HTTP 403** (rate-limited/blocked) for vLLM, TGI, Ollama and SGLang. Tag existence is proven indirectly by the four `HTTP 200` raw GETs at the pinned tags/commits; the advice's "latest release" claims were not independently re-verified.
- `tools/server/server-http.h` is not in the pinned set, so `is_ready`'s initial `false` is [INFERENCE] from the `server.cpp` ordering plus the middleware's purpose. The pinned `.cpp` alone shows "not ready", not the initializer.
- I re-checked one key anchor per engine, not every file:line in the four advice files; the advice files were treated as the object of the fidelity question, not re-audited end to end.
- No language server applies to Markdown/corpus prose in this checkout; `read`/`grep`/`nl` were the only available methods (no `lsp` device is mounted for this seat). All searches were bounded to the lane paths named above.
- Markdown line numbers were taken with `nl -ba` on the working tree at lane commit `b8e485c`; the file was not edited.

# Installs

None — no pacman/`uv`/`npx`/binary install or upgrade; host pacman pause untouched.
