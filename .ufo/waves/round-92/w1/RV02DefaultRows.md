# RV02DefaultRows — K2 read of C1, round 92 wave 1

## Scope
Per-row K2 judgment of `SKILL.md` §Serving defaults (round 92 revision) R01–R15 at M1
(`18153ebb5f9e2ae83f53e7fef57ee579bc409331`; lane working tree byte-equal to M1 for SKILL.md,
SOURCES.md, QUALITY.md, serving-thresholds.md — `git diff --stat 18153ebb -- <files>` empty). Each
row: parameter name, value+unit, flag/env cell, cited line, literal, and whether the probe-decision
cell overreaches. All five pinned sources re-fetched by me (S593–S597), digests compared to their
S-rows; consumers read (arg.cpp lambdas, tools/server/server.cpp + server-models-sched.cpp +
server-http.cpp @ b12177; Ollama v0.40.11 sched.go, cmd/cmd.go, llm/llama_server.go; vLLM v0.32.0
v1/engine/core_client.py, entrypoints/launchers/api_server/entry.py); pinned `llama-server --help`
run and every H1 row compared. Knowledge entry §Round 92 revision and SOURCES §Round-92 correction
read and checked.

## Commands and outputs (exit codes)
- `curl -fsSL` × 5 pinned URLs → exit 0. `sha256sum` (exit 0), vs S-rows:
  common.h `c3010a3c…e073` =S593 ✓; config.go `0b0ea669…1895` =S594 ✓; envs.py `e963af06…0694` =S595 ✓;
  arg.cpp `c69c0e07…6f67` =S596 ✓; server.cpp `d4d343db…f08b` =S597 ✓. K3 met; all re-opened.
- `sha256sum ~/.local/opt/llama-b12177/llama-server` → `ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0`,
  equals counter pin (`tools/round92-server-defaults.py:57`). `llama-server --help` → exit 0 (753 lines).
- help default lines (llama-b12177-help.txt in out dir): :468 `-np, --parallel N … (default: -1, -1 = auto)`;
  :512 `--port PORT … (default: 9931)`; :612 `-to, --timeout N … read/write … (default: 3600)`;
  :614 `--sse-ping-interval N … (-1 = disabled, default: 30)`; :446 `-cram, --cache-ram N … (default: 8192, …)`;
  :639-640 `--models-max N … (default: 4, 0 = unlimited)`; :731-732 `--sleep-idle-seconds … (default: -1; -1 = disabled)`.
  All 7 H1 rows agree → independent confirmation of `help_checked=7 help_disagree=0`.
- Consumer evidence (paths relative to each pinned tag): arg.cpp:1372-1373, 2514-2522, 3561-3564, 1688-1690,
  3319-3321, 3569-3571, 3665-3667, 3826-3831; server.cpp:115-116, 126-130; server-models-sched.cpp:87-88, 197;
  server-http.cpp:217-218; config.go:20-23, 42, 126-130, 146-150, 276-277, 280-281; sched.go:122, 126, 540, 555;
  cmd/cmd.go:2266-2270; llm/llama_server.go:1327-1340; envs.py:14, 26, 111, 617, 809-813, 1142-1145, 2291-2298;
  vllm/v1/engine/core_client.py:26, 735-741; vllm/entrypoints/launchers/api_server/entry.py:153.
  All greps exit 0 (matches found); one retry: first vLLM consumer fetch hit an 1854-byte `api_server.py` shim
  (entrypoints restructured at v0.32.0) → resolved via repo tarball grep.
- Probe claims: `tools/kama-probe.sh` :148 `--timeout S … (default 5)`; :840 `RT_VERDICT=MODEL_OK; RT_REASON=router-sleeping`;
  :853 `RT_VERDICT=MODEL_OK; RT_REASON=router-unloaded-autoload`.

