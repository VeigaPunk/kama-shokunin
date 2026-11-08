# MT01ProbeMutants — C1 mutation test (round 94, w1)

## Scope
Fourteen single-point mutants of the M1 probe's GGUF-verdict code (`tools/kama-probe.sh` @
a27656a4 = M1 = a27656a454b1a2364f8b6e55f42fbca8c2e86ee4; M1 probe sha256
27065a5c487ec819a975cc96d3c990ab5161d0e55d82be02a87dde86974ed3b4). Each mutant is the full M1
file with one behaviour-bearing edit; every file was bash -n and py-compile checked. Each mutant
was run through the frozen C1 counter (`tools/round94-router-budget.py`, 19 cells, two passes,
`--burners 32 --runs 1`) and the C1 harm counter (`tools/round89-unloadable-cells.py`, 11 cells).
Unmutated M1 was run through both as the baseline. Nothing in the lane was modified; nothing was installed.

## Commands and outputs (exit codes)
Baseline (probe from `git show a27656a4`, load1 190.64):
`python3 tools/round94-router-budget.py --repo . --rev a27656a4 --work <scratch>/base94 --burners 32 --runs 1`
→ `ROUTER_BUDGET cells=19 mismatches=0 positive_mismatches=0 load_cells=19 load_stable=1 probe=rev`
exit 0. `round89-unloadable-cells.py --probe-file <M1 bytes>` → `cells=11 mismatches=0
positive_mismatches=0`, exit 0 (load1 374.65).
Mutants: 41 94-attempts → 7 exit 0 (survivors), 7 exit 1 (killed), 27 exit 2 (counter guard, NOTE-3);
44 89-attempts → 12 exit 0, 3 exit 1 (M03/M07/M13), 29 exit 2 (DEFECT-4, pre-isolation). Per-mutant
table: `out/MT01ProbeMutants/mutants.tsv`; every attempt log is in `out/MT01ProbeMutants/logs/`.

| mutant | change (M1 line) | 94 | killing cells | 89 |
|---|---|---|---|---|
| M01 | deadline set once at import +4.0 s, reset removed (570,606) | KILLED | R04 nat, R08 nat+load → MODEL_OK; UNSTABLE R04/R05/T01 | pass |
| M02 | reset moved to the `files` loop — one 15 s budget per invocation (607→782) | **SURVIVED** | none (R08 10.67 s nat / 15.48 s load) | pass |
| M03 | `PER_FILE_SECONDS = 0.0` (569) | KILLED | R01-R08, P04, T01; pm=2 | KILLED U4 |
| M04 | `PER_FILE_SECONDS = 3600.0` (569) | **SURVIVED** | none | pass |
| M05 | `MAX_STEPS = 10**15` (568) | **SURVIVED** | none | pass |
| M06 | memo key = path string (599) | KILLED | R05/R05b 60.8 s → MODEL_OK, R07 35 s > BUDGET | pass |
| M07 | `gguf_state` OSError → "-" (595) | KILLED | P03, P04; pm=2 | KILLED U1, U5 |
| M08 | `SEEN.clear()` per candidate (593) | KILLED | R03,R04,R05,R06,P02,P02b,P05,R05b,R07; pm=3 | pass |
| M09 | wrapper `timeout 60`→`8` (820) | KILLED | R08 load 8.67 s → MODEL_OK; stable=0 | pass |
| M10 | wrapper `timeout 60`→`3600` (820) | **SURVIVED** | none | pass |
| M11 | wall deadline removed, MAX_STEPS only (634,684) | **SURVIVED** | none | pass |
| M12 | memo key drops `st_ctime_ns` (599) | **SURVIVED** | none | pass |
| M13 | `FileNotFoundError` → "-" (610) | KILLED | P03, P04; pm=2 | KILLED U1, U5 |
| M14 | count overflow → "invalid" (711) | **SURVIVED** | none | pass |

