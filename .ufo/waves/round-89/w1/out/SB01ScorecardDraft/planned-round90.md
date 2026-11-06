### Planned (round 90)

1. Operability (carried r88 R5): repair `tests/probe-verdicts/check.py` so it can grade `MODEL_UNLOADED`
   rows — at this round's tip the file names no `MODEL_UNLOADED`, so the verdict class the round-88 rule
   emits is outside its own gate, and the round-89 wave's held-out cells cannot be added to it.
2. Operability (carried r87 R4): investigate the `round75-instruments` arm's `APPEND_DEBT` red and record
   the cause before any round claims an all-green gate.
3. Calibration: extend C1's file classes to the held-out cells the wave reports (near-end truncation, a
   directory or FIFO at the path, unreadable permissions, a missing mmproj, a split shard) only from
   committed receipts that also record the base verdict for the same cell.
4. Freshness: re-run `tools/round89-router-signatures.py` at the next pinned llama.cpp release and re-grade
   all eight rows, so the table cannot silently outlive the build that was asked.
5. Calibration: grade each capability row's evidence pointer against the rule that row describes — round
   88's D1 (a row describing the repaired rule while its first pointer certified the superseded one)
   survived to this round's freeze, so the class is not yet closed by a counter.

