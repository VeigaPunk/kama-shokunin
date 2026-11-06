# MT01ProbeMutants — round-89 C1 mutation probe (operability)

## Scope

Mutation-tested the C1 change in `tools/kama-probe.sh` at M=`4f9eacf720aa59ed806b31b758571e364658179b`
(blob sha256 `a4f496bb0ed931792641171a1269a91a8307dce5d534d5f4ee03daba01a7ddaf`, identical to the lane
working-tree file): the `router_entries` file-state Python (magic, version rules, counts-fit, alignment,
n_dims, block divisibility, contiguity, data-past-EOF, unknown type `-`, budgets, `args[0]` locality,
relative-path skip, path-flag list) and `router_refine` (unloadable vs unloaded precedence, autoload gate,
loading precedence). 31 single-point mutants, each one exact-substring replacement, one diff hunk, `bash -n`
exit 0, sha256 recorded. Each was measured by the frozen counter (11 live b12177 cells) and by
`tests/probe-verdicts/check.py` (72 tests). No tracked lane file was modified (read-only `git show` only).

## Commands and outputs (true exit codes)

1. Baseline, M bytes: counter exit 0, `cells=11 mismatches=0 positive_mismatches=0` (`base/counter.out`, 16.4 s);
   check.py exit 0, `tests=72 passes=72 failures=0` (`base/check.out`).
2. Per mutant: `python3 tools/round89-unloadable-cells.py --repo <lane> --rev 4f9eacf7… --work <scratch>/runs/<m>
   --probe-file mutants/<m>.sh`, then `python3 tests/probe-verdicts/check.py --probe mutants/<m>.sh`.
   All 31: `bash -n` exit 0; every counter line's `probe_sha256` equals that mutant's sha256 (asserted while
   building `results.tsv`), so the measured bytes are proven to be the mutant bytes.
   Result: counter killed 8/31 (exit 1); check.py killed 0/31 (exit 0, `72/72` on all 31).
3. Witness harness: `python3 witness.py` exit 0, `witness_cases=31 distinct=31 non_distinct=0` (`witness.out`).
4. Post-mutation baseline on the lane's own bytes (`--probe-file kama-shokunin/tools/kama-probe.sh`): counter
   exit 0, `cells=11 mismatches=0 positive_mismatches=0` (`base/counter-after.out`); lane file and
   `git show M:tools/kama-probe.sh` both sha256 `a4f496bb…`.
5. Table: `results.tsv` (mutant, sha12, counter exit, cells, mismatches, positive_mismatches, bad cell,
   check.py exit/passes/failures, verdict).

## Findings

1. **DEFECT (frozen detector, not the probe): the counter compares verdicts only.** `for cid, exp, code, got,
   reason in rows: ok = exp == got` (`tools/round89-unloadable-cells.py:308-309`); `reason` is printed but never
   asserted, and `positive_mismatches` is likewise verdict-only. Mutant **M23** stops consulting autoload for
   unloadable entries (`tools/kama-probe.sh:714`), so U1–U5 print `MODEL_UNLOADED reason=router-unloaded`
   instead of the claimed `router-model-missing`/`router-model-invalid`; the counter still passes with
   `mismatches=0 positive_mismatches=0`, exit 0 (`runs/M23-autoload-only-for-unloaded/counter.out:1-5,12`).
   Witness `W23`: M=`MODEL_UNLOADED/router-model-invalid` vs mutant=`MODEL_UNLOADED/router-unloaded`.
   The C1 heading/rule advertise those reason strings; the frozen predicate cannot see their loss.
2. **DEFECT: the counter never exercises the wildcard path.** Every cell is graded with `--expect <concrete
   mid>` (counter lines 251–296), so four refine mutants that only differ when several entries match survive:
   M26 (`-|loaded` no longer short-circuits, kama-probe.sh:712), M27 (`down` last-wins, :708), M28
   (unloadable before loading, :720–721), M29 (loading value last-wins, :720). Witnesses W26–W29 show distinct
   output (M28/W28 even flips the verdict LOADING→UNLOADED). A held-out cell would need `--expect '*'`; the
   counter's `oracle()` always POSTs a concrete model id, so no frozen cell can kill these.
