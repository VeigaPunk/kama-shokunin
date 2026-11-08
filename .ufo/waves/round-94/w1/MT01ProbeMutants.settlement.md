# MT01ProbeMutants — settled seat with deliverables (kama r94 w1)

Seat role: mutation-tester (attack). Spawned 2026-11-07T23:42:06 with the rest of wave `w1`.

**Liveness.** The dispatcher lost its handle in a kernel restart mid-wave and the wave initially
settled without it; the handle reappeared after the restart and the seat completed. Its
`w1-results.json` row still carries an `<output unavailable: FileNotFoundError('Output not found:
MT01ProbeMutants-5…')>` marker from the settle that happened before the handle returned; the
authoritative record is its report and artifact, both present:

- `.ufo/waves/round-94/w1/MT01ProbeMutants.md` (119 lines)
- `.ufo/waves/round-94/w1/out/MT01ProbeMutants/` (`mutants/M01..M14` + diffs, `mutants.tsv`,
  `logs/`, `direct/`, `scripts/`)

It is a **settled seat with deliverables**, not a dead seat, and it was never replaced.

**Verdict: partial.** 14 single-point mutants of the M1 probe through the frozen counter: 7 killed,
7 survived. Four survivors are coverage gaps with measured separating inputs (per-invocation budget
M02 — an 8-distinct-slow-file listing; ctime-less memo key M12 — a mid-invocation same-size rewrite
with restored mtime; count overflow M14 — a 2 M-tensor sparse header; the 60 s wrapper M10 — a
~20-file listing). M04/M05/M11 are measured equivalents (the MAX_STEPS and wall bounds cross within
±10 %). Its BLOCKER-1 is decisive for the claim: the plan's F1 control ("a per-call (not per-file)
deadline → the synthetic-load cell red") is **false** — the M02 shape exits 0 at load1 323.04, and
the L1's own `controls/c1-forgeries.out` F3_shared_deadline reports `mismatches=0`, because R08's
four distinct slow files fit inside a single 15 s budget. The per-file reset is therefore ungraded.
Other routed items it records: the counter's cell budget is 30 s not the plan's 20 s; K1 as worded is
narrower than the counter's exit condition; `round89-unloadable-cells.py` needs
`LLAMA_CACHE`/`HF_HOME` isolation after a cache-sourced router model appeared at 00:11; at load1
240–424 the counter itself is often unevaluable (25/41 attempts exit 2).
