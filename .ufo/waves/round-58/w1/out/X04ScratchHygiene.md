# X04 Scratch hygiene — round 58 (kama), axes: operability + calibration

Env for every run: `HYAKU_SCRATCH` unset (`env` check: `[unset]`), `TMPDIR=<fresh empty dir under S>`;
lane `/home/vgpnk/Projects/shokunin/kama-shokunin` read only via `git -C … show/rev-parse`;
`S=/fast/scratch/hyaku/kama-r58/X04ScratchHygiene` (removed before yield).
Pins used: build tip `e4891d8a4c9c70e97124980c2ec9aee5762a7f0a` (lane HEAD had moved to `e4f207f5`; every read pinned),
manifest rev `941acf70583a2b3a1d33460b31967e0efd291f3e`. Tools were extracted from tip blobs and verified byte-identical
(`git hash-object` == blob): checker `02616f0f…`, c1 counter `ed2dfa49…`, c2 counter `99798397…`.

## Runs (fresh TMPDIR, HYAKU_SCRATCH unset); stdout+rc retained in seat dir
1. `TMPDIR=$S/tmp-checker python3 $S/tools/round58-battery-exec-check.py --repo <lane> --tip e4891d8a…`
   `present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True`, rc=0.
2. `TMPDIR=$S/tmp-c1 python3 $S/tools/round58-c1-counter.py --repo <lane> --tip e4891d8a… --checker-blob e4891d8a…:tools/round58-battery-exec-check.py`
   `genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, rc=0 (15/15 detail lines: genuine/B1–B3 accept exit=0, N01–N11 reject exit=1).
3. `TMPDIR=$S/tmp-c2 python3 $S/tools/round58-c2-counter.py --repo <lane> --tip e4891d8a… --manifest-rev 941acf70…`
   `claim=N=57 token=rejected-honest-stop maxN=57 manifest=rejected-honest-stop`, `r42=0 missing=0 stale=0 verdict=0 including=0 mismatches=0 met=True`, rc=0.

## Scratch hygiene result (the assigned check)
- TMPDIR listing before/after exit: **0 / 0 entries** in every run (checker, checker-under-strace, C1, C2). No work tree remains;
  traces show each work root created and removed, e.g. `mkdir("$TMPDIR/exec-vh423fn3",0700)=0` then `rmdir("$TMPDIR/exec-vh423fn3")=0`
  (C1: 15 exec- roots + 1 c1- root rmdir'd; C2: c2- root + r41 child dirs rmdir'd).
- `/tmp` top-level listing diff per run window: **empty** for checker run 1 and C1. Two windows each picked up one or two unrelated,
  transient entries that did not come from these tools: `/tmp/kotoba-governance-05_izo7u` (checker run 2), `/tmp/k74-c1census-gync9s1s`
  and `/tmp/omp-jq-aa44b1e4-….err` (C2 window); all three were gone when re-checked seconds later (sibling seat / harness activity).
- `strace -f -e trace=mkdir,mkdirat,openat,unlink,rmdir` per run: write-ish syscalls under `/tmp` = **0**; any `/tmp` path mention = **0**.
  Writes went only under TMPDIR: `openat O_CREAT` = 2 (checker) / 541 (C1) / 1908 (C2); mkdirs = 1 / 331 / 124.
- No writes to the lane tree: 0 `O_CREAT|O_WRONLY|O_RDWR|mkdir|unlink|rmdir` under `kama-shokunin` in all three traces
  (C1 lane opens were 21 × `O_RDONLY`).
- Pre-existing ambient `/tmp` files (`c1-3bc0b10.json`, `c1-46xxx.txt`, `c2-receipt.json`, `exec-c2-diff-check.diff`, …; 13 total)
  predate all runs and were unchanged afterwards; none were produced by these runs.

## Limits found (neither refutes a frozen predicate as measured)
- L1 attack: `tools/round58-c2-counter.py` does not create its TMPDIR root (passes it straight to `tempfile.TemporaryDirectory(dir=…)`).
  With `TMPDIR` pointing at a nonexistent path it dies with an uncaught `FileNotFoundError` traceback, rc=1, instead of its documented
  rc=2 "could not evaluate". Checker and C1 counter call `os.makedirs(root)` and pass the same probe; they leave the empty TMPDIR root
  itself behind (created by them), but no work tree.
- L2 attack: C2's r42 child writes `__pycache__` inside its temp dir (`mkdir("…/c2-mi72okpo/__pycache__")`); it was removed with the dir
  in every observed run, but cleanup is `TemporaryDirectory`/`rmtree(ignore_errors=True)`, so a hard kill would strand the tree. No at-exit residue.

## What this attacks / supports
- C1 (operability) and its frozen counter, under the wave scratch contract: both met at the build tip and leak-free — no falsification.
- C2 (calibration) counter and its claim/verdict/maxN rendering at the build tip: met, `mismatches=0` — no falsification; confirms the
  freeze's post-row-fix state (N=57, `rejected-honest-stop`, r42=0).
- Kill rules of C1/C2 were not triggered by these runs. L1/L2 are tool-robustness limits, not predicate credit or debit.

## Evidence (seat dir `.ufo/waves/round-58/w1/out/X04ScratchHygiene/`)
`checker.out`, `checker2.out`, `c1.out`, `c2.out`; `tmp-{checker,checker2,c1,c2}-{before,after}.txt` + targeted lists;
`checker.strace` (+ `*-strace-extract.txt`), `strace.sha256` (full c1/c2 traces hashed, then discarded for size);
`commands.txt`. Scratch `S` and all probe dirs removed after copying; final TMPDIRs empty.
