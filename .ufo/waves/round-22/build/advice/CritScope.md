# CritScope — C1 critic: nonregular/link/directory invariance and loader limits

Seat: KamaR22.CritScope (critic, read-only). Dimension: does fail-closed `install_tree` keep
symlink/directory/special-file behaviour unchanged, and does C1 stay inside what a
one-directory scan can prove about the code the loader uses. No verification runs, no
builds or tests, no installs or updates. One scratch file (`/tmp/critscope-live.py`, from
`git show HEAD:tools/kama-llamacpp-live.py`) was written outside the build directory and then
deleted. That breaks the seat-output rule, so I am disclosing it here.

Axes touched: operability (axis 7, the C1 target), identity integrity, claim scope/provenance.

## Subject under attack (observed)

- Frozen `tools/kama-llamacpp-live.py` at 10271460, `install_tree` (lines 178–202): `os.listdir` →
  per-entry `os.lstat` → `if not stat.S_ISREG(st.st_mode): continue` → `sha256_file`. The
  `lstat` is done first, so symlinks (dangling, looping, to a directory, to a member), directories and
  FIFO/socket/device entries are skipped and **never opened**.
- The lane checkout currently has an **uncommitted diff** (`git status`: ` M tools/kama-llamacpp-live.py`,
  ` M tests/llamacpp-live/install-links-grid.py`). Its three handlers now raise
  `SetupError('install-tree-unpinnable:listdir' | ':lstat:{name}' | ':read:{name}')`, and the
  `lstat`→`S_ISREG`→read ordering is byte-identical. I treat it as the de facto ApiFix proposal.
  No `sandboxes/` directory exists under `.ufo/waves/round-22/build/`.

## Verdict on my dimension: PASS-AS-WRITTEN, with four bounded findings

### F1 — Nonregular/link/directory invariance (holds; must be pinned, not assumed)

The diff does not change which entries are skipped. All three e2e cases in
`tests/llamacpp-live/unpinnable-e2e.py:62-68` are still not install_tree errors, so they still
reach `install_links` and keep the colon reason that `:91-94` requires (`startswith('install-tree-unpinnable:')`):
`hwcaps-directory` is a directory skip, `hwcaps-symlink-to-dir` is an lstat symlink skip, and
`dangling-soname` is an lstat symlink skip.

**Falsifiable rejection condition.** Reject C1 if any of the following holds, on any integrated revision:
1. `install_tree(server)` on the `_install_identity_selftest` fixture (`tools/kama-llamacpp-live.py:1124-1140`)
   returns map keys that include `libllama.so` or `libllama.so.0`. This would mean the code follows
   symlinks, for example through `os.stat`, `os.path.isfile`, or `scandir().is_file()` with its default
   `follow_symlinks=True`.
2. `install_tree` raises for a lone dangling symlink, a symlink loop, a symlink to a directory, a
   subdirectory, or a FIFO. Any of these would collapse an `install_links` diagnostic into an install_tree
   token. It would also make `unpinnable-e2e.py` fail on `dangling-soname` if the token lost its colon.
3. `sha256_file` or `open` is ever called on an entry that `lstat` reported as non-regular. A FIFO would
   block forever: a hang, not a refusal.
4. On any tree with no injected fault, the `(tree, combined)` tuple differs from the frozen arm.

**Minimum remedy (for Matrix, not an implementation).** Add nonregular controls to
`tests/llamacpp-live/install-io-grid.py` and run them in both arms:
- **Real entries, no root or privilege needed:** a symlink to a member, a dangling symlink, a symlink
  loop, a symlink to a directory, `glibc-hwcaps/`, `openvino-licensing/`, and a FIFO (`os.mkfifo`).
- **Mocked entries:** an AF_UNIX socket and a character device, both via an `os.lstat` mock that returns
  `S_IFSOCK`/`S_IFCHR`.
- **Expected oracle for both arms:** no raise, and a tuple equal to the frozen digest.
- **Spy check:** a spy on `sha256_file` must record calls only for names whose `lstat` is `S_ISREG`.

Cross-boundary cell: an `lstat` fault injected on an entry that is really a symlink **must refuse**. The
code cannot know the type of an entry it failed to `lstat`, so "intentional skip" applies only after a
successful `lstat`. Pin this cell so that nobody later "fixes" it into a skip.

### F2 — Loader and external-library limits (claim-scope risk, not a code defect)

`install_tree` identifies only the regular files one level inside `dirname(server_real)`, at scan time,
before launch. It is computed once (`:1414`) and nothing rechecks it after teardown. Code that is loaded
but outside this identity, from local evidence:
- System libraries resolved from `/usr/lib` through `ld.so.cache`: `libstdc++.so.6`, `libgcc_s.so.1`,
  `libc.so.6` (NEEDED), and libssl, libcrypto, libgomp, libz, brotli, zstd
  (`.ufo/waves/round-16/build/advice/SentinelInstallChain.md` F4). Host-level `/etc/ld.so.preload`
  and `ld.so.cache` are also outside it.
- The contents of unpinned subdirectories. Only their names are recorded, in `install_unpinned`.
- Time-of-scan to time-of-load: bytes can change between the scan and `exec` or a later `dlopen` of the
  `libggml-cpu-*` variants. Those variants live in the same directory, so they are only hashed at scan time.
