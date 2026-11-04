# MT01Mutants — mutation report (kama round 72, wave 1)

Seat: `MT01Mutants`, role mutation-tester, axis **calibration**.
Frozen claim context: `plans/round-72-claims.md` §C1 (`ROUND_SCOPE`, cases A/B/C) and §C2
(`RECEIPT_TIP_BINDING`, classes `unbound|shifted|stale`), plus the C1 amendment that enters
the counter as the gate's arm 6 `round-scope`.
Verdict scope: this seat scores the **instruments' discriminative power**, not the round.
No frozen rule was edited; no lane byte was written outside this seat's own directory.

## 1. Subject bytes scored

| tool | sha256 | when scored |
|---|---|---|
| `tools/pre-report-gate.py` | `2c141b516fb8348d50db45b5934e4f4d1681aee46cfc6508924a0ee64727565c` | pinned, unchanged across the whole seat |
| `tools/round72-round-scope.py` | `45321056d621a3fe481b0e9179b694463cf08b2f6613b0f34cfd686f763aaec4` | pinned |
| `tools/round72-receipt-tip-binding.py` | `a9a4e8d30546a11e6d5165b566e856e4eb8cccb11d48c5526587fd3d859b2bbd` | pinned (`stable_run.py`) |

The gate and the scope module were stable. The **binding module changed three times while
this seat ran** (`94ae3b4a` → `ef3d6fd5` → `5ccc6120` → `a9a4e8d3`); each earlier family run
was discarded and the family re-run, and `stable_run.py` now re-runs a family until the lane
hash is identical before and after the run. Every verdict below is from the pinned hash, and
`finalize.py` refuses to publish if the lane hash differs from the scored copy.

## 2. Method (and why the verdicts mean something)

* Every tool is copied out of the lane into `$S/mut/pristine*`; each mutant is a **copy** of
  that pristine file with one exact-once textual replacement (a pre-image count ≠ 1 aborts the
  mutant, so a drifting source is reported rather than mis-scored), then `py_compile`-checked.
* Two detectors per mutant: the tool's **own `--selftest`**, and an **independent fixture
  battery** built in `$S/fixtures` (`git init` inside the scratch dir, toplevel asserted before
  the first commit, every later call `-C`-scoped).
* The pristine run is checked against the frozen predicate's own observables **before** any
  mutant is scored: `ROUND_SCOPE round=<N> cases=3 findings=<f>`, the named
  `ROUND_SCOPE_FINDING <case>` set, `RECEIPT_TIP_BINDING round=<N> cited= bound= unbound=
  shifted= stale=`, the named `RECEIPT_TIP_FINDING <class>` set, and the gate's
  `PRE_REPORT round=<N> arms=6 failed= uncommitted=` / `PRE_REPORT_SELFTEST pass= fail=`.
  Both module baselines and the gate baseline report `nonconforming=none`; a baseline failure
  would have been reported as inconclusive, not as a kill.
* Verdict is **baseline-relative**: a mutant is *killed* iff at least one observable (exit
  status, `findings`/`cited`/`bound`/`unbound`/`shifted`/`stale` counts, or the named case/class
  set) differs from pristine on the same fixture. Detail strings are free-form and never score.
* The fixture battery is deliberately wider than the shipped selftests at the exact boundaries
  the frozen predicate names — that is how the coverage gaps in §4 were found.

## 3. Result — 22 mutants, 22 killed, 0 survived

| tool | mutants | killed | survived |
|---|---|---|---|
| `pre-report-gate.py` (arm-6 wiring) | 4 | 4 | 0 |
| `round72-round-scope.py` | 9 | 9 | 0 |
| `round72-receipt-tip-binding.py` | 9 | 9 | 0 |

Full rows (id, mutation, verdict, detector that killed it) — machine-readable copy in
`mutants.tsv`; per-mutant observation in `logs/<id>.json` and `logs/<id>.diff`.

