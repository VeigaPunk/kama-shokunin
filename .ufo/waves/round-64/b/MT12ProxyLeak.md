# MT12ProxyLeak — round 64, wave b, attack item C1 (environment and network)

Seat: MT12ProxyLeak (leaf, advisory; no subagents; no verdict on the claims; no commit to the lane).
Judged on: operability. Milestone: falsify C1 binding.
Tip under test: `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a` (freeze commit).
Instrument under test: `tools/round64-c1-counter.py` at the freeze, sha256 `b69c4b075f36b12fe275869da056fe6debe49db45bdf68c53d0eb4e8cbb12c84`; tool `tools/kama-completion-live.py` sha256 `a0c26e14184d664bef75013aac6f1c2a7bb47881eb4bf372b5bb70a26861423c`.
Scratch clone: `/fast/scratch/hyaku/kama-r64/b/MT12ProxyLeak/clone` (all edits and commits there only; scratch removed at yield, receipts copied to `out/`).

## Result in one paragraph

The honest tip is robust to the environment, network, cwd, PATH and namespace perturbations I applied: every perturbed run of the honest tip gave `met=True` except one read-only-TMPDIR run (1 of 14 such runs, flake, see D4); the 13 repeats under the same condition all passed. The C1 binding does **not** hold on one axis: the held child's **initial environment** is only checked for `LD_*` and `GLIBC_TUNABLES`. A tool that adds a benign `LLAMA_ARG_*` variable to the pinned server's environment (one line, `LLAMA_ARG_LOG_COLORS=0` or `LLAMA_ARG_CORS_ORIGINS=*`) passes all 76 controls with `met=True`. That contradicts the frozen predicate's "initial environment ... the pinned set". A six-line tightening of `bind_env` to the counter's own five-key set kills it while the honest tip stays `met=True` 76/76. Two of the environment variants I was asked to run (proxy, `LD_LIBRARY_PATH` from the caller) never reach the tool or the server, so their `met=True` says nothing about the binding (see §3).

## 1. Procfs observations that decide each run

| Observation (counter-side, procfs or probe) | Where in counter | What decides |
|---|---|---|
| Holders of the run-port listener: `/proc/net/tcp{,6}` inode -> `/proc/<pid>/fd` | `listeners()`, `holder_pids()` -> `bind_holders` | Only pids holding the run-port LISTEN socket count; a second pinned server on another port is not a holder |
| `/proc/<pid>/environ` **keys** | `holder_record()` -> `bind_env` | Only `LD_*` and `GLIBC_TUNABLES*` are rejected; every other key passes (the gap, §4) |
| `/proc/<pid>/exe` re-hashed, `/proc/<pid>/cmdline` | `bind_exe`, `bind_argv` | pinned sha at the counter's chosen path (realpath of PATH hit, or `~/.local/opt/llama-b11755/llama-server`) |
| `/proc/<pid>/stat` ppid chain and start ticks | `bind_ancestry`, `hold_fresh` | the tool pid must be an ancestor; start ticks >= tool start |
| `/proc/<pid>/maps` | `bind_maps` | mappings under the server dir must hash to the LIBS table; `/usr/lib`, `/lib` prefixes are not hashed (note N1) |
| Probe answers from the held child vs. a reference pinned server (counter-started) | `probe()`, `score()` | answer agreement; unaffected by an env var that changes no output |
| Counter-observed teardown (`pid_gone`, port closed) | `witness_run()` | after the counter's own release |

## 2. Runs (all at the freeze tip unless stated; full stdout/stderr under `out/MT12ProxyLeak/variants/`, `procfs/`, `flake/`)

Verdict lines below are the counter's own one-liner with the `missing_families` and `families[...]` tails elided (the full lines are in the out files; the elided tail is only per-family counts). `met=True` for an honest run means no false reject.

