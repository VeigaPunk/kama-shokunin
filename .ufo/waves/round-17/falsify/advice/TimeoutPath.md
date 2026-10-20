VERDICT: partial — F7 correctly fails a timed-out probe and distinguishes M5, but a shell probe's external sleep survives the checker.

# Scope and axes

Seat: `KamaR17.TimeoutPath`. Advisory recommendation only; no admission or integration decision.

Attacked C1's timeout branch, exact M5 `timeout-pass`, and F7 at commit `54a29268e2083caa2b1e0d54ee1e7d90961302f3`; compared the affected source against round start `cff9e62f05aa7cfb9059444f62eb787100719713`.

Axes: **calibration** (failed record, explicit error, sensitivity to M5); **operability** (bounded completion and descendant cleanup); **measurement fidelity** (isolated F7 versus F0-plus-F7 elapsed time). These are scoped checks, not additional round claims or scalar scores.

All executions used a pinned clone at `/tmp/KamaR17.TimeoutPath-clone`; never ran a lane tool in the lane worktree. Only lane write: this Report.

# Findings, by severity

## P2 — timeout handling kills the immediate probe, not its external child; F7 does not exercise this topology

Locations and short quotes:

- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:275-279`: `proc = subprocess.run(argv, capture_output=True, timeout=PROBE_TIMEOUT)`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:447-451`: `record["error"] = f"probe timed out after {PROBE_TIMEOUT}s"`, followed by return. The initial record remains `passed: false`.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/check.py:487-490`: the finally block closes the HTTP stub, not the probe process tree.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:197-198,239-240`: `exec python3 - "$@"` and `time.sleep(float(os.environ.get("FAULT_SLEEP", "40")))`. Bash is replaced, and this hang has no external sleep child.
- `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:346-368`: group termination occurs only when the **whole checker** exceeds the separate 150-second cap; its normal exit path returns immediately.

Concrete counterexample: byte-copy the current checker and its nine matrix files; replace only the scratch probe with:

```bash
#!/usr/bin/env bash
sleep 120
printf "sleep completed\n"
```

The trailing command deliberately prevents the shell from simply exec-replacing itself with its final command. Run only `ReadyControls.expect-exact-id` with the unmodified 30-second checker timeout.

Observed checker result after **31.023 s**: exit **1**, parseable JSON, `tests: 1`, `passes: 0`, `failures: 1`, `passed: false`, `error: "probe timed out after 30s"`, `probe_exit: null`, and `route_ok: false`. Thus grading is correct, but cleanup is not:

```text
$ pgrep -a -g 3660548
3660606 sleep 120
# exit 0
```

The accompanying `ps -eo pid,ppid,pgid,sid,stat,args` snapshot contained:

```text
3660606 3660493 3660548 3660548 S    sleep 120
```

The checker had exited. The live sleep had been adopted by the assay supervisor, which was explicitly configured as a Linux child subreaper; PPID `3660493` is that supervisor, not a surviving checker. This preserves the escaped child for observation and permits cleanup without leaving a zombie at PID 1. It does not kill the child or change the checker's timeout behavior.

Feeding this exact emitted row into the existing F7 `classify_run()` returned **true**: `"check exited 1 with JSON; all 1 faulted rows failed the 'error' conjunct"`. `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:482-538` checks exit, JSON, failed rows and targeted conjuncts, not child-process survival. Therefore F7 detection is not evidence of process-tree cleanup.

The supervisor then sent SIGKILL to **only its owned group 3660548**, reaped PID `3660606` with wait status `9`, and repeated `pgrep -a -g 3660548`: exit **1**, empty output. No escaped process was left running.

This is an **inherited limitation**, not a newly introduced regression: the actual round-start-to-build diff retains the same direct-child subprocess timeout and early timeout return. It does not refute the narrow accepted-fault delta or the M5 result. It does refute extending those measurements into a general "a hanging shell probe leaves no descendants" claim. Recommendation: process-tree containment/cleanup plus a descendant-bearing hang control if that stronger contract is intended; no code changed in this review.

# Confirmed behavior and elapsed time

