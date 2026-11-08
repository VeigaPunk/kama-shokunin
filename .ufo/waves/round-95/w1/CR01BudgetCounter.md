# CR01BudgetCounter — C1 frozen-counter attack (kama round 95 w1)

## Scope
Attacked `tools/round95-router-budget.py` (sha256 `9e1da6f4…e429733c`, unchanged since freeze
`c798e831`) at M1 `f63256607916cdeb35580a7af315b5f4b54eba18`. The counter was run with
`--probe-file` on copies of `tools/kama-probe.sh` at M1 (sha256 `436d994c…7931b722`); each
forgery is the M1 probe with one minimal edit (`probes/DIFFS.txt`). All runs used my own scratch
work dirs; no lane file was edited. Host load1 82–146 during the runs. Counter baseline (M1 probe,
full defaults, runs=2): exit 0, `cells=10 mismatches=0 positive_mismatches=0 load_cells=10
load_stable=1`, `w03_seconds=168.0`, load-pass W03 check 279.85 s against the counter's own
`KILL=400`.

"Met" below = the counter prints `mismatches=0 positive_mismatches=0 load_cells=10
load_stable=1` and exits 0. `--probe-file` always prints `probe=override`, so these runs do not
satisfy the literal `probe=rev` token; they exercise the same 10-cell grading as the `--rev` path.

## Commands and outputs (true exit codes; logs in `out/logs/`)
| id | flags after `--repo . --rev f6325660 --work <scratch> --probe-file probes/<f>` | exit | printed aggregate |
|---|---|---|---|
| base M1 | (none), runs=2 | 0 | cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1; w03=168.0 |
| F1a shared 4 s | --allow-clock --skip-load --runs 1 | 1 | cells=10 mismatches=5 positive_mismatches=4 load_stable=1; w03=5.2 |
| F2 no ctime | --allow-clock --skip-load --runs 1 | 0 | cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1; w03=192.4 |
| F3 MAX_STEPS 1.5M, default | --runs 1 | 2 | `could-not-evaluate: W03 natural pass 70.1s < 1.2 x 60s` |
| F3 graded | --allow-clock --skip-load --runs 1 --slow-files 8 | 1 | cells=10 mismatches=5 positive_mismatches=4 load_stable=1; w03=16.5 |
| F4 no MAX_META | --runs 1 (two passes) | 0 | cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1; w03=204.8 |
| F5 const 60, default | --runs 1 | 2 | `could-not-evaluate: W03 natural pass 60.6s < 1.2 x 60s` |
| F5 graded | --allow-clock --skip-load --runs 1 | 1 | cells=10 mismatches=1 positive_mismatches=1 load_stable=1; w03=60.5 |
| G1 burners 0 | --burners 0 --runs 1 | not run (round filed) | — |
| G2 counter copy, W06 expects `router-model-absent` | --allow-clock --skip-load --runs 1 --slow-files 8 | 1 | cells=10 mismatches=1 positive_mismatches=1 load_stable=1 |
| G3 skip-load receipt | --allow-clock --skip-load --runs 1 --slow-files 8 | 0 | cells=10 mismatches=0 positive_mismatches=0 load_cells=10 load_stable=1; `burners=64` printed |
| F6 unreadable→invalid | --runs 1 | not completed (natural pass green, W03 99.2 s; load pass reaped at filing) | — |
| F7 count shortcut | --runs 1 | not run (round filed) | — |
| F1b shared 600 s | --runs 1 | not run (round filed) | — |

Killed/survived: base, F4, F2, G3 = met/survived; F1a, F3-graded, F5-graded, G2 = red/killed;
F3-default, F5-default = exit 2 (could-not-evaluate); F6/F7/F1b/G1 = not run to completion. The
in-flight F6 run was reaped at filing (job exit 137): its 64 `while True: pass` burners and all
descendants were SIGKILLed by PID tree, re-scan of `/proc` found 0 alive and 0 leaked, `pgrep -af
run-met.sh` empty.

## Findings

BLOCKER 1 (F2 met/survived): W10 cannot observe the memo key it claims to grade. The cell runs
three separate `bash kama-probe.sh check` processes (`tools/round95-router-budget.py:321-345`),
while `SEEN` is process-local (`tools/kama-probe.sh:600-607`); the ctime key is never consulted
across the rewrite, and `v1` is not graded (`:345`). Direct proof of the capability loss (the r93
RV01 shape: one call, body `[X, slow, X]`, same-size rewrite with mtime restored during slow's
parse): M1 `0 - | 1 invalid | 2 invalid`, F2 `0 - | 1 invalid | 2 -` on 3/3 runs — the stale
`ok` is served in the loadable/false-green direction (`logs/f2-ctime.out`). The frozen cell that
names the ctime key is met while the key is gone. (`--skip-load` was used for speed; the memo is
rebuilt per probe process, so no loaded pass can change this cell, and F4 shows the two-pass
path is gradeable on this host.)

