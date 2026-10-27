# F08C1ChildSignal — child teardown under parent signals

## Evidence

Read W1 `w1/out/A03OrphanOnKill.md`: its synchronized SIGKILL-during-readiness probe found a live Ollama PID with HOME under the run work directory; its SIGTERM/SIGINT attempts missed the active phase. Frozen C1 sentence says the tool “tears the child down”; its stated limit is one lane-owned child for the length of a run, and the tool doc says it tears the server down and proves teardown. Source at `tools/kama-ollama-live.py:283-284` launches with `start_new_session=True`; its only termination is in `finally` at `:405-425`.

I reran the actual tool twice, starting each own server and signaling the tool as soon as `/proc` showed its child (before readiness completed). Probe stdout:

```
{'signal': 'SIGKILL', 'tool_pid': 3193329, 'tool_rc': -9, 'child_pid': 3193330, 'child_home': '/fast/scratch/hyaku/kama-r60/F08C1ChildSignal/run-sigkill/home', 'home_under_work': True, 'child_alive_after_parent_signal': True}
{'signal': 'SIGTERM', 'tool_pid': 3193382, 'tool_rc': -15, 'child_pid': 3193383, 'child_home': '/fast/scratch/hyaku/kama-r60/F08C1ChildSignal/run-sigterm/home', 'home_under_work': True, 'child_alive_after_parent_signal': True}
```

Both observed children were then individually sent SIGTERM by their recorded PID; no process-name kill was used. Scratch was removed by the command's EXIT trap. Disk guard before probing: `/fast` had 592G available. No lane files changed.

## Finding

The leak reproduces for SIGKILL and also for SIGTERM during active startup: default SIGTERM exits Python without running `finally`, and the detached server survives. Thus teardown is demonstrated only on the ordinary completed/error path that reaches `finally`, not when the harness is terminated. If “tears the child down” is read as applying to interrupted runs, that claim is falsified; if restricted to runs that reach `finally`, interruption cleanup is outside the frozen limits and must not be claimed. SIGKILL is uncatchable; SIGTERM is catchable but no handler is installed. The two specific live observations are actionable regardless of any broader wording.
