# RV02ThresholdRows — C2 kill rule K2 (semantic fit of the 14 threshold rows)

## Scope
Read all 14 rows of `SKILL.md` §Serving timeout and limit thresholds at M2 (3f317ecd211e80929c673e306e3230be287fdf20);
re-opened each pinned source myself (S593-S595) plus context, arg.cpp @ b12177, and usage sites; judged per row:
threshold name, value/unit, and whether the probe decision follows from the line or overreaches. Also checked
`corpus/knowledge/serving-thresholds.md` against the sources. Lane tree at HEAD=M2; `git status --porcelain`
shows only untracked `.ufo/waves/round-91/*`, `git diff --stat HEAD -- SKILL.md corpus tools tests` empty —
working-tree reads are M2 bytes.

## Commands and outputs (exit codes)
- `git -C <lane> rev-parse HEAD` → 3f317ecd211e80929c673e306e3230be287fdf20 (0).
- `curl -fsSL` raw.githubusercontent.com (GET, no creds): common.h, arg.cpp, config.go, envs.py, server.cpp
  (first try 404, retry 200, 32346 B), server-{context,http,stream,task,models-sched}.cpp, core_client.py,
  api_server.py, launchers/launcher.py, launchers/api_server/entry.py — all 0; 404s: ollama
  `scheduler/scheduler.go` (layout moved; not needed), vllm `entrypoints/utils.py` (moved to launchers/).
- `sha256sum` live fetches == SOURCES rows: S593 c3010a3c…73, S594 0b0ea669…95, S595 e963af06…94 (0).
- `grep -n` exact literals in fetches: all 14 rows' literals on the stated lines (common.h 464, 632, 634, 636,
  644, 669, 703; config.go 23, 130, 150, 277, 281; envs.py 26, 111) (0).
- Read `.ufo/waves/round-91/measured/c2.out`: `rows=14 bound=14 unbound=0 duplicates=0 engines=3
  fetch_failures=0 rev=3f31…` exit=0 — matches the frozen measurement.

## Per-row verdicts
| id | verdict | evidence beyond the row's own line |
|---|---|---|
| T01 port 9931 | holds | common.h:632; `--port` help prints default, env LLAMA_ARG_PORT (arg.cpp:3318-3323) |
| T02 3600 s | holds (NOTE-2) | common.h:634-635 (write=read); `-to/--timeout` sets both (arg.cpp:3560-3565); probe default 5 s is real (tools/kama-probe.sh:97,148) |
| T03 30 s ping | holds | ping emitted when silence >interval: server-context.cpp:5543-5557 sends `":\n\n"`, comment names undici clients |
| T04 8192 MiB | holds (NOTE-3) | common.h:644 `-1 = no limit, 0 - disable`; arg.cpp:1687-1692 |
| T05 -1 off | holds | comment "if >0, server will sleep" common.h:669; sleep disabled when negative server-context.cpp:5301; `--sleep-idle-seconds` rejects 0 and < -1 (arg.cpp:3825-3833); `router-sleeping` is a real probe code (SKILL.md:1861) |
| T06 4 | holds | common.h:703; "0 = unlimited" (arg.cpp:3664-3669); gate `models_max<=0 || count_running()<models_max` and LRU eviction (server-models-sched.cpp:86-88,197-200) |
| T07 1 | holds | common.h:464 "number of parallel sequences to decode" |
| T08 11434 | holds | config.go:20-23,41-42 fallback `127.0.0.1:11434`; EnvConfig :324 "(default 127.0.0.1:11434)" |
| T09 5 min | holds | config.go:126-130 "Negative…infinite. Zero…no keep alive. Default is 5 minutes."; env :325 "(default \"5m\")" |
| T10 5 min | holds | config.go:146-150 "Zero or Negative…infinite"; env :327 "How long to allow model loads to stall before giving up" |
| T11 1 | holds | config.go:276-277 "number of parallel model requests" |
| T12 512 | holds | config.go:280-281 "maximum number of queued requests" |
| T13 600 s | holds | core_client.py:739-750 poll, TimeoutError kills startup; socket bound before engine setup (launcher.py:396-398, race-avoidance comment), so inside the window the endpoint accepts TCP but serves no HTTP — "loading" is the honest read; consumed only after ready via entry.py:195 |
| T14 5 s | OVERREACH (minor) | envs.py:111 `= 5  # seconds`, registration comment 1142, consumed as uvicorn `timeout_keep_alive=envs.VLLM_HTTP_TIMEOUT_KEEP_ALIVE` (entry.py:153) |

## Findings
1. **NOTE (T14, overreach — no blocker):** decision sentence "a client that reuses one later gets a reset and
   must reconnect". The line establishes the 5 s idle close (uvicorn `timeout_keep_alive`), not the client-side
   symptom: a clean FIN/RemoteDisconnected is as likely as a RST. Proposed corrected text: "a client that reuses
   a pooled connection idle for over 5 s gets a failed first request (closed connection) and must reconnect,
   which is not a server fault." No row cell contradicts its source, so K2's misstate test is not met.
2. **NOTE (T02):** 3600 s is the per-read/per-write idle bound (comment "http read timeout in seconds"); a
   request with continuing progress is not hard-bounded to an hour. The decision's operative claim — a probe
   timeout is the probe giving up (probe 5 s vs server ≥1 h) — holds.
3. **NOTE (T04):** `cache_ram_explicit = false; // set by --cache-ram, decision models disable the cache
   otherwise` (common.h:645) and arg.cpp:1687 "(0 for decision models…)": for decision models the host-RAM
   prompt cache defaults off. The row's growth-toward-8-GiB diagnosis holds for ordinary models only.
4. **NOTE (T01 vs knowledge Limits):** T01 says "read the port from the unit argv" while the knowledge entry
   says "kama does not read service units". Consistent only if T01 addresses registry authoring (an operator
   action), not the probe. One clarifying word would prevent misreading. LLAMA_ARG_PORT (named in the row)
   also overrides argv-less defaults.
5. **NOTE (S593 descriptor):** SOURCES quote locator says "`common_params` lines 464-705" — that brackets all
   cited lines (first 464, last 703) but not the struct's own extent (opens at line 457). Cosmetic.
6. **Integrity (all hold):** every one of the 14 literals sits on exactly its stated line at the pinned tag;
   live sha256 of all three sources equals the frozen SOURCES digests; SOURCES rows are tier A, status mined,
   opened 2026-11-06 (K3: re-opened this review, no drift); knowledge-entry rules 1-5 verified line-exact
   (incl. "doc comment line 128" = config.go:128 and "comment line 1142" = envs.py:1142).

## Deliverables
- Report: `.ufo/waves/round-91/w1a2/RV02ThresholdRows.md` (this file; copy in `w1a2/out/RV02ThresholdRows/`).
- `w1a2/out/RV02ThresholdRows/sha256s.txt` — fetched URLs, digests, 404s, cited-line grep results.
- Scratch `/fast/scratch/hyaku/kama-r91/RV02ThresholdRows/` removed before yield.

VERDICT: holds — 14/14 rows' name, value/unit and decision match their pinned lines at M2; one minor
overreach (T14 "reset" mechanism) with proposed correction; zero misstates, C2 K2 passes.
