# RV01ProbeDiff — kama round 93 wave 1 (operability)

Seat RV01ProbeDiff. Lane `kama-shokunin` read-only except this report and my out dir.
Scope: the C1 diff `5af7949…` → `fe5f031c…` on `tools/kama-probe.sh` — every behaviour change against
base other than the intended one — by extracting `ROUTER_PY` from both revisions and running it
verbatim as `python3 -c "$ROUTER_PY" <body.json> files <idx...>`.

## Scope

Diff surface (measured, not assumed): `git diff --numstat` = **20 added / 0 deleted**, two `@@` hunks,
blob `d53c9a9b…` → `b22a319a…`, mode `100755` → `100755`, no other hunk. Extracted `ROUTER_PY`
(`# Round 93 …` block): base sha256 `cd3bd8b0…` (224 lines), M1 `e0f44759…` (244 lines); the only
text difference is the `SEEN`/`gguf_state` wrapper plus the rename of the old body to `gguf_parse`.
`router_file_states` (probe:869) is the only caller that reaches the memo, once per `check` with all
candidate indexes; `entries` mode (probe:799) never calls it. Host load 71–89 during these runs
(`uptime` in `harness.log`); every number below is within-run and reproducible (3/3 where repeated).

## Commands and outputs (cwd = my scratch, exit codes true)

| # | Command | Exit | Result |
|---|---|---|---|
| 1 | `git -C <lane> diff 5af7949… fe5f031c… -- tools/kama-probe.sh` | 0 | 1 file, 2 hunks, 20/0 (receipt: probe diff above) |
| 2 | `awk` extract of `ROUTER_PY` from both revisions | 0 | `router-base.py`, `router-m1.py`; sha256 in `harness.log` |
| 3 | `python3 harness.py` | 0 | 46 single-candidate bodies + 7 args-shape bodies + 4 alias cells: **58 SAME**, `ALL_SINGLE_AND_ALIAS_SAME=True` |
| 4 | `python3 test4.py direct` | 0 | 35 single files compared at `gguf_state` level (not the `file_state` collapse): **DIFFS: 0** |
| 5 | `python3 test2.py` | 0 | repeat/alias/mmproj/P02/`timeout 8` cells + rewrite cells |
| 6 | `python3 test3.py` | 0 | hostile path strings, false-green direction, bind attempt, distinct-slow limit |
| 7 | `unshare -rm` + `mount --bind … /dev/shm/rv01` + inline driver | 0 | `BIND_OK`; NO_OPEN-vs-memo ordering, 5/5 SAME |
| 8 | `python3 test4.py all` | 0 | 2048-candidate budget + 3× rewrite determinism |

## Findings

**No BLOCKER.** Every single-candidate state is byte-identical to base, and no non-mutating
multi-candidate input changes.

**DEFECT-1 (low, real regression, not the intended class).** The memo key is
`(st_dev, st_ino, st_size, st_mtime_ns)` — it omits `st_ctime_ns`, so an in-place rewrite of the
same inode that keeps the length and lands on the same `mtime_ns` is served the stale parse.
Deterministic 3/3, both directions (`test4.log`, `test3.log`), body
`[X, yslow, X]` written during `yslow`'s 1.3 s parse:
- invalid→valid: base `0 invalid | 1 invalid | 2 -` / M1 `0 invalid | 1 invalid | 2 invalid`.
- **valid→invalid (the false-green direction): base `0 - | 1 invalid | 2 invalid` / M1 `0 - | 1 invalid | 2 -`.**
  `file_state` maps `ok` and `-` to `-`, so entry 2 stays "not bad" — the same loadable direction as
  r92 SC02 F6, just triggered by mutation instead of repetition.
Boundaries measured: same size + **new** mtime → SAME (mtime is in the key); different size + restored
mtime → SAME; replacement by `rename` (new inode) → SAME; every ordinary in-place write (`cp`, `dd`,
`curl -o`) changes mtime and is caught. Only a writer that also restores/duplicates the nanosecond
mtime (or an fs with coarse mtime — see NOTE-1) reaches it, between two candidates of one call.
Does **not** falsify C1's predicate (the counter's cells never mutate the file). Remedy is one field:
add `st_ctime_ns` to the key — `utime()` cannot restore ctime (measured `ctime changed=True` on every
rewrite above), and the extra re-parses it would cost are only on metadata churn. Otherwise disclose
it next to "many DISTINCT slow files".

**NOTE-1 (undisclosed limit class, [INFERENCE]).** On filesystems whose `st_mtime_ns` has coarse
granularity (vfat/exfat 2 s, NFS/SMB 1 s), the DEFECT-1 window widens to any same-size in-place write
inside one granule. Not measured: mounting such an fs needs privileges I do not have (`/dev` is
read-only even in `unshare -rm`); `xfs`, `ext4`, `tmpfs` all give ns, which is what I measured.

**NOTE-2 (double stat, benign TOCTOU).** The wrapper stats, then `gguf_parse` stats again. A file that
appears between the two stats yields a decided state where base said `missing`; sub-microsecond
window, conservative direction, not reproducible.

**NOTE-3 (intended, quantified).** Repeats now cost one parse: `slow-x64` 4.16 s → 0.55 s; through the
probe's own `timeout 8` at 2048 repeats base returns **rc=124 with 1639/2048 lines (7 decided, 1632
undecided)** — the F6 false green reproduced at the `ROUTER_PY` level — while M1 returns rc=0, 0.61 s,
2048/2048 `invalid`. Aliases (`R05`, 33 strings × 64) and `-m ok --mmproj slow` (`R06`) behave the
same way.

**NOTE-4 (intended side effect).** The budget repeats no longer spend also *decides* later distinct
candidates base left undecided: 3 distinct slow files ×3 → base `…7 invalid, 8 -`, M1 all `invalid`.
Benefit direction; the disclosed limit is unaffected (3 distinct slow files, one each: identical in
both).

**NOTE-5 (ordering preserved).** The `NO_OPEN` check runs before the memo. With the same inode
reachable as `/…/valid-small.gguf` (memoized `ok`) and as `/dev/shm/rv01/valid-small.gguf`, both
revisions answer `invalid` for the latter (5/5 SAME, both orders, incl. a 3×-memoized first path) —
no `ok` leaks into a `/proc`,`/sys`,`/dev` path.

**NOTE-6 (cost).** One extra `os.stat` + `os.path.realpath` per candidate (twice on a miss). Measured
on 2048 distinct candidates: missing 0.05 s, valid 0.08–0.09 s, bad magic 0.08 s — identical to base
within noise. `SEEN` is per process, so it lives exactly one `check`; nothing crosses checks.

## Deliverables

`.ufo/waves/round-93/w1/out/RV01ProbeDiff/`: `harness.py`, `test2.py`, `test3.py`, `test4.py`,
`harness.log`, `test2.log`, `test3.log`, `test4.log`, `test4-direct.log`, `router-base.py`,
`router-m1.py`. Scratch `/fast/scratch/hyaku/kama-r93/RV01ProbeDiff` removed after copying.

VERDICT: holds — the intended repeat-invariance is correct on all 58 single-candidate and all non-mutating multi-candidate inputs, with one narrow regression (DEFECT-1: key omits `st_ctime_ns`, so a same-size same-`mtime_ns` in-place rewrite between two candidates returns the stale state, in the false-green direction too) that the L1 should fix by adding `st_ctime_ns` or disclose.