| Run | Perturbation | Counter one-liner (`met=`) | Decider (procfs or probe) | Classification |
|---|---|---|---|---|
| base | default env, freeze tip | `tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 eval_selftest=3/3 errors=0 met=True` | all bind checks true | control |
| V1 proxy | `HTTP_PROXY`, `http_proxy`, `HTTPS_PROXY`, `ALL_PROXY=socks5h://192.0.2.1:1` (unreachable), `NO_PROXY=''` | `... 76/76 ... errors=0 met=True` | child environ keys `HOME,LANG,PATH`: no proxy key reaches the child; counter opener is `ProxyHandler({})` | **vacuous** (§3); not a defect |
| V2 `LD_LIBRARY_PATH=/nonexistent/lib` in caller env | `... 76/76 ... errors=0 met=True` | child environ keys `HOME,LANG,PATH`: the variable is dropped by the counter's five-key filter before the tool starts | **vacuous** (§3); not a defect |
| V3 TMPDIR = read-only dir (`chmod 555`, verified unwritable) | `... 75/76 of 76 families_exact=0 ... errors=0 met=False` (stalehold/stale_old escape, nfails=24) | child environ `HOME,LANG,PATH`; the escape needs `hold_fresh` absent from the failure set (see D4) | **flake** (1 of 14 read-only-TMPDIR runs; §5 D4) |
| V3b rerun of V3 | same | `... 76/76 ... errors=0 met=True` | rerun passed | flake confirmed as intermittent |
| V4 cwd `/`, absolute args | `... 76/76 ... errors=0 met=True` | unchanged bindings | cwd-independent |
| V5 cwd = scratch root, relative `--repo`/`--work` | `... 76/76 ... errors=0 met=True` | unchanged | cwd-independent |
| V6 PATH without `~/.local/bin` | `... 76/76 ... errors=0 met=True` | `command -v llama-server` under that PATH: none, so the fallback `~/.local/opt/llama-b11755/llama-server` is used; that path is also what `~/.local/bin/llama-server` resolves to (symlink), so this is the same file, not a second binary | fallback exercised; passes |
| V7 second pinned llama-server (started by this seat, pid 2020393, other port), PATH intact | `... 76/76 ... errors=0 met=True` | run-port holder set = {hold pid} only; the foreign server is not a holder | not a defect; the analogous forging tool is killed (F4) |
| V7b as V7 with PATH without `~/.local/bin` | `... 76/76 ... errors=0 met=True` | same | not a defect |
| V8 `unshare -rn` (user+net namespace, `ip link set lo up`) | `... 76/76 ... errors=0 met=True` | `/proc/net/tcp` of the namespace; same bindings | passes; plain `unshare -n` is EPERM (H1) |
| Diagnostic copies (output-only instrumented counter) | `diag/`, `procfs/` | environ keys `[HOME, LANG, PATH]` for the held pid in D0, D2 and D3 | observation confirmed |
| Foreign listener on the released hold port (404 answers; diagnostic copy) | `... met=True` | both stale scenarios received the 404s; the verdict stayed True | D4 mechanism test, negative |
| Widened write-to-backdate window in stale forger (0.6 s; diagnostic copy) | `... met=True` | stale scenario mtime observed fresh by the counter (`OBSERVE`), `hold_fresh` still failed (no holder in snapshot) | D4 mechanism test, negative |

Counts over the seat's counter runs in `out/MT12ProxyLeak/summary.tsv`: 40 rows, 36 `met=True`, 4 `met=False` (V3 flake; F3 contrast; F-tighten-forged; F4 second-server forgery). Read-only-TMPDIR runs: 14 (V3, V3b, four diagnostic, eight repeats), 13 `met=True`, 1 `met=False`. Default-env runs: 4 repeats plus base and V0, all `met=True`.

## 3. The proxy and `LD_LIBRARY_PATH` variants are vacuous (counter test design, not a defect)

The counter starts the tool and the reference server with `env = {k: v for k in os.environ if k in _TOOL_ENV_KEYS}`, where `_TOOL_ENV_KEYS = ('PATH','HOME','LANG','LC_ALL','TMPDIR')`. The counter's own HTTP opener is `urllib.request.build_opener(ProxyHandler({}))`, so proxy variables are ignored by design. The consequence, observed on procfs (`diag/D2`, `diag/D0`, `diag/D3-*`): the held pid's `/proc/<pid>/environ` keys are exactly `HOME, LANG, PATH` in every run. No proxy variable and no `LD_*` variable from the caller ever reaches the child, so V1 and V2 do not exercise a proxy or a loader injection; they only show that the filter works. A loader injection that does reach the child, put there by the tool, is killed (F3, §4).

## 4. Forgeries and contrast controls (the valuable part)

