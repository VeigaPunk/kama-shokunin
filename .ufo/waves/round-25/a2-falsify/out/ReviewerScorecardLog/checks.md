# ReviewerScorecardLog: command log

Pinned tip: fa3b62ae6475d111eb466d79af616aeebb08bbb9 (SCORECARD.md 1252-1295, LOG.md 1635-1678).
Lane HEAD at review time: 46be41c. That commit adds only `a2-falsify/advice/swarm-registry.json`,
`a2-falsify/dispatch.json`, `a2-falsify/spec.json` and `report-draft.md`; it does not touch
SCORECARD.md or LOG.md (`git show --stat 46be41c`, exit 0).
Scratch clone: /fast/scratch/hyaku/kama-r25a2w2/ReviewerScorecardLog/clone (checked out at fa3b62ae;
`git rev-parse HEAD` confirmed).

| # | Check | Where run | Exit | Result |
|---|---|---|---|---|
| 1 | C1 counting command (preregistration.json C1.command) | clone at efe58e96 | 0 | `registered 27 stale 2 ['M11-listing-surrogates', 'M17-ref-shadow']` |
| 2 | same command | clone at 1fc41e34 | 0 | `registered 28 stale 0 []` |
| 3 | same command | clone at fa3b62ae | 0 | `registered 28 stale 0 []` |
| 4 | `python3 .ufo/waves/round-25/count-c2.py` | clone at fa3b62ae | 0 | `registered 14 observed 14 bound True missing []` |
| 5 | `python3 .ufo/waves/round-25/count-c2.py /nonexistent.json` | clone | 2 | `cannot read receipt ...`, no count printed |
| 6 | sha256 of receipt at 5c95c8f, at fa3b62ae, and in lane worktree | lane (git show) | 0 | all `78c51385991b1261359503e604adaf09113476d82ef7691f999d18abc673b98c` |
| 7 | sha256 of fixture server binary and model | host, read only | 0 | server `b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`; model `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d` (matches receipt model_sha256 and K1 server_sha256) |
| 8 | sha256 of tools/kama-context-capacity.py at 46fb04bd and fa3b62ae | lane (git show) | 0 | both `589841cd4d4890eeb22a5582f78b2bb4c7dcc961253c465fbc9e6d899adc4c27` (= receipt tool.sha256) |
| 9 | c1-tip-mutants.json fields | lane | 0 | pristine passed; mutants 28; killed 26; surviving [M17-ref-shadow, M20-log-sha-shape]; retired 4; c1-tip-mutants.exit `exit=0`; .err 0 bytes |
| 10 | sha256 of final/c1 JSON vs ExecC1TipReplicate copy | lane | 0 | both `75ad1e03dff31571dcfe85eca26d7154e509daa60ca092238d6942459c56eda1`, 5959 bytes |
| 11 | runs.json.gz decompressed size and sha256 | lane (git show, zcat) | 0 | 11141804 bytes; `38e4ab053e5cc7bfc53bdd8d9479a206d29dd37ccbc36f7f352582f42d766a09` |
| 12 | isolation-mutants.py diff 1fc41e34..fa3b62ae | lane (commit-to-commit diff) | 0 | 7 insertions, lines 33-39, inside the docstring that closes at line 45; auditor path not in the diff |
| 13 | `validate kama` of sources-census (fleet script, read only, cwd clone) | clone | 0 | 0 E codes; 29 W04 warnings; stderr 0 bytes; copy in out/ReviewerScorecardLog/census-validate-113-rows.out |
| 14 | SOURCES.md rows: 147f5bdd vs fa3b62ae | lane (git show) | 0 | rows 105 -> 113; A 100 -> 108; cells equal to `mined` 86 -> 94; S106-S113 present; lane working copy sha256 equals fa3b62ae copy (`45810d49...`) |
| 15 | verbatim quote: SCORECARD 1270 vs CriticC1Calibration.md line 73 | clone | 0 | exact match |
| 16 | receipt cells: L1 two 500s; L2 and L3 four 200s in total; K1 and X2 props 2048 and total_slots 4; pools 2048 vs 8192; X1 props 2048; X3 props 512 | git show of receipt | 0 | as stated in LOG 1661-1663 |
| 17 | tool CELLS args vs receipt cell args | clone (import, no server) | 0 | equal for all 14 ids |
| 18 | probe_git_shadow.out lines 5-13 | clone | 0 | abbreviation shadow: predicate fires True (lines 7, 9); full 40-hex token: fires False (line 13) |
| 19 | ed1cc3a-tipM17-causal.json | clone | 0 | failed_rows F13; grid_exit 1 |
| 20 | line-number lookups (grep -n) for every SCORECARD and LOG citation | clone and scratch copies | 0 | as cited in the report |
| 21 | `git status --short | head -5` in lane, first command | lane | 0 | read-only status; it can refresh the index stat cache (disclosed) |

Not run, by design:
- `python3 tools/kama-context-capacity.py --out .ufo/waves/round-25/final/context-capacity-receipt.json`
  (the capability row's demonstration). It starts llama-server children on 47400-47419 and writes the
  committed receipt and its 70 raw files, so it was not executed.
- The C1 full mutant run (about 16 minutes). The committed run was compared byte for byte with the
  1fc41e34 replicate (check 10) instead.

No llama-server child was started. No tools were installed or upgraded. No git write was run in the lane.
