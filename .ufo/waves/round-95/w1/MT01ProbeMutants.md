# MT01ProbeMutants — round-95 C1 mutation sweep (leaf, mutation-tester)

## Scope
- 12 single-semantic-change mutants of `tools/kama-probe.sh` at the revision my tasking named,
  **M1 = f6325660** (blob sha256 `436d994c…`), as copies under
  `.ufo/waves/round-95/w1/out/MT01ProbeMutants/mutants/`. No tracked lane file was written.
- Each mutant graded with the frozen counter `tools/round95-router-budget.py`
  (sha256 `9e1da6f4…` = freeze commit `c798e831`) via `--probe-file`, `--rev f6325660`.
- Two mutants the counter cannot see (M06 clock, M04/M05 MAX_META) plus the separating inputs of
  M01/M02 (step bound) and M09 (ctime) were separated with a direct end-to-end probe
  (`mtdrv.py`: lane-owned stub router on a free 127.0.0.1 port, `check --json`, verdict+reason).
- **HEAD moved during the sweep**: `c810f51e` (C1 repair) and `a9b5014c`; probe is now
  sha256 `b49d961a…` (+46/−13). Nothing below was re-run at M1b (L1 stop). Receipts grade
  f6325660 only.

## Commands and outputs (exit codes)
- `python3 make_mutants.py` → pristine + 12 mutants; pristine sha `436d994c…` ==
  `git show f6325660:tools/kama-probe.sh`; `bash -n` and compile of every embedded `ROUTER_PY`
  exit 0; `mutants/DIFF.txt` shows exactly one intended hunk per mutant.
- Matched grading invocation (identical for baseline and mutants):
  `python3 tools/round95-router-budget.py --repo <lane> --rev f6325660 --work <scratch>/work-<L>
   --probe-file mutants/<M>.sh --runs 1 --skip-load` (`--allow-clock` only where noted).
- Baseline `pristine-skip` rc=0: `cells=10 mismatches=0 positive_mismatches=0 load_cells=10
  load_stable=1 … w03_seconds=210.8 load1_nat=109.44`.
- Per-mutant output files: `receipts/counter-<M>.out`; exit codes and probe shas:
  `receipts/counter-exit-codes.txt`.

| M | one semantic change | rc | decisive counter line | verdict |
|---|---|---|---|---|
| M01 | `if steps[0] > MAX_STEPS` in `need()` deleted | 0 | `cells=10 mismatches=0` (w03=206.3) | **SURVIVED** |
| M02 | `MAX_STEPS 4_000_000 → 4_000_000_000` | 0 | `cells=10 mismatches=0` (w03=224.8) | **SURVIVED** |
| M03 | step counter shared for the whole pass (not per file) | 2 | `W02 ok=0 … MODEL_OK/6.31s`, `W03 ok=0 … MODEL_OK/5.99s`, then `could-not-evaluate: W03 6.0s < 1.2 x 60s` | **INCONCLUSIVE** (red cells, guard); `--allow-clock` rc=1 `mismatches=2` |
| M04 | both `MAX_META` checks deleted | 0 | `cells=10 mismatches=0` (w03=215.9) | **SURVIVED** |
| M05 | `MAX_META 512MiB → 1GiB` | 0 | `cells=10 mismatches=0` (w03=164.4) | **SURVIVED** |
| M06 | 15 s per-file residue clock re-added (`DEADLINE`, `(steps[0]&0xFFF)==0`) | 2 | `could-not-evaluate: … probe still decides on a wall clock` (byte guard) | **REFUSED**; with `--allow-clock` rc=0 `cells=10 mismatches=0` → **SURVIVED**; direct probe KILLS it |
| M07 | `local limit=$((20 + 15 * ncand))` → `20 + 15` | 2 | `W02 ok=0 … MODEL_OK/35.94s`, `W03 ok=0 … MODEL_OK/36.02s`, guard | **INCONCLUSIVE**; `--allow-clock` rc=1 `mismatches=2` |
| M08 | … → `20 + ncand` | 2 | `W03 ok=0 … MODEL_OK/60.34s`, guard `60.3s < 1.2 x 60s` | **INCONCLUSIVE**; `--allow-clock` rc=1 `mismatches=2` |
| M09 | memo key drops `st_ctime_ns` | 0 | `cells=10 mismatches=0` | **SURVIVED**; direct race probe KILLS it |
| M10 | `file_state` `-` fallthrough → `invalid` | 1 | `cells=10 mismatches=4`; `W04`,`W05`,`W09`,`W10` ok=0 on both passes | **KILLED** |
| M11 | `skip_strings` charge (`n//64`, chunk steps) deleted | 0 | `cells=10 mismatches=0` | **SURVIVED** (observationally inert, see F5) |
| M12 | `MAX_STEPS 4_000_000 → 1_000_000` | 2 | `W01`,`W02`,`W03`,`W08`,`W10` ok=0, then guard `25.6s < 1.2 x 60s` | **INCONCLUSIVE**; `--allow-clock` rc=1 `mismatches=5` |

