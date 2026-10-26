# Sen2Archive — host safety of `verify_archive_member()` at 74558c71 (round 49, lane kama)

**Verdict:** the bounded archive-member verification is safe on every axis the round-49 build
claims (file cap, entry cap, sparse/size/truncation checks all measured and holding), but two
*bounds it does not claim and does not have* let a caller-supplied archive make record time
unbounded: the 1 GiB cap limits the **archive file**, not the **inflated stream** (measured: a
204 KB bz2 file = 52 s of record time, projecting to ~75 h at the cap), and a PAX extension
header is materialised at its **declared** size, which tarfile accepts in base-256 (measured:
a 4.7 MB archive = 5.2 GB RSS). A validated ~30-line bound (SIGALRM + `RLIMIT_AS` around the
walk, plus a hash read bounded by the checked size) closes both, with no cost to legitimate
archives. One fail-closed contract defect (chained PAX headers → `internal:RecursionError`
instead of a `provenance-` token) also measured.

Reviewed bytes: `tools/kama-llamacpp-live.py` at `74558c71c38ceaeace15fd4cf8aa9d84977584b1`,
sha256 `72e76079995c5ba8269bbaa31e30b8c15c5e503de2a58e603b78561424bffd4c`, extracted read-only
with `git -C <lane> archive 74558c71 tools/kama-llamacpp-live.py | tar -x -C $S/build74558`
(same sha256 as `git show 74558c71:tools/kama-llamacpp-live.py`). Nothing in the lane was
executed against the working tree except where explicitly marked *worktree*.

```
S=/fast/scratch/hyaku/kama-r49/Sen2Archive; export TMPDIR=$S
mkdir -p $S/build74558 && cd $S/build74558
git -C /home/vgpnk/Projects/shokunin/kama-shokunin archive 74558c71 tools/kama-llamacpp-live.py | tar -x -C .
sha256sum tools/kama-llamacpp-live.py       # 72e76079…bffd4c
export KLL_TOOL=$S/build74558/tools/kama-llamacpp-live.py
python3 $S/m1_cap.py ; python3 $S/m2_bombs.py ; python3 $S/m3_members.py
python3 $S/m4_trunc.py ; python3 $S/m6_pax.py ; python3 $S/m8_bigbombs.py
```
Each script imports the reviewed file by path and calls `verify_archive_member` directly
(`$S/lib.py` → `load()`), so the numbers are the record-time path itself, which the tool runs
before anything is started (`tools/kama-llamacpp-live.py:1662-1666`). No untrusted binary was
executed: the stub server in the CLI run is a two-line `/bin/sh` script that verification
rejects before start (`$S/stub-server.sh`, never wrote its marker).

## Severity table

| # | severity | what | measured cost of one record run | line |
|---|---|---|---|---|
| D1 | **major (host DoS, record time)** | walk must inflate the *whole* compressed stream; cap applies to the file | bz2 204 KB → 52 s; xz 4.8 MB → 12 s; gzip 287 MB → 29 s | 208, 248-255 |
| D2 | **major (host DoS, memory)** | PAX extension body read at its declared size (base-256: unbounded) and never counted | 4.7 MB archive → 5.2 GB RSS; 1.17 MB → 1.3 GB RSS | 248-267 |
| D3 | moderate (contract, fail-closed) | chain of ≥ ~900 PAX extensions raises `RecursionError`, which `except (OSError, EOFError, tarfile.TarError)` does not catch | 6.9 KB archive → CLI exit 2, `setup_error: "internal:RecursionError"` | 270 |
| D4 | moderate (cap bypass) | size cap is checked on a path `stat` before `open`; the hash loop then reads to EOF | stat 1 MiB, file 1.28 GiB → 1.28 GiB hashed in 0.55 s | 228-243 |
| D5 | low (label) | a short/truncated member payload is reported `provenance-archive-unreadable`, not a member token | 4 crafted archives, ≤ 0.001 s each | 270 |