All forgeries are one- or two-line edits to `tools/kama-completion-live.py` in the scratch clone, committed there, and scored by the freeze counter run from the clone path (`--repo` clone, `--tip` = the forged commit). Patches are in `out/MT12ProxyLeak/patches/`.

**F1, SURVIVED — `LLAMA_ARG_LOG_COLORS` in the held child's environment.** One added line after the env allowlist (`tools/kama-completion-live.py`, after line 324):
```
        env['LLAMA_ARG_LOG_COLORS'] = '0'
```
Commit `dbc1965203cbc7c5d3a9fd19a24a8c871af46575`. Counter one-liner:
`tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 eval_selftest=3/3 errors=0 met=True`
Decider: the held pid's `/proc/<pid>/environ` keys are `['HOME','LANG','LLAMA_ARG_LOG_COLORS','PATH']` (diagnostic copy, `out/.../patches`, `procfs/`). The counter reads these keys (`holder_record`) and `bind_env` tests only `k.startswith('LD_') or k.startswith('GLIBC_TUNABLES')`, so it passes. The verdict is "met" while the predicate's "initial environment ... the pinned set" is false. The variable is log-only and changes no answer, so the probes cannot see it; this is a pure binding-scope survivor.

**F2, SURVIVED — `LLAMA_ARG_CORS_ORIGINS=*` (network-facing).** Same one-line form. Commit `4176603f5f60aa78226213ec23d5dc6fe3750c1c`. One-liner: `... errors=0 met=True` (identical shape to F1). The same procfs decider applies; I did not dump the environ keys for this run (same tool line, same filter), so the environ claim for F2 rests on F1's observation. The CORS wildcard widens the browser-reachable surface of the answering process, which the counter does not look at at all.

Why the llama.cpp `LLAMA_ARG_*` names matter: `strings` on the pinned `libllama-common.so.0.7.0` shows the server reads `LLAMA_ARG_*` (for example `LLAMA_ARG_LOG_COLORS`, `LLAMA_ARG_CORS_ORIGINS`, `LLAMA_ARG_CACHE_PROMPT`, `LLAMA_ARG_API_PREFIX`) as defaults for flags. An argv flag overrides its env twin, so only env names without a matching argv flag in the counter's `argv` are live channels; F1 and F2 are such names.

**F3, KILLED (contrast) — `LD_LIBRARY_PATH=/usr/lib` put into the child by the tool.** Commit `cce32ea544be3d682a1cf6cc46dea1d3763e143a`. One-liner:
`tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 ... eval_selftest=0/3 errors=1 met=False`
`error: live: ["bind_env"]`. Decider: `LD_LIBRARY_PATH` present in `/proc/<pid>/environ` keys. So the environ check works when the key is in its scope; F1/F2 pass only because the scope is `LD_`/`GLIBC_TUNABLES` only.

**F4, KILLED — second pinned llama-server used as the held child.** The seat's own second pinned server (pid 1515283, port 43509, started with the pinned binary, env `PATH,HOME`, still alive during the run). The tool's hold.json advertises that port and pid instead of its own child (`kama-completion-live.py` lines 536–537 read `second.json`); the tool's own child is left running. Commit `e5fea1985a11b61c62a83eabed71ad166ca41009`, freeze counter:
`tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 ... eval_selftest=0/3 errors=1 met=False`
`error: live: ["bind_ancestry", "bind_claim", "hold_fresh", "live_pid", "live_port", "teardown_observed"]`
Decider: `bind_ancestry` (the second server's ppid chain does not contain the tool pid) and `hold_fresh` (the second server's start ticks predate the tool, so it is not started after the tool). `/proc/net/tcp` on port 43509 and the holder set are correct (it is a real, pinned, answering process); the stacking is entirely procfs ancestry and start time, so a pinned server started outside the tool cannot be laundered in as its child.