- Already closed, and not to be re-claimed: the child environment drops `LD_LIBRARY_PATH`, `LD_PRELOAD`
  and `GGML_BACKEND_PATH`, because `CHILD_ENV_KEYS = ('PATH','HOME','LANG','LC_ALL','TMPDIR')` at `:84`.
  `glibc-hwcaps` is refused by `install_links`. Both predate C1, so C1 must not take credit for them.

**Falsifiable rejection condition.** Reject or limit C1 if the round-22 lesson, QUALITY row, claim text,
SCORECARD line, or the new `install_tree` docstring says or implies any of these:
- the install identity covers the libraries the server loads;
- "all consumers refuse incomplete identity" applies to anything beyond the one-level regular-file scan;
- the fault matrix proves race-freedom or load-time identity.

The diff's docstring opens with "Complete regular-file map…". It is unscoped and could be read that way.

**Minimum remedy.** Scope the wording, with no code change. For example: "complete over the regular files
directly in `dirname(server_real)` at scan time; libraries the loader resolves elsewhere, unpinned
subdirectory contents and post-scan changes are outside this identity". The lesson should also list these
as non-claims, following KQ29's "names what it omits" (`corpus/QUALITY.md`, round-21 section).

### F3 — The lstat→open race is unchanged and must stay a non-claim

Between `lstat` (S_ISREG) and `open` in `sha256_file`, an entry can be swapped for one of two things:
- a symlink to an external file, which then gets hashed under the member's name;
- a FIFO, which makes `open` block.

Frozen code has the same window, so this is **not a regression**. Closing it would take
`O_NOFOLLOW|O_NONBLOCK` plus an `fstat` S_ISREG check. That would change `sha256_file`, which the model and
probe digests share, and it is outside C1.

**Rejection condition.** Reject only if C1 claims TOCTOU safety or "no hang on read". This is a tradeoff,
not a fixable C1 defect.

### F4 — Reason-token detail (low operability)

- `:lstat:{name}` and `:read:{name}` embed the raw name. `install_links` formats control-character names
  with `{name!r}` (`:239-240`).
- An unreadable regular member now refuses inside `install_tree`, so the producer token changes:
  - frozen: `install-tree-unpinnable:<name>:unreadable`, from `install_links` via `:1418`;
  - diff: `install-tree-unpinnable:read:<name>`.
- The `install_links` branches `unreadable` and `not-hashed` become reachable on the producer path only
  through races or an explicitly supplied partial map. SimplifyAPI rightly says to keep them.

**Rejection condition.** Reject if any pinned expectation, in the e2e test, the grid, or the lesson text,
still asserts the frozen `:unreadable` token for the producer path.

**Minimum remedy.** Use `{name!r}` in both f-strings. The lesson should record the token change as a
deliberate change, not keep the round-21 wording at `corpus/lessons/round-21.md:134-138` as current
behaviour (KQ26: name the superseded text).

## Mistake mining (observed, same class as round 21 M4)

`corpus/lessons/round-21.md:66` M4 says: "A build seat wrote into the lane checkout … the wave context
forbade lane edits". In round 22, during the build wave, the lane checkout again shows ` M` on
`tools/kama-llamacpp-live.py` and `tests/llamacpp-live/install-links-grid.py`. The author is unknown to
this seat. The fail-capable step in M4 was L1's pre-integration `git status --porcelain`. L1 should run it
before integrating and should compare against the sandbox diffs instead of trusting the lane bytes.
[INFERENCE] If L1 made these edits intentionally, the finding is moot; otherwise it is a recurrence and
belongs in the round-22 lesson.

## Strongest cross-dimension counterexample (out of scope, for Matrix and CritClaim)

Take a directory with mode `r--` (readable, no search bit). `listdir` succeeds and every `lstat` fails with
EACCES. Frozen `install_tree` then returns `({}, sha256(b'') = e3b0c442…b855)`: an equal, comparable
digest for **every** such directory. The diff refuses at the first `lstat`. The producer path cannot reach
this case, because `os.path.isfile(server_real)` fails first and yields `server-not-executable`. Direct
callers can reach it: both grids, `unpinnable-e2e.py:73`, and the selftest.

## Owned paths

- Written: `.ufo/waves/round-22/build/advice/CritScope.md` (this file; append-only from now on).
- Read only: `tools/kama-llamacpp-live.py` (HEAD and lane working tree), `tests/llamacpp-live/{install-links-grid,unpinnable-e2e,check-receipt}.py`,
  `corpus/QUALITY.md`, `corpus/lessons/round-21.md`, `.ufo/waves/round-16/build/advice/{SentinelInstallChain,ScoutHostRuntimeFacts}.md`,
  `.ufo/waves/round-22/build/{spec.json,advice/SimplifyAPI.md,advice/SrcOpen.md}`.

## Checks for L1 after integration (proposed, not run)

1. Run `python3 tools/kama-llamacpp-live.py --selftest`. The soname-chain map is unchanged and retargeting
   leaves the `install_tree` identity unchanged.
2. Run `python3 tests/llamacpp-live/install-io-grid.py --arm both --json`. The F1 nonregular controls must
   show no raise, a frozen-equal digest, and a `sha256_file` spy that recorded regular names only.
3. Run `python3 tests/llamacpp-live/install-links-grid.py --selftest` and `--arm both`.
4. Run `tests/llamacpp-live/unpinnable-e2e.py`. All three cases keep the colon token.
5. Grep the round-22 lesson, QUALITY row and docstring for the F2 non-claims.

Tooling: no installs or updates.

Report: .ufo/waves/round-22/build/advice/CritScope.md