Survivor classification (distinguishing input in `out/.../direct/`):
- **M02 — coverage gap, and the claim's F1 control is false.** F1 reads "a per-call (not per-file)
  deadline → the synthetic-load cell red"; M02 is that shape and is green at both loads (load1 323.04).
  Distinguishing input: one `files` invocation naming 8 distinct slow invalid GGUFs (R08 uses 4, and
  4 fit inside one 15 s budget) — base all `invalid`, M02 s5-s7 `-` (= loadable), 30.46 s vs 15.22 s.
  Independently reproduced by the L1's own battery: `controls/c1-forgeries.out` line F3_shared_deadline
  is byte-identical in shape and reports `mismatches=0`.
- **M12 — coverage gap.** Input: one invocation, three candidates (invalid file, long-parse filler,
  hard link), in-place same-size rewrite with mtime restored at t=6 s. Base re-parses → `-`; M12
  serves the stale `invalid`. T01 uses three invocations, so it cannot see a ctime-less key.
- **M14 — coverage gap.** 48,000,000-byte sparse header declaring n_tensors=2,000,000 (size
  pre-check passes) → base `-`, M14 `invalid` in 0.12 s. Deterministic and load-free.
- **M10 — coverage gap.** Input: ~20-entry listing of distinct slow invalid files (total ≈75 s,
  under the counter's KILL=120 s). Base is killed by the 60 s wrapper with the python stdout buffer
  lost → all `-` (worst case of the disclosed limit; the same mechanism is measured in M06's R05
  `MODEL_OK` at 60.84 s); M10 completes → MODEL_UNLOADED. No frozen cell reaches 60 s.
- **M04, M05, M11 — equivalent (measured, not a gap).** Measured step cost 3.6-4.2 µs/step puts
  MAX_STEPS=4,000,000 at 14.5-16.8 s, i.e. the two bounds are crossed within ±10% of each other, and
  both raise Unknown → `-`. Measured on a 900k-tensor header: base `-` at 14.74 s (wall), M04 `-` at
  15.89 s (MAX_STEPS), M05 `-` at 15.20 s (wall). Separating M05 needs >4M steps in <15 s (host ≥1.4x
  faster per step); separating M04 needs a sub-4M-step parse over 15 s (≥1.4x slower). The frozen
  cells never approach either bound (slowest fixture 0.6M steps, 2.5-3.8 s).

## Findings
- **BLOCKER-1 — the claim's F1 forgery control does not hold.** `plans/round-94-claims.md:43-44`: "F1
  a per-call (not per-file) deadline → the synthetic-load cell red". Measured: M02 (reset moved to the
  invocation) exits 0 at load1 323.04, and the L1's own `controls/c1-forgeries.out` F3_shared_deadline
  reports `mismatches=0`. The counter's only multi-file cell (R08, 4 distinct slow files) fits a single
  15 s budget; the per-file reset is therefore ungraded. The C1 predicate itself still reproduces
  (baseline above), so this is a control/coverage statement, not a predicate failure — but F1 must not
  be reported as red.
- **DEFECT-1 — the do-nothing control receipt is an exit-2.** `controls/c1-base.out` is
  `ROUTER_BUDGET could-not-evaluate: fixture slow.gguf: base loader state '-', designed 'invalid'` +
  `C1BASE_EXIT=2`, not the "r93 counter's positive_mismatches=1 reproduction" that
  `plans/round-94-claims.md:39-41` describes. `controls/c1-base-load.out` is the same exit-2 text.
- **DEFECT-2 — a named control file does not exist.** Claims:42 names `controls/c1-forgeries.py`; only
  `.out` exists, and its own header says "the named pre-freeze python battery does not exist".
- **DEFECT-3 — the K2 harm baseline is 2 suites, not 7.** `controls/harm-base.out` =
  `tests=77 passes=77 failures=0` + `RESULT pass=30 fail=0` (tests/probe-verdicts/check.py,
  tools/test-snapshot.sh). Claims:46-49 name seven suites including `round89-unloadable-cells.py`,
  whose baseline is absent — I measured it at M1: `cells=11 mismatches=0 positive_mismatches=0`, exit 0.
