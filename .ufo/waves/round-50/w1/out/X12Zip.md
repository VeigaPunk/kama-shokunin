# X12Zip — record-time archive bounds (round-50 carried item, lane kama)

**Verdict:** the four required archive shapes at `97c864b` are all refused **before any
byte of the member is hashed**, in ≤0.05 s and with flat ~30 MB peak RSS — the round-49
count/size/truncation bounds hold. But the record-time bounds do **not** bound
*decompressed* work: `tarfile`'s index walk skips a member by seeking its declared size,
and on a compressed archive that seek decodes the bytes, so a **24,054-byte bz2 archive
costs 52.1 s** of record time (measured) and the 1 GiB `ARCHIVE_MAX_BYTES` cap permits
**~27 days** from one archive. Defect **F1** (below) with a proposed, measured fix
(`proposed/verify-archive-walk-bound.diff`).

Probe target: `tools/kama-llamacpp-live.py` at lane commit
`97c864bead3ee4a2f629574e77263d33834ec98a`, sha256
`61e777b743aedb55c9532c4892d14a6cf0600f9f6f260595d635ec50ff708507` (byte-identical at the
lane tip `3b79eadd`). No archive member was ever executed; "server" is inert stub bytes
(8192 B, `\x7fELF` + a fixed pattern); no `llama-server` was started. Neither frozen counter
was run from this seat — the subject is the live tool's record-time verifier itself
(`verify_archive_member`, `tools/kama-llamacpp-live.py:216`), which both counters exercise
indirectly.

Method: `measure_case.py` imports the frozen tool verbatim, wraps `hashlib.sha256` so every
digest instance is counted with the bytes fed to it (instance 0 = archive digest,
instances ≥1 = member digest), wraps `tarfile.TarFile.extractfile` and `TarFile.next`
(walk offsets, decompressed position), then calls `verify_archive_member` once. One case per
process, spawned by `run_probe.py`; `seconds` is the call, `peak_rss_kb` is
`getrusage(RUSAGE_SELF).ru_maxrss` of that child. (RSS is only quoted from
driver-spawned children: a direct child of this session's shell inherits a 7.2 GB
hiwater mark and reports nonsense.)

## 1. The four required cases (frozen tool)

| case | archive | shape | token | seconds | peak RSS | member hashes | extractfile |
|---|---|---|---|---|---|---|---|
| (a) `a_20000_tiny` | 9.78 MiB | 20,000 zero-length members then the real member | `provenance-archive-too-many-members` | **0.049** | 31 MB | **0** | **0** |
| (b) `b_truncated_declared_size` | 5.51 KiB | one member *declaring* the 8192-byte server size, data cut at 4103 B, no EOF blocks | `provenance-archive-unreadable` | **0.001** | 27 MB | **0** | **0** |
| (c) `c_gzip_zeros_huge` | 17.87 MiB | gzip of 4 GiB of zeros (decompressed "index" that never is a tar) | `provenance-member-absent` | **0.010** | 29 MB | **0** | **0** |
| (d) `d_valid_many` | 24.82 KiB | **positive control**: 4000 members + the real member, correct archive sha, member sha and size | **accepted** (`(archive_sha, member_sha)`) | **0.048** | 29 MB | 1 (8192 B, as intended) | 1 |

Evidence for "before any hash of the member": `member_hash_instances == 0` and
`extractfile_calls == 0` in (a), (b), (c); the only digest in those runs is the archive
digest, fed exactly `archive_bytes` (compressed bytes). In (c) the walk consumed **512
decompressed bytes** (`tar_walk.last_tell`) — the 4 GiB never materialise because the
first decompressed block is an all-zero (end-of-archive) header. Raw rows:
`run1/results.json`, `summary.csv`.

## 2. Controls and boundaries (frozen tool)

| case | archive | token | seconds | note |
|---|---|---|---|---|
| `b2_padded_wrong_data` | 10.00 KiB | `provenance-member-digest-mismatch` | 0.001 | declared size == server size, wrong bytes: hashes **exactly 8192** member bytes (the member-hash bound is the declared/server size) |
| `boundary_4096_ok` | 2.01 MiB | **accepted** | 0.040 | exactly `MEMBER_MAX_COUNT` entries — cap is `count > 4096` |
| `boundary_4097_cap` | 2.01 MiB | `provenance-archive-too-many-members` | 0.040 | one entry past the cap; refused without hashing the member |
| `c2_gzip_seek_512m` | 2.23 MiB | `provenance-member-absent` | 0.247 | a declared 512 MiB skip is **decoded** |
| `c2_gzip_seek_2g` | 8.94 MiB | `provenance-member-absent` | 0.952 | 2 GiB decoded |
| `c3_gzip_seek_past_eof` | 1.12 MiB | `provenance-archive-unreadable` | 0.127 | declares 64 GiB, holds 256 MiB: cost stops at the stream end |
| `e_xz_seek_4g` | 610.25 KiB | `provenance-member-absent` | 5.939 | 4 GiB decoded (xz) |
| `f_bz2_seek_256m` | **274 B** | `provenance-member-absent` | 0.407 | 256 MiB decoded |
| `f_bz2_seek_8g` | **5.96 KiB** | `provenance-member-absent` | 12.895 | 8 GiB decoded |
| `f_bz2_seek_32g` | **23.49 KiB** | `provenance-member-absent` | **52.118** | 32 GiB decoded (`run3/`) |
| `f_bz2_seek_past_eof` | 5.96 KiB | `provenance-archive-unreadable` | 12.678 | declares 64 GiB, holds 8 GiB |

Peak RSS never leaves **26–31 MB** across all 15 cases, including the 32 GiB one: the
failure mode is CPU time, not memory, so a memory bound would not see it.

## 3. F1 — record-time bounds do not bound decompressed bytes (defect)

**Where:** `tools/kama-llamacpp-live.py:258-264` (frozen at `97c864b`):

```
258            with tarfile.open(fileobj=arc, mode='r:*') as tf:
259                found, count = None, 0
260                for info in tf:
261                    count += 1
262                    if count > MEMBER_MAX_COUNT:
263                        raise SetupError('provenance-archive-too-many-members')
264                    if info.name == member:
```

`mode='r:*'` auto-detects gzip, bz2 and xz. `tarfile` skips member *k*'s data when it
fetches header *k+1* (`TarFile.next()` → `fileobj.seek(offset_data + blocks(size))`), and
on a compressed stream that seek **decodes** `size` bytes. The only bounds are
`ARCHIVE_MAX_BYTES` (`:212`, compressed file size) and `MEMBER_MAX_COUNT` (`:213`), neither
of which is a bound on decoded bytes; the member-size check (`:275`) and the sparse check
(`:273`) both run *after* the walk has already paid for every skip.

**Show it** (`run2/`, `run3/`):

```
python3 -I run_probe.py --out run2 --scratch <S> --builder build_cases2.py \
        --tool <clone at 97c864b>/tools/kama-llamacpp-live.py
python3 -I run_probe.py --out run3 --scratch <S> --builder build_cases3.py --tool <same>
```

- `f_bz2_seek_32g`: archive on disk **24,054 B**, one 512-byte header naming `rel/other`
  with `size = 32 GiB`, followed by zeros, bz2 level 9, sha equal to the
  `--server-asset-sha256` the caller supplies → **52.118 s**, token
  `provenance-member-absent`, `tar_walk.last_tell = 34359738880` (the whole 32 GiB decoded).
- Scaling is linear and codec-selected (`codec-ratios.txt`): bz2 on zeros is **1,290,555×**
  at 647 MB/s of decode, gzip-9 1,029× at 651 MB/s, xz 6,851× at 705 MB/s.
  Measured bz2 bombs: 274 B → 0.407 s, 5.96 KiB → 12.895 s, 23.49 KiB → 52.118 s
  (≈ **2.17 ms of record time per archive byte**; 1 h ≈ 1.7 MB, 1 day ≈ 40 MB).
- At the tool's own cap (`1 GiB` compressed) that is ≈ **2.3×10⁶ s ≈ 27 days** of record
  time from a single archive that passes every existing check.
- The digest check does not defend: `asset_sha256` is the audited object's own claim
  (`tools/kama-live-replay.py:290` acquires the archive against the receipt's
  `server.asset_sha256`, and `:326` passes it as `--server-archive`), so the attacker
  writes the sha of their own bomb.

**Proposed fix** (`proposed/verify-archive-walk-bound.diff`, applies with `patch -p1` at the
lane root; verified `APPLIES_CLEAN` against the frozen file): bound the walk's *declared*
bytes from the header, before `tarfile` performs the skip —

```python
ARCHIVE_MAX_WALK = 1 << 30       # decompressed bytes the index walk may skip (round 50)
...
                for info in tf:
                    count += 1
                    if count > MEMBER_MAX_COUNT:
                        raise SetupError('provenance-archive-too-many-members')
                    if info.sparse is not None:
                        raise SetupError('provenance-member-sparse')
                    walk += 512 + info.size
                    if info.size > ARCHIVE_MAX_WALK or walk > ARCHIVE_MAX_WALK:
                        raise SetupError('provenance-archive-walk-too-large')
                    if info.name == member:
                        found = info
```

The loop body runs *between* the header being yielded and the next `next()`, i.e. before the
skip, so the refusal costs nothing. The patch also moves the sparse refusal into the loop
(any sparse member, same `provenance-member-sparse` token — otherwise a 10¹⁵-byte sparse
header would be caught by the new bound and change the round-49 token), drops the now
unreachable post-loop sparse check, documents the token, and adds a bz2 bomb case to
`_provenance_selftest`.

**Measured effect** (`run1p/`, `run2p/`, `run3p/`, same cases, patched copy in
`proposed/kama-llamacpp-live.py`):