| Assay | Observed result | Timed interval |
|---|---|---:|
| Current canonical `fault-controls.py --only-fault F7 --json` | F0 healthy, 5/5 rows passed; F7 checker exit 1; `detected: 1`, `accepted: 0`; suite exit 0 | **33.625 s**, F0 plus F7; document `seconds: 33.3` |
| Exact canonical M5 applied to scratch checker, same F7 command | F0 healthy; F7 checker exit 0; `detected: 0`, `accepted: 1`; suite exit 1 | **33.629 s**, F0 plus F7 |
| Isolated original F7 wrapper, one checker row | Checker exit 1; explicit timeout error; `passed: false`; process-group census empty | **30.980 s** |
| Shell-child counterexample above | Same correct failed row; live sleep remains after checker exit | **31.023 s** |

The first three observations support C1's **specific timeout grading and M5 sensitivity**. M5 was generated using the committed `apply_mutant()` and the exact `M5` entry at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-17/c1/mutants.py:510-522,624-631`. Its reported application was:

```text
literal-insert: insert after 'record["error"] = f"probe timed out after {PROBE_TIMEOUT}s"'
```

That inserts `record["passed"] = True` inside the timeout branch. The baseline-to-M5 accepted count changes **0 → 1** under the targeted detector. This establishes the relevant distinction without claiming a rerun of the entire mutant grid.

For the isolated original F7 case, the actual row was:

```json
{"name":"ReadyControls.expect-exact-id","requests":[],"route_ok":false,"probe_exit":null,"verdict":null,"reason":null,"drift":null,"served_model":null,"error":"probe timed out after 30s","passed":false,"port":51516}
```

`pgrep -a -g 3660547` returned exit **1**, empty output, without supervisor termination. This original F7 run left neither bash nor sleep in its process group. The negative result is narrow: F7 uses a single exec-replaced Python process and does not spawn an external sleep.

Timing clarification: `/home/vgpnk/Projects/shokunin/kama-shokunin/tests/probe-verdicts/fault-controls.py:37,628-629` describes F7 as approximately 40 seconds. **40 is its requested sleep duration, not the observed test duration**: the checker cuts it off at 30 seconds. On this host the isolated path took about 31 seconds, and the public F0-plus-F7 command about 33.6 seconds. Intervals above end at `communicate()` return and exclude later `pgrep`/`ps` census cost. The complete four-assay command took **75.37 s**, including those census operations.

# Residual risk and verification gaps

- The full F1–F8 suite, all four mutant-grid cells, frozen-checker execution, other matrix rows under hangs, and C2 live behavior were not rerun. This report supports neither a new aggregate count nor a saturation claim.
- The shell-child counterexample proves a live descendant leak, not an incorrect timeout verdict. No nested-bash, detached-session, or signal-ignoring child variant was exercised.
- LSP was unavailable: requesting `xd://lsp` returned `No such tool: xd://lsp` and a mounted-device list without LSP. Status, semantic references, definitions and diagnostics could not be requested; there was no cold indexing result to interpret. Used explicit-file literal searches and source/diff inspection instead, **not semantic proof**. Literal call sites reviewed: checker `run_probe()` → `grade()` → `main()`; controls `run_check()` → `run_fault()`/`classify_run()` → `main()`.
- All Python execution used the same `/usr/bin/python3` 3.14.8. No UFO runtime, rerouting, admission, integration, resume path, or llama-server was invoked or reviewed.
- Safety-only adaptation: an isolated `sitecustomize.py` selected loopback ports in **49152–60999** for requests to bind `127.0.0.1:0`. The host's unreserved ephemeral range includes protected port 34113. The shim did not alter source bytes, timeout values, verdicts or process handling. Registered ports 8080/34113 were neither bound nor contacted. It was supplied only through this assay's `PYTHONPATH` and removed with scratch.

# Exact command and evidence log

Commands below were executed as shown; commands launched by the assay inherited `PYTHONDONTWRITEBYTECODE=1`, `TMPDIR` under `/tmp/KamaR17.TimeoutPath-work`, and `PYTHONPATH=/tmp/KamaR17.TimeoutPath-work`.

## Setup and read-only review