- **DEFECT-4 — the round-89 harm counter is unrunnable for every seat after 00:11.** The pinned router
  lists cache-sourced models, and `~/.cache/huggingface/hub/models--ggml-org--embeddinggemma-300M-qat-
  q4_0-GGUF` (created 2026-11-08 00:11 by another seat, 265 MB) makes `start()`'s identity guard abort
  with `entry 'ggml-org/embeddinggemma-300M-qat-q4_0-GGUF:Q4_0' is not owned by this run` → rc=2
  (22 measured attempts, M08/M09/M03/M13/M02/M04/M05/M10/M11/M12/M14). Workaround, measured and used
  here: run with `LLAMA_CACHE=<scratch>/empty HF_HOME=<scratch>/empty`. The K2 gate needs this or the
  harm suite cannot produce a receipt.
- **NOTE-1 — the disclosed limit misstates the counter.** Claims:51 says "the counter's own 20 s cell
  budget"; `tools/round94-router-budget.py:108` is `BUDGET = 30.0` (and cells are graded `dt <= BUDGET`).
- **NOTE-2 — K1 as worded is narrower than the counter's exit condition.** K1 is
  "positive_mismatches>0 or load_stable=0"; M06 fails with mismatches=3, positive_mismatches=0,
  load_stable=1 and still exits 1 (`bad>0`). A mutant that only reddens R05/R05b/R07 would pass K1 as
  written; the predicate's `exit 0` requirement is what catches it.
- **NOTE-3 — the counter can only grade in a host-load band.** 25 of 41 94-attempts exited 2 with
  `fixture slow.gguf: base loader state '-', designed 'invalid'` at load1 240-424 (the base probe's own
  15 s per-file slice was exceeded while parsing the counter's own fixture; 4 of 5 retries succeeded
  unchanged in the same band). Consequence for the claim's wording: at that load ONE slow invalid GGUF
  still flips to undecided (`-` → loadable), i.e. the r93 SC02 F1 shape returns at ~15 s per file —
  C1 removes starvation, not the load-dependence of a single file's own slice.
- **NOTE-4 — the control receipts postdate the freeze.** Claims:15-16 say every control "was executed
  before this file was committed"; the controls files carry mtimes 2026-11-08 01:34-01:40 while F
  (285f1783) is 2026-11-07 23:05:23, and at 01:41 all of them were untracked (`git ls-tree -r 285f1783
  .ufo/waves/round-94/` contains only `plans/round-94-claims.md`); the L1 began committing them during
  integration (c1-base.out shows as `M` against HEAD). They must all be in the integration commit or
  K2/K3 have no receipt.
- **NOTE-5 — cross-seat corroboration runs both ways.** My M06 and M09 probes are byte-identical
  (sha256 464606c8…, 103547e5…) to the L1 battery's F2_pathstring_memo and F5_wrapper8, and both
  agents' runs kill them with the same cells; CR01's F6 (no dev/ino) and F7 (NO_OPEN → "-") survivors
  are the complements of my M12 (no ctime) and M07 (OSError → "-", killed). Nothing in the lane's
  control set covers either survivor family.

## Deliverables
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-94/w1/out/MT01ProbeMutants/`:
`mutants/M01..M14/kama-probe.sh` + `mutants/Mxx.diff` (unified vs M1) + `mutants/BASE/`,
`mutants.tsv`, `logs/*.out` (every counter attempt incl. the 27 guard failures),
`direct/{m02-eight-slow,m12-invocation-rewrite,m14-count-overflow,m04-m05-m11-bounds}.txt`, `scripts/`
(build-distinct.py, build-slow.py, direct-check.py, m12-race.py, probe-state.sh, run-mutants.sh,
run89.sh, run94.sh, run-rest.sh, M1-probe.sh).

VERDICT: partial — C1's predicate reproduces at M1 (19 cells, mismatches=0, positive_mismatches=0, load_stable=1, exit 0) and 7/14 mutants die, but the claim's F1 control is false (M02 has the same shape and is green at load1 323, matching CR01's F3 survivor), 4 survivors are coverage gaps with separating inputs (8-file listing, mid-invocation rewrite, 2M-tensor header, 20-file listing), and the named do-nothing/forgery receipts are an exit-2 and a non-existent script.