Direct behavioural probes (all receipts in `receipts/direct-*`):
- M04/M05, sparse GGUF (logical 600 000 053 B, header position 600 000 045 > 512 MiB):
  pristine `MODEL_OK/router-unloaded-autoload`, M04 `MODEL_UNLOADED/router-model-invalid`,
  M05 `MODEL_UNLOADED/router-model-invalid` — the same bytes, different state.
- M01/M02, 900 000-tensor GGUF (4.5M steps, ≤ MAX_TENSORS): pristine `MODEL_OK` (the disclosed
  `-`), M01 `MODEL_UNLOADED`, M02 `MODEL_UNLOADED`.
- M09, one invocation naming one inode twice, in-place same-size rewrite + mtime restored at
  t=0.5 s: pristine 3/3 `MODEL_OK`, M09 3/3 `MODEL_UNLOADED`.
- M06, probe+burners pinned to one core: dose 0 → `invalid` (3.69 s), 4 → `invalid` (12.21 s),
  8 → `MODEL_OK` (16.77 s), 16 → `MODEL_OK` (18.00 s); pristine dose 0 → `invalid`, dose 16 →
  `invalid` (26.91 s). Burners reaped, `pgrep` empty each time.

## Findings
- **F1 DEFECT (coverage):** the two bounds C1 *names* are graded by no frozen cell. MAX_STEPS
  removed (M01) or raised (M02), MAX_META removed (M04) or doubled (M05) all return
  `cells=10 mismatches=0` (receipts/counter-M01/M02/M04/M05*.out), yet each changes the verdict
  on a listing a real router could serve (above). The cells cover MAX_TENSORS (W09) and the
  wrapper, not the step/byte budgets, so "work is bounded by MAX_STEPS / MAX_META" is unmeasured.
- **F2 DEFECT (counter claim vs behaviour):** W10 is labelled "(ctime key)" but cannot grade it.
  W10 issues three separate `check` invocations (counter lines ≈373–392), each a fresh
  `bash kama-probe.sh` → fresh `ROUTER_PY` process → empty `SEEN`; M09 keeps W10 green
  (rc=0). Within one invocation the key is load-bearing (direct race, 3/3 vs 3/3 above), so the
  cell grades cross-invocation re-read, not the memo key, and the r93 ctime protection is
  regression-blind.
- **F3 DEFECT (guard masks red cells):** the margin guard measures the W03 duration of the probe
  *under test*, so probes that truncate (M07 36.0 s, M08 60.3 s, M03 6.0 s) or bound work earlier
  (M12 25.6 s) exit 2 without the predicate being evaluated. Three of five behaviourally-killed
  mutants (M03/M07/M12, plus M08) therefore read "could-not-evaluate", not red: a regression to
  `timeout 60` is not caught by K1 (`mismatches>0`). Only `--allow-clock` skips the guard, and its
  label asserts the opposite of a truncation mutant.
- **F4 DEFECT (nominal load cells):** `--skip-load` still prints `load_cells=10 load_stable=1 …
  burners=64` (value is the flag, not evidence); the receipt can only be told apart by the absent
  `load` cell lines. The clock mutant survives the natural pass (w03 248.5 s ≈ 6.2 s/file, its
  15 s slice never fires) and is killed only by direct pinned contention (8-way, above). The
  lane's `measured/c1-override.out` likewise used `--burners 0` (no synthetic load). Whether the
  counter's 64-burner pass reaches the ~2.5× slowdown needed on this host is unmeasured here.
- **F5 NOTE:** M11 is observationally inert on f6325660 — the biggest chargeable string array
  under MAX_META is 64M strings → `n//64` = 1 048 576 steps < 4M
  (`receipts/bound-arithmetic.txt`); no separating input exists with both constants intact. It was
  still an unsound *work* bound (matches the M1b repair `c810f51e`).
- **F6 NOTE:** M01/M02/M04/M05 flip `-`→`invalid` (fail-closed): no false green. M06 flips
  `invalid`→`-`, the fail-open direction the round-89 rule grades loadable — the one no cell caught.
- **F7 NOTE:** the M07/M08 family overlaps the M1b entry→path pricing (`20 + 25 * npaths`); my
  mutants target the entry-priced allowance they were written against.
- **F8 NOTE (seat):** two invocations carried an empty `$M` (no probe bytes, rc=1); logged and
  superseded in `receipts/counter-exit-codes.txt`; they graded nothing.

## Deliverables
- `mutants/` — pristine + 12 mutant probe copies, `DIFF.txt` (single-hunk proof), sha256s.
- `make_mutants.py`, `mtdrv.py` (direct probe driver), `run_counters.sh`, `run_batch.sh`.
- `receipts/` — 17 counter receipts + `counter-exit-codes.txt`, 6 direct-probe receipts
  (two transcribed verbatim), `bound-arithmetic.txt`.

VERDICT: partial — the pristine C1 predicate is green at f6325660, but 7/12 mutants survive the frozen cells (4 of them with demonstrated byte-decided verdict flips, 1 the ctime key, 1 the clock), 4 more are refused by the margin guard instead of killed, and only M10 is killed by the counter's own exit.
