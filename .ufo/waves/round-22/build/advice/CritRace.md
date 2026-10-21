# CritRace — C1 attack on one dimension: TOCTOU windows and authentication overclaim

Seat: `KamaR22.CritRace` (critic, read-only). Base read: `master` = `HEAD` =
`10271460cc575fc2280aa831e442726385fc2319` (`git rev-parse`, observed).
No sandbox drafts existed under `build/sandboxes/` when read, so this attacks the
frozen source plus the shared-interface contract, not ApiFix's diff.
No verification run, no installs, no REA devices.

## Evidence (frozen source, read with ranged reads)

- `tools/kama-llamacpp-live.py:171-176` `sha256_file` uses `open(path, 'rb')`:
  follows symlinks, blocking open, reads to EOF with no size bound.
- `:178-202` `install_tree`: `os.listdir` → per name `os.lstat` → `S_ISREG` test →
  `sha256_file(full)` by **path**. The lstat result (dev/ino/size/mtime) is
  discarded; nothing ties the opened object to the object that was classified.
- `:213-259` `install_links` does a **second, independent** `listdir`/`lstat` pass
  later; its `tree is not None and name not in tree` check (`:258`) catches a
  regular member that *appeared* between passes, nothing else.
- `:1413-1414` `server_sha = sha256_file(server_real)` and `install_tree` hash the
  server twice; gate `tests/llamacpp-live/check-receipt.py:406` rejects
  `install_tree[base] != server.sha256` — the only cross-time consistency check.
- Launch: `Popen(server_argv)` at roughly `:1495` (within `:1445-1530`), after
  impl hash, probe hash, port pick. **No rescan of the install directory after
  hashing, before exec, or after the run** (grep: `install_tree(` only at
  `:1135,1157` selftest and `:1414`).
- Corpus already bounds authentication: `corpus/knowledge/llamacpp-loading-lifecycle.md:311-312,322,358-359`
  ("binds the bytes the lane observed … not authentication of execution");
  `corpus/lessons/round-21.md:27,109`; `corpus/QUALITY.md` KQ29 (`:152`).

## Counterexamples (strongest available locally; all [INFERENCE], not executed)

1. **lstat → open swap to a symlink.** `lstat(name)` sees `S_ISREG`; a concurrent
   `rename(2)` installs `name -> libother.so.1` (same dir) before `open`. `open`
   follows, so `tree[name]` = digest of `libother`'s bytes under `name`. If the swap
   reverts before `install_links` runs, no problem is reported and the gate
   (`check-receipt.py:406` only covers the server basename) accepts a
   self-consistent, **wrong** tree. Not an OSError, so ApiFix's
   fail-closed-on-OSError contract does not see it.
2. **lstat → open swap to a FIFO or char device** (e.g. `name -> /dev/zero` or a
   FIFO). `open(FIFO,'rb')` blocks forever; `/dev/zero` reads forever. Result is a
   hang / unbounded CPU, neither a digest nor `SetupError`. This is an
   **operability** failure (axis 7, the assigned lowest axis) that survives C1's
   fix unchanged, because the fix only converts *raised* errors.
3. **Mid-read in-place rewrite** (`cp` over an existing member, not rename):
   `read` returns a mix of old and new pages → a digest matching neither
   version, returned as a successful member. No error is raised.
4. **Post-hash replacement.** Any member renamed after `:1414` and before the
   loader maps it at `Popen` produces a receipt whose `install_tree`/`install_links`
   describe bytes never executed. [INFERENCE, not grounded in corpus] llama.cpp
   builds with dynamically loaded ggml backends `dlopen` members after exec,
   extending the window into the run; the corpus has no source for this.
5. **Authentication overclaim.** A unittest.mock fault matrix (Matrix seat)
   injects *raised* OSErrors at listdir/lstat/open/read. It cannot show
   race-freedom, scan/exec equality, or provenance; a same-uid writer can replace
   files and then every pin re-records the new bytes consistently.

## Falsifiable rejection condition (L1/judge)

Reject C1's after-state, or its lesson/knowledge/QUALITY text, if **any** of
these holds:

