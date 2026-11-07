# SC01SourceReopen — independent re-open of C1's sources (round 92, L1 KamaR92)

## Scope

Re-open, independently of the lane counter, the five sources C1 binds to (S593–S597) and scout for overrides the round-92 table misses. Read-only in the lane except my
out dir and this report; scratch `/fast/scratch/hyaku/kama-r92/SC01SourceReopen/` (removed at end). Revisions (full hashes): base
`ed018ca0fa956c5052b3dc6b714a2cb72973da21`, freeze `309eadafd4d0557a056c1bf61455c59778cf5e1d` (added `plans/round-92-claims.md`), M2
`fa8aedb73d18448383c7a4d75405aba448fe8e38`, M1 `18153ebb5f9e2ae83f53e7fef57ee579bc409331` (parent of M2 confirmed: `git rev-parse 18153ebb^` =
`fa8aedb73d18448383c7a4d75405aba448fe8e38`), HEAD `83f9e3d4`. Counter blob `4c5bca0def4a2901fb9392efa04e2c82a89c768e` byte-identical at F, M1 and HEAD. Host Linux
7.2.11-arch1-1, curl 8.23.0, python 3.14; `uptime` → `load average: 38.63, 52.55, 43.34` (no timing claims — every check is digest- or text-exact).

## Commands and outputs (true exit codes)

`curl -sS -L --max-time 90 -o src-<f> <url>` (5 URLs, all 200) → `sha256sum src-*` (0); `python3 independent_check.py` (0) — my own re-implementation of B1–B7/H1–H3, not
the lane counter; `python3 lines_exact.py` (0); vLLM importlib probe (0); `python3 presets.py` (0); `grep -rn -E
'\b(port|timeout_read|timeout_write|sse_ping_interval|cache_ram_mib|sleep_idle_seconds|models_max|n_parallel)\s*=[^=]' tools/server/`; `python3 tools/round92-server-defaults.py --repo . --rev 18153ebb… --binary <pinned>` (0).

Fetched digests, each equal to the SOURCES anchor at M1 (`corpus/SOURCES.md`): S593 `common.h` `c3010a3c662a14556adb651b79bff00089564fde6b5e336959403e3db34e6073`; S594
`config.go` `0b0ea669b31cfe2b54313427257326a2b7a909bbc7bf8a671035efc446fb1895`; S595 `envs.py` `e963af06cf6c775fe285147e0d811ea5b4d679e5cbd6958980ec2a0d1da70694`; S596
`arg.cpp` `c69c0e0703dbd343aec148ff4a65a343da80f65064d9385bc60120ed765e6f67`; S597 `server.cpp` `d4d343db7c1b648eb5358ae2b87966a5f78ce5c9b245c7fbfe9827ba6971f08b` (all
under `raw.githubusercontent.com/…/b12177|ollama/v0.40.11|vllm/v0.32.0/…`). Second transport (release tarballs `codeload.github.com/…/tar.gz`, extracted, hashed): the
same five files hash identically — two transports, same bytes. My independent row re-check: all 15 rows OK, `rows=15 fails=0` (exit 0), each row's `--help` default
agreeing (`--port` 9931, `--timeout` 3600, `--sse-ping-interval` 30, `--cache-ram` 8192, `--sleep-idle-seconds` -1, `--models-max` 4, `--parallel` -1); pinned binary
sha256 `ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0`, each of the 7 options appears exactly once in `--help`. Lane counter at M1 (read-only):
`SERVER_DEFAULTS rows=15 bound=15 unbound=0 duplicates=0 engines=3 fetch_failures=0 help_checked=7 help_disagree=0 supersedes=14 … rev=18153ebb…` exit 0, all 15 rows
`bound=1`; I independently recomputed the supersession set (the rows name all 14 distinct T01–T14 ids). Per-row detail: receipts.txt §4.

## Findings

**NOTE — every R-row's literal sits on its stated line in the bytes the URL serves today.** Exact lines and quotes: receipts.txt §5. The set is
`common.h:632/634/636/644/669/703` (`int32_t port = 9931;`, `int32_t timeout_read = 3600;`, `int32_t sse_ping_interval = 30;`, `int32_t cache_ram_mib = 8192;`, `int sleep_idle_seconds = -1;`, `int models_max = 4;`), `arg.cpp:1373` (`params.n_parallel = -1;`), `server.cpp:129` (`params.n_parallel = 4;`), `config.go:23/130/150/277/281`
(`defaultPort := "11434"`, `keepAlive = 5 * time.Minute`, `loadTimeout = 5 * time.Minute`, `NumParallel = Uint("OLLAMA_NUM_PARALLEL", 1)`, `MaxQueue = Uint("OLLAMA_MAX_QUEUE", 512)`), `envs.py:812/1144` (`os.environ.get("VLLM_ENGINE_READY_TIMEOUT_S", "600")`, `os.environ.get("VLLM_HTTP_TIMEOUT_KEEP_ALIVE", "5")`). The
SKILL literals are trimmed forms of these lines (source lines carry trailing `//` comments); each trimmed literal is a literal substring of its stated line, which is what
B6 applies. **No row misstates its line, value or source.** The S593/S595 anchors are accurate too: `common.h:464` is `int32_t n_parallel = 1;` (round-91 T07's line,
cited by R07), `common.h:705` is `bool models_autoload = true;`, and `envs.py:26`/`:111` are the TYPE_CHECKING declarations with `:809-813`/`:1142-1145` the two lambda
blocks.