| id | mutation | killed by | the observable that moved |
|---|---|---|---|
| G1 | drop the `{round}` substitution in the gate | selftest + argv-probe | `PRE_REPORT_SELFTEST pass=0 fail=8`; the stub never receives `--round 72` |
| G2 | `return 0` on a fixture-build failure | build-failure-probe | forced `PATH` without `git`: pristine exit 2, mutant exit 0 |
| G3 | drop arm 6 from `ARM_SPECS` | selftest + argv-probe + round-clean-probe | verdict `arms=5`; round-scope stub never invoked |
| G4 | `-uall` → plain `--porcelain` in the round-clean arm | round-clean-probe | `uncommitted=1` vs `2` on an untracked directory |
| S1 | drop the `!! ` filter | selftest + `wave-uncommitted` + `allow-dir` | case set becomes `[ignored, stray]`, and `allow-dir` (documented clean) turns into a finding |
| S2 | `-uall` → plain status in the stray scan | fixture `stray-dir` | `findings=1` vs `2` (one collapsed directory record) |
| S3 | drop the round-label case | selftest + 3 label fixtures | exit 0 / `findings=0` where case `label` must be named |
| S4 | an allow-listed path counts as a finding | selftest + `allow-exact` + `allow-dir` | exit 1 where the allow-list must make it clean |
| S5 | drop `--ignored` from the ignored scan | selftest + `ignored` | exit 0 / no `ignored` finding |
| S6 | accept a heading anywhere in the plan | fixture `label-later` | exit 0 where the **first** heading names another round |
| S7 | exit 0 even when findings are named | selftest + 8 fixtures | every defect fixture exits 0 |
| S8 | drop the wave-dir pathspec from the ignored scan | fixture `ignored-root` | reports `ignored` for a path outside the wave dir (clean must be exit 0) |
| S9 | rename record keeps only the destination path | selftest + `rename` | `findings=1` vs `2` on `R  LOG.md -> LOG2.md` |
| B1 | drop the ancestor check | selftest + `nonancestor` | header naming a real non-ancestor commit is accepted as bound |
| B2 | `rev..tip` parsed as `tip..rev` | selftest + `shifted` | empty delta → exit 0 where `shifted` is required |
| B3 | skip brace expansion | selftest + `brace` | exit 2 (could-not-evaluate) vs clean `cited=2 bound=2` |
| B4 | header accepted anywhere in the receipt | fixture `late-header` | header on line 11 becomes `bound` instead of `unbound` |
| B5 | count every cited path as `bound` | selftest + 6 fixtures | `bound` printed equal to `cited` while `unbound`/`shifted`/`stale` are non-zero |
| B6 | never call a delta `shifted` | selftest + `shifted` | `tools/probe.py` in `rev..tip` accepted |
| B7 | absent receipt treated as `bound` | selftest + `stale` | exit 0 where `stale` is required |
| B8 | exit 0 even when findings are named | selftest + 6 fixtures | every defect fixture exits 0 |
| B9 | accept the first of two conflicting headers | fixture `conflict` | `# tip=<base>` + `# rev=<side>` becomes `bound` instead of `unbound` |

## 4. Calibration findings — five behaviors no shipped selftest exercises

These are **coverage findings, not contract changes**. Each mutant below survives the tool's
own `--selftest` and is killed only by an independently built fixture, so the instrument is
correct today but its shipped battery would not notice the regression.

1. **S2 — `-uall` in the stray scan.** The module's own stray fixture adds one untracked
   *file*, which both `git status --porcelain` and `-uall` count as one record. Fixture
   `scope-stray-dir` puts two files in a **fully untracked directory**: pristine `findings=2`,
   mutant `findings=1`. This is the same collapse the round-71 note measured (26 files vs 14
   entries) and is exactly what C1's case B exists to stop.
2. **S6 — "first heading" vs "any heading".** The shipped label fixtures are *missing* the
   plan or name the wrong round in the only heading. Fixture `scope-label-later` has
   `# kama round 71` first and `## kama round 72` later: the frozen predicate says the **first**
   heading must name the round, and only that fixture separates the two readings.
3. **S8 — the ignored scan's pathspec.** The shipped battery only plants an ignored file
   *inside* the wave dir. Fixture `scope-ignored-root` ignores `notes.log` at the repo root:
   pristine `files=0`, case C must stay silent; the mutant reports an `ignored` finding for a
   path outside the wave dir. The predicate's third clause is scoped to `.ufo/waves/round-<N>/`.
4. **B4 — the five-line header window.** The shipped fixtures either place the header on line 1
   or omit it. Fixture `bind-late-header` puts `# tip=<sha>` on line 11: pristine `unbound`,
   mutant `bound`. The frozen predicate allows only a `# tip=`/`# rev=` **header**, and the
   five-line window is the module's own (documented) reading of "header".
5. **B9 — two conflicting headers.** No shipped fixture carries both `# tip=` and `# rev=`
   naming different revisions. Fixture `bind-conflict` does: pristine `unbound` with the
   conflicting-header detail, mutant silently accepts the first one as `bound`.

Two more, in the gate's own selftest, surfaced by purpose-built probes:

