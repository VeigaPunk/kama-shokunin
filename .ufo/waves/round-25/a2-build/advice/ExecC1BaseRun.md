# ExecC1BaseRun — C1 before evidence (round 25, attempt 2)

Verdict: at both pre-repair revisions efe58e96e6cfbef88a0fba9d64505e18b7ad7356 and 147f5bdd3228ab712520b5f377346cb2d9a64769, the registered measure is exactly as preregistered — `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` (counting command exit 0) and the instrument `isolation-mutants.py --json` exits 2 with `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times` — but the instrument reaches that exit 2 only after ten mutants (M01–M10) have already been applied and grid-evaluated; it does NOT abort before any mutant ran.

---

## Setup

- Own clones in scratch (no fleet-repo writes; no git/jj mutations):
  - `/fast/scratch/hyaku/kama-r25a2/ExecC1BaseRun/clone` — checkout `efe58e96e6cfbef88a0fba9d64505e18b7ad7356` (`git rev-parse --short` -> `efe58e9`)
  - `/fast/scratch/hyaku/kama-r25a2/ExecC1BaseRun/clone147` — checkout `147f5bdd3228ab712520b5f377346cb2d9a64769` (`147f5bd`)
- Both clones `git status --porcelain` clean after the runs.
- No llama-server child started (assignment forbids it); verified afterwards `pgrep -x llama-server` exit 1 (no process), and `ss -ltn` shows no listener on 8080 / 34113 / 47311.
- No tools installed; no tooling directive installs to record.

## Commands run (identical at both revisions)

C1 counting command (verbatim from preregistration.json, C1.command):

```
python3 -c "import importlib.util as u;s=u.spec_from_file_location('m','tests/report-audit/isolation-mutants.py');m=u.module_from_spec(s);s.loader.exec_module(m);src=m.AUDIT.read_text();bad=[n for n,o,_ in m.MUTANTS if src.count(o)!=1];print('registered',len(m.MUTANTS),'stale',len(bad),bad)"
```

Instrument:

```
python3 tests/report-audit/isolation-mutants.py --json
```

## Results

### efe58e96e6cfbef88a0fba9d64505e18b7ad7356 (clone)

- Counting command stdout (exit 0):
  `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']`
- Instrument `--json`, full run (budget 3600 s, completed): exit 2.
  - stdout (the JSON doc file): 0 bytes — no JSON emitted.
  - stderr, exactly: `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times`
  - wall time 349.20 s.

### 147f5bdd3228ab712520b5f377346cb2d9a64769 (clone147)

- Counting command stdout (exit 0): same line as above.
- Instrument `--json`, full run #1 (completed): exit 2; stdout 0 bytes; stderr same M11 line; wall 349.46 s.
- Instrument `--json`, full run #2 (replicate, completed): exit 2; stdout 0 bytes; stderr same M11 line; wall 349.54 s.

### Initial shorter-budget attempts (honesty note)

My first instrument attempts ran under the tool default deadlines (180 s, then 240 s) and were killed by those deadlines before finishing (both timed out with empty stdout/stderr, no exit code captured). They are instrumentation timeouts, not instrument behavior; the full-budget runs above are the recorded evidence.

## Did the instrument abort before any mutant ran? No.

- `isolation-mutants.py` fails fast inside the per-mutant loop (`tests/report-audit/isolation-mutants.py:167-176`): for each mutant it writes the mutant file and runs the grid before the next mutant; the `source.count(old) != 1` check for M11 happens at the 11th iteration. M01–M10 all match exactly once (only M11 and M17 are stale per the counting command), so each of them is applied and grid-evaluated before M11 is reached.
- Corroborating timing: a standalone pristine grid run `python3 tests/report-audit/repo-state-grid.py --arm current` completes in 33 s (exit 0) at both revisions (summary tail identical: `current faults=26/26 contracts=4/4 controls=14/14 tracebacks=0 executed=0 timeouts=0 violations=0`). The instrument's ~349 s wall time matches pristine (33 s) + ten mutant grid runs (~31.6 s each); an immediate abort would be ~35 s.
- Order demonstration at 147f5bdd (same code path at both revisions):
  - `--only M10-log-surrogates --only M11-listing-surrogates`: exit 2 (M10 ran its grid first, then M11 fail-fast). stdout 0 bytes; stderr `could-not-evaluate: M11-listing-surrogates: pattern matches 0 times`.
  - `--only M11-listing-surrogates`: exit 2, same stderr (pristine passed, then immediate fail-fast on M11).
  - `--only M10-log-surrogates`: exit 0, JSON doc `{"killed": 1, "mutants": 1, "pristine": "passed", ...}` with row `M10-log-surrogates` killed (grid_exit 1, failed_rows F18-bad-byte-unrelated-subject / F19-bad-byte-round-subject), `surviving": []`.
  - Side observation: short selector names select nothing (`--only M10` -> `could-not-evaluate: --only selected no mutant: ['M10']; ...`, exit 2); selectors must be full ids.

## Implication for the C1 claim framing

The preregistration C1 text says the stale instrument means "the registered counting command aborts with exit 2 before any mutant runs". Measured before-state: the counting command itself exits 0 and reports the 2 stale anchors; the instrument exits 2 with "could not evaluate" only after M01–M10 have run and been evaluated. The M11/M17 root causes are as claimed: M11's literal is split across a line wrap in the auditor, so `src.count(o) == 0`; M17's literal occurs twice. The fix target (stale 0, instrument exit 0 with all 28 mutants evaluated) is therefore an improvement this wave can measure.

## Files written (artifacts, relative to kama-shokunin)

- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/efe58e96-count.stdout` (line above) and `efe58e96-count.exit` (0)
- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/efe58e96-instrument.stderr` / `.exit` (exit 2)
- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/147f5bdd-count.stdout` / `.exit` (0)
- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/147f5bdd-instrument.stderr` / `.exit` (exit 2)
- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/147f5bdd-instrument-replicate.stderr` / `.exit` (exit 2)
- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/147f5bdd-only-M10-M11.stderr`
- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/147f5bdd-only-M11.stderr`
- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/147f5bdd-only-M10.json`
- `.ufo/waves/round-25/a2-build/out/ExecC1BaseRun/efe58e96-grid-pristine.out`, `147f5bdd-grid-pristine.out`
- `.ufo/waves/round-25/a2-build/advice/ExecC1BaseRun.md` (this report)

## Risks / notes

- A full `--json` run at these revisions takes ~6 minutes (pristine + ten mutant grid runs); any automated gate should budget >6 minutes, or it will kill the run mid-mutant (as my first two attempts did).
- Two of my killed attempts left `isolation-mutants-*` temp directories under `/tmp` (process SIGKILL before `TemporaryDirectory` cleanup). They are junk, not evidence; I did not delete other seats' temp dirs.
- The count measure counts literal occurrences with `str.count`, so the wrapped M11 call reads as 0 occurrences — that is the registered definition and matches the preregistered before-value.
