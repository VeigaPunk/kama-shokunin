# CR01BudgetCounter — round94-router-budget attack

## Scope

Tested the frozen C1 counter `tools/round94-router-budget.py` (19 cells,
19 cells at two loads) against forged `tools/kama-probe.sh` variants at
M1=`a27656a454b1a2364f8b6e55f42fbca8c2e86ee4`, plus the counter's own
fixture/burner/stability assumptions. All runs `--probe-file`
(`probe=override`; can never meet the predicate — these grade the
counter's teeth, not the predicate).

## Commands and outputs

- Base P0 control, `python3 tools/round94-router-budget.py --repo . --rev M1
  --work <scratch>/work --probe-file probe_base.sh --burners 32 --runs 2`
  → exit 0, `ROUTER_BUDGET cells=19 mismatches=0 positive_mismatches=0
  load_cells=19 load_stable=1 probe=override load1_nat=225.46 burners=32`
  (38 `ok=1` lines). `base.log`.
- Forgery sweep (same command, `--burners 16 --runs 1` unless noted):
  F1 basename memo → exit 1, `mismatches=3 positive_mismatches=1`
  (`F1_retry.log`); F2 path-string memo → exit 1, `mismatches=3`
  (`F2_pathstring_memo.log`); F3 shared deadline → exit 0
  (`F3_shared_deadline.log`); F4a MAX_STEPS=900k → exit 1,
  `mismatches=11 positive_mismatches=2`; F4b 500k → exit 1, same;
  F4c MAX_STEPS=1500k (`--burners 4`) → exit 0, `mismatches=0`
  (`F4c_1500k.log`); F5 wrapper `timeout 8` → exit 1, `mismatches=1
  load_stable=0`; F6 no-inode memo → exit 0 (`F6_no_inode_memo.log`);
  F7 NO_OPEN→`-` → exit 0 (`F7_noopen_dash.log`); F8 wrapper `timeout 30`
  → exit 0 (`F8_wrapper30.log`); F9 basename+size memo → exit 1,
  `mismatches=3 positive_mismatches=1`.
- Fixture probes (standalone ROUTER_PY): slow parse 1.29s at 150k tensors,
  0.22s at 15k (linear); instrumented step count `LOADSTEPS=900004` for
  slow.gguf; 8-distinct file ROUTER_PY sweep (honest all `invalid`, F3
  last two `-`); 300k-tensor discriminator (honest `invalid`, F4c `-`);
  equal-mtime P05 discriminator (honest `-` for b/slow.gguf valid,
  F6/F1 `invalid`); burner check `load1` 142→150 with 8 burners.

## Findings

- **BLOCKER-F3 counter does not grade the per-file deadline reset.**
  F3 (remove the `gguf_parse` deadline reset; shared 15s deadline from
  import) scores `mismatches=0 load_stable=1`. A shared deadline only
  bites once the listing's cumulative parse time exceeds 15s; R08's 4
  distinct slows total ~9.5s natural / ~9.4s loaded, never crossing it.
  Real worst cell it should fail: R08-distinct-slow-k4 (the designated
  distinguishing cell) under heavier host load, or any listing of ≥7
  distinct slow files — measured: 8 distinct slows → files 6–7 flip
  `invalid`→`-` (honest keeps all 8), so a real router listing with 8
  slow invalid files grades `MODEL_OK` (loadable, wrong) instead of
  `MODEL_UNLOADED`. Smallest safe correction: raise R08's file count so
  the cumulative parse exceeds the shared slice (e.g. R08 = 8 distinct
  slows), or add a long-tail cell; do not lower PER_FILE_SECONDS
  (would punish the honest probe under load). Evidence: `F3_shared_deadline.log:31`.
- **BLOCKER-F6 counter does not grade inode identity in the memo.**
  F6 (key `(size, mtime_ns, ctime_ns)`, no inode) scores `mismatches=0
  load_stable=1`. P05 builds `a/slow.gguf` then `b/slow.gguf`
  sequentially, so their `mtime_ns` differ and F6 accidentally
  distinguishes them. Any real listing whose same-basename pair shares
  size+timestamps — e.g. `cp -p` of a directory tree, `rsync -a`,
  model downloads unpacked together — gives the valid copy the invalid
  copy's cached state: 63 invalid + 1 same-mtime valid grades
  `MODEL_UNLOADED` instead of `MODEL_OK`. Measured standalone:
  equal-mtime pair → honest `0 invalid / 1 -`, F6 `0 invalid / 1
  invalid`. Smallest safe correction: make P05 force equal
  `st_mtime_ns` (and equal `st_ctime_ns` where possible) on the pair via
  `os.utime`, so only inode separates them. Evidence:
  `F6_no_inode_memo.log`, discriminator output in report text.
- **BLOCKER-F4c counter does not grade MAX_STEPS headroom.**
  MAX_STEPS=1500k scores `mismatches=0` (F4c_1500k.log). slow.gguf needs
  900004 of the honest 4M steps, so the counter's slowest file sits at
  22.5% of the bound; any forgery with bound >900k passes. Real listing
  with a 300k-tensor invalid file (~1.8M steps) grades `-`→`MODEL_OK`
  (wrong) under F4c vs `invalid`→`MODEL_UNLOADED` honest. The counter
  has no file between 150k and the 4M bound. (Note F4a=900k *is* caught
  — 900004 > 900000 — but a 1M/1.5M forgery is not.) Smallest safe
  correction: add a cell with a ~300k-tensor slow-invalid file, or shrink
  TENSORS/MAX_STEPS so the counter's slow file sits near the bound.
- **DEFECT-F7/F8 counter does not cover NO_OPEN or the wrapper ceiling.**
  F7 (return `-` for `/proc,/sys,/dev` paths instead of `invalid`) and
  F8 (wrapper `timeout 60`→`30`) both score `mismatches=0`. No cell
  names a NO_OPEN path or stacks enough distinct slows to approach 30s.
  Real: `-m /proc/self/mem` grades loadable under F7, invalid honest;
  an 8-slow listing under load needs ~30s+ and F8 kills it at 30s
  (fail-open → `MODEL_OK`, wrong) where the honest 60s completes.
  F5 (`timeout 8`) *is* caught (`load_stable=0` on R08) — so the
  wrapper is graded at 8 but not at 30. Smallest safe correction: add a
  NO_OPEN-path cell and a distinct-slow count that brackets 30s
  (e.g. 6–8 distinct slows, which the F3 discriminator already shows
  both shared-deadline and 30s-wrapper forgeries failing).
- **NOTE-correctly catches F1/F2/F4a/F4b/F5/F9.** Basename memo reds P05+aliases; path-string re-parses until the 60s wrapper kills (R05 flips at ~61s); 900k/500k red every slow cell; wrapper-8 flips R08 `load_stable=0`. Memo/deadline headroom is graded as far as it goes.
- **NOTE-counter checks (verified, they hold).** (1) slow.gguf is truly
  parsed to the end before `invalid`: linear timing 0.22s@15k → 1.29s@150k,
  header guard 3.6M < size 6.0M, invalid from the final offset check
  after all 150k tensor infos. (2) `start_burners` does raise contention:
  8 burners moved load1 142→150 and per-parse time roughly doubles
  (c1.out R01 2.4s→4.5s); load1 is ambient, not a delta proof, but the
  parse-time doubling is the real signal. (3) `load_stable` requires
  BOTH passes to agree *and* match expectation: counter
  `tools/round94-router-budget.py:537-543` (`nv != lv` → unstable;
  `cell_ok = ng and lg`). Runtime ~35 min at load1 150–260; two `could-not-evaluate` aborts were load noise.

## Deliverables

- Out dir: `.ufo/waves/round-94/w1/out/CR01BudgetCounter/`
- Forgery probes: `F1_basename_memo.sh`, `F2_pathstring_memo.sh`,
  `F3_shared_deadline.sh`, `F4a_MAXSTEPS_900k.sh`, `F4b_MAXSTEPS_500k.sh`,
  `F4c_MAXSTEPS_1500k.sh`, `F5_wrapper8.sh`, `F6_no_inode_memo.sh`,
  `F7_noopen_dash.sh`, `F8_wrapper30.sh`, `F9_basename_size_memo.sh`,
  `probe_base.sh` (each: git show M1 probe with one mechanism broken).
- Cell logs: `base.log`, `F1_retry.log`, `F2_pathstring_memo.log`,
  `F3_shared_deadline.log`, `F4a_MAXSTEPS_900k.log`, `F4b_MAXSTEPS_500k.log`,
  `F4c_1500k.log`, `F5_wrapper8.log`, `F6_no_inode_memo.log`,
  `F7_noopen_dash.log`, `F8_wrapper30.log`, `F9_basename_size_memo.log`.

VERDICT: holds — counter catches basename/path-string/low-MAX_STEPS/old-wrapper forgeries, but F3 shared-deadline, F6 no-inode memo, F4c MAX_STEPS=1.5M, F7 NO_OPEN, and F8 wrapper=30 all score mismatches=0 while misgrading real listings; R08/P05 need equal-mtime and longer-tail cells to bite