3. **DEFECT: single-check removals survive because every corrupt cell is invalid for several reasons.** Counter
   kills are only M04 (counts-fit, via U3), M12/M13/M30/M31 (valid-file parse, via P1), M15 (P4), M24 (N1),
   M25 (P3). Escaped with 11/11 `ok=1`: M01 (magic gate), M02 (version 1), M03 (version 4), M05 (alignment
   power-of-two), M06 (n_dims>4), M07 (`ne[0]%block`), M08 (contiguity), M09 (data-past-EOF weakened to
   offset-only). U2/U3/U4 remain `invalid` through a second rule, so the header checks are individually
   unverified. Each is killed by a held-out cell of its own class on an autoload router (oracle 500
   `failed to load`): M01 GGML magic, M02 v1, M03 v4, M05 alignment 3, M06 5 dims, M07 `ne[0]%block`, M08
   non-contiguous offsets, M09 near-end truncation (the claims' named held-out class).
4. **DEFECT: `tests/probe-verdicts/check.py` is blind to the round-89 logic** — all 31 mutants pass 72/72,
   exit 0. The K2 harm check `check.py 72/72` is a regression guard for older behaviour and corroborates
   nothing about C1's file-state/refine code (`base/check.out` vs `runs/*/check.out`).
5. **NOTE — the harm guard on the real model is live.** M12 (default alignment 64), M13 (+1 block), M30
   (u32 string length), M31 (string-array off-by-one) are all killed with `positive_mismatches=1` on P1
   (`runs/M12…/counter.out:6` etc.), and M15/M24/M25 on P4/N1/P3. The stories260K header parse is genuinely
   load-bearing: 19 KVs, max key length 38, types {4,6,8,9}; string/alignment/block accounting changes flip
   the valid cell to red.
6. **NOTE — M04 (counts-fit off) is killed by U3 only** because the noise header's random counts exceed
   `MAX_KV`/`MAX_TENSORS` and become `-` → MODEL_OK (`runs/M04-counts-fit-off/counter.out:3`). U3 is the only
   cell exercising the budget branches.
7. **NOTE — false-red classes escape and are only rule-protected, not cell-protected.** M21 (unreadable file →
   `invalid`), M11 (>64-byte metadata key forced to `general.alignment`), M22 (>MAX_KV budget → `invalid`),
   M10 (unknown type → `invalid`), M14 (`args[0]` isfile check dropped). Only a loadable model the probe cannot
   parse would kill them (probe-unreadable but router-readable, a legal long metadata key, >100k KVs, a type
   absent from `QSIZES`, or a router whose binary path is not local). M14 is reachable today for any remote
   router: M returns no change, the mutant reports `router-model-missing`
   (`witness.out` lines W10, W11, W14, W21, W22).
8. **NOTE — remaining escapes are false-green classes.** M16 (missing `--model-draft`), M17 (`-m` dropped from
   `PATH_FLAGS`), M18 (`--model=` form dropped), M20 (`S_ISREG` guard dropped → directory at path returns `-`).
   A held-out cell = that file/args on an autoload router (oracle 500 `failed to load`): M correct, mutant
   MODEL_OK `router-unloaded-autoload`. M19 swaps missing/invalid precedence: reason-only, needs a reason-level
   assertion.
   Witnesses are `witness/stub/Wxx-*.json` + `witness/files/*` (18 crafted inputs: 16 files, one of them
   000-mode, plus a directory at a model path); they prove probe-output divergence, not oracle harm — the crafted header-valid files are
   not loadable models, so a held-out cell must still pair the class with the router's real 500 answer
   (`witness.out` lines W16–W20).

Escaped (23): M01, M02, M03, M05, M06, M07, M08, M09, M10, M11, M14, M16, M17, M18, M19, M20, M21, M22, M23,
M26, M27, M28, M29.
Killed (8): M04 (U3), M12 (P1, +), M13 (P1, +), M15 (P4, +), M24 (N1, +), M25 (P3, +), M30 (P1, +), M31 (P1, +).

## Deliverables

`.ufo/waves/round-89/w1/out/MT01ProbeMutants/`:
- `probe-M.sh`, `mutants.sha256`, `results.tsv`, `mk_mutants.py`, `witness.py`, `witness.out`,
  `extracted_entries.py`
- `mutants/M01…M31*.sh` (31 single-hunk mutants), `runs/<mutant>/{counter.out,check.out,counter.rc,check.rc}`
- `witness/stub/*.json` (31 stub router bodies), `witness/files/*` (18 crafted GGUFs/dir/000-mode file)
- `base/{counter.out,check.out,counter-after.out}` (baseline before, check.py baseline, lane-byte re-run)

VERDICT: partial — the frozen C1 counter reproduces 11/11 at M before and after mutation, but 23/31 single-point mutants escape it (31/31 escape check.py) and M23 drops the claimed `router-model-missing`/`router-model-invalid` reasons while still printing `mismatches=0`, so C1's verdict flip is corroborated and its diagnostic half is not.