```text
# cwd /tmp; exit 0
git clone -q /home/vgpnk/Projects/shokunin/kama-shokunin /tmp/KamaR17.TimeoutPath-clone && git -C /tmp/KamaR17.TimeoutPath-clone checkout -q 54a29268e2083caa2b1e0d54ee1e7d90961302f3

# cwd /tmp; exit 0
mkdir /tmp/KamaR17.TimeoutPath-work

# cwd /tmp; exit 1, no pre-existing scoped match
pgrep -a -f '^([/]?usr/bin/)?(bash|sleep|python3) .*KamaR17[.]TimeoutPath'

# cwd /tmp/KamaR17.TimeoutPath-clone; exit 0
git -C /tmp/KamaR17.TimeoutPath-clone diff cff9e62f05aa7cfb9059444f62eb787100719713 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tests/probe-verdicts/check.py tests/probe-verdicts/fault-controls.py

# cwd /tmp/KamaR17.TimeoutPath-clone; exit 0
git -C /tmp/KamaR17.TimeoutPath-clone diff --no-ext-diff --unified=4 cff9e62f05aa7cfb9059444f62eb787100719713 54a29268e2083caa2b1e0d54ee1e7d90961302f3 -- tests/probe-verdicts/check.py

# cwd /tmp; exit 0
python3 --version && bash --version && pgrep --version && ss --version

# cwd /tmp/KamaR17.TimeoutPath-clone; exit 0
sha256sum /tmp/KamaR17.TimeoutPath-clone/tests/probe-verdicts/check.py /tmp/KamaR17.TimeoutPath-clone/tests/probe-verdicts/fault-controls.py /tmp/KamaR17.TimeoutPath-clone/.ufo/waves/round-17/c1/mutants.py /tmp/KamaR17.TimeoutPath-clone/tools/kama-probe.sh
```

The Git pathspecs above are repository-relative as actually executed; all filesystem targets and working directories are absolute. File reads/searches used the dedicated tools, not recursive shell grep. No privacy-bounded directory was searched.

SHA-256 observations:

```text
ddc3f3cceaee9687de4d6aa29cd4adb72833e08ef0657371dff97cf582fe2099  current checker
d3eaadeb8a061b4e322868d569df77afbd7331089d06b06c86a2063fdc31b312  fault controls
498d1f7fa7f248d7c794db95ac6208a59c13297305226774e6aa4dc6ff88ac1e  mutant definitions
36b64978ee3a3aa29e1b73f04ca5c7ad04a9aee880e7032abfd894fa7b3a29d3  real probe
d0bac95c60fbe82e4e59c3aedca9f82c8b73b2991d2b6a9c8fac4f30460aab46  generated M5 checker
bf9068d89e4cb8a080167cb32cc818943d717a65fcbd21edb2b8256e22771f32  matrix set (9 files, 72 tests)
```

## Assay invocation and child commands

Created only scratch files through the write tool: the safety shim and `/tmp/KamaR17.TimeoutPath-work/timeout-review.py`. The latter loaded the cloned control/mutant modules, staged scratch checker/matrix copies through their existing functions, applied exact M5 to a new scratch file, and ran the following four independent cases in a four-worker thread pool. It used `start_new_session=True` for its checker/suite children, captured JSON/stderr, timed `communicate()` using `time.monotonic()`, then ran the recorded group censuses. A Linux subreaper was enabled before spawning; no process was terminated before the after-run evidence census.

```text
# cwd /tmp/KamaR17.TimeoutPath-clone; exit 0; complete batch wall time 75.37 s
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/KamaR17.TimeoutPath-work PYTHONPATH=/tmp/KamaR17.TimeoutPath-work python3 /tmp/KamaR17.TimeoutPath-work/timeout-review.py

# cwd /tmp/KamaR17.TimeoutPath-clone; exit 0
/usr/bin/python3 /tmp/KamaR17.TimeoutPath-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.TimeoutPath-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17.TimeoutPath-clone/tools/kama-probe.sh --only-fault F7 --json

# cwd /tmp/KamaR17.TimeoutPath-clone; exit 1 (expected detector failure on M5)
/usr/bin/python3 /tmp/KamaR17.TimeoutPath-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.TimeoutPath-work/M5-check.py --probe /tmp/KamaR17.TimeoutPath-clone/tools/kama-probe.sh --only-fault F7 --json

# cwd /tmp/KamaR17.TimeoutPath-work/raw-F7; exit 1 (expected timed-out row)
/usr/bin/python3 /tmp/KamaR17.TimeoutPath-work/raw-F7/check.py --probe /tmp/KamaR17.TimeoutPath-work/raw-F7/wrap.py --json --only ReadyControls.expect-exact-id

# cwd /tmp/KamaR17.TimeoutPath-work/shell-child; exit 1 (expected timed-out row)
/usr/bin/python3 /tmp/KamaR17.TimeoutPath-work/shell-child/check.py --probe /tmp/KamaR17.TimeoutPath-work/shell-child/wrap.py --json --only ReadyControls.expect-exact-id
```

