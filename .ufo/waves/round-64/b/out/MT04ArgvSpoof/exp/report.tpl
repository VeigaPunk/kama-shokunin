# Round 64 · wave b · seat MT04ArgvSpoof · C1 argv-spoof falsification

Scope: attack item C1 (argv is spoofable, S532 limit). Tip under test `f6a4ea9a8b5a876d685b08e7e582ec0723412a4a` (freeze). Scored only with the committed, unmutated `tools/round64-c1-counter.py`; every forged tool was committed in my scratch clone and run against that counter (`python3 tools/round64-c1-counter.py --repo <clone> --tip <commit> --work <scratch>/work/<name>`). Leaf seat: no subagents, no edits outside my scratch and this report/out path. Judged on: operability.

## 1. Result

- The frozen tip is green: `met=True` twice (base run and an independent re-run in a fresh work dir).
- **Forgeries that the binding rejects** (the held process is not the pinned server): python cmdline spoof with `exec -a` or ctypes argv rewrite (both KILLED by `bind_exe` and `bind_maps`); duplicate `--port`, duplicate `--model` (long form), `--alias a,b` (KILLED by `bind_argv`); a short `-m` copy of the model (KILLED by `bind_maps`); a second `--port` with a different value (KILLED by the tool's own run-port health wait).
- **Forgeries that SURVIVE the binding** (the counter prints `met=True`, or `live_ok=1/1` with all eight bind checks true):
  - **B4** extra short `-a other-alias` flag (argv not compared as a set);
  - **B5** extra `--no-slots` flag;
  - **R1** extra `--models-preset` flag: the held process is the pinned binary running in router mode with a preset file in the work dir (the answer still comes from the held pid);
  - **E1** extra environment key (`LLAMA_ARG_NO_WEBUI=1`);
  - **C2b** `sh -c '<server> ...; :'` with the tool reporting the grandchild as the holder (`live_ok=1/1`; the `met=False` on that line comes from a counter replay artifact, section 4).
- Expected pass, not a forgery: **C1** `sh -c 'exec <server> ...'` (same pid, the held process is the genuine server).
- The decider of the python spoof is the procfs exe observation (`/proc/<pid>/exe` = `/usr/bin/python3.14`, sha256 ≠ pinned) and, independently, the maps observation (`/usr/bin/python3.14` mapped, outside `SYSTEM_PREFIXES` and the server dir). Ablation below shows each alone is sufficient.
- Net C1 finding for L1: the counter binds the *identity* of the holder (exe, maps, holders set, ancestry) well, but it does not bind the *configuration*: `argv_ok` (round64-c1-counter.py lines ~421-433) reads four flags (`--port`, `--host`, `--alias`, `--model`) and never compares the full argv; `bind_env` (lines ~434-437) rejects only `LD_*` and `GLIBC_TUNABLES`. The frozen wording (freeze.txt lines 25-28: "its argv, initial environment and mapped files are the pinned set") is therefore not what the code checks. B4, B5, R1 and E1 are SURVIVED against that wording.

## 2. Baseline

Base run (fresh work dir, tip f6a4ea9a):
```
@@BASE@@
```
Independent re-run at the same tip (fresh work dir, `work/base2`): `@@BASE2@@`

## 3. Mutant table

| id | forgery (what the tool does) | decider (procfs observation or other) | verdict |
|---|---|---|---|
| A1 | python holds the run port; bash `exec -a <server> python3 fwd.py ...` so argv[0] is the pinned path; proxies to a genuine child | `/proc/<pid>/exe` = `/usr/bin/python3.14` (readlink + sha256 via the link); maps list `/usr/bin/python3.14` | KILLED by `bind_exe`, `bind_maps` (cmdline check `bind_argv` PASSED: the spoof works; the honest tool claim also fails `listener_holders_pinned` and `verdict`) |
| A2 | A1 + tool's own holder claim fabricated to the pinned exe | the same, plus the counter's exe vs claimed exe | KILLED by `bind_claim`, `bind_exe`, `bind_maps` |
| A3 | python rewrites its own argv area in place (setproctitle style, ctypes `memmove` over `/proc/self/stat` arg_start..arg_end) to the pinned argv; proxies to a genuine child | `bind_exe`, `bind_maps` as A1; `bind_argv` PASSED on the rewritten `/proc/<pid>/cmdline` | KILLED by `bind_exe`, `bind_maps` |
| A4 | A3 + fabricated holder claim | as A2 | KILLED by `bind_claim`, `bind_exe`, `bind_maps` |
| A5 | root: `prctl(PR_SET_MM, PR_SET_MM_EXE_FILE, fd(pinned))` to repoint the exe link | kernel refuses: EBUSY while the original executable mapping exists (exp/exe-spoof-root-test.txt) | NOT DEMONSTRATED; exe re-pointing needs the forger to unmap its own text first (INFERENCE, not tested) |
| B1 | `--port RUN` repeated with the same value | `bind_argv` (port list must be exactly one value) | KILLED |
| B2 | second `--port` with a different value (last-wins: server listens on the other port) | no procfs check reached: run port never listened; tool's wait_ready on run port fails | KILLED (`tool exited before hold.json`) |
| B3 | short `-m` pointing at a byte-identical copy in the work dir (argv `--model` still pinned) | `bind_maps`: the copy's mapping is outside server dir / pinned model path | KILLED by `bind_maps` |
| B6 | long `--model` repeated (copy in work dir) | `bind_argv` (model list length), `bind_maps` | KILLED |
| B7 | `--alias kama-completion-probe,other` | `bind_argv` (alias list must equal `[ALIAS]`) | KILLED |
| B4 | extra short `-a other-alias` appended | none: the four-flag projection ignores `-a`; the server ignores it too (alias-extra-flag-check.txt: `/v1/models` lists only the pinned alias) | **SURVIVED** (ineffective extra argv accepted) |
| C1 | `sh -c 'exec <server> ...'` (no extra hop) | none: same pid, genuine binary, argv identical | expected pass (genuine server, not a forgery) |
| C2a | `sh -c '<server> ...; :'`, tool reports the sh pid | the tool's own `listener_owned` check: receipt `setup_error` "listener on 37621 is not owned by child 1780986" (before the counter sees it) | KILLED by the tool, not by the counter |
| C2b | same wrapper, tool reports the grandchild as child and holder | `bind_ancestry` admits the hop (tool pid is in the 8-deep ppid chain at depth 2); `bind_holders`, `bind_exe` pass | **SURVIVED at the binding** (`live_ok=1/1`); printed `met=False` is forge-replay artifact (section 4) |
| B5 | extra `--no-slots` | none: argv projection ignores it | **SURVIVED** (met=True) |
| R1 | extra `--models-preset <work>/preset.ini`; preset = pinned model under the pinned alias; the router runs in-process (`pgrep -P` found no children) | none: no check reads the extra flag; the process, exe, maps and answers are the pinned binary's | **SURVIVED** (met=True) |
| E1 | extra environment key `LLAMA_ARG_NO_WEBUI=1` in the tool's env | none: `bind_env` checks only `LD_*`/`GLIBC_TUNABLES` (server effect of the key not verified) | **SURVIVED** (met=True) |

Ablations (which observation decides A1/A3; ablate.py, transcript in out/exp/ablation-transcript.txt, tool = A4 fabricated):
- Neutering `bind_exe` and `bind_claim` leaves only `bind_maps` failing: the maps observation alone rejects it.
- Neutering `bind_maps` and `bind_claim` leaves only `bind_exe` failing: the exe observation alone rejects it.
- Neutering all three crashes `build_controls` (StopIteration, see 4(iii)); a forgery survives only if exe and maps are both absent.

## 4. Counter-side defects seen while scoring (fail-closed, not survivals; for L1)

i. Forge replays are fuzzy textual patches (`patch -F3`). Any edit that moves lines in the run() block misplaces them: an early variant produced `forgeA-build/tools/kama-completion-live.py` line 305 IndentationError; another produced "patch did not apply" for forge-A/A2/B2. The three `forge` controls then go uncredited and `met=False` for reasons unrelated to binding. I worked around it with line-count-preserving edits (drive3.py): forge=3/3 restored for B4, B5, C1, R1, E1. C2b still reports forge=0/3 (patch did not apply).
ii. `witness_run` does not clear `hold/release` on a reused `--work`. A stale release makes a fake's hold return at once; the fake exits before the counter sees hold.json: `tool exited before hold.json`, 7 fake controls uncredited (detach, proxy, canned, stale_old, stale_future, preload, pathcopy). The live tool itself clears it (`prepare_witness_dir`), the fakes do not. I hit this in my own first batches (reused dirs: `work/*/fake-*/hold/release` present, ls evidence). Re-runs in fresh dirs were clean. Fail-closed, but `met` depends on work-dir hygiene; the C2 predicate refuses reuse, the C1 counter does not.
iii. If the live stage passes with a holder whose maps lack a `.so.0.7.0` mapping (ablation with exe/maps/claim neutered), `build_controls` raises StopIteration (round64-c1-counter.py, bind_maps control) and the counter prints a traceback and no `met=` line (exit 1). Fail-closed; it should print `met=False`.
iv. Positive control for the counter: the same forged tool passes when it is the genuine tool (base lines above).

## 5. Attribution of the verdicts

- KILLED lines above come from `live_ok=0/1` with `error: live: [...]`; the decisive check is the one listed.
- SURVIVED lines show `live_ok=1/1` and, where printed, `met=True`. For B4, B5, R1, E1, C1 the full counter output is `met=True` (76/76, families exact, errors=0).
- C2b prints `met=False` with `live_ok=1/1`; I count it as SURVIVED at the binding and report the `met` gap as the forge artifact (4.i).
- Fake-control flake: my first B4/B5/C1/C2b/R1/E1 batches printed fake-control failures (4.ii). Both outputs are kept (`out/.../receipts/result-*.json` vs `*_r3`); the `_r3` runs use fresh dirs. Not a host flake.

## 6. Minimal fixes (for L1; not applied, I did not edit lane source)

- Bind argv as a set: `bind_argv` should require `cmdline[1:]` to equal the pinned tuple with the run port substituted (or an allowlist of flags, rejecting unknown ones); the same for `bind_env` (exact allowlist of keys, not a denylist of two prefixes). This closes B4, B5, R1, E1. It changes the frozen binding wording only if L1 narrows it; otherwise it is an AMENDMENT before wave f (freeze.txt line 109).
- Retire the textual forge patches (or anchor them by content, not `-F3`) so that a tool edit fails loudly instead of going uncredited.
- `witness_run`: remove `release` and `hold.json` before starting, or refuse a reused `--work` (as the C2 predicate does).
- Wrap `build_controls`/`run_controls` so an exception prints `met=False`.
- The exe and maps observations are the strongest checks I could not get past (sections 1, 3). Keep them.

## 7. Procedure, tools, cleanup

- Clone: `/fast/scratch/hyaku/kama-r64/b/MT04ArgvSpoof/clone` at f6a4ea9a (checked with `git rev-parse --show-toplevel`). Every variant: reset to base, write the edited tool, `git add -A`, commit as seat (`--allow-empty`), run the unmutated counter at that commit, reset `--hard` to base. Only my clone was touched; no git mutation outside it.
- Drivers and sources: out/MT04ArgvSpoof/exp/{drive.py, drive2.py, drive3.py, run3.py, run4.py, run5.py, ablate.py, fwd_src.py, exe_spoof.py}. Patches (tip vs base): out/MT04ArgvSpoof/patches/*.patch. Result JSON + live receipts: out/MT04ArgvSpoof/receipts/. Counter outputs: out/MT04ArgvSpoof/counter/.
- Tools installed or upgraded: none. Used `sudo -n` once (prctl test, exp/exe-spoof-root-test.txt); no package operation; pacman untouched. Used system python3 3.14.8 and the pinned llama-server b11755 (sha b6a31a8e) only.
- Live ports: all servers were on counter-chosen loopback ports or my own probe ports from a free-port bind; I did not touch 8080, 34113 or any other seat's listener. Process check at the end: no process of mine remains.
- Scratch root removed after receipts were copied to out/.

## 8. Verbatim counter output lines (one per variant; the `met=` line is the counter's own)

Each block shows the tip, exit code, the counter's one-line output and the error lines it printed.
Names: A1=`A_exec`, A2=`A_exec_fab`, A3=`A_retitle`, A4=`A_retitle_fab`, B1=`B1_dup_port_same`, B2=`B2_dup_port_other`, B3=`B3_short_model_copy`, B4=`B4_short_alias_r3`, B5=`B5_extra_flag_benign_r3`, B6=`B6_dup_model_long_r3`, B7=`B7_alias_comma_r3`, C1=`C1_sh_exec_r3`, C2a=`C2_sh_hop_nofix`, C2b=`C2_sh_hop_pidfix_r3`, R1=`R1_router_preset_argv_r3`, E1=`E1_env_extra_r3`. The `_r3` suffix marks the fresh-work-dir re-run; the un-suffixed files of the same variant are the reused-dir first runs (section 4.ii).


@@L:A_exec@@

@@L:A_exec_fab@@

@@L:A_retitle@@

@@L:A_retitle_fab@@

@@L:B1_dup_port_same@@

@@L:B2_dup_port_other@@

@@L:B3_short_model_copy@@

@@L:B6_dup_model_long_r3@@

@@L:B7_alias_comma_r3@@

@@L:B4_short_alias_r3@@

@@L:C1_sh_exec_r3@@

@@L:C2_sh_hop_nofix@@

@@L:C2_sh_hop_pidfix_r3@@

@@L:B5_extra_flag_benign_r3@@

@@L:R1_router_preset_argv_r3@@

@@L:E1_env_extra_r3@@

## 9. Counter tally (one line)

Frozen tip, committed unmutated counter, fresh work dir: `@@BASE2@@`