**F-tighten, KILLED — proposed counter fix.** In a clone copy of the counter, `bind_env` is tightened to the counter's own spawn key set:
```
    def env_ok(h):
        keys = h.get('environ_keys')
        if keys is None:
            return False
        if any(k.startswith('LD_') or k.startswith('GLIBC_TUNABLES') for k in keys):
            return False
        return set(keys) <= set(_TOOL_ENV_KEYS)
    out['bind_env'] = bool(hs) and all(env_ok(h) for h in hs)
```
Commit `836a32373d1da77ad5ec6d3a0ce44a49980cbf14` (freeze tool, honest): `tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 eval_selftest=3/3 errors=0 met=True` (no false reject). Commit `5bdf25952018a2ce68c0f3dfea92e0e0895e0be9` (F1 forgery on tightened counter): `tool_present=1 live_ok=0/1 controls_targeted=0/0 of 76 families_exact=0 ... eval_selftest=0/3 errors=1 met=False`, `error: live: ["bind_env"]`. Patch in `out/MT12ProxyLeak/patches/counter-bind_env-tightened.patch`. This is a candidate change for the L1 to weigh under the freeze's amendment rule; I have not applied it to the lane.

## 5. Defects, classified

- **D1 — counter (predicate-to-code gap). SURVIVED F1, F2.** The binding grades only `LD_*`/`GLIBC_TUNABLES` in the held child's environment; the frozen predicate says the initial environment is "the pinned set". Minimal fix: F-tighten (verified above: honest 76/76, forgery killed). The tool-side env channel (D3) is the source of the forgeries; the counter is the gate that should catch it.
- **D2 — counter (test design). V1 and V2 do not test what their names say.** The counter's five-key spawn filter means proxy and loader variables never reach the child, so `met=True` for them proves nothing about proxy or loader handling. The loader case is only tested through the tool-side injection (F3). Recommend the L1 drop the two variants from any "env robustness" claim or replace them with tool-side injections.
- **D3 — tool (unpinned env allowlist).** `kama-completion-live.py` lines 322–324 forward `LD_LIBRARY_PATH`, `LLAMA_ARG_THREADS` and `XDG_CACHE_HOME` from the tool's own environment into the answering child. Run outside the counter, a human's `LD_LIBRARY_PATH` or `LLAMA_ARG_*` reaches the pinned server unchecked except for the `LD_` subset. Minimal tool-side fix: trim the allowlist to `PATH, HOME, LANG, LC_ALL` (the counter's set), which makes D1 unnecessary for these keys.
- **D4 — counter, unexplained flake. V3 escape.** One run in 14 under read-only TMPDIR: `stalehold/stale_old` expected `hold_fresh`, escaped, nfails=24. The official counter prints only the first eight failing checks (`fails=[:8]`); I could not capture the full set for that run. The stale scenarios have live cap 99 (`credit(..., 99, ...)`), so an escape is possible only when `hold_fresh` is absent from the failure set, which requires the counter's snapshot to contain a holder on the released hold port with start ticks >= the tool's and mtime > t0. Reproduction attempts, all `met=True`: eight more read-only runs, four default runs, a diagnostic copy with a foreign 404 listener on the released port (the stale scenarios did receive the 404s), and a diagnostic copy widening the forger's write-to-backdate window to 0.6 s (the counter observed a fresh mtime, `OBSERVE`, and `hold_fresh` still failed because the snapshot had no holders). The mechanism is therefore unconfirmed. Classification: counter (the stale controls reuse the hold port the counter has just released, so their result depends on port-table state at a moment outside the counter's control); trigger unknown, plausibly concurrent live servers on the host (other seats were running llama-servers during this window). Fix candidate: point the stale scenarios at a port the counter has never bound (a fresh `free_port()` with nothing listening) so the scenario depends on no released state. Logged as data; not a pass.
- **D5 — host.** Plain `unshare -n` returns `Operation not permitted` (no `CAP_SYS_ADMIN`); `unshare -rn` (user+net namespace with `ip link set lo up`) works and gives `met=True` (V8). `/etc/ld.so.preload` is absent on this host (checked). `~/.local/bin/llama-server` is a symlink into `~/.local/opt/llama-b11755/`, so the PATH-less fallback resolves to the same file and does not test a second, independent copy of the pinned binary.
- **N1 — counter note, not exercised (no evidence of exploitability).** `maps_ok` accepts any mapping whose raw path begins with `/usr/lib/`, `/lib/`, `/usr/lib64/` or `/lib64/` without hashing it, and `SYSTEM_PREFIXES` is tested on the unresolved string. A root-writable system library could sit there; a user-level forgery cannot place one without `LD_*` (which `bind_env` rejects). Recorded for the L1; not a finding against C1 as frozen.