**NOTE — the disclosed counter limit V7 is resolvable by a reviewer, and the table's choice is correct.** `vllm/envs.py` has `if TYPE_CHECKING:` spanning **lines 14–335**
(AST-verified), so lines 26 and 111 never execute; `"VLLM_ENGINE_READY_TIMEOUT_S" in vars(module)` → **False**, and the module-level `__getattr__` (`envs.py:2291`)
resolves the name via `environment_variables` (dict starts `envs.py:617`). Loading the module standalone: `attr VLLM_ENGINE_READY_TIMEOUT_S = 600`, `attr
VLLM_HTTP_TIMEOUT_KEEP_ALIVE = 5`; after `os.environ[…]="1234"` it became `1234`; a real `from vllm.envs import VLLM_ENGINE_READY_TIMEOUT_S` returned the live value too.
The run-time reader is therefore the `environment_variables` lambda at `envs.py:812` / `envs.py:1144` — exactly the lines R14/R15 cite, so the `corpus/SOURCES.md:703-712`
round-92 correction holds. Corroborating use sites: `vllm/v1/engine/core_client.py:740` and `:1854`; `vllm/entrypoints/launchers/api_server/entry.py:153`
(`timeout_keep_alive=envs.VLLM_HTTP_TIMEOUT_KEEP_ALIVE`); `vllm/v1/utils.py:362-363` forwards both to the Rust frontend, whose independent defaults agree
(`rust/src/cmd/src/cli.rs:655` `default_engine_ready_timeout_secs() -> u64 { 600 }`; `rust/src/server/src/config.rs:25` `DEFAULT_KEEP_ALIVE_TIMEOUT: Duration =
Duration::from_secs(5)`).

**DEFECT — R08's value `4` is role-conditional and the table's flat value cannot show that.** `tools/server/server.cpp:116` (`if (role_type != SERVER_ROLE_ROUTER) {`)
guards `server.cpp:126` (`if (params.n_parallel < 0) {`) and `server.cpp:129` (`params.n_parallel = 4;`). A router-role server keeps `n_parallel = -1` and `server-context.cpp:1489` (`for (int i = 0; i < params_base.n_parallel; i++)`) creates **zero** slots. R08's decision cell does say "the router role keeps auto (line 116)" — the
row is not blind to it — but R08 binds via H2 (derived default; `--parallel` prints `-1`, not `4`), so the counter can never see that "4" holds only for the instance
role. The value is literally on the cited line and is what an instance-role server runs, so whether this crosses K2 is the non-author reviewer's call, not mine.

**DEFECT — R01's port has three listener paths the table names no override for.** Normally `tools/server/server-http.cpp:116` (`port = params.port;`), but `server-http.cpp:96` (`port = std::stoi(getenv("AIP_HTTP_PORT", "8080"));`) plus `server-http.cpp:125` (`port = gcp.port;`) replace it wholesale when `AIP_MODE=PREDICTION`
(`server-http.cpp:93`) — `server-http.cpp:122` warns "overriding server port %d with AIP_HTTP_PORT %d". Also `server-http.cpp:508-512` (`port = bound_port;`, i.e. `--port
0` → ephemeral) and `tools/server/server-models.cpp:1218` (`inst.meta.port = common_http_get_free_port();`) — a **router-spawned child listens on a free port, not 9931**
(`server-models.cpp:1235` passes `SERVER_ENV_ROUTER_PORT` to the child). R01's cell requires citing "the argv or environment"; AIP_HTTP_PORT and the free-port child are
neither. Same shape for R06: `tools/server/server-models-sched.cpp:87` shows `models_max` governs the router's concurrent model count, and `server-models.cpp:914-917`
warns "number of models to load on startup (%zu) exceeds models_max (%d)" — a startup error path unmentioned.

**NOTE — eleven llama.cpp presets silently override `port` and `n_parallel` after parsing.** `common/arg.cpp:4607-4621` (`--embd-gemma-default`) sets `params.port =
8011;` (4613) and `params.n_parallel = 32;` (4616); `arg.cpp:4711-4725` (`--gpt-oss-20b-default`) sets `params.port = 8013;` (4717) and `params.n_parallel = 2;` (4720);
`arg.cpp:4730` sets port 8013 / n_parallel 2; six `--fim-qwen-*` set `params.port = 8012;` (4629, 4643, 4657, 4673, 4689, 4703); two `--vision-gemma-*` set port 8014
(4753, 4764). All are `.set_examples({LLAMA_EXAMPLE_SERVER, …})` and live in `llama-server --help` (help lines 735-751). A server started with `--embd-gemma-default`
listens on **8011** and runs **32** slots, not 9931/-1/4 — R07's "1 is never the server's slot count" is true of the parser but silent on presets, and R08's "the count is
fixed at startup" holds only without one.

