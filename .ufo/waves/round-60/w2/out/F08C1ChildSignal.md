# F08C1ChildSignal
- Attacked W1 A03OrphanOnKill against frozen C1 child teardown wording.
- Disk guard: 592G available on `/fast` before live probes.
- Re-ran actual tool; signaled own harness PID after observing child in `/proc`.
- SIGKILL: tool rc -9; PID 3193330 survived; HOME under isolated scratch work.
- SIGTERM: tool rc -15; PID 3193383 survived; HOME under isolated scratch work.
- Both specific child PIDs were individually SIGTERM-cleaned; scratch removed by EXIT trap.
- Source `start_new_session=True` plus finally-only cleanup explains both cases; no lane edits.
- Ordinary completion reaching `finally` is distinct from either interrupted-run case.
- Finding/evidence: `.ufo/waves/round-60/w2/out/F08C1ChildSignal/findings.md`.