## 6. Mutant table (KILLED / SURVIVED)

| Mutant / forgery | Expected | Result | Decider |
|---|---|---|---|
| F1 `LLAMA_ARG_LOG_COLORS` in held child env | killed | **SURVIVED** (`met=True`) | environ key (not in scope of `bind_env`) |
| F2 `LLAMA_ARG_CORS_ORIGINS=*` in held child env | killed | **SURVIVED** (`met=True`) | same mechanism (environ key) |
| F3 `LD_LIBRARY_PATH` in held child env (contrast) | killed | KILLED (`live_ok=0`, `bind_env`) | environ key `LD_LIBRARY_PATH` |
| F4 hold.json points at a second pinned server | killed | KILLED (`live_ok=0`, `bind_ancestry`, `hold_fresh`) | ppid chain + start ticks |
| F-tighten (counter fix) applied to F1 | killed | KILLED (`live_ok=0`, `bind_env`); honest tip still `met=True` 76/76 | environ key set |
| Proxy env in caller (V1) | n/a (not a forgery) | `met=True` (vacuous) | environ keys `HOME,LANG,PATH` |
| LD_LIBRARY_PATH in caller (V2) | n/a | `met=True` (vacuous) | same |
| Read-only TMPDIR (V3) | honest passes | 1 of 14 `met=False` (flake, D4) | unknown; see D4 |
| Foreign 404 listener on released hold port | honest passes | `met=True` | probes; bind checks unaffected |
| Second pinned server, PATH intact / PATH-less | honest passes | `met=True` both | run-port holder set |
| `unshare -rn` | honest passes | `met=True` | (namespace; procfs view consistent) |

## 7. Tools and installs

No tool was installed, upgraded or removed. I used the host's `unshare` and `ip` (util-linux, iproute2). No pacman transaction was run. Nothing was written to `~/.local/bin` or any PATH directory; the second pinned server was started from `~/.local/bin/llama-server` (symlink into the opt install) and stopped by its own handle (exit 0). Other seats' llama-servers on ports 1234, 45669, 47743, 59487 and others were left alone.

## 8. Limits

- The forgeries F1, F2, F4 are one-tool edits, scored by the freeze counter with its own 76-control suite. They show the binding gap; they do not show that the claim as a whole is false, since the probes and the teardown checks still bind the answering process to a pinned server.
- F2's environ keys were not dumped; its verdict rests on F1's identical mechanism.
- D4 is unexplained. I did not establish the cause of the single escape; the instrumentation I added is output-only in scratch copies, and no lane source was changed.
- Instrumentation copies (`round64-c1-counter-diag.py` and its perturbed variants) were written with a small in-cell rewrite inside scratch only; they are not lane files. Their diff against the official counter is `out/.../patches/diag-copy-vs-official.diff`.
- I did not run the counter under a different user or on a read-only repo; the repo was only read via git blobs.

## 9. Evidence

`.ufo/waves/round-64/b/out/MT12ProxyLeak/`:
- `summary.tsv` — every counter run this seat, with `met`, `live_ok`, controls, errors (40 rows).
- `variants/` — stdout/stderr of each variant and forgery, including `forgeries/` outputs and `second.json`, `second-server-2.log`.
- `procfs/` — output-only diagnostic binding dumps (`*-binding.json`: holder pids, exe sha, environ keys, cmdline, ppid chain, maps, teardown).
- `flake/` — repeats, perturbation and timing runs for D4, with `OBSERVE` and `CREDIT` traces.
- `patches/` — `forgery-LLAMA_ARG_LOG_COLORS.patch`, `forgery-LD_LIBRARY_PATH-contrast.patch`, `forgery-second-pinned-server-hold.patch`, `counter-bind_env-tightened.patch`, `diag-copy-vs-official.diff`.

Final counter line (freeze tip, default env, `cd tools && python3 round64-c1-counter.py --repo <clone> --tip f6a4ea9a8b5a876d685b08e7e582ec0723412a4a --work <scratch>/work-base`; full line in `variants/base-tip-default-env.out`):

`tool_present=1 live_ok=1/1 controls_targeted=76/76 of 76 families_exact=1 missing_families=[] eval_selftest=3/3 errors=0 met=True`