**NOTE — R04's cache default has a server-side override; R03's ping interval is per-request overridable.** `tools/server/server-context.cpp:1591-1594` (`if (decision.type
!= COMMON_DECISION_TYPE_NONE && !params_base.cache_ram_explicit) { … params_base.cache_ram_mib = 0; }`) forces the prompt cache to 0 for a *decision* model unless
`--cache-ram` was given explicitly (`common/arg.cpp:1691` sets `cache_ram_explicit = true`). The binary's own help says "set the maximum cache size in MiB (default: 8192,
0 for decision models, -1 - no limit, 0 - disable)". R04's cited value and line 644 are right; its decision cell carries no decision-model exception. R03:
`tools/server/server-schema.cpp:42` adds a per-request `sse_ping_interval` field, applied at `server-context.cpp:5392`. Neither reaches K2 alone — the values and lines
are correct. Separately, the counter's H1 check passes on a number its own help block qualifies: `help_default()` takes the first `default:\s*(-?\d+…)` in the block, i.e.
`8192`, while the same block continues "0 for decision models" — a calibration observation about the frozen counter's reach, not a row defect.

**NOTE — Ollama: keep-alive has a per-request path; the env rows name the only env readers.** `server/sched.go:555-558` (`sessionDuration := envconfig.KeepAlive(); if
req.sessionDuration != nil { sessionDuration = req.sessionDuration.Duration }`) lets a per-request `keep_alive` override the 5-minute default — field `api/types.go:97`
(`KeepAlive *Duration`), plumbed at `server/routes.go:551`. R10's cell ("the keep-alive that applied to a given model is not inferred from elapsed time") is consistent.
`OLLAMA_KEEP_ALIVE` is read at exactly one place (`config.go:131`), `OLLAMA_NUM_PARALLEL` at `:277`, `OLLAMA_MAX_QUEUE` at `:281` — the table's env rows name the only
readers of those variables. `OLLAMA_MAX_LOADED_MODELS` (`config.go:279`, default 0) and `OLLAMA_CONTEXT_LENGTH` (`config.go:230`) are env defaults the table does not
carry; they are outside C1's eight bound parameters, so their absence is not a defect against the predicate. And `server/sched.go:540` (`numParallel :=
max(int(envconfig.NumParallel()), 1);`) plus `:544-546` (`if !completion { numParallel = 1 }`) and `:550-552` clamp `NumParallel` down to 1 for embeddings and for a list
of model families (mllama, qwen3vl, qwen35, …), so R12's default holds a fortiori.

**NOTE — no post-parse override exists for `timeout_read`/`timeout_write` or `sleep_idle_seconds`.** The exhaustive `tools/server/` sweep yields only the sites quoted
above. `timeout_read/write` are set solely by `arg.cpp:3563-3564` and consumed at `server-http.cpp:217-218` (`set_read_timeout` / `set_write_timeout`).
`sleep_idle_seconds` is set only at `arg.cpp:3831` and consumed at `server-context.cpp:5221` and `:5604`. Each option also carries an env twin — `arg.cpp:1693`
`LLAMA_ARG_CACHE_RAM`, `:2523` `LLAMA_ARG_N_PARALLEL`, `:3323` `LLAMA_ARG_PORT`, `:3566` `LLAMA_ARG_TIMEOUT`, `:3573` `LLAMA_ARG_SSE_PING_INTERVAL`, `:3669`
`LLAMA_ARG_MODELS_MAX` — the argv-free path a registry row must cite, which R01's cell names explicitly.

## Deliverables

- `.ufo/waves/round-92/w1/out/SC01SourceReopen/receipts.txt` — 262 lines: fetch digests (2 transports), SOURCES anchors, independent binding re-check, exact line dump, vLLM reader proof, preset sweep, post-parse assignment sweep, `--help` blocks, lane-counter run, uptime.
- `.ufo/waves/round-92/w1/SC01SourceReopen.md` — this report.

Nothing else written; scratch removed. No tools installed or upgraded (none needed). For the non-author reviewer (K2 input, not my judgment): R08's flat `4` vs the role-conditional resolution; R04's decision-model `cache_ram_mib = 0`; R01's AIP_HTTP_PORT / ephemeral / router-child port paths; R03's per-request `sse_ping_interval`; and
the eleven arg.cpp presets re-setting `port`/`n_parallel`.

VERDICT: partial — all 15 rows bind to the live sources at their stated lines with digests matching SOURCES (re-verified independently over two transports) and the
disclosed V7 limit resolves in the table's favour; but four override classes the table misses (role-conditional auto slot count, the decision-model cache override, the
AIP/ephemeral/router-child port paths, and eleven arg.cpp presets re-setting port and n_parallel) remain unrepresented and need a non-author K2 reading.
