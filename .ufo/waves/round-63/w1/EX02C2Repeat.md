# EX02C2Repeat - round63-c2-counter repeat at tip 03a6a1d850902a66a13dfad33f89cf3a8b759a09

Setup: clone `--shared` of the lane checked out at the tip (counter run from clone `tools/`), `--repo` = lane path, `--tip` = tip, `--work` under my scratch (run1/run2/run3). No tools installed.
Receipts: out/EX02C2Repeat/{out,err}{1,2,3}.txt

## Runs (stdout, one line each; stderr empty in all three)
run1: `population=12 rows=12 covered=12/12 bound=12 eval_lines=12 sensitive=12/12 dead=0 host_busy=1 mismatches=0 canonical=63 selfdesc_mismatches=8 sens_selftest=4/4 controls_rejected=12/12 errors=0 met=False`
run2: identical string.
run3 (extra, timed): identical string.

| run | exit | wall | stderr | pgrep -x llama-server start | end |
|---|---|---|---|---|---|
| 1 | 1 | NOT MEASURED (my `bc` timer failed: command not found) | empty | 3262613 1706355 242776 2556904 | 3262613 1706355 242776 |
| 2 | 1 | NOT MEASURED (same defect); run1+run2 together = 102.33 s tool wall | empty | 3262613 1706355 242776 | 3262613 1706355 242776 2853755 |
| 3 | 1 | 42.546 s | empty | 3262613 1706355 242776 2853755 | 3262613 1706355 242776 2853755 |

Run3 was added only to obtain a wall time; run1/run2 exit codes were captured (1) by `$?`.

## Agreement
All three runs agree byte-for-byte on the one-line output. Expected-by-design: selfdesc_mismatches=8, met=False. Everything else: host_busy=1, sensitive=12/12, mismatches=0, dead=0, covered=12/12, bound=12, sens_selftest=4/4, controls_rejected=12/12, errors=0.

## llama-server processes (pgrep, cmdline read from /proc)
- 1706355: port 1234 (operator, foreign); 242776: port 45669 (operator, foreign).
- 3262613: ollama-v0.40.11 llama-server on a /fast/scratch/hyaku/kama-r61-closure blob (foreign leftover, present throughout).
- 2556904 (gone by end of run1) and 2853755 (stories260K, alias kama-completion-probe, port 34451; appeared at end of run2, still present at start/end of run3) are other seats' live-tool children, not mine; I spawned no llama-server directly and signalled nothing. The counter's own children are not visible at start/end sampling points.
- The persistence of 3262613/1706355/242776 explains the host_busy=1 row (context-capacity-receipt host-busy).

Risks: none beyond missing run1/run2 individual wall times (two-run total 102.33 s; third run 42.5 s suggests ~50 s each).
