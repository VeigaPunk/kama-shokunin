# FalsifyAudit — check.py process-audit and marker counters

Scope: `tests/ollama-corpus-guard/check.py` (launcher audit hook, wrapper marker, grade) against `.ufo/waves/round-14/measure.py`. This was static reading plus metadata reads of the host interpreter (`strings`/`nm` on libpython and `_posixsubprocess`, grep of stdlib source). I did not run any check, test or probe. I installed nothing.

Axes: zero-child proof (rejected branch), wrapper-entry distinction, counter completeness, regression risk.

## Verdict
- **Zero runner child creation on duplicate rejection: holds** for the committed runner. Static reading and the two dynamic counters agree. No counterexample against the actual candidate.
- **Wrapper entry vs runner spawn: kept apart.** The marker counts wrapper process entries; the audit counts runner-process spawn calls. Rejection requires both counters to be 0. Acceptance requires both to equal `len(names)`.
- **One fixable overclaim (low severity, not a judge-reject tradeoff):** `PROCESS_EVENT_PREFIXES` is described as "the observable process-creation surface of a Python runner on this platform". It leaves out the `_posixsubprocess.fork_exec` audit event. That gap does not affect the committed runner.

## Evidence

### Zero child in the rejected branch (static)
1. The runner has exactly one spawn site: `subprocess.run` at measure.py:240, inside `measure_case`. The grep over `subprocess|os.(system|fork|exec|spawn|posix_spawn|popen)|multiprocessing|pty|ctypes` finds nothing else. The imports are argparse, hashlib, json, os, subprocess, sys, tempfile and pathlib. None of them spawns at import.
2. `measure_case` is reached only from the `elif tool_present:` branch of `run()` (measure.py:379-383). The `if corpus:` branch comes first (measure.py:375-378) and builds only `unmeasured_record`s. Those records have `observed_exit: None` (measure.py:166).
3. The duplicate guard `len(declared) != unique` uses `name.strip()` (measure.py:350-364). It runs after `load_cases`, `is_file` and `sha256_file(tool)`. All three are file reads, not spawns. `error_result` and `main` contain no spawn either.

### Zero child in the rejected branch (dynamic, check.py)
- The launcher calls `sys.addaudithook(_hook)` before `runpy.run_path(RUNNER, "__main__")` (check.py:257-286). So the runner's imports and all of its code are inside the observed window.
- Rejected grading requires all of these together (check.py:529-583): exit 1, `verdict_exit` 1, an error containing "duplicate case names", `passed` 0, `failed == total`, `tool_present` true, `observed_exit` null on every record, marker 0, process events 0 and Popen events 0.
- Missing and zero cannot be confused. Both files are created empty in advance (check.py:340-343). An unreadable file gives `None`, which fails the test (`count_lines`/`read_audit` → reasons).
- A failing hook cannot produce a false zero. The hook is not wrapped in a try, so a failing `open(AUDIT)` aborts the audited operation and the run fails. The hook's own `open` raises the "open" audit event, which re-enters the hook but does not match any prefix, so there is no loop.

### Wrapper entry is distinct from runner spawn
- The marker path appears only inside the generated wrapper source (check.py:289-309). The wrapper appends `x\n` before `runpy.run_path(CLASSIFIER)`, so the marker counts entries, not classifier success. LIMITS line 1 states this.
- In the classifier, `subprocess.run` (tools/kama-ollama-evidence.py:401) is only inside `run_selftest`, which runs only under `--selftest` (lines 491-493). The runner's argv never passes `--selftest`. Wrapper children therefore create no grandchildren. Grandchildren would be unattributed anyway, as LIMITS line 2 says.
- Stdlib detail: the runner passes `cwd=`, so `subprocess.py:1860` rules out `posix_spawn`. Each runner child then emits `subprocess.Popen` (subprocess.py:1858) and `_posixsubprocess.fork_exec`. The accepted branch grades only the Popen count (`== total`), not the total event count. So there is no double-count regression whichever spawn path is used.

### Counterexample to the surface claim (does not affect this runner)
- `nm -D` on `lib-dynload/_posixsubprocess.cpython-314-x86_64-linux-gnu.so` shows `U PySys_Audit`. `strings` shows the event name `_posixsubprocess.fork_exec` next to its error strings. In libpython 3.14.7 the only process events present are os.exec, os.fork, os.forkpty, os.posix_spawn and os.system (plus os.kill and os.killpg).
- `multiprocessing/util.py:518-526` (`spawnv_passfds`, which starts the 3.14 Linux default forkserver) calls `_posixsubprocess.fork_exec` directly. It emits no `subprocess.Popen`, `os.fork*`, `os.exec` or `os.posix_spawn` event.
- So a mutated runner whose reject branch starts a **non-wrapper** child through multiprocessing or `_posixsubprocess.fork_exec` would show process events 0 and marker 0. It would grade as a zero-child rejection although a child was created. A child that runs the wrapper is still caught by the marker.
- The committed runner never imports multiprocessing or `_posixsubprocess` (see above), so this gap does not weaken the round-15 claim for the candidate. It does make the "observable process-creation surface" comment (check.py:77-78) and the docstring event list (check.py:30-33) incomplete.

### Other checks (no defect)
- `"os.fork"` also matches `os.forkpty`, which covers `pty.spawn`. `posix_spawnp` raises `os.posix_spawn`. POSIX `os.spawn*` and `os.popen` reduce to fork/exec or Popen, so they are covered.
- `audit_observation` counts `subprocess.Popen` by exact match, while `grade` uses `startswith`. The results are the same because only the exact event name exists.
- Blank or whitespace-only names: none in any matrix JSON. I grepped for literal and escaped whitespace. So the `load_matrix` "≥16 distinct stripped" check (which would count `""`) cannot drift from the runner's rule of skipping blank names.
- Startup window before the hook: `site` and `/usr/lib/python3.14/site-packages/distutils-precedence.pth` run before `addaudithook`. That is interpreter startup, not runner code, so it is not runner child creation. It is not listed in LIMITS but does not affect this claim.

## Affected axes
Only counter completeness, and only in wording or for a hypothetical runner. The zero-child proof, wrapper distinction and regression risk are intact.

## Smallest safe correction (optional, fixable)
Either option is enough:
- add `"_posixsubprocess.fork_exec"` to `PROCESS_EVENT_PREFIXES` and to the docstring event list. The rejected branch still requires 0. The accepted branch still grades only the Popen count, so valid-corpus measurement is unchanged. `runner_process_events` becomes 2×total in accepted runs, which is not graded.
- or reword check.py:77-78 to "audit events for the listed prefixes" and add a LIMITS line noting that direct `_posixsubprocess.fork_exec`/multiprocessing and ctypes spawns are not recorded.
