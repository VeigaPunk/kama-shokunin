VERDICT: confirm — the repaired combine/exit logic and the fresh official artifact reproduce (family-b rerun: 0 divergences), with residuals limited to a stale selftest-kill docstring, no full-enumeration check, and truncated FC-target kill evidence, none of which changes a verdict.

## Evidence (executed in /tmp/kama-r18-res-ResidCounterC2; lane untouched)
1. `combine_arms` (survivors.py:976-985), rows = selftest arm, cols = main arm:
   | killed => killed | survived => killed | inconclusive => killed |
   | survived => killed | survived => survived | inconclusive => inconclusive |
   | inconclusive => killed | inconclusive => inconclusive | inconclusive => inconclusive |
   Inconclusive main + killed *targeted* selftest = `killed` (the repaired seam); inconclusive-only = `inconclusive`, never `survived`/pass. Real classifiers: `main_arm(good, exit-2)=inconclusive`, `selftest_arm(target problem)=killed` → `combine=killed`; unrelated-failure selftest → `inconclusive` → `combine=inconclusive`.
2. `python3 .ufo/waves/round-18/c2/survivors.py --selftest` → exit 0, `selftest: 60/60 checks passed`, 43.21 s, incl. "(b) targeted selftest kill survives an other-arm exit 2" and "(b/c) unrelated selftest failure is inconclusive".
3. `--family b --json --out /tmp/.../family-b.json` → exit 0, 479.7 s, 16 runs, own_faults [], before {survived 3} → after {killed 3}, inconclusive 0/0. Official vs rerun, per mutant (frozen→current): FC-target survived→killed, FC-f6cache survived→killed, FC-f0gate survived→killed; `why` strings and `mutant_sha256` identical; **0 divergences**.
4. Synthetic attacks through the real `run_count()` (fake family-b finisher; real count/witness/exit code): all-inconclusive → exit 2, reasons name all 3; all-killed → 0; all-survived → 1; 2 survived + 1 inconclusive → 2 (names FC-f0gate); before=killed → 2 (3 witness mismatches).
5. Official artifact: tool sha `87cad1ca…` == copy bytes == HEAD bytes (`git diff HEAD -- survivors.py` empty); 15 ids = FROZEN_EXPECTED ids, no dupes/drops; after {killed 11, correct 1, handled 3}; inconclusive before/after 0; own_faults []; witnesses 15, mismatches 0; `count()` recompute == `counts`; exit-rule replay → 0; `.exit` file `exit=0`; stdout == JSON; 42 runs, 0 spawn_error/timeout, argv[0] == recorded `/usr/bin/python3` 3.14.8; bind guard 1464 binds, 0 protected hits, nothing listening. Main-arm claims re-derived from embedded baselines agree for all 6 family-b side entries. Direct mutant runs: frozen selftests exit 0/passed; current mutants exit 1 with the named problem (FC-target problem #2 = "target-conjunct attribution"; FC-f6cache = F6 shared cache).

## Findings (severity order)
1. **medium — docstring kill rule ≠ code.** Docstring :34/:45: family (b)/(c) killed iff the selftest exits non-zero where the unmutated copy exits 0; `selftest_arm` (:928-953) requires the named title literal and returns inconclusive otherwise (asserted by the selftest). Outcomes unaffected here (all 3 kills are name-matched), but the declared contract is stale.
2. **medium — no full-enumeration check (ConnectTameshi D4 open).** FC-f6cache is killed by a selftest reporting `wrapper_checks: 32` vs pristine 35 (artifact tail; direct runs agree). `selftest_arm` ignores matrix_tests/rows_checked/wrapper_checks: a synthetic early abort (matrix_tests 1, rows_checked 0, wrapper_checks 0) with the target literal returns `killed`, so an aborted selftest can read as a targeted kill.
3. **low — FC-target kill not re-derivable from the artifact.** `selftest.stdout_tail` (600 B) truncates the literal to "onjunct attribution"; only `why` asserts the match. A direct run shows the full problems list. Retain the matched problem line.
4. **low — `counts.after.total` folds inconclusive in** (it is "not in GOOD"; ConnectTameshi D3). Exit 2 blocks any pass containing an inconclusive, so no false pass, but a kill rate must be killed/(killed+survived).
5. **low — doc drift:** docstring claims 22 fc suites / 44 runs; artifact has 20 fc-main + 8 fc-selftest + 6 AO + 2 provenance + 6 crash = 42 (shared baseline memoized by `Runner.submit` on `(argv,cwd)`).
6. **scope — denominator label.** `named_universe` reads "round-17 published named survivors", but a-e omit the two controls.py survivors round-17 published (MutControlsSelf c/d, round-17.md:290). They are killed 3/3 in `runs/c1-self-mutants.json`; a global claim needs the union, not C2's 15.
7. **latent** — `combine_arms([]) == "survived"` (`all()` on empty); unreachable (always two arms), fails safe, but should be `inconclusive`.

## Limits
- Only family b was rerun in the copy (479.7 s); a/c/d/e were reviewed via the official artifact with `count()`, `main_arm` and the exit rule recomputed from its embedded evidence (not re-executed).
- No lane writes except this report; copy and /tmp mirrors deleted. Pre-existing `/tmp/kama-c2-survivors-*` dirs are dated 2026-10-20 20:16–20:33 (earlier runs), not this artifact; this run's teardown reports `scratch_removed: true`, no marked stragglers.
- Not tested: the 1800 s fc-main cap, `--jobs > 1`, or a fresh wave-2 denominator (declared excluded).
