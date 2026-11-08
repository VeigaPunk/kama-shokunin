# SC01SetterSweep — K2 hunt for C2 (round 94, lane kama-shokunin)

## Scope

Independent K2 hunt: find every way the listen port or slot count of a llama-server process
can be set or changed that is **not** a population row of `SKILL.md`
`## Listen port and slot-count setters (round 94 revision)`, and say whether it changes what
R18 (port) or R19 (n_parallel) state.

Read-only in the lane except my out dir and this report. No tool installs (no tooling needed
beyond the pre-existing pinned llama.cpp b12177 build and coreutils). No delegation.

Revisions / artefacts measured (full hashes):
- base `e6f1dccecbad6dea44a129dabc928822c458e824`; measured M2 `6aa5fa6bd9bbf44c4b2ca3f1e2158e7d5aa92623`
  (`SKILL.md` + `tools/round94-setter-sweep.py` read from that commit).
- pinned archive `b12177.tar.gz` sha256 `f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13`
  (matches the counter's `TARBALL_SHA256`).
- pinned binary `/home/vgpnk/.local/opt/llama-b12177/llama-server`
  sha256 `ba272ee3446d9b98c9150c79667e6a8b217f25ee58ce0c6156cc96d2b5b362b0`.
- model `~/.cache/kama-shokunin/models/stories260K.gguf` (lane fixture).
- Host load during the run: `uptime` 23:42 → 141.70/145.15/135.77; 00:31 → 255.39/215.90/188.85.
  All timing-bearing claims below are structural (counts/argv), not wall-clock.

## Commands and outputs (exit codes)

```
git -C <lane> show 6aa5fa6b...:SKILL.md | awk '/^## Listen port and slot-count setters \(round 94 revision\)/,/^## [^L]/'
  -> exit 0; section at SKILL.md:2074-2210, 92 P-rows + R18 + R19
curl -sSL -o b12177.tar.gz https://codeload.github.com/ggml-org/llama.cpp/tar.gz/refs/tags/b12177
  -> exit 0; sha256 f50a52f4... (matches pin)
python3 tools/round94-setter-sweep.py --repo . --rev 6aa5fa6b... --work <scratch> --archive <scratch>/b12177.tar.gz
  -> exit 0
     SETTER_DECISION R18 bound bound / R19 bound bound
     SETTER_SWEEP 92 92 2 92 0 0 0 0 derived_checked=47 derived_disagree=0 decisions=2/2 pop=92 met=True
     SETTER_DIGEST f50a52f4ba45dd5b4b906db97cf230ce2e3b1117a0b9017411322ecba63eea13
# my own population re-derivation (same POP_RE/CFG/ENTRY as the counter, plus a wide setter scan)
python3 pop.py   -> exit 0; POPULATION_N 92 (identical set to the counter's)
python3 outside.py -> exit 0; 108 wide-pattern hits outside the population under common//tools/
# behavioural probes (each: fresh pinned llama-server/llama-cli, own free loopback port, killed)
bash exp1.sh  -> exit 0  (config.ini port, argv override, no-config)
bash exp3.sh  -> exit 0  (config.ini section scope; cli slot count x3)
bash exp4.sh  -> exit 0  (router child slot count: default / --parallel 3 / env)
bash exp5.sh  -> exit 0  (config.ini parallel/port/env-name key; cli via config.ini)
bash exp6.sh  -> exit 0  (router --embd-gemma-default; cli --parallel 0)
bash exp7.sh  -> exit 0  (router child argv + slot count: env5 / base / --parallel 7)
bash exp8.sh  -> exit 0  (config.ini -> router child; models-preset parallel -> child; AIP env -> child)
bash exp9.sh  -> exit 0  (AIP env on router: router + child ports)
bash exp10.sh -> exit 0  (AIP env on router: child bind failure)
bash exp11.sh -> exit 0  (config.ini < env < argv precedence)
bash exp12.sh -> exit 0  (models-preset INI port vs router free port; argv>env>file)
bash exp13.sh -> exit 0  (AIP_HTTP_PORT vs argv vs config.ini)
bash exp14.sh -> exit 0  (cli --parallel -1 and --parallel 0)
bash exp15.sh -> exit 0  (AIP_HTTP_PORT non-numeric, with and without AIP_MODE)
```
Scratch `/fast/scratch/hyaku/kama-r94/SC01SetterSweep` removed at the end (`rm -rf`, exit 0).
No stray processes left; the only llama-server running is the operator's pre-existing PID 1505
on 127.0.0.1:1234 (never contacted, never signalled).

## Findings

### F1 — BLOCKER: R19 gives no slot count for the `cli` and `router-child` entries, and the section's only prose for `cli` ("with 1 slot") is falsified

R19's entry cell is `server+shared`; the section's `Entry` taxonomy also defines `cli`
("llama-cli's embedded server") and `router-child`. R18 covers `cli` and `router-child` for
**port**; R19 covers neither for **slot count**. The only prose is SKILL.md:2097-2098:

> "`llama-cli` runs an embedded server on a free port with 1 slot (`tools/cli/cli-server.h:35-44`, S606, S612), ignoring the parsed `params.port`."

Measured (receipts `exp3_cli_v_*`, `exp14_*`, `exp5_c_cfg_parallel.log`), the cli embedded
server's slot count is **not** 1 in general:

| cli invocation | embedded server |
|---|---|
| default | `n_slots = 1` |
| `--parallel 4` | `n_slots = 4` |
| `LLAMA_ARG_N_PARALLEL=6` | `n_slots = 6` |
| config.ini `[default] parallel = 5` | `n_slots = 5` |
| `--parallel -1` | `n_parallel is set to auto, using n_parallel = 4` → `n_slots = 4, kv_unified = 'true'` |
| `--parallel 0` | `n_slots = 0` |

Route (the carrier is **not** a population row):
- `tools/cli/cli-server.h:43` — `common_params server_params = params; // copy`
  (whole-`common_params` copy; only `.port` is overwritten on the next line). Not in the
  counter's population: the pattern needs a `port =`/`n_parallel =` token or a config/entry
  anchor, and this line has none.
- `common/arg.cpp:2529` — `params.n_parallel = value;` (the non-server `--parallel` lambda,
  row P16, entry `other`) writes the CLI's own `params.n_parallel`; the copy then carries it
  into the embedded llama-server, where `tools/server/server.cpp:126` (`if (params.n_parallel < 0)`)
  and `:129` (`params.n_parallel = 4;`) decide slots, realised at
  `tools/server/server-context.cpp:1489` — `for (int i = 0; i < params_base.n_parallel; i++) {`
  (that file has **zero** rows in the population).

Router-child entry, same defect class (receipts `exp7_rt_par7.log`, `exp7_rt_env5.log`,
`exp8_e1_cfg_child.log`, `exp8_e2_preset_par.log`): child slot count measured 4 (auto,
`kv_unified = 'true'`), 7, 5, 6, 9 — set by the router's argv, the router's inherited env,
config.ini, and the `--models-preset` INI. Carriers, none of them a population row:
`tools/server/server-models.cpp:400` — `base_preset(ctx_preset.load_from_args(argc, argv)),`
and `:774` — `preset.merge(base_preset);`, then `common/preset.cpp:37`
— `std::vector<std::string> common_preset::to_args(const std::string & bin_path) const {`
renders the child's argv. The child argv in `exp7_rt_par7.log` literally shows `--parallel 7`.

Does it change R18/R19? **Yes.** R19 is the decision a registry row cites for slot count; it
is silent for two of the section's own entries, and the prose that stands in for them ("1
slot") is wrong in the general case. R19's own words "the router role keeps auto and resolves
no count" describe the router process, not the router-child, which R19 never covers.

### F2 — BLOCKER: R18 covers the router-child's port but not that the child inherits the router's env, so the child's effective port is not the router-assigned free port

R18 lists `AIP_MODE=PREDICTION` (`AIP_HTTP_PORT`, else 8080) and "a router child's
`LLAMA_ARG_PORT` free port" as port setters without precedence. Measured:

- `exp10_aip.log` — router with `AIP_MODE=PREDICTION AIP_HTTP_PORT=18230`: the router bound
  18230; the **child** then logged
  `Google Cloud Platform compat: overriding server port 39547 with AIP_HTTP_PORT 18230`
  followed by `couldn't bind HTTP server socket, hostname: 127.0.0.1, port: 18230`
  → the child never starts. The child inherits the router's whole environment
  (`tools/server/server-models.cpp:288` `get_environment()` → `:399` `base_env(get_environment()),`
  rows P72/P76, entry `router`, effect `copies`), so `AIP_HTTP_PORT` reaches the child and
  overrides the free port the router assigned (row P74).
- `exp13_i1_aip_vs_argv.log` — `AIP_HTTP_PORT` beats **argv**: `--port 18260` + `AIP_HTTP_PORT=18262`
  → `listening on http://127.0.0.1:18262`; `exp13_i2` shows the same against config.ini.

The AIP override itself is row P66 (`tools/server/server-http.cpp:125` — `port = gcp.port;`,
entry `server`, condition "env `AIP_MODE` equals `PREDICTION`"), and P62
(`tools/server/server-http.cpp:96` — `port = std::stoi(getenv("AIP_HTTP_PORT", "8080"));`).

Does it change R18/R19? **Yes.** R18 asserts the router-child's port is the router's free port
(P74/P82) and lists the AIP override as a separate setter; measured, the child inherits the
AIP env and its port becomes `AIP_HTTP_PORT`, colliding with the router and failing to bind.
A registry row citing R18 for "the router child's port" would be wrong in exactly this
deployment.

### F3 — DEFECT: the config.ini route applies only the `default` and `*` sections to the process's own params; the prose overstates it

SKILL.md:2094-2095:

> "A `port` or `parallel` line in a user config.ini therefore sets the listen port or slot count just as `--port`/`--parallel` do, and argv still beats env beats the file."

Measured (`exp3_srv_cfg_*.log`): only the `default` and `*` sections reach the process params;
a named section does not.

| config.ini | server bound |
|---|---|
| `[default] port = 18081` | 18081 |
| `[*] port = 18084` | 18084 |
| `[other] port = 18083` | **9931** (default; the line was ignored) |

Code: `common/arg.cpp:764` (`global.apply_to_params(params);`) and `:767`
(`it->second.apply_to_params(params);`) — only the `*` global and the `default` section are
applied; other sections become per-model presets. The precedence half of the prose is correct
(`exp11`: file 6 → env 7 → argv 3; `exp12`: argv 3 > env 7 > file 6).
Additional scope limit: `port` is not even a known key for the CLI example (`--port` is
registered only under `LLAMA_EXAMPLE_SERVER`, `common/arg.cpp:3318/3323`), so a config.ini
`port` line never reaches llama-cli.

Does it change R18/R19? Partly — R18/R19's decision text names "a config.ini `port` line" /
"a config.ini `parallel` line" as setters; that is right for `[default]`/`[*]` and wrong for
named sections, so the decision as written is not usable as a registry rule without the
section qualifier.

### F4 — NOTE: `--parallel 0` is refused on the server branch but not on the non-server branch, and the copy carries 0 into the embedded server

`common/arg.cpp:2519` — `throw std::invalid_argument("error: invalid value for n_parallel\n");`
(server branch, row P13) vs `common/arg.cpp:2529` — `params.n_parallel = value;` (non-server
branch, row P16, no refusal). Measured: `llama-server --parallel 0` → `error: invalid value for
n_parallel` (exit 1, `exp5_s_cfg_parallel0.log`); `llama-cli --parallel 0` → the embedded server
runs `n_slots = 0` (`exp6_cc_parallel0.log`). The section documents the refusal for the server
branch only; the cli entry's row P16 carries no such caveat.

### F5 — NOTE: the file that materialises the slot count has no rows at all

`tools/server/server-context.cpp` contributes **zero** rows to the population (my re-derivation:
no `server-context` line in the 92-line population). The slot count is realised there:
`:1489` — `for (int i = 0; i < params_base.n_parallel; i++) {` and reported at
`:5697` — `{ "total_slots",                 params.n_parallel },`, over
`params_base = params;` (`:1213`). So the section never shows a row proving that
`n_parallel` *is* the server's slot count; "slot count" appears only in prose.

### F6 — NOTE: `AIP_HTTP_PORT` is parsed unconditionally, so a non-numeric value aborts any server

`tools/server/server-http.cpp:96` — `port = std::stoi(getenv("AIP_HTTP_PORT", "8080"));` runs in
the `gcp_params` constructor, i.e. on every start regardless of `AIP_MODE`
(`exp15_j1_non_numeric_no_mode.log`: `terminate called after throwing an instance of
'std::invalid_argument'  what():  stoi` — the process aborts; `exp15_j2` same with
`AIP_MODE=PREDICTION`; `exp15_j3`: numeric value without `AIP_MODE` is harmless, port stays on argv).
P62's condition text ("applied only under `AIP_MODE=PREDICTION`") describes the *effect*, not
the *parse*, which is unconditional.

## Deliverables

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/SC01SetterSweep.md`
- Receipts (36 files: every behavioural log quoted above, plus `pop.txt` and `counter.out`):
  `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/out/SC01SetterSweep/receipts/`
- Scratch removed; no tool installs; no lane file outside my out dir was modified.

## Verdict

The counter still passes (92/92 bound, R18+R19 bound, `met=True`), and the section's *row
mechanics* are sound, but the section's decisions do not state the slot count for two of its own
entries and the prose standing in for them is measurably wrong, and R18's router-child port
claim does not survive the env inheritance the section itself documents. F1 and F2 are K2
material for the C2 claim.

VERDICT: partial — the round-94 setter section passes its counter but omits the `cli`/`router-child` slot counts and the router-child port precedence, both falsified by measurement on the pinned b12177 build.