6. **G2 — the gate's could-not-evaluate path is never exercised.** Its selftest always builds
   a valid fixture; the `return 2` on a fixture-build failure is untested. Forcing
   `PATH=/nonexistent-bin-dir` (so the fixture's `git init` raises `FileNotFoundError`) gives
   pristine exit 2; the mutant returns 0 — i.e. a broken fixture would have been reported as a
   pass.
7. **G4 — the gate's case (b) cannot see `-uall`.** Case (b) adds a single uncommitted file
   (`uncommitted=1` under both status forms). A fully untracked directory inside the wave dir
   is needed: pristine `uncommitted=2`, mutant `1`. The gate's round-clean arm inherits the
   same blind spot the C1 module was built to remove.

## 5. Containment and restoration evidence

* **No lane byte written by this seat.** All mutation happened on copies under
  `/fast/scratch/hyaku/kama-r72/MT01Mutants/mut/`; the lane's three tools were only read.
  Post-run `git -C <lane> status --porcelain -uall` shows this seat's untracked paths only
  under `.ufo/waves/round-72/w1/MT01Mutants/` (the tools' `M` entries are the authors' work,
  not this seat's).
* **No git mutation outside scratch.** Every fixture is a fresh `git init` inside
  `$S/fixtures/<case>/repo`, with `git rev-parse --show-toplevel` asserted equal to that
  directory before the first commit, its own throwaway identity
  (`-c user.name=fixture -c user.email=fixture@invalid`), and `-C <repo>` on every later call.
* **Restoration**: nothing in the lane needed restoring; the scratch root
  `/fast/scratch/hyaku/kama-r72/MT01Mutants` is deleted after the artifacts below were copied
  into the wave dir.
* **Tooling**: no install or upgrade was needed (`python3 3.14`, `git` already present).

## 6. Commands run and observed output (tails)

```
$ python3 fixtures.py            # builds 22 fixture repos under $S/fixtures
{"scope-clean": ".../fixtures/scope-clean/repo", ... }
$ git -C fixtures/scope-stray-dir/repo status --porcelain -uall | wc -l   -> 2
$ git -C fixtures/scope-stray-dir/repo status --porcelain       | wc -l   -> 1
$ git -C fixtures/scope-ignored/repo status --porcelain -uall --ignored -- .ufo/waves/round-72
!! .ufo/waves/round-72/scratch.log

$ python3 scope_mutants.py
BASELINE sha=45321056d621a3fe nonconforming=none
S1 killed ... S9 killed          (9 rows, all killed)

$ python3 bind_mutants.py
BASELINE sha=a9a4e8d30546a11e nonconforming=none
B1 killed ... B9 killed          (9 rows, all killed)

$ python3 gate_mutants.py
G1 killed: SELFTEST exit=1 PRE_REPORT_SELFTEST pass=0 fail=8
G2 killed: BUILDFAIL exit=0 (want 2)
G3 killed: SELFTEST exit=1 ... PROBE calls=[]
G4 killed: CLEANPROBE line='... uncommitted=1' != '... uncommitted=2'

$ python3 stable_run.py
scope: already scored at 45321056d621a3fe (bytes unchanged) -- skip
bind: PINNED at a9a4e8d30546a11e
gate: already scored at 2c141b516fb8348d (bytes unchanged) -- skip

$ python3 finalize.py
gate: lane=2c141b516fb8348d scored=2c141b516fb8348d OK
round72-round-scope.py: lane=45321056d621a3fe scored=45321056d621a3fe OK
round72-receipt-tip-binding.py: lane=a9a4e8d30546a11e scored=a9a4e8d30546a11e OK
rows=22 killed=22 survived=0 diffs=22

$ python3 classify.py
killed=22 selftest-only=[]
fixture-only=['S2', 'S6', 'S8', 'B4', 'B9']
```

Baseline lines actually observed (verbatim):

```
ROUND_SCOPE round=72 cases=3 findings=0                    # clean fixture, exit 0
RECEIPT_TIP_BINDING round=72 cited=1 bound=1 unbound=0 shifted=0 stale=0   # clean fixture, exit 0
PRE_REPORT_SELFTEST pass=8 fail=0                          # gate selftest, exit 0
PRE_REPORT round=72 arms=6 failed=0 uncommitted=0          # gate argv probe, exit 0
PRE_REPORT round=72 arms=6 failed=1 uncommitted=2          # gate clean probe, exit 1
```

## 7. Files written

* `.ufo/waves/round-72/w1/MT01Mutants/mutants.tsv` — 22 rows (header + one row per mutant:
  id, tool, mutation, verdict, command, evidence).
* `.ufo/waves/round-72/w1/MT01Mutants/logs/` — `{S,B,G}<n>.json` (per-fixture observables),
  `{S,B,G}<n>.log` (deviation list), `{S,B,G}<n>.diff` (pristine → mutant), the three
  `*-baseline.json` files, `kill-sources.tsv`, and `harness/` (the fixture builders and family
  runners, so every verdict above is reproducible).
* `.ufo/waves/round-72/w1/MT01Mutants.md` — this report.

## 8. Disagreements

None with the frozen claim. One measurement note for the round's own receipts: the C1 kill rule
lists "one uncommitted file at the repo root" for case B, and that fixture alone cannot
distinguish `-uall` from plain `--porcelain`; the `-uall` property is only observable with a
**fully untracked directory**. That is a fixture-shape remark about how the case should be
demonstrated, not a change to the rule.