The raw-F7 child inherited `FAULT_MODE=hang`, `FAULT_PROBE=/tmp/KamaR17.TimeoutPath-clone/tools/kama-probe.sh`, `FAULT_SLEEP=40`, and `FAULT_WRAPPER_EXIT=9`; its wrapper was the unchanged committed `WRAPPER` string. The shell-child wrapper was the three-line script quoted in P2. Each scratch checker and all nine matrices were byte-copied using the existing `stage_scratch()`; `M5-check.py` was a separate newly generated file. Canonical controls used their unmodified temporary staging and F0 preflight.

An earlier attempted launch of the public F7 command with `/usr/bin/time` was refused by the tool before execution (`Background job limit reached (100)`); it has **no process exit code and supplied no timing evidence**:

```text
env PYTHONDONTWRITEBYTECODE=1 TMPDIR=/tmp/KamaR17.TimeoutPath-work /usr/bin/time -f 'F7_CLI_ELAPSED=%e EXIT=%x' python3 /tmp/KamaR17.TimeoutPath-clone/tests/probe-verdicts/fault-controls.py --check /tmp/KamaR17.TimeoutPath-clone/tests/probe-verdicts/check.py --probe /tmp/KamaR17.TimeoutPath-clone/tools/kama-probe.sh --only-fault F7 --json
```

## Process/socket census and cleanup

```text
pgrep -a -g 3660543   # exit 1, empty; M5 suite outer group
pgrep -a -g 3660540   # exit 1, empty; canonical suite outer group
pgrep -a -g 3660547   # exit 1, empty; isolated original F7 checker group
pgrep -a -g 3660547   # exit 1, empty; second census, no cleanup signal sent
pgrep -a -g 3660548   # exit 0, "3660606 sleep 120"
ps -eo pid,ppid,pgid,sid,stat,args   # exit 0; scoped row quoted in P2
ps -eo pid,ppid,pgid,sid,stat,args   # exit 0; other raw group empty
# Supervisor: os.killpg(3660548, signal.SIGKILL), then os.waitpid(-3660548, 0).
pgrep -a -g 3660548   # exit 1, empty after kill/reap
pgrep -a -f '^bash /tmp/KamaR17[.]TimeoutPath-work/'   # exit 1, empty

# cwd /tmp; exit 0; only header, no listening rows; run before and after cleanup
ss -ltnp '( sport = :51516 or sport = :59997 )'

# cwd /tmp; exit 0
rm -rf /tmp/KamaR17.TimeoutPath-clone /tmp/KamaR17.TimeoutPath-work && test ! -e /tmp/KamaR17.TimeoutPath-clone && test ! -e /tmp/KamaR17.TimeoutPath-work

# cwd /tmp; exit 1, empty final census
pgrep -a -g 3660540,3660543,3660547,3660548
```

The outer suite-group censuses alone do not cover the controls' nested new sessions; the isolated original-F7 checker-group census is the evidence for that wrapper's cleanup. No global claim about unrelated host bash/sleep processes is made. All owned scratch, copied sources, generated M5, shim and result JSON were removed. Stub ports 51516/59997 were confirmed closed; no llama-server was started.

# Installs

**None.** Used existing Python **3.14.8**, GNU bash **5.3.20(1)-release**, pgrep **0.2.0**, and ss/iproute2 **7.2.0**. Read the operator rules first; no pacman transaction, package update, runtime install, or host-service restart occurred.
