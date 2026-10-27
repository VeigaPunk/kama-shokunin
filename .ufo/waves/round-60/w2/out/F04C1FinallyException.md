# F04C1FinallyException — C1 H4

Axis: operability. W1 artifact reproduces an exception after `log.close()` in `finally`.
Exact outcome: exit 1; receipt absent; stderr traceback ends `OSError: A09-simulated-finally-failure`.
Child had already been reaped; cleanup proof was lost. Exit 1 collides with documented graded-FAIL status.
This is ambiguous/lost classification, not false green. Frozen claim/predicate unchanged.
Evidence: `w1/out/A09FalseGreenReading.md:45-50`, `w1/out/A09FalseGreenReading/repro/p5.stderr`, `tools/kama-ollama-live.py:405-432`.
No independent rerun in this seat; findings document the assigned W1 reproduction.