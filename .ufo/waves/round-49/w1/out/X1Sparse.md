# X1Sparse — round 49: host-safety probes re-run against `verify_archive_member()`

**Verdict:** all eight round-48 Sen2Live host-safety inputs are now refused in 0.001–0.043 s with a
stable `provenance-*` token (before: two indefinite hangs, two unbounded hash loops, and a 2 GiB
archive that also hung), and the real b11909-shaped asset still verifies in 0.149 s. One unbounded
path survives *inside* the new 1 GiB gate: a PAX decimal `size` record over a large gzip payload is
drained before the refusal — 1.803 s for a 4 GiB payload, 7.021 s for 16 GiB, ≈100 s at the gate —
and malformed GNU sparse pax headers still escape as an uncaught `ValueError`. A two-hunk fix in
this directory removes both (0.012–0.032 s; `provenance-archive-unreadable`), and both findings are
still live at lane HEAD `7fab24e7` (post-integration), measured separately.

Seat: X1Sparse (leaf). Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, read-only except this
report and `w1/out/X1Sparse/`. Round-49 build commit `74558c71c38ceaeace15fd4cf8aa9d84977584b1`,
round-48 code `438127bc01ff3b99f98468549d58046f932490ef`. Judge axis: operability, task 1
(attack + frontier).

## 1. What was actually executed

The function under test is imported from a **byte copy** of the lane tool at each commit, never
re-implemented:

```
sha256 1e5ea0fd…f9a6d2  before/kama-llamacpp-live.py   (git show 438127bc:tools/…)
sha256 72e76079…bffd4c  after/kama-llamacpp-live.py    (git show 74558c71:tools/…)
                        (identical to lane clone 122c4ee9 tools/kama-llamacpp-live.py)
sha256 5447bf63…ac1343  fixed/kama-llamacpp-live.py    (after + proposed-fix.diff, scratch only)
sha256 0b31f8e6…88a3ba  head/kama-llamacpp-live.py     (lane HEAD 7fab24e7, post-integration)
```

* `scripts/build_art.py` builds every crafted archive **once**; before/after/fixed consume the
  identical bytes (`art/artifacts.json` holds path, sha256 and size of each).
* `scripts/cell.py` wraps `hashlib.sha256` with a delegating counter (the real hash still does the
  work) and checkpoints bytes-hashed every 128 MiB, so a killed cell still reports a lower bound;
  `scripts/matrix.py` runs one cell per subprocess with a hard timeout.
* Nothing was run against the lane tree; one `git clone --shared` supplied the lane-shaped copy used for
  the `--selftest` check and for confirming the commit/file identity.
  No llama-server was started by this seat (`pgrep -af llama-server` shows only other seats' trees).

## 2. Token and seconds per case

`table.md` is generated from `rows-{before,after,fixed}.jsonl` + `extras.jsonl`; the "killed" rows
are hard timeouts with the measured lower bound in `rows-before.jsonl`.

| case | before 438127bc | s | after 74558c71 | s | after + proposed fix | s |
|---|---|---|---|---|---|---|
| regular member, right digests (control) | **ok** | 0.001 | **ok** | 0.002 | **ok** | 0.001 |
| regular member, wrong member digest | `provenance-member-digest-mismatch` | 0.001 | `provenance-member-digest-mismatch` | 0.001 | `provenance-member-digest-mismatch` | 0.002 |
| member entry is a symlink | `provenance-member-not-a-file` | 0.001 | `provenance-member-not-a-file` | 0.001 | `provenance-member-not-a-file` | 0.002 |
| member entry is a directory | `provenance-member-not-a-file` | 0.003 | `provenance-member-not-a-file` | 0.002 | `provenance-member-not-a-file` | 0.002 |
| member entry is a FIFO | `provenance-member-not-a-file` | 0.002 | `provenance-member-not-a-file` | 0.001 | `provenance-member-not-a-file` | 0.002 |
| member absent | `provenance-member-absent` | 0.001 | `provenance-member-absent` | 0.001 | `provenance-member-absent` | 0.001 |
| duplicate names: first good, last decoy | `provenance-member-digest-mismatch` | 0.001 | `provenance-member-size-mismatch` | 0.001 | `provenance-member-size-mismatch` | 0.002 |
| duplicate names: first decoy, last good | **ok** | 0.002 | **ok** | 0.001 | **ok** | 0.002 |
| old-GNU `S` sparse, realsize 1 GiB | `provenance-member-digest-mismatch` | 0.545 | `provenance-member-sparse` | 0.001 | `provenance-member-sparse` | 0.003 |
| old-GNU `S` sparse, realsize 8589934591 | `provenance-member-digest-mismatch` | 4.243 | `provenance-member-sparse` | 0.001 | `provenance-member-sparse` | 0.002 |
| PAX 0.0 sparse, `GNU.sparse.size` 10^15 | **no return**, killed at 30 s | 30 | `provenance-member-sparse` | 0.001 | `provenance-member-sparse` | 0.002 |
| PAX 0.1 sparse, `GNU.sparse.size` 10^15 | **no return**, killed at 20 s | 20 | `provenance-member-sparse` | 0.002 | `provenance-member-sparse` | 0.001 |
| PAX 1.0 sparse, `GNU.sparse.realsize` 10^15 | **no return**, killed at 20 s | 20 | `provenance-member-sparse` | 0.002 | `provenance-member-sparse` | 0.002 |
| tar index of 20 000 entries | `provenance-member-absent` | 0.215 | `provenance-archive-too-many-members` | 0.043 | `provenance-archive-too-many-members` | 0.05 |
| gzip that inflates to 8 GiB of zero blocks | `provenance-member-absent` | 0.054 | `provenance-member-absent` | 0.021 | `provenance-member-absent` | 0.021 |
| PAX `size` 10^15 over a 4 GiB zero payload | `provenance-archive-unreadable` | 1.821 | `provenance-archive-unreadable` | 1.803 | `provenance-member-too-large` | 0.012 |
| PAX `size` 10^15 over a 16 GiB zero payload | `provenance-archive-unreadable` | 7.008 | `provenance-archive-unreadable` | 7.021 | `provenance-member-too-large` | 0.032 |
| plain zeros archive, 512 MiB | `provenance-member-absent` | 38.4 | `provenance-member-absent` | 48.098 | – (fix does not touch this path) | – |
| archive is a 2 GiB sparse file | **no return**, killed at 60 s | 60 | `provenance-archive-too-large` | 0.001 | `provenance-archive-too-large` | 0.001 |
| archive path is a FIFO | **no return**, killed at 6 s | 6 | `provenance-archive-not-regular` | 0.001 | `provenance-archive-not-regular` | 0.001 |
| archive path is /dev/zero | **no return**, killed at 6 s | 6 | `provenance-archive-not-regular` | 0.001 | `provenance-archive-not-regular` | 0.001 |
| malformed `GNU.sparse.map` (`"zz"`) | uncaught `ValueError` | 0.001 | uncaught `ValueError` | 0.002 | `provenance-archive-unreadable` | 0.001 |
| PAX 1.0 header with no map block | uncaught `ValueError` | 0.002 | uncaught `ValueError` | 0.001 | `provenance-archive-unreadable` | 0.001 |
| real b11909-shaped asset, 62 entries, 24.5 MB, member `35ac50fb…d7ff0` | **ok** | 0.149 | **ok** | 0.149 | **ok** | 0.149 |

### 2b. Still true at lane HEAD (`7fab24e7`, after the 24e906f0 integration)

The integration commit hardened the descriptor handling (`os.open(O_RDONLY|O_NONBLOCK)` +
`fstat`, seat V1Live's TOCTOU finding) and the witness dir, but left every archive bound
untouched: at HEAD there is no `provenance-member-too-large` token and the except tuple is still
`(OSError, EOFError, tarfile.TarError)`. `rows-head.jsonl` (tool sha256
`0b31f8e6bd98f978c98e6029bfa322c37bac6ae09f9ebf4d770a3fe9ab88a3ba`) re-runs the same fixtures:

| case | HEAD 7fab24e7 (post-integration) | s |
|---|---|---|
| regular member, right digests (control) | **ok** | 0.001 |
| member entry is a symlink | `provenance-member-not-a-file` | 0.001 |
| member absent | `provenance-member-absent` | 0.001 |
| old-GNU sparse, realsize 1 GiB | `provenance-member-sparse` | 0.001 |
| old-GNU sparse, realsize 8589934591 | `provenance-member-sparse` | 0.001 |
| PAX 0.1 sparse, `GNU.sparse.size` 10^15 | `provenance-member-sparse` | 0.002 |
| PAX 1.0 sparse, `GNU.sparse.realsize` 10^15 | `provenance-member-sparse` | 0.001 |
| tar index of 20 000 entries | `provenance-archive-too-many-members` | 0.043 |
| gzip that inflates to 8 GiB of zero blocks | `provenance-member-absent` | 0.032 |
| PAX `size` 10^15 over a 4 GiB zero payload | `provenance-archive-unreadable` | 1.786 |
| archive is a 2 GiB sparse file | `provenance-archive-too-large` | 0.001 |
| archive path is a FIFO | `provenance-archive-not-regular` | 0.001 |
| archive path is /dev/zero | `provenance-archive-not-regular` | 0.001 |
| PAX `size` 10^15 over a 16 GiB zero payload | `provenance-archive-unreadable` | 7.198 |
| PAX 0.0 sparse, `GNU.sparse.size` 10^15 | `provenance-member-sparse` | 0.002 |
| member entry is a directory | `provenance-member-not-a-file` | 0.001 |
| member entry is a FIFO | `provenance-member-not-a-file` | 0.001 |
| malformed `GNU.sparse.map` ("zz") | uncaught `ValueError` | 0.001 |
| PAX 1.0 header with no map block | uncaught `ValueError` | 0.002 |
| real b11909-shaped asset, 62 entries | **ok** | 0.154 |

So F1 (~100 s drain) and F2 (uncaught `ValueError`) are live at HEAD, and the FIFO/device cases
are still refused — now even before `open()` can block, which is what the non-blocking descriptor
buys. The proposed fix still applies to HEAD unchanged (its line context is inside the loop and the
except tuple, neither of which the integration touched).

Per-case notes on the eight requested inputs:

1. **old-GNU sparse** (`S` header, realsize in the 12-byte octal field at 483): tarfile synthesises
   the hole and the old loop hashed 1.07 GB / 8.59 GB before seeing a digest mismatch; the new
   `found.sparse is not None` check stops at the header.
2. **PAX 0.1** (`GNU.sparse.map` + `GNU.sparse.size`) and 3. **PAX 1.0** (`GNU.sparse.realsize`,
   decimal, no octal ceiling): both were unbounded — killed at 20 s having hashed 39.6 GB / 38.4 GB
   (≈2.0 GB/s). Same `sparse` token now, 0.002 s. **PAX 0.0** (`GNU.sparse.offset/numbytes` +
   `GNU.sparse.size`) behaves the same way in both directions and is included for completeness.
4. **FIFO path**: old code blocked in `open()` forever (S_ISREG was never checked); now
   `provenance-archive-not-regular` from `os.stat` before any open.
5. **Device path** (`/dev/zero`): old code hashed 15.0 GB in the 6 s before kill; now refused from
   `st_mode` in 0.001 s.
6. **20 000-entry index**: `getmember()` materialised the whole index (round-48 measured 300 k
   entries at 3.1 s and 1 M at 23.2 s / 444 MB); the streaming cap fires at entry 4097 → 0.043 s.
7. **Duplicate member names**: last occurrence wins in both versions (matches extraction).
   With `server_size` the last duplicate's declared size is also compared, so
   *good-then-decoy* now refuses with `provenance-member-size-mismatch` where it used to refuse
   with a digest mismatch; *decoy-then-good* is still accepted (0.001 s), which is correct because
   extraction would install the good file. No acceptance regression.
8. **gzip that inflates to a huge tar index of zero blocks**: already benign in round-48 code
   (0.054 s) because `tarfile.next()` ends the archive at the first all-NUL header; the new code is
   the same (0.021 s) and only the archive digest (37 MB) is read — none of the 8 GiB materialises.
   A large index of *real* headers is bounded by `MEMBER_MAX_COUNT` (case 6).

## 3. Measured bounds (`rates.txt`)

| quantity | measured | derivation |
|---|---|---|
| member-hash loop, old code | 1.97–2.02 GB/s | 1.07 GB/0.545 s, 8.59 GB/4.243 s |
| a 10^15-byte declared member, old code | **5.8 days** (499 475 s) | at the mean 2.00 GB/s |
| archive digest pass | 1443 MB/s ⇒ 1 GiB = 0.71 s | 512 MiB in 0.355 s |
| gzip drain of a PAX `size` bomb | 2.22–2.28 GiB/s | 4 GiB/1.803 s, 16 GiB/7.021 s |
| payload/archive ratio of that bomb | 229.2 : 1 | 16 GiB in a 74 967 352-byte archive |
| ⇒ worst refusal inside the 1 GiB gate (gz path) | **≈100 s** | 229 GiB drained / 2.3 GiB/s |
| `xzopen` sniff of a plain/non-gz archive | 10.6–13.3 MB/s ⇒ 1 GiB = 77–96 s | 512 MiB in 38.4 s and 48.1 s |
| new gate, worst case (hash + sniff) | **≈96 s single-core** | 0.71 s + 96 s |

The two 512 MiB runs differ (38.4 s vs 48.1 s) because several other seats' llama-servers were
running on the host; both were measured through the lane function, not a proxy.

## 4. Findings

### F1 — residual unbounded drain: a PAX decimal `size` is skipped *before* any check (medium)

`tools/kama-llamacpp-live.py:250-263` — `for info in tf:` yields the member, `tarfile` then seeks to
`offset + block(size)` on the **next** iteration, and only after the loop finishes
(`:256-263`) are `isfile()` / `sparse` / `size != server_size` evaluated. A PAX `size=` record can
declare 10^15 in a 165-byte header; the skip decompresses the whole payload first, and the exception
is `ReadError` → `provenance-archive-unreadable`, so the `size-mismatch` check never runs.

* Command: `python3 one.py --root $S --tag after --case pax-size-1e15-payload-16g`
* Output: `{"outcome":"refused","token":"provenance-archive-unreadable","seconds":7.021,"archive_bytes":74967352}`
  (4 GiB payload: 1.803 s). Both before and after behave identically — the round-49 gate caps the
  *archive* at 1 GiB but not the decompressed volume (229 GiB ⇒ ≈100 s).
* Reachable when the pin itself is hostile: `kama-live-replay.py` passes the receipt's
  `archive_sha256`, so a malicious receipt + matching archive reaches this parse.

Proposed fix (in `proposed-fix.diff`, measured in the `fixed` column — 7.021 s → 0.032 s):

```diff
                 for info in tf:
                     count += 1
                     if count > MEMBER_MAX_COUNT:
                         raise SetupError('provenance-archive-too-many-members')
+                    if info.name == member and info.sparse is not None:
+                        raise SetupError('provenance-member-sparse')
+                    if info.size > ARCHIVE_MAX_BYTES:
+                        raise SetupError('provenance-member-too-large')
                     if info.name == member:
                         found = info
```

The body runs before `tarfile` advances, so the drain never happens. The `sparse` clause must stay
**first**: a sparse member's `info.size` *is* the 10^15 real size, so a size-first ordering would
change the token to `-member-too-large` and break the build's own `_provenance_selftest` assertion
(`provenance-member-sparse`). With the ordering above the fixed tree passes
`python3 tools/kama-llamacpp-live.py --selftest` (rc=0, lane shape) and the frozen C1 `cap` leg's
requirement (`setup_error` starting `provenance-member`, exit 2, server never executed) still holds.

### F2 — malformed GNU sparse pax headers escape as `ValueError` (low, pre-existing)

`tools/kama-llamacpp-live.py:270` catches `(OSError, EOFError, tarfile.TarError)`; tarfile's
`_proc_gnusparse_01` (`int(x)` over `GNU.sparse.map`) and `_proc_gnusparse_10` (map block split)
raise `ValueError`, which is outside that tuple and outside the "raises `SetupError` with a stable
token" contract.

* Command: `python3 one.py --root $S --tag after --case pax_bad_map`
* Output: `{"outcome":"uncaught","exc":"ValueError: invalid literal for int() with base 10: 'zz'"}`
  (same for `pax10_nomap`: `ValueError: not enough values to unpack (expected 2, got 1)`; same in
  the round-48 code, so this predates the build).
* End-to-end the tool still refuses safely — `rc=2`, receipt written, server never starts — but the
  receipt says `setup_error = "internal:ValueError"` (the `main()` catch-all at
  `:1868-1874`) and the schema stays v4, so the reason is lost and no `provenance-` code appears.

Fix: add `ValueError` to the tuple (`proposed-fix.diff`, second hunk) → both cases become
`provenance-archive-unreadable` in 0.001 s.

### F3 — `mode='r:*'` makes liblzma scan the whole sub-cap archive (low)

`:248` opens with transparent compression, and `TarFile.open` tries `bz2, gz, xz, zst, tar` in
that order; on a non-gz/bz2/zst file `lzma` consumes the entire file at 10.6–13.3 MB/s before
`taropen` is tried (direct probe: `xzopen` on 64 MiB of zeros = 5.689 s, every other candidate
<1 ms). Inside the new 1 GiB gate that is 77–96 s of single-core work per hostile archive.

Optional fix: sniff the first six bytes (`\x1f\x8b`, `BZh`, `\xfd7zXZ`, zstd magic) and open with
the explicit mode, else `'r:'`. Not applied to the `fixed` tree — it changes a path the frozen
round-48 probes also exercise, so it is a decision for the L1, not a leaf.

### F4 — non-findings worth recording

* The `--selftest` failure mode of a *bare* tool copy is a harness artefact, not a build defect:
  `_selftest()` → `refused_ports()` reads `<tool-dir>/../registry/endpoint-consumers.tsv` and raises
  `SetupError registry-unreadable` when the registry is absent. Lane-shaped copies pass (rc=0).
* `member-dir` in round-48's own harness named the directory `rel`, so it measured "absent"; with a
  directory entry named `rel/llama-server` both versions return `-not-a-file` (0.002 s).
* Correction to the artefacts previously committed at this path (an earlier seat run): its
  `extras.jsonl` recorded the *before* code on the real asset as `TypeError` (the harness passed five
  positional arguments to the four-argument round-48 function); the regenerated `extras.jsonl` records
  `ok 0.149 s`. No lane finding depended on the old row, but a wave report citing it should be updated.
* The real asset's member digest 35ac50fb2cfd9c4f363720bb88ac17e799716595802c9105103593977d8d7ff0
  is the frozen C1 digest, so the positive control is the same binary the counter expects;
  62 entries is far below `MEMBER_MAX_COUNT = 4096` and 24.5 MB far below the 1 GiB gate.

## 5. Effect on the frozen instruments

* C1 `cap` leg (`round49-replay-witness-audit.py:385`) asserts `exit == 2`,
  `setup_error.startswith("provenance-member")`, and that the stub never executed. The measured
  `provenance-member-sparse` (0.002 s) satisfies it, and so does the proposed `-member-too-large`
  (0.012 s) — but the proposed fix is **not** required for C1 to be met; it removes a ~100 s burn.
* Nothing here touches the `witness` legs, `kama-live-replay.py` or `append-only-audit.py` (C2).
* Both round-49 counters stay outside this seat's write scope; no lane file was modified. The
  pre-existing C1 `cap` path is unaffected by the residual drain because that leg's archive is
  1 byte, not 229 GiB of payload.

## 6. Reproduction

```
S=/fast/scratch/hyaku/kama-r49/X1Sparse; mkdir -p "$S"; export TMPDIR="$S"
git show 438127bc…:tools/kama-llamacpp-live.py > $S/before/kama-llamacpp-live.py
git show 74558c71…:tools/kama-llamacpp-live.py > $S/after/kama-llamacpp-live.py
cp -r $S/after $S/fixed && (cd $S/fixed && patch -p1 < ../proposed-fix.diff)
python3 scripts/build_art.py $S/art            # ~14 s, 2.3 GB of sparse fixtures
python3 scripts/matrix.py --tool-dir $S/before --art $S/art --tag before \
        --out rows-before.jsonl --progress-dir $S/prog --sizes good      # ~2 min
python3 scripts/matrix.py --tool-dir $S/after  --art $S/art --tag after \
        --out rows-after.jsonl --progress-dir $S/prog --sizes good,none  # ~6 s
python3 scripts/gen_extras.py --root $S --out extras.jsonl               # ~2 min
```

Files written by this seat (all under
`/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/X1Sparse/`):

```
X1Sparse.md (this report)  table.md  evidence.txt  rates.txt  extras.jsonl
rows-before.jsonl  rows-after.jsonl  rows-fixed.jsonl  rows-head.jsonl  table-head.md
proposed-fix.diff
scripts/{build_art,cell,matrix,malformed,extra,one,gen_extras}.py  (one.py is gen_extras' cell runner)
scripts/kama-llamacpp-live-round48.py  …-round49.py  …-round49-proposed-fix.py
art/  (16 crafted archives, each <= 198 KB, + artifacts.json with path/sha256/size)
```

### Concurrent integration note

The lane committed a mid-run snapshot of this directory in `24e906f0` (20:41:53, 32 files) while this
seat was still measuring; `7fab24e7` (20:43:13) did not touch it. Three files changed after that
snapshot and are **working-tree only** (`git status`: modified `extras.jsonl`, `proposed-fix.diff`,
`table.md`; new `X1Sparse.md`, `evidence.txt`, `rates.txt`, `rows-head.jsonl`, `table-head.md`,
`scripts/one.py`, `scripts/kama-llamacpp-live-head-7fab24e7.py`). Integration should re-read the
current files, because the snapshot versions are wrong in two ways: its `extras.jsonl` carries the
harness `TypeError` row described in F4, and its `proposed-fix.diff` is the earlier ordering that
puts the size check *before* the sparse check — applying that one verbatim would change the sparse
token and break `_provenance_selftest`. The committed `rows-*.jsonl` are byte-identical to the
current ones and need no re-copy.

No tool was installed or upgraded. Scratch `/fast/scratch/hyaku/kama-r49/X1Sparse` was removed
after the receipt copies above were verified.
