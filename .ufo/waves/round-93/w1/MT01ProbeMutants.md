# MT01ProbeMutants — C1 mutation test (round 93 w1)

## Scope
Mutation probe of C1 as frozen in `plans/round-93-claims.md`: the memo code added at M1
`fe5f031cb1b9d33e1160360d892149b8ac3c7771` in `tools/kama-probe.sh` (`SEEN`, `gguf_state`, and the
`gguf_parse` paths it defers to). 16 single-point mutants (`>=12` required), each byte-identical to the
M1 probe except one behaviour-bearing snippet, built by `out/MT01ProbeMutants/mt-mutants.py` (asserts the
needle occurs exactly once; every mutant re-parsed as bash + Python: 16/16 OK). Detectors: the frozen C1
counter `tools/round93-router-repeat.py` at M1 via `--probe-file` (prints `probe=override`, cannot meet the
predicate), plus `tools/round89-unloadable-cells.py` at M1. Four supplementary gap cells
(`mt-gapcells.py`, explicitly NOT a counter) classify survivors.

Measured revisions: M1 `fe5f031cb1b9d33e1160360d892149b8ac3c7771`, probe blob sha256
`159c80688c5d903ea776e3e548a980f64e6ddedf43b8d7a35ab4724acab48dbb`; BASE `5af794958b0f…`,
probe sha256 `36631d498901c40f76e1c36471166fecb71a2e84124c4795c301e9e8e5cbf962`. Lane tip sampled
read-only for the transfer check: `00a0246d35d3e8d1b041a80a92c09bd94274b751`, probe sha256
`1e21c1fb5d3fac1d6abc06ef1c541531e261acba36fb6678c1fb3fe9591e29c3` (M1 + `st_ctime_ns` in the key,
commit b3765799 / RV01 DEFECT-1). Lane `tools/kama-probe.sh` was never written; M1 bytes were taken with
`git show` and every mutant is a copy in the out dir (restoration evidence: `git -C <lane> status` shows no
`tools/` change; the working tree hash above is the L1's own tip, not mine).

## Commands and outputs (exit codes)
- Baseline, load1=61: `python3 tools/round93-router-repeat.py --repo <lane> --rev fe5f031cb… --work <sc>` →
  `ROUTER_REPEAT cells=10 mismatches=0 positive_mismatches=0 probe=rev … load1=61.46`, **exit 0**, 26 s.
- Baseline harm, load1=62: `… --rev fe5f031cb… round89-unloadable-cells.py` →
  `cells=11 mismatches=0 positive_mismatches=0`, **exit 0**, 11.8 s.
- Sweep (twice, 23:44–23:54 load1 49–76 and 23:59–00:10 load1 47–75), per mutant:
  `python3 tools/round93-router-repeat.py --repo <lane> --rev fe5f031cb… --work <sc>/<m> --probe-file
  mut-<m>.sh` and `python3 tools/round89-unloadable-cells.py … --probe-file mut-<m>.sh`. Both sweeps gave
  the **same kill set** and the same exit codes: m05 1, m06 1, m10 1, m11 1, all others 0.
- Gap cells, load1 82–100: `python3 mt-gapcells.py --probe-file <p> --work <sc> --runs 2 [--distinct N]`
  on M1, the tip probe, and the survivors named below; receipts `mt-gapcells-*.out`, `mt-gapcells-tip.out`.
- Table (receipts `mut-*.r93.out`, `mut-*.r89.out`; `mutants-summary.tsv`; `mutants-sha256.txt`).

| # | mutant (single point) | frozen C1 counter | round-89 harm | class |
|---|---|---|---|---|
| m01 | key drops `st_dev` | survives, 0/0 | 0 | coverage gap — needs two mounts with colliding (ino,size,mtime); not constructible here |
| m02 | key drops `st_ino` | survives, 0/0 | 0 | **coverage gap, killer found: GD** |
| m03 | key drops `st_size` | survives, 0/0 | 0 | equivalent — (dev,ino) identifies a live file; size/mtime only guard inode reuse |
| m04 | key drops `st_mtime_ns` | survives, 0/0 | 0 | coverage gap — needs an in-place same-size rewrite mid-call (live writer) |
| m05 | key = path string | **killed R05** (`MODEL_OK/…-autoload` 4.52 s ×3) | 0 | killed |
| m06 | no memo | **killed R02,R03,R04,R05,R06** (5 mismatches) | 0 | killed |
| m07 | memo keeps only `invalid` | survives, 0/0, slowest cell 1.13 s | inconclusive→0 | coverage gap, **latency only** (GB 1.81 s → 4.66 s) |
| m08 | regular/NO_OPEN guard after memo | survives, 0/0 | 0 | equivalent — inode uniqueness keeps a non-regular file from sharing a regular file's identity |
| m09 | `os.stat` → `os.lstat` | survives, 0/0; R05 2.02 s | 0 | **coverage gap, killer found: GA** |
| m10 | `OSError` → `"-"` | **killed P03,P04** (`positive_mismatches=2`) | **2** (U1, U5) | killed by both |
| m11 | `SEEN` cleared per candidate | **killed R03,R04,R05,R06** (sweep 1) / R02–R06 (sweep 2) | 0 | killed; R02 marginal (finding 8) |
| m12 | `mtime_ns` → `ctime_ns` | survives, 0/0 | 0 | equivalent on any static listing (strictly fresher) |
| m13 | `mtime` at 1 s | survives, 0/0 | 0 | coverage gap — needs a same-size in-place rewrite inside one second |
| m14 | non-regular half of the guard removed | survives, 0/0 | 0 | equivalent (same argument as m08) |
| m15 | `except Unknown: return "invalid"` | survives, 0/0 | 0 | **coverage gap, killer found: GC-12** |
| m16 | per-call deadline removed | survives, 0/0 | 0 | **coverage gap, killer found: GC-10** |

Gap cells (M1 → mutant, `--runs 2`):- **GA** 16 symlink path strings naming one slow invalid file: M1 `MODEL_UNLOADED/router-model-invalid`
  1.51/1.91 s vs **m09 `MODEL_OK/router-unloaded-autoload` 4.91/4.93 s**.
- **GD** an invalid 192-byte file and the valid `ok.gguf` (192 B) with equal `st_mtime_ns`:
  M1 `MODEL_OK/router-unloaded-autoload` 0.60/0.84 s vs **m02 `MODEL_UNLOADED/router-model-invalid`**.
- **GC-12** 12 distinct copies of the slow invalid file: M1 `MODEL_OK/…-autoload` 4.69/4.65 s vs
  **m15 `MODEL_UNLOADED/router-model-invalid` 4.53/4.47 s**.
- **GC-10** 10 distinct copies: M1 `MODEL_OK` 4.56/4.58 s vs **m16 `MODEL_UNLOADED/router-model-invalid`
  6.49/6.84 s**.
- **GB** 16 entries naming one slow *valid* file: M1 1.81/1.79 s, m07 4.66/4.74 s, same verdict.
- Tip probe (`1e21c1fb…`) on the same four cells: GA invalid 0.82 s, GB `MODEL_OK` 0.81 s, GC `MODEL_OK`
  4.25 s, GD `MODEL_OK` 0.23 s — the coverage findings transfer to shipped bytes.

## Findings
1. **DEFECT (counter coverage).** The frozen counter grades *path-string* keying (m05 → R05) but not
   *identity* keying: m02, m03, m04 each survive all 10 cells 0/0 (`mut-m02-drop-ino.r93.out`,
   `mut-m03-drop-size.r93.out`, `mut-m04-drop-mtime.r93.out`). R05 cannot separate them because its 33
   aliases all resolve to the same (dev,ino,size,mtime) — as they must. killer for m02: GD
   (`mt-gapcells-M1-m02-m07-m09-m15-m16.out`); `M1 MODEL_OK` vs m02 `MODEL_UNLOADED/router-model-invalid`
   for two files of equal size and mtime.
2. **DEFECT (counter coverage).** m09 (`lstat` instead of `stat`) survives: R05 carries exactly one symlink
   among 33 alias strings, used twice, so the two extra parses cost 2.02 s of the 4 s deadline
   (`mut-m09-lstat.r93.out` R05 ok=1, both sweeps). GA (16 symlinks) flips it to
   `MODEL_OK/router-unloaded-autoload` 4.9 s. `identity = … inode` is therefore not exercised for
   symlinked listings by any frozen cell.
3. **DEFECT (counter coverage, aligned to a disclosed limit).** The claim's rule "undecidable stays
   loadable" (round 89) is untested: m15 grades an aborted parse `invalid` and survives 0/0; GC-12 flips
   the verdict from `MODEL_OK` to `MODEL_UNLOADED/router-model-invalid`. A future edit could tighten
   undecided → invalid with the frozen counter still green.
4. **NOTE.** m16 (no deadline) also survives; GC-10 shows the deadline is what bounds the disclosed limit
   (M1 aborts at 4 s and stays loadable; m16 completes and returns `MODEL_UNLOADED`). Both GC shapes are
   "many DISTINCT slow files", the limit the claim already discloses — so these are guard gaps, not
   predicate failures.
5. **NOTE (latency-only blind spot).** m07 (memo keeps only `invalid`) is verdict-invisible: 0/0 in every
   frozen cell, and identical verdicts in GA/GC/GD. Its only effect is cost — GB 1.81 s → 4.66 s for 16
   repeats of one slow *valid* file — and it cannot be turned into a verdict difference, because a valid
   file's state is `-` and never reaches `nbad == ncand`; the 4 s deadline caps the added cost below the
   counter's 20 s per-run budget. Killing it needs a per-cell wall-clock bound, not a verdict cell. This
   is the same class as carried R4/CR01/MT01.
6. **NOTE (harm-suite robustness).** One round-89 run (m07, sweep 1, load1 62) died with an unhandled
   `ConnectionRefusedError` on child D's oracle POST and no `ROUTER_UNLOADABLE cells=` line
   (`mut-m07-memo-invalid-only.r89.out`), i.e. exit 1 with a traceback instead of exit 2. Solo re-run at
   load1 78: `cells=11 mismatches=0 positive_mismatches=0`, exit 0
   (`mut-m07-memo-invalid-only.rerun.out`). Environment fault, not a mutant effect; it means the harm
   suite can report a red for its own child startup.
7. **NOTE (corroboration).** m10 is the one mutant both detectors kill, with the same flip
   (`MODEL_UNLOADED/router-model-missing` → `MODEL_OK/router-unloaded-autoload`) on P03/P04 and on
   U1-missing-preset/U5-deleted-after-list — the C1 positive cells are not redundant with the harm suite,
   and both fire on the round-89 rule.
8. **NOTE (marginal cell).** m11's R02 (8 candidates, one parse each, ≈4.0 s against a 4 s deadline) passed
   in sweep 1 (load1 52) and failed in sweep 2 (load1 54); R03–R06 are decisive in both. Consistent with
   the claim's own note that the flip count moves with host load; no kill classification rests on R02.
9. **NOTE (tip).** The shipped tip adds `st_ctime_ns`, which makes m04/m13 equivalent at the tip while
   m01/m02/m09/m15/m16 stay uncovered — the counter still has no two-distinct-files and no
   undecided-parse cell. This is the same hole RV01 used to find DEFECT-1 by review, not by counter.

No mutant produced an environment fault on the C1 counter: 32/32 runs printed `cells=10`, no
`could-not-evaluate`, all under budget (slowest 8.45 s vs 20 s).

## Deliverables (out dir `.ufo/waves/round-93/w1/out/MT01ProbeMutants/`)
`mt-mutants.py`, `mt-gapcells.py`, `probe-M1.sh`, 16 × `mut-mNN-*.sh`, `mut-*.r93.out` (32 runs),
`mut-*.r89.out` + `.rerun.out`, `mt-gapcells-M1-m02-m07-m09-m15-m16.out`,
`mt-gapcells-M1-m16-distinct10.out`, `mt-gapcells-tip.out`, `mutants-summary.tsv`, `mutants-sha256.txt`.
No tool installed or upgraded; no model passed; scratch `/fast/scratch/hyaku/kama-r93/MT01ProbeMutants/`
removed after the receipts were copied.

VERDICT: holds — C1's predicate reproduced twice at M1 (10/10, 0 positive, exit 0) and the frozen counter kills every mutant that changes the repeat count's share of the deadline (4/16), but 12/16 single-point mutants survive and 4 of them flip a verdict on plausible listings (GD/GA/GC), so the counter under-guards the identity fields and the undecided-stays-loadable rule rather than the claim being false.