| case | frozen | patched |
|---|---|---|
| `f_bz2_seek_32g` (declares 32 GiB) | 52.118 s, `member-absent` | **0.002 s**, `provenance-archive-walk-too-large` |
| `f_bz2_seek_8g` | 12.895 s | **0.002 s**, `walk-too-large` |
| `f_bz2_seek_past_eof` | 12.678 s | **0.002 s**, `walk-too-large` |
| `e_xz_seek_4g` | 5.939 s | **0.001 s**, `walk-too-large` |
| `c2_gzip_seek_2g` | 0.952 s | **0.005 s**, `walk-too-large` |
| `c3_gzip_seek_past_eof` | 0.127 s | **0.001 s**, `walk-too-large` |
| `f_bz2_seek_256m` (under the bound) | 0.407 s, `member-absent` | 0.411 s, `member-absent` (residual, by design) |
| `a_20000_tiny` / `b_truncated` / `c_gzip_zeros` / `b2_padded` / boundaries / `d_valid_many` | tokens above | **unchanged tokens**, ≤0.042 s |
| `--selftest` | `selftest: ok` (exit 0) | `selftest: ok` (exit 0), now including the bomb case |

Residual after the fix: a skip *under* 1 GiB still decodes (256 MiB → 0.41 s) and the
worst case at the bound is 1 GiB/647 MB/s ≈ 1.6 s (bz2). If that is still too much, lower
`ARCHIVE_MAX_WALK`; the real b11909 asset is ~70 MB compressed, so 1 GiB has ≳10× headroom
on both `ARCHIVE_MAX_BYTES` and `ARCHIVE_MAX_WALK`.

## 4. Secondary observations (no action implied for this round)

1. **Truncated-but-same-declared-size** is refused as `provenance-archive-unreadable`
   (`:280`, from the walk's `ReadError`), never reaching the size check at `:275`. That is
   *stricter* than needed and safe (no member byte hashed), but it is not the
   `provenance-member-size-mismatch` token the docstring's taxonomy suggests; a receipt
   defect looks like an unreadable archive. Informational.
2. **Boundary is `>` not `>=`**: 4096 entries accepted (`boundary_4096_ok`), 4097 refused.
   Consistent with the docstring ("at most 4096").
3. **`member_hash_bytes` is exactly the declared/server size** (8192 in
   `b2_padded_wrong_data`) — the member hash itself is bounded by `server_size`, which is
   the on-disk `--server` file the tool already hashes. The only unbounded lever is the
   walk, i.e. F1.
4. **Adjacent, code-read only (not measured)**: `tools/kama-live-replay.py:130-142`
   (`fetch`) writes the response body to disk with no size cap, and `:290` calls it before
   `verify_archive_member` applies `ARCHIVE_MAX_BYTES`; an oversized asset is fully
   downloaded and only then refused `provenance-archive-too-large`. Disk-fill lever, not
   exercised here (would need an https origin).
5. The two frozen round-50 counters, the preregistration and the controls were not touched;
   F1 is in neither counter's predicate, so it does not move C1/C2 (`bind`/`teardown` and
   `fixture`/`lane`/`scenarios` are silent on record-time archive cost).

## 5. Hygiene

- Lane `/home/vgpnk/Projects/shokunin/kama-shokunin` read-only: only `git log/diff/show`,
  file reads, and one `--selftest` run in-tree (writes nothing; it uses a temp dir and
  loopback listeners that it closes). No mutating git or jj.
- Tooling: nothing installed or upgraded; python 3.14.8 stdlib only, no network access from
  this seat (no downloads; the counters were not run).
- No `llama-server` was started (`pgrep -af llama-server` empty before finishing); scratch
  `/fast/scratch/hyaku/kama-r50/X12Zip` removed.

## 6. Artifacts

- `summary.md` / `summary.csv` — the 15-case table (frozen vs patched).
- `run1/`, `run2/`, `run3/` — frozen-tool receipts (`results.json`, `results.txt`);
  `run1p/`, `run2p/`, `run3p/` — the same cases against the proposed fix.
- `cases/<case>/case.json` — per-case manifest (archive size, archive sha, member, member
  sha, server size, shape); archives themselves were built in scratch and are regenerated
  deterministically by the builders.
- `build_cases.py`, `build_cases2.py`, `build_cases3.py` — case builders (a–d + boundary,
  codec bombs, 32 GiB dose point); `measure_case.py` — instrumented single-case prober;
  `run_probe.py` — driver; `summarize.py` — table; `codec_ratios.py` +
  `codec-ratios.txt` — codec ratio/decode sample.
- `proposed/kama-llamacpp-live.py` (full patched copy, 2232 lines, sha256
  `a4db2f07be9f8ef71729a018d76b19affdb8dbe4744a6e96cf5b53ad487d6e71`) and
  `proposed/verify-archive-walk-bound.diff` (unified diff, 83 lines, `patch -p1` at lane
  root, `APPLIES_CLEAN` against `97c864b`).