BLOCKER 2 (F4 met/survived): no cell reaches a header position above `MAX_META` (fixtures have
<24 MB headers), so removing both `MAX_META` checks leaves all 10 cells byte-identical (exit 0,
two passes). At a 600 MB header position M1 returns `-` and F4 returns `invalid` (measured,
`logs/oracle-micro-test.out`): the position/work bound the plan names is ungraded.

BLOCKER 3 (F6 incomplete, evidence at probe level): no cell contains an unreadable file. Changing
the three unreadable `return "-"` branches to `return "invalid"` (`tools/kama-probe.sh:616,622,626`)
flips a mode-000 file from `-` (round-89 undecidable→loadable) to `invalid` (measured, same log).
Its natural pass was green at filing (W03 99.2 s); the full two-pass run did not finish.

BLOCKER 4 (F7 not run; probe-level proof): the only valid fixtures have ≤2 tensors (`ok.gguf`,
`ok2.gguf`, counter `:295-300`), so a probe returning `invalid` for every GGUF declaring >2
tensors passes W04/W05 unchanged. Measured: a valid 3-tensor GGUF with data is `-` on M1 and
`invalid` on F7 — every real model (hundreds of tensors) would be false-unloaded. The counter's
own oracle shares the shortcut (`fixture_class`: `n_tensors > 2 → invalid`, `:156-171`), so it
cannot catch it.

BLOCKER 5 (F1b not run; F1a met the guard only because of its value): the `DEADLINE` guard is a
byte-substring test (`counter:390`), and F1a/F1b carry a renamed `time.monotonic()` shared
deadline with no such token. At 4 s it reddens (W01/W02/W03/W08 red; a single slow file already
takes 4.98 s at load1 144). A 600 s shared deadline is inside the probe's own derived 620 s
wrapper for W03 and was not run; the counter has no mechanism to distinguish it except a cell
cost that this host does not reach.

DEFECT 1 — the counter's wall clock is tighter than the probe's derived limit. `KILL=400`
(`counter:85`) caps each check; the probe's pass limit for the 40-candidate W03 is
`20+15*40=620 s` (`tools/kama-probe.sh:829`). Measured W03 checks: 279.85 s (base load) and
231.79 s (F4 load) — 58–70 % of KILL at load1≈100–136. At ~1.4× more load the harness truncates
the honest probe and records a mismatch, the same truncation disease the counter was built to
redden.

DEFECT 2 — the margin guard is load-dependent and swallows the exact round-94 defect. F5's
constant `timeout 60` always ends W03 at ≈60 s, so `w03 < 1.25*60` (`counter:404`) makes the
default invocation exit 2, not 1, for the regression the counter must redden; grading needs
`--allow-clock`, which also disables the DEADLINE guard. F3's 70.1 s vs the 75 s threshold is a
load-dependent coin flip (exit 2 vs graded red). Docstring/comments say "1.5 x 60 s"
(`:52,400`) while `MARGIN=1.25` (`:90`).

DEFECT 3 — the receipt misstates what ran. `--skip-load` sets `loaded = natural` (`:409-410`) and
still prints `load_cells=10 load_stable=1 burners=64` (`:438-440`) although no loaded pass ran and
no burner was started (G3 exit 0); `--burners 0` would compare two natural passes (G1 not run).
The frozen predicate prefix is satisfiable with the load axis disabled, and the loaded pass's
`load1` is never recorded (`load1_nat` only, `:440`).

DEFECT 4 (G2): the cell comparison is two-sided for `mismatches` (`all(v==wv and r==wr)`, `:314`):
an expectation the probe can never print reddens (exit 1, mismatches=1, positive=1). But
`positive_mismatches` excludes W09 and W10 (`:435`), so a W10 failure would print
`positive_mismatches=0` while `mismatches=1`.

NOTE 1 — the fixture oracle is a count shortcut, not a validity oracle: it calls a valid 3-tensor
GGUF `invalid` and a truncated 24-byte GGUF `ok` (measured), and it never grades probe output; it
only self-checks the generator. It also raises `PermissionError` on an unreadable fixture
(`:165`).

NOTE 2 — the verdict is a function of `(bytes, dev, ino, size, mtime, ctime)`, not bytes alone
(`tools/kama-probe.sh:605`); on coarse-timestamp filesystems the r93 window widens (carried r93
NOTE-1), and no frozen cell can test it (BLOCKER 1).

## Deliverables
`probes/probe-{M1,BASE,F1a,F1b,F2,F3,F4,F5,F6,F7}.sh`, `probes/DIFFS.txt`,
`round95-router-budget-G2.py`, `logs/` (all runs), `logs/oracle-micro-test.out`,
`logs/f2-ctime.out`, `scripts/{run-cheap.sh,run-met.sh,oracle-test.py,f2-ctime.py}`.

VERDICT: falsified — F2 and F4 score exit 0 (mismatches=0, load_stable=1) while removing protections the claim names (ctime memo key; MAX_META), so the frozen cells are met by probes that are not byte-decided; KILL/margin/skip-load defects weaken the receipt further.