## Per-row table (source quotes ≤25 words; URLs per S-row)
| row | verdict | key evidence (quote / pointer) |
|---|---|---|
| R01 | holds | common.h:632 `int32_t port = 9931;` = literal; help :512; `LLAMA_ARG_PORT` help :518; env-name claim established |
| R02 | holds | common.h:634 `timeout_read = 3600` (=635 `timeout_write = timeout_read`); help :612 "read/write"; arg.cpp:3563-3564 sets both; applied http.cpp:217-218 `set_read_timeout/set_write_timeout`; probe's own `--timeout` default 5 (probe :148) |
| R03 | holds* | common.h:636 `sse_ping_interval = 30`; help :614 "-1 = disabled, default: 30". *second clause is kama policy — see NOTE-1 |
| R04 | holds* | common.h:644 `cache_ram_mib = 8192; // -1 = no limit, 0 - disable`; help :446-448 default 8192; arg.cpp:1688-1690. *see NOTE-2 |
| R05 | holds | common.h:669 `int sleep_idle_seconds = -1; // if >0, server will sleep`; help :731-732; "sleeping needs non-default" follows; probe grades `MODEL_OK`/`router-sleeping` (:840) |
| R06 | holds | common.h:703 `int models_max = 4;`; help :639-640 "(default: 4, 0 = unlimited)"; enforced sched2.cpp:87-88 `count_running() < models_max`, :197 `n_free = models_max - …` (0 ⇒ unlimited :87); probe `router-unloaded-autoload` (:853) |
| R07 | holds* | arg.cpp:1372-1373 `} else if (ex == LLAMA_EXAMPLE_SERVER) { params.n_parallel = -1; // auto by default`; help :468; common.h:464 = 1 named as overridden. *see NOTE-3 |
| R08 | holds | server.cpp:126-130 `if (params.n_parallel < 0)` → trace :127, `params.n_parallel = 4;` (:129) `params.kv_unified = true;` (:130); router keeps auto (:116 `if (role_type != SERVER_ROLE_ROUTER)`); help :450-456 kv-unified "default: enabled if number of slots is auto" |
| R09 | holds | config.go:23 `defaultPort := "11434"`; doc :21 "Default is scheme \"http\" and host \"127.0.0.1:11434\""; unset path :42 `host, port = "127.0.0.1", defaultPort`; listener cmd/cmd.go:2270 `net.Listen("tcp", envconfig.Host().Host)` |
| R10 | holds | config.go:130 `keepAlive = 5 * time.Minute`; doc :127-128 negative=infinite, zero=none, default 5 min; consumer sched.go:555 `sessionDuration := envconfig.KeepAlive()` |
| R11 | holds | config.go:150 `loadTimeout = 5 * time.Minute`; doc :146 "stall detection during model loads", :147 zero/negative=infinite; consumer llama_server.go:1331 `stallTimeout := envconfig.LoadTimeout()` → loadDeadline from last activity ⇒ not a first-answer deadline |
| R12 | holds | config.go:277 `NumParallel = Uint("OLLAMA_NUM_PARALLEL", 1)`; doc :276; consumer sched.go:540 `numParallel := max(int(envconfig.NumParallel()), 1)`; hedge "how further requests wait is not set on this line" is accurate |
| R13 | holds | config.go:281 `MaxQueue = Uint("OLLAMA_MAX_QUEUE", 512)`; doc :280; consumer sched.go:126 caps `pendingReqCh`, `ErrMaxQueue` :122 "server busy … maximum pending requests exceeded" |
| R14 | holds | envs.py:812 `os.environ.get("VLLM_ENGINE_READY_TIMEOUT_S", "600")` — inside `environment_variables` dict (:617), served by `__getattr__` :2291,2297-2298 (run-time reader, resolves disclosed limit V7); comment :809-810; consumer core_client.py:740 `poll(timeout=VLLM_ENGINE_READY_TIMEOUT_S * 1000)` "Wait for ready messages from each engine" |
| R15 | holds | envs.py:1144 `os.environ.get("VLLM_HTTP_TIMEOUT_KEEP_ALIVE", "5")` (run-time reader); comment :1142; consumer entry.py:153 `timeout_keep_alive=envs.VLLM_HTTP_TIMEOUT_KEEP_ALIVE` (uvicorn) |

Supersedes check: R01–R06→T01–T06, R07+R08→T07, R09–R15→T08–T14 = 14 distinct T ids ⇒ `supersedes=14` plausible;
T07 at SKILL.md:1888 indeed carries the superseded value `1` bound to `common.h:464` — the round-91 defect exactly as
described; round-91 rows remain above as declared.

## Findings
- BLOCKER: none. No row misstates its parameter, value, line, literal, or binary default; no probe-decision cell
  asserts engine behavior its cited code does not establish.
- NOTE-1 (R03, SKILL.md:1936): the clause "kama names this default when it reports a quiet stream" has no backing
  reporting path — "quiet"/"stream" appear nowhere else in SKILL.md or tools/kama-probe.sh (grep, exit 1). It is a
  policy pre-commitment (paired with "grades no stream by it", deliberately retracting T03's "stream silent for well
  over 30 s is a stall" grading), not a source misstatement. K2 does not fire; flagging for the L1's awareness.
- NOTE-2 (R04): pinned help (:446-448, arg.cpp:1688) contains an extra clause "0 for decision models" (paired with
  `cache_ram_explicit`, common.h:645 "decision models disable the cache otherwise"): decision models default the
  effective cache off unless `--cache-ram` is explicit. The row's "(-1 no limit, 0 off)" gloss matches its cited
  common.h:644 comment exactly; the row does not quote help for the gloss. Not a misstatement; nuance unmentioned.
- NOTE-3 (R07, SKILL.md:1940): "so `1` is never the server's slot count" is default-scoped (the sentence is about the
  parser replacing the shared default); an explicit `-np 1` does set 1 (arg.cpp:2521, rejects only 0). Correct as a
  defaults-table claim; wording could be read absolutely.
- Disclosed limit V7 independently confirmed: envs.py:26/:111 are `TYPE_CHECKING` declarations (block :14+); the
  run-time defaults are the dict lambdas :812/:1144 via `__getattr__` :2291-2298, and those are the lines R14/R15
  cite. Counter's blind spot does not affect these rows.
- Host load during session: `uptime` load average 34.6-40.8; no timing claims made by this seat, none affected.

## Deliverables
- Report: .ufo/waves/round-92/w1/RV02DefaultRows.md (this file)
- .ufo/waves/round-92/w1/out/RV02DefaultRows/llama-b12177-help.txt (full `--help`, exit 0)
- .ufo/waves/round-92/w1/out/RV02DefaultRows/digests.txt (five source + binary sha256, all equal to their rows/pin)
- .ufo/waves/round-92/w1/out/RV02DefaultRows/llamacpp-b12177-root-tree.json, ollama-v0.40.11-tree.json
- Scratch /fast/scratch/hyaku/kama-r92/RV02DefaultRows/ removed before yield; one accidental scratch file
  (`t.json`) I wrote to the lane root was moved into my out dir; no tracked lane file touched, no git mutation in
  the lane. No installs/upgrades performed (existing curl/python3 sufficed). Live endpoint 1234: only nothing sent
  (no GET needed by this item).

VERDICT: holds — all 15 rows R01–R15 bind to their cited lines, agree with the pinned b12177 `--help` defaults (7/7 checked options), cite the run-time readers for vLLM, and no probe-decision cell overreaches its source; C1 passes the K2 read with three non-firing notes.