Not re-reported (already owned elsewhere): the `stat`→`open` FIFO hang is seat **V1Live**'s F1
(reproduced here, see "duplicate" below) and is already fixed in the lane worktree.

## D1 — inflated size is unbounded; the 1 GiB cap is on the compressed file (major)

`ARCHIVE_MAX_BYTES = 1 << 30` (`:208`) is checked against `st.st_size` (`:233-234`), but
`tarfile.open(fileobj=arc, mode='r:*')` (`:248`) inflates gzip/bz2/xz/**zstd** (Python 3.14
`tarfile` sniffs zstd too), and iterating the catalogue to its end (`:250-255`) must consume
every inflated byte, including the payload of members that are skipped. The member itself is
bounded (`size == server_size`, `:262-263`); the walk is not. Fixtures: target member first,
then one zero-filled member of N bytes, correct archive digest, in each case a real regular
file far below the cap.

```
$ python3 $S/m8_bigbombs.py          # at KLL_TOOL=74558c71 bytes
gzip_64GiB {"archive_bytes": 299868536, "inflated_bytes": 68719476736, "ratio": 229.2, "seconds": 28.886, "mb_per_s": 2268.8, "projected_cap_seconds": 103.4}
xz_32GiB   {"archive_bytes": 4997908,  "inflated_bytes": 34359738368, "ratio": 6874.8, "seconds": 11.709, "mb_per_s": 2798.5, "projected_cap_seconds": 2515.5}
bz2_32GiB  {"archive_bytes": 208203,   "inflated_bytes": 34359738368, "ratio": 165030.0,"seconds": 52.244, "mb_per_s": 627.2,  "projected_cap_seconds": 269432.1}
$ python3 $S/m2_bombs.py
gzip4g   {"archive_bytes": 18741957, "seconds": 1.819, "result": "ok"}      # 4 GiB inflated
bz2_512m {"archive_bytes": 3397,     "seconds": 0.844, "result": "ok"}      # 512 MiB inflated
$ python3 $S/../zstd (evidence/zstd_74558.txt)
zstd_8GiB  {"archive_bytes": 262270,  "seconds": 0.239, "mb_per_s": 34276.2}
zstd_32GiB {"archive_bytes": 1048701, "seconds": 0.937, "mb_per_s": 34971.2}
```

Tool level, same bytes, verification failing *after* the walk (so no server is started):

```
$ KLL_TOOL=$S/build74558/tools/kama-llamacpp-live.py python3 $S/m9_cli.py
{"label": "bz2_8g", "archive_bytes": 52160, "exit": 2, "seconds": 13.626,
 "setup_error": "provenance-member-size-mismatch", "internal_fault": null, "outcome": "setup-error"}
```

Exploit path: `--server-archive` is a file the caller points at; in the lane's own flow the
archive is what `kama-live-replay.py` re-acquires from the receipt's `provenance.server.asset_url`
(a receipt whose URL and digest are attacker-chosen is exactly what the round-47/48 provenance
work exists to distrust). 52 KB of bz2 buys 13.6 s of process time; the arithmetic at the cap
(measured ratio × measured inflate rate, `[INFERENCE]` by linear extrapolation) is ~103 s for
gzip, ~42 min for xz, ~75 h for bz2, ~17 min for zstd. The record-time walk has no time bound
anywhere in the tool, and the C1 counter's cap leg only budgets 30 s around a *sparse* fixture
(`tools/round49-replay-witness-audit.py:353-391`), so C1 keeps passing while this is open.

Smallest remediation: bound the walk, not the file. `ARCHIVE_WALK_SECONDS = 20` around the
`tarfile` block via `signal.setitimer(ITIMER_REAL, …)` with a private exception mapped to
`provenance-archive-walk-timeout`; measured benign worst case at the cap is 1.0 s (below), so
20 s is 20× headroom and 1/5 of the failure cost of the cheapest bomb above.
(Cheaper-but-ad-hoc alternative: refuse compressed archives whose measured ratio shows
`st.st_size < 1 MiB` while the member is ≫ server size — not recommended, it is a guess about
content rather than a bound on work.)

## D2 — PAX extension bodies are materialised at declared size and are not counted (major)

`MEMBER_MAX_COUNT` (`:209`, `:251-253`) counts catalogue entries; a PAX extended header is
consumed inside `tarfile`'s `_proc_pax` and never reaches the loop, and its size field is
`nti()`-decoded, so `0x80…` base-256 gives sizes beyond the 8 GiB octal maximum. `_safe_read`
(Python 3.14) avoids one huge pre-allocation but still joins the whole body in memory
(`chunks.append`/`b"".join`), then decodes the record to `str`.

```
$ python3 $S/m6_pax.py
pax_valid_256m  {"archive_bytes": 1171599, "record_bytes": 268435456,  "rss_mb": 1306.2, "seconds": 0.382, "result": "ok"}
pax_valid_1024m {"archive_bytes": 4685688, "record_bytes": 1073741824, "rss_mb": 5232.9, "seconds": 1.460, "result": "ok"}
pax_b256_1PiB   {"archive_bytes": 182, "seconds": 0.0, "token": "provenance-archive-unreadable"}
pax_chain_200   {"archive_bytes": 1742, "pax_headers": 200,  "result": "ok"}          # never counted
pax_chain_3000  {"archive_bytes": 22568, "pax_headers": 3000, "result": "RecursionError"}
```

RSS is `VmHWM` (`$S/lib.py:rss_mb`) — `ru_maxrss` is unusable in this environment (6.2 GiB at
baseline). Peak is ~5× the declared record (buffer + chunk list + joined copy + decoded `str`),
and on success the decoded value is retained in `tf.pax_headers` for the life of the open.
Extrapolating linearly `[INFERENCE]`: a 3-4 GiB declared extension (reachable from a ~18 MB
gzip or ~25 KB bz2 body) is ~15-20 GB RSS on a 30 GB host, i.e. the record run is OOM-killed
along with whatever else the operator is doing.

Smallest remediation: `ARCHIVE_WALK_RSS_BYTES = 2 << 30` set as the `RLIMIT_AS` **soft** limit
around the same block, restored in `finally`, with `MemoryError` mapped to
`provenance-archive-walk-memory`. It bounds the extension allocation wherever tarfile puts it,
costs nothing on the benign path (measured peak at the 1 GiB archive cap: 29.7 MB), and needs
no knowledge of tarfile internals. Validated below: 1 GiB record under a 1 GiB budget refuses
at 0.6 s with 1010 MB peak instead of 5.2 GB.

## D3 — a PAX chain raises `RecursionError` past the token boundary (moderate, fail-closed)

`_proc_pax` fetches the next header through `_fromtarfile`, so each chained extension recurses
one frame; the interpreter limit (~1000) is reached before `MEMBER_MAX_COUNT` ever fires.
`RecursionError` is not in `except (OSError, EOFError, tarfile.TarError)` (`:270`), so it leaves
`verify_archive_member` and lands in the tool's generic handler:

```
$ KLL_TOOL=…/74558…/kama-llamacpp-live.py python3 $S/m9_cli.py     # chain of 900 PAX ext headers
{"k": 900,  "bytes": 6947,  "exit": 2, "seconds": 0.084,
 "setup_error": "internal:RecursionError", "internal_fault": "internal:RecursionError", "outcome": "setup-error"}
{"k": 3000, "bytes": 22567, "exit": 2, "setup_error": "internal:RecursionError", …}
{"k": 200,  "bytes": 1741,  "exit": 2, "setup_error": "provenance-member-size-mismatch", …}
```

Impact is operability, not safety: exit 2 before any server start (fail-closed, measured: no
stub marker, no child), but a 6.9 KB archive reports an *internal fault* rather than a
`provenance-` refusal, i.e. any consumer that classifies on the token prefix (the counters do:
`startswith("provenance-member")`) sees a different class of event. Smallest remediation: add
`RecursionError` (and `MemoryError` if D2 is handled in-process) to the caught tuple at `:270`.

## D4 — the cap is checked on a path `stat`, then bytes are read to EOF (moderate)

`:228` `os.stat(archive)` → `:236` `open(archive, 'rb')` → `:241` `iter(lambda: arc.read(1<<20), b'')`.
The size that passed `:233` is not used to bound the read, and the object read is re-resolved by
`open`, so anything that grows or is swapped in between is hashed in full (a path in a shared
cache, an in-flight download, or a same-user actor).

```
$ KLL_TOOL=…/74558… python3 $S/m7_race.py grow
grow_beyond_cap  {"stat_size": 1048576, "real_bytes": 1342177280, "seconds": 0.546,
                  "token": "provenance-archive-digest-mismatch"}
grow_calibration_sha {"real_bytes": 1342177280, "seconds": 0.546}   # = full-file hash of 1.28 GiB
```
(the stat is shimmed to model the window; the 0.55 s equals a full 1.28 GiB sha256, so all
1.28 GiB were read although the cap check saw 1 MiB.)

Same window, worktree (uncommitted V1Live fix, `os.open`+`O_NONBLOCK`+`fstat`): the FIFO hang is
gone, but the fstat size still does not bound the read —

```
worktree_grow_after_fstat {"reported_size": 1048576, "real_bytes": 1342177280,
                           "verify_seconds": 0.688, "token": "provenance-archive-digest-mismatch"}
```

Smallest remediation (independent of which open path is kept): `remaining = st.st_size` and
`while remaining: chunk = arc.read(min(1<<20, remaining))` — the hash then covers exactly the
bytes the cap was checked on, and everything after is out of scope by construction. Validated
below (`v2_growth_stops_at_stat_size`: 4096 bytes read from a 64 MB file).

## D5 — truncated member is called "archive unreadable" (low, label only)

Header declares 4096 (= `--server` size), payload short:

```
trunc_payload_100   {"archive_bytes": 1024, "token": "provenance-archive-unreadable", "seconds": 0.001}
no_payload          {"archive_bytes": 1536, "token": "provenance-archive-unreadable"}
cut_mid_payload     {"archive_bytes": 1512, "token": "provenance-archive-unreadable"}
good_then_lying     {"archive_bytes": 6147, "token": "provenance-archive-unreadable"}   # later member declares 1 TiB, no payload
wrong_payload_full  {"archive_bytes": 5632, "token": "provenance-member-digest-mismatch", "seconds": 0.0}
```

All five refuse (so the answer to the brief's "declared size equals the server size but data is
truncated" is: caught, cheaply). The token chosen is the archive-class one, though the archive
is well-formed; a consumer distinguishing "archive damaged in transit" from "member bytes
damaged" cannot. Optional: rename to `provenance-member-truncated`, or leave and document.

## Bounds that hold (measured, no action)

| case | bytes | seconds | outcome |
|---|---|---|---|
| archive at the cap, member = 1 GiB (two sha256 passes + walk) | 1,073,735,680 | 1.069 | ok |
| archive at the cap, small member (hash pass + seek walk) | 1,073,735,680 | 0.451 | ok |
| 4096 members, 3000-char PAX names (compressed) | 89,317 | 0.129 | ok |
| 4096 members, short names, uncompressed | 4,208,640 | 0.038 | ok |
| 4097 members | 28,510 | 0.047 | `-too-many-members` |
| regular file one byte over the cap (sparse 1 GiB + 1) | 1,073,741,825 | 0.000 | `-too-large`, no read |
| GNU sparse member declaring 10^15 (build's own control) | 104 | 0.000 | `-member-sparse` |
| member size ≠ `--server` size | any | 0.000 | `-member-size-mismatch` |
| directory instead of archive | – | 0.000 | `-archive-not-regular` |

So the four claims in the round-49 build's docstring (`:217-225`) are all true as written; D1/D2
are the case where "the member is bounded" was mistaken for "the work is bounded".

## Proposed bounds (validated in scratch, full text + diff in this directory)

`proposed/kama-llamacpp-live.py` (full proposed file) and
`proposed/proposed-verify-archive-bounds.diff` (`git apply -p1` against 74558c71). Changes,
~30 lines net, stdlib only, no tarfile internals touched:

1. `ARCHIVE_WALK_SECONDS = 20` + `ARCHIVE_WALK_RSS_BYTES = 2 << 30` next to the existing caps
   (`:208-209`), `import resource`.
2. Hash loop bounded by the checked size: `remaining = st.st_size`.
3. Around the `tarfile` block only: save/handler `SIGALRM`, `setitimer(ITIMER_REAL, 20)`,
   `setrlimit(RLIMIT_AS, min(current_soft, 2 GiB))`; restore all three in `finally`.
4. `except _ArchiveWalkTimeout → provenance-archive-walk-timeout`, `except MemoryError →
   provenance-archive-walk-memory`, and `RecursionError` added to the unreadable tuple.

Measured on the patched file (`$S/m11_patch_v2.py`, `$S/m10_patchtest.py`):

```
v2_bz2_8g_5s_budget            {"archive_bytes": 52160,   "seconds": 5.0,     "token": "provenance-archive-walk-timeout"}
v2_gzip_64GiB_20s_budget       {"archive_bytes": 299868535, "seconds": 20.124, "token": "provenance-archive-walk-timeout"}
v3_pax_1GiB_under_1GiB_RLIMIT_AS {"archive_bytes": 4685642, "seconds": 0.615, "token": "provenance-archive-walk-memory", "rss_mb": 1010.0}
v2_chain900                    {"archive_bytes": 6947,   "seconds": 0.004, "token": "provenance-archive-unreadable"}
v2_growth_stops_at_stat_size   {"archive_bytes": 67114496, "seconds": 0.0, "token": "provenance-archive-digest-mismatch"}   # 4096 bytes read, not 64 MB
v2_good_gz                     {"archive_bytes": 120,    "result": "ok"}
v2_cap_1GiB                    {"archive_bytes": 1073735680, "seconds": 1.003, "result": "ok"}   # no regression at the cap
```

Choosing the numbers: benign worst case measured at the cap is **1.0 s / 30 MB** (table above),
so 20 s is 20× time headroom and 2 GiB is ~70× memory headroom; the cheapest measured bomb
(52 KB) is refused in 5 s at a 5 s budget and in 20 s at the production budget, i.e. cost is
capped at one wall-clock budget per archive no matter what the archive is.

## Duplicate, not mine (state check only)

`stat` → `open` swapped for a FIFO blocks forever at 74558c71; reproduced with the stat
shimmed to a regular file and the path a FIFO, `timeout 10 python3 $S/m7_race.py fifo` → **rc=124**.
That is seat V1Live's F1 and the lane worktree already carries the `os.open(O_NONBLOCK)`+`fstat`
fix (uncommitted `git diff 74558c71 -- tools/kama-llamacpp-live.py`), which I confirmed closes it;
the residual window is D4 above, which that fix narrows but does not close.

## Hygiene

- Reviewed bytes only read from the lane (`git archive` of one file); no clone, no lane write, no
  jj/git mutation, no `git add/commit`. Scratch `S=/fast/scratch/hyaku/kama-r49/Sen2Archive`
  (`TMPDIR=$S`), removed after packaging.
- No server was started by this seat: `pgrep -af llama-server` → none; the m9 stub never ran
  (verification refuses before start; receipts show `outcome: "setup-error"`).
- No tool installs or upgrades were needed (python3 3.14.8 stdlib only); nothing to record.
- Evidence: `evidence/*.txt` (raw script output), `measurements.jsonl` (43 rows),
  `scripts/*.py` (every fixture generator, so every number is reproducible),
  `tool-level/*.receipt.json` (CLI receipts: chain200/900/3000 and the 52 KB bz2 case).