- **R-1 (overclaim).** Any C1 artifact (lesson, knowledge append, QUALITY row,
  docstring, receipt field doc, report summary) says or implies that refusing
  incomplete identity makes `install_tree`/`install_tree_sha256` *complete*,
  *race-free*, *atomic*, *tamper-evident*, *the loaded/executed bytes*,
  *authenticated*, or *provenance*. It also fails if the text cites the
  mock matrix as evidence for anything beyond "raised OSError at an injected
  site → `SetupError('install-tree-unpinnable…')`, never a returned digest".
  Test: grep the C1 diff for those words and for "identity" without a
  scan-time qualifier. One unqualified hit means reject.
- **R-2 (silent residual).** The C1 knowledge/lesson append does not name the
  four residual windows as **out of C1 scope**: lstat→open object swap,
  blocking/unbounded open of a swapped special file, mid-read mutation, and
  hash→exec (and post-exec load) replacement. Omitting them means C1 says
  "fail closed" without bounding it. This is the round-21 "Fail closed, never
  smaller" overstatement repeated (`llamacpp-loading-lifecycle.md:343`,
  superseded at `:364`).
- **R-3 (regression via hardening).** If ApiFix *does* harden the read path
  (e.g. switches to `os.open`/fd hashing), reject if any successful-scan
  map/digest changes for a static tree. Also reject if the Matrix grid's
  read-failure rows inject only at `builtins.open`/`sha256_file`, so that after
  the switch they never fire. A row whose fault never fires must be
  `site_missing` (not applicable), never counted as green.

C1 is **not** rejected merely because the windows exist: closing them is a
different claim (concurrency/integrity), not "raised error → refusal". This is a
scoped tradeoff, not a defect of C1, *provided* R-1 and R-2 hold.

## Minimum remedy (not an implementation)

1. **Required, text-only:** in the C1 knowledge append and lesson, add one
   boundary sentence. It should say that `install_tree` is a scan-time
   observation and that C1 converts raised listdir/lstat/open/read errors into
   `install-tree-unpinnable` refusals. It should also say that concurrent
   successful mutation (the lstat→open swap, a special file swapped in, mid-read
   rewrite, and hash→exec or post-exec replacement) is unhandled and outside
   C1, and that this is not execution authentication. This needs no code and
   preserves every digest.
2. **Optional, only as a separately declared future claim (not C1):** hash from an
   fd opened `O_RDONLY|O_NOFOLLOW|O_NONBLOCK|O_CLOEXEC`. `fstat` must show
   `S_ISREG` with `(st_dev, st_ino)` equal to the classifying `lstat`, and
   size/`mtime_ns`/`ctime_ns` must be unchanged between pre-read and post-read
   `fstat`. Then rescan tree and links after child exit and compare. A mismatch
   is a refusal or an invalid receipt, never a new digest. This narrows the
   windows but still does not authenticate: a same-uid writer defeats it.
3. **If (2) lands inside C1 anyway:** the Matrix grid must add injection sites
   for `os.open`/`os.fstat`/`os.read` so the read-failure rows still fire (R-3),
   and must pin a static-tree positive control digest equal to frozen.

## Impacted axes

- Axis 7 operability (assigned lowest): counterexample 2 leaves a hang that C1 does
  not convert into a refusal. Covered by R-2 bounding, or by remedy 2 in a later
  claim.
- Calibration/honesty (claim wording): R-1, R-2.
- Regression and preservation of the success digest: R-3.

## Owned paths

- Written: `.ufo/waves/round-22/build/advice/CritRace.md` (this file only).
- Read-only: `tools/kama-llamacpp-live.py`, `tests/llamacpp-live/check-receipt.py`,
  `corpus/knowledge/llamacpp-loading-lifecycle.md`, `corpus/lessons/round-21.md`,
  `corpus/QUALITY.md`.

## Proposed checks for L1 (post-integration; not run here)

- `grep -nEi 'race-free|atomic|tamper|authenticat|complete identity|executed bytes' <C1 diff>`
  must show only negated/boundary uses (R-1).
- Matrix `--arm both --json`: every read-failure row reports a fired injection
  count > 0 on the current arm (R-3).
- Static-tree positive control: the current `install_tree` digest must be
  byte-equal to the frozen one (R-3).

Tools installed/updated: none.
