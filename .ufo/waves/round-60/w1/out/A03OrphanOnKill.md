# A03OrphanOnKill — teardown falsification

Axes: operability (assigned); calibration is the round's lowest axis (7). Scope: teardown behavior of `tools/kama-ollama-live.py`.

## Finding

**Actionable, high-confidence defect: uncatchable tool termination leaks its Ollama child.** At the ready-wait point, I started the live tool with an isolated `--work` directory and sent SIGKILL to the tool PID. The tool exited `-9`; after two seconds, `/proc` still contained PID `1970293`, command `/home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama serve`, with `HOME` inside that run's scratch work. This is a running leaked server, so the lane cannot claim unconditional teardown for interrupted runs.

Evidence command: `TMPDIR=/fast/scratch/hyaku/kama-r60/A03OrphanOnKill python3 /fast/scratch/hyaku/kama-r60/A03OrphanOnKill/probe.py` (exit 0). Output: `ready signal 9 tool_rc -9 leaked_home_procs [(1970293, '/home/vgpnk/.local/opt/ollama-v0.40.11/bin/ollama serve ')] receipt False`. The probe then sent SIGTERM only to that discovered Ollama PID; it did not kill by process name. The leak resulted because `Popen(... start_new_session=True)` detaches the server from the tool's process group, while cleanup exists only in Python's `finally` block. SIGKILL cannot run that block.

## Other requested signal observations / limits

The same probe attempted SIGTERM during nominal create and SIGINT during nominal generate, with fixed waits of 5s and 14s. Both runs had already completed by signal delivery: `create signal 15 tool_rc 0 leaked_home_procs [] receipt True`; `generate signal 2 tool_rc 0 leaked_home_procs [] receipt True`. These do **not** demonstrate behavior during create/generate and are not counted as passes or falsifications for those phases. SIGTERM/SIGINT during ready wait were not separately sampled. Thus the demonstrated defect is specifically SIGKILL during readiness; the other requested phase/signal combinations remain unverified. The captured two cases prove only that completed runs left no observed process with that run's scratch HOME.

## Minimal fix proposal (not applied)

A signal handler/`atexit` alone cannot guarantee cleanup on SIGKILL. For catchable SIGTERM/SIGINT, install handlers that terminate the owned process group and wait, then exit through the existing receipt/cleanup path. To cover SIGKILL, arrange an OS-enforced parent-death signal for the server child (e.g. a tiny launcher using Linux `PR_SET_PDEATHSIG`, with the parent-race check), or avoid asserting teardown under uncatchable parent death. Keep normal `finally` cleanup as the ordinary path.

## Verification gaps

No create- or generate-phase interruption was successfully synchronized; the fixed-delay probe was too slow relative to this fixture's completion. No full live receipt was produced by the interrupted run. Disk guard status was checked before the probe: `/fast/scratch/hyaku` reported 593.9G free. No lane source was edited.