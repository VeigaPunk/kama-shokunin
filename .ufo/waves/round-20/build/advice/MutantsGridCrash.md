VERDICT: confirm - a crashing check.py is counted as a killed mutant against a clean baseline

# Scope and provenance
- Scratch clone: `/tmp/kama-r20-MutantsGridCrash/lane`, HEAD `37bd4c5bd456a2f8a54d3312c28495c321715856` (`git rev-parse HEAD`, exit 0); clean immediately after clone (`git status --short | wc -l` = 0).
- Frozen runner SHA-256: `498d1f7fa7f248d7c794db95ac6208a59c13297305226774e6aa4dc6ff88ac1e`; source and scratch copies matched (`sha256sum`, exit 0).
- No tools installed or updated.

# Finding
At the pinned revision, `.ufo/waves/round-17/c1/mutants.py:52-55` says verbatim: “Killed = any observable difference versus baseline: exit code, doc totals, per-row … vector, run failure where baseline was clean, or a fault-controls accepted delta.” Implementation agrees: `diff_observations()` at `:809-820` appends `run_failure` when mutant output has no document and the baseline had a document (or errors differ); `run_cell()` at `:960-998` records any nonempty diff as a kill and sets `status` to `killed` when `killed_by` is nonempty. A clean baseline is required: `:942-945` instead marks applicable mutants `inconclusive` when baseline runs are invalid.

Executed the frozen runner's real `run_cell()` with synthetic `check.py` subprocesses (no ports and no external probe execution). Command: `PYTHONDONTWRITEBYTECODE=1 python3 /tmp/kama-r20-MutantsGridCrash/reproduce.py` (exit 0). The result is retained at `.ufo/waves/round-20/build/out/MutantsGridCrash/mutants-crash-repro.json`. Against valid exit-0/JSON baselines, the injected uncaught `RuntimeError` (exit 1, traceback, no JSON) was `killed` by `pair:before` and `pair:current`, with both `exit` and `run_failure` diffs. Silent exit 1 and SIGKILL (observed `-9`) were also `killed`; no-op survived and an actual row-verdict change was killed. Thus the crash itself is sufficient; no subject verdict was observed.

The full detector has another error-as-kill route in the code: `:977-986` appends `full:controls_fault` if mutant controls error or provide no accepted count, and `:996-998` converts that to `killed`. This full-controls path was not dynamically exercised in this reproduction.

# Requested dry/selftest runs
- `python3 .ufo/waves/round-17/c1/mutants.py --selftest` (in scratch; `PYTHONDONTWRITEBYTECODE=1`; exit 0): stdout summary `pass 30 30`.
- Bare `--dry-run` (exit 2): `error: --check (or --grid) is required`. Scratch `SKILL.md:572` lists the grid command; `:633` states: “The round-17 mutants dry-run requires `--check /absolute/path/to/check.py --dry-run`, not bare `--dry-run`.”
- Required explicit dry-runs, each exit 0 and JSON written under the permitted out directory: current `--check <scratch>/tests/probe-verdicts/check.py --dry-run` found 9/10 mutation sites (M5 `site_missing`); frozen `--check <scratch>/.ufo/waves/round-17/frozen/tests_probe-verdicts_check.py --dry-run` found 8/10 (M6/M7 `site_missing`). These are site-discovery results, not a full grid measurement.
- One real current `check.py` baseline run (72 tests) exited 0 with 72 passes / 0 failures in 37.8 s.

# Verification gap
The reproduction proves the pair detector's crash classification but does not run the full `--grid` or exercise full-controls dynamically. The observed current-arm M5 `site_missing` also means that dry-run did not exercise that timeout mutation. No code was changed in the lane.