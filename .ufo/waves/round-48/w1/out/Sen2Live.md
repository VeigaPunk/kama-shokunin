# Sen2Live — round 48 host-safety review: `verify_archive_member`, `--compare`, replay→live hand-off

**Verdict:** No escape survives — every member-type, path, extraction and digest case I could craft is refused with a stable token, the archive→member→executed-binary binding is sound, and replay hands the live tool exactly one digest-verified archive — but one **High** availability defect is reachable (a 104-byte archive makes `verify_archive_member` hash ~10^15 bytes — ≈6 days of one core at the measured 2.0 GB/s — before the server starts) and twelve further gaps remain (three Medium, five Low, four informational), led by `--compare` leaving its own 0/1/2 exit contract with a traceback.

Reviewed bytes — frozen tip `380bcdff9c8af06997c482f6eb03db926a794a2b`, not the working tree:

| file | sha256 |
|---|---|
| `tools/kama-llamacpp-live.py` | `1e5ea0fde985367d9d6335eae3825068e64063f032bbbc59fc8909e7b7f9a6d2` |
| `tools/kama-live-replay.py` | `69837013ec64b78a192e91b5b6a604a7437890c9e5a9c21dd175a0e87eb8b15f` |

Both copies are byte-identical to `git show 380bcdff:…` (checked). The working tree currently carries an **uncommitted** edit to `tools/kama-live-replay.py` (`7be002a1…`, +69/−26) by another seat; §Coordination says what it already covers and what it does not. `tools/kama-llamacpp-live.py` is unmodified in the tree, so findings F1–F4 apply to both.

Line numbers below are **tip** line numbers, read from the pinned copies in `out/Sen2Live/`.

---

## Method

Scratch only (`/fast/scratch/hyaku/kama-r48/Sen2Live`): byte copies of the two tip tools, crafted archives and receipts, and every probe calls the **real lane function** (imported from the pinned copy) or the **real CLI**, so both the code path and the exit codes are measured. No untrusted binary was executed; no server was started (the one real-live replay stops at the argparse https gate, before `pick_port`); no lane file, index or jj state was touched; no subagent. `repro_all.py` re-runs every cited measurement in order (≈2 min) and its output is `evidence.txt`.

## Trust model (stated once, it decides reachability)

`kama-live-replay.py` consumes a receipt that names **both** the asset/model URL and its `sha256` (`provenance()`, tip `:96-123`), downloads it, checks the digest (`acquire`, `:126-132`), extracts it, and then executes the extracted member through the live tool. The digest gate therefore proves *the bytes are the ones this receipt claims*, not that the receipt is authentic, and nothing anchors who serves them (§F12). **Every archive-shaped input below is therefore reachable with a receipt that did not come from the lane**, and the hardening is not defence-in-depth.

---

## 1. `verify_archive_member` (live `:193-219`)

### 1.1 What holds (measured, `probe_archive.py`; log in `evidence.txt`)

| crafted input | result |
|---|---|
| regular member, right digests | verified → `ok` |
| regular member, wrong `--server` digest | `provenance-member-digest-mismatch` |
| symlink / hardlink / directory / chrdev / blkdev / FIFO member | `provenance-member-not-a-file` (6/6) |
| contiguous (`CONTTYPE`) member | hashed as regular → digest compared |
| absent member | `provenance-member-absent` |
| wrong archive digest, non-tar, directory-as-archive, truncated member, missing file | `provenance-archive-digest-mismatch` / `provenance-archive-unreadable` |

The type gate at `:207` (`info.isfile()`) is doing real work: `REGULAR_TYPES` excludes `SYMTYPE`, `LNKTYPE`, `DIRTYPE`, `CHRTYPE`, `BLKTYPE`, `FIFOTYPE`, so none of the classic extraction primitives is even hashed.

**Duplicate member names are consistent, not a hole:** `tarfile.getmember()` is defined to return the **last** occurrence, and `extractall()` writes in archive order, so the bytes verified at `:206` are the bytes that land on disk. Measured with a good-first/decoy-last archive: verifying against the decoy digest succeeds and `extract()` writes exactly the decoy. No finding.

Digest is checked before the archive is parsed (`:199-203` before `:205`), and the whole call sits inside `main`'s guarded block (`:1559` inside the `try` whose `except BaseException` is `:1759-1760`), so an unexpected exception degrades to `internal:<Type>` + exit 2 with a receipt — the harness only loses its receipt when the call never returns (F3).

### F1 (High, availability) — the member's *declared* size drives an unbounded read

`tools/kama-llamacpp-live.py:210-212` (loop) with the guard at `:207` and `:206`:

```python
            info = tf.getmember(member)          # :206
            if not info.isfile():                # :207  sparse passes this
                raise SetupError('provenance-member-not-a-file')
            ...
            for chunk in iter(lambda: fh.read(1 << 20), b''):   # :211
                h.update(chunk)                                    # :212
```

`TarInfo.isfile()` is true for `GNUTYPE_SPARSE`, `_proc_sparse()` rewrites `info.size` to the **declared** realsize, and `extractfile()` synthesises zeros for every hole. The loop has no size bound; the digest comparison (`:217`) happens **after** the read, so a wrong `server_sha256` still pays the full price.

```
$ python3 pax_sparse_probe.py          # PAX 0.1 and 1.0, 189 / 204-byte archives, realsize=10**15
0.1 declared=1000000000000000 archive_bytes=189 read=34360786944 eof=False seconds=3.70 GiB_per_s=9.28
1.0 declared=1000000000000000 archive_bytes=204 read=34360786944 eof=False seconds=3.84 GiB_per_s=8.95
$ python3 sparse_bounded_probe.py      # the read is bounded exactly by the declared size
declared=68719476736 archive_bytes=194 read=68719476736 eof=True seconds=9.19 -> 10**15 B would take 37 h (read only)
$ python3 sparse_rate_probe.py         # the real verify loop: read + SHA-256, the number that matters
declared=1073741824 archive_bytes=104 seconds=0.530 GB_per_s=2.03 -> a 10**15 declared member takes 137 h
declared=4294967296 archive_bytes=104 seconds=2.134 GB_per_s=2.01 -> a 10**15 declared member takes 138 h
$ python3 probe_archive.py ... (old-GNU header, 12-byte octal cap)
gnu-sparse-declared-1073741824   seconds 0.578   archive 104 bytes
gnu-sparse-declared-8589934591   seconds 4.438   archive 103 bytes
```

Impact: 137–143 h (5.7–6 days) of one core on a 104-byte input, single-threaded, before `pick_port` (`:1579`) and `Popen` (`:1648`) — the harness never reaches its 10 s SIGTERM grace, its readiness timeout or its receipt, and `--server-archive` has no timeout. The verifier runs at ≈2.0 GB/s because the loop also hashes (a read-only loop reaches 9.3 GB/s, so 137 h is the cost of SHA-256 on zero pages, not of I/O). The 12-byte octal field of old GNU format caps the damage at ~8 GiB (≈4 s); PAX `GNU.sparse.size`/`GNU.sparse.realsize` are decimal and cap nothing.

Smallest fix (verified, `proposed-verify.diff` / `proposed_verify.py`): refuse sparse members and cap the member — `if not found.isfile() or found.sparse or found.size > MEMBER_MAX_BYTES:`. Against the same matrix the sparse case is now refused in 0.000 s and every other verdict is unchanged.

### F2 (Medium) — `getmember()` materialises the whole index

`tools/kama-llamacpp-live.py:206`. `getmember` calls `getmembers`, which scans the entire archive into a list of `TarInfo` before any name comparison:

```
1M members:  archive_bytes=9852048  python_peak_MB=443.9  seconds=23.19  index_len=1000000
300k members: archive 2.97 MB, 3.1 s, 133 MB heap (tracemalloc)
```

Impact: ≈444 bytes of Python heap and ≈23 µs per member, all before the one member that matters is read. A ~50 MB gzip with 5M entries is ≈2.2 GB RSS **[INFERENCE: linear extrapolation of the measured 1M point]**, on a host that is also running the lane's other seats.

Smallest fix (verified): iterate the `TarFile` (streaming), keep the last match, and cap the entry count — `for info in tf: count += 1; if count > MEMBER_MAX_COUNT: raise SetupError('provenance-archive-too-many-members')`. Measured after the fix: 20k entries refused in 0.054 s, last-occurrence semantics preserved.

### F3 (Low) — a non-regular archive path blocks forever

`tools/kama-llamacpp-live.py:199` (`sha256_file(archive)` → `open()`) and `:205` (`tarfile.open(archive)`), no `S_ISREG` check:

```
$ python3 -c "... verify_archive_member('fifo.tgz', ...)"; echo fifo_rc=$?      → fifo_rc=124   (timeout 5)
$ python3 -c "... verify_archive_member('/dev/zero', ...)"; echo devzero_rc=$?  → devzero_rc=124
```

`open()` on a FIFO blocks until a writer appears; `/dev/zero` hashes forever. `:200` catches only `OSError`, so neither is classified `provenance-archive-unreadable`. Not reachable through replay (it downloads into a regular file); reachable by any `--server-archive` mistake or a symlink planted in a shared `$TMPDIR`. The block happens before the signal handlers are installed, so even SIGINT handling is not yet in place.

Smallest fix (verified): `os.stat` + `stat.S_ISREG` + size cap before opening → `provenance-archive-unreadable` in 0.000 s.

### F4 (Low) — hash-then-reopen: the recorded archive digest need not be the parsed bytes

`:199` hashes **by path**, `:205` opens **by path** again. An attacker with write access to the archive's directory (shared `$TMPDIR`, or `--work` on a shared filesystem) can swap the file between the two opens: `provenance.verified.archive_sha256` then records an archive whose member was never read. The member→executed-binary binding still holds (`:1561` passes `server_sha`, `:1564-1566` record the digest it returned), so the impact is a false provenance record, not wrong execution.

Smallest fix (verified in the same patch): open once, hash that descriptor, `seek(0)`, `tarfile.open(fileobj=arc, mode='r:*')`.

---

## 2. `kama-live-replay.py --compare` (tip `:154-202`, `:404-414`)

### 2.1 What holds

Identical receipts → `compare match=True`, exit 0; schema, outcome, `server/model.sha256`, presence/evaluation and projection differences each produce a line and exit 1; missing, empty and invalid-UTF-8 files → `compare could-not-read: …`, exit 2. The module docstring's contract is otherwise honoured.

### F5 (Medium) — malformed-but-parseable receipts escape the contract with a traceback and **exit 1**

`:157` (`json.loads` on a body that may be a dict), `:161-163` (a dict-valued `data`), `:197` (`projection` outside every handler), `:412` (`except (OSError, ValueError)` only), `:409`.

```
$ python3 compare_probe.py deep     # 200 000-deep JSON array
{"rc": 1, "stdout": "", "stderr_tail": "RecursionError: Stack overflow (used 8140 kB) while decoding a JSON array ..."}
$ python3 compare_probe.py shape
{"rc": 1, "stderr_tail": "TypeError: the JSON object must be str, bytes or bytearray, not dict", "label": "models-body-is-object"}
{"rc": 1, "stderr_tail": "TypeError: 'int' object is not iterable", "label": "models-data-is-int"}
```

Exit **1 is the documented "the receipts differ" code**, so a caller cannot distinguish unusable input from a real disagreement, and gets a traceback instead of a `mismatch:` line. In the replay path the same escape is worse: `compare()` is called at `:249`, and `replay()`'s handler at `:261` lists `(OSError, ValueError, tarfile.TarError, TimeoutExpired, URLError)` — a `TypeError` or `RecursionError` from `projection`/`json.load` (`:209`) leaves `replay()` and `main` writes **no `--out` JSON at all**.

Smallest fix (verified, `proposed-replay.diff`): strict `projection` raising `ValueError`, `compare()` turning it into an explicit `projection:unreadable:<why>` mismatch, and `except (OSError, ValueError, RecursionError, MemoryError)` on the read path. After the fix: deep nesting → exit 2 `could-not-read: RecursionError…`; the two `TypeError` cases → exit 1 with a named mismatch; identical and the three real round-48 receipts → exit 0 (unchanged).

### F6 (Medium) — a dict-valued `models.data` silently projects to `[]`: two different receipts compare equal

`:161-163` iterates `body.get("data") or []` and keeps only `dict` elements; a JSON object where a list belongs is iterated as its **keys**, every key is dropped, and the surface becomes `{"data": [], "models": []}` on both sides.

```
$ python3 compare_probe.py vacuous
{"rc": 0, "stdout": "compare match=True mismatches=0", "label": "dict-data-A-vs-B"}
   # A: {"data": {"real-model-1": {"owned_by": "team-a"}}}
   # B: {"data": {"totally": {"different": "content"}}}
```

This is exactly the vacuous match `compare()`'s docstring (`:178-179`, *"never a vacuous match"*) promises not to allow, on the strongest surface the round-47 D4 closure added. Reachable with a hand-edited or foreign receipt; the live tool always writes a JSON string body.

Smallest fix (verified): require list-typed `data`/`models` and refuse otherwise → `projection:unreadable:models-body-shape`, exit 1.

### F7 (Info) — no input size bound

A 400 MB receipt loads in 1.09 s with an **824 MB** child RSS (`compare_probe.py big`). Both paths are operator-named, so this is not an attack surface; noted because receipts also arrive from elsewhere.

---

## 3. Replay → live hand-off (tip `:126-137`, `:223-252`)

### 3.1 What holds (measured end to end, `passthrough_probe.py`)

```
[fake-live v5] replay rc=0 match=True
  --server-archive occurrences=1 value=['.../work-v5/download/llama.tgz']
  --server value=['.../work-v5/server/rel/llama-server']
  tail=['--out', '.../work-v5/rerun-receipt.json']
[fake-live v4] replay rc=0 match=True
  --server-archive occurrences=0
[real-live file://] replay rc=2 refused=kama-llamacpp-live.py: error: --server-asset-url must be an https:// URL
  live_exit=2 extracted=True
```

- v5: exactly one `--server-archive`, the digest-verified download, spliced at `:241` before the trailing `--out`; v4: none. `--server` is the extracted member, and it is re-hashed against `server.sha256` after extraction and **before** execution (`:223-230`) — so "verified the archive" and "executed a binary" are the same bytes.
- `extractall(filter="data")` (`:137`) refuses `..`, outside/absolute symlinks, absolute hardlinks and special files (measured: `OutsideDestinationError`, `LinkOutsideDestinationError`, `AbsoluteLinkError`, `SpecialFileError`). An absolute *member name* is sanitised into the tree instead of refused — contained, acceptable.
- The live tool re-verifies the archive at record time (`:1559`) before `pick_port` (`:1579`) and `Popen` (`:1648`), so the hand-off is verified twice.
- A `file://` receipt gets copied, hashed and extracted, and then the live tool refuses at the https gate with exit 2 and no server — the backstop is real (F8 is about the wasted work, not execution).

### F8 (Low) — `fetch()` accepts `file://` in production

`:81-84`: `if not (url.startswith("https://") or url.startswith("file://")): raise Refused(f"url-scheme:{url}")`, while the docstring says *"file:// only for the selftest"* and the module doc says *"Network: https only"*. Consequence (measured above): replay reads, hashes and extracts any local path a receipt names before the live gate refuses. Smallest fix: `allow_file=False` parameter, set only by `_selftest` — already present in the uncommitted worktree edit (§Coordination).

### F9 (Low) — no download bound

`:89` `shutil.copyfileobj(r, fh, CHUNK)` with no byte counter and no `Content-Length` check (`:86`'s `timeout` is a socket timeout). A receipt URL that streams indefinitely fills `--work`; the digest is only computed after the whole copy (`:128`). [Code-level; not exercised — a hostile server was out of scope for this seat.]

Smallest fix: a per-asset byte cap enforced in the copy loop (assets are ~70 MB and ~4 MB, so 512 MiB is generous) plus a `Content-Length` precheck.

### F10 (Info) — the same declared-size problem reaches disk

`extract()` (`:135-137`) writes the declared size of a sparse member. On this filesystem the result is **sparse** (`extract_bomb_probe.py`: `apparent=1073741824 allocated=4096`), so I did **not** confirm disk fill; but `replay()` then re-reads the same declared size in `sha256_file(server)` (`:228`) and the live tool reads it again (`:211`), so a 10^15-declared member costs the F1 budget **twice per replay** — and on a filesystem without sparse support the extraction itself would allocate it.

---

## 4. Contract text

### F11 (Low, documentation) — the frozen C2 docstring overstates the live contract

`tools/round48-live-replay-v5-audit.py:41-47` says *"given any provenance flag, the live tool requires all of `--server-asset-url`, `--server-asset-sha256`, `--server-member`, `--model-url` **and `--server-archive`**; https:// URLs; a model URL pinned to a 40-hex `/resolve/<commit>/`"*. The code requires the four flags together (`:1462-1466`), takes `--server-archive` as the **v5 selector**, and applies the commit pin only inside that branch (`:1474-1479`):

```
$ python3 urlgate_probe.py
v5-any-host-unpinned             rc=2 stderr=... '--model-url must be pinned to a 40-hex /resolve/<commit>/ revision (v5)'
v4-any-host-unpinned-no-archive  rc=2 schema=kama-llamacpp-live/v4 setup_error=server-not-executable:.../missing-server
```

i.e. with the four v4 flags, **no** `--server-archive` and `--model-url https://evil.invalid/m.gguf`, the tool passes the provenance gate and records a v4 receipt. A reader grading against the contract would believe v4 runs are archive-bound and revision-pinned; they are not. Smallest fix: `"…and, for v5, --server-archive (which selects the revision pin)"`. The counter is frozen, so this is a finding, not an edit.

---

## 5. Origin anchoring (scope note for the L1)

### F12 (Info) — nothing anchors who serves the bytes

`--server-asset-url` only needs the `https://` prefix (`:1469-1470`), and `PINNED_MODEL_URL` (`:71`) is `^https://[^/]+/.+/resolve/([0-9a-f]{40})/.+` — **any host** with the right path shape passes:

```
v5-any-host-pinned-shape  rc=2 schema=kama-llamacpp-live/v4 setup_error=server-not-executable:.../missing-server
```

It reached `server-not-executable`, so the whole v5 gate accepted `https://evil.invalid/x/resolve/<40hex>/m.gguf` as an `https://evil.invalid/a.tgz` archive URL. Since replay then **executes** the archive's member, a receipt from an untrusted source is code execution with a fully green provenance block. That is consistent with what the v5 claim actually says (integrity against the receipt) and it does not weaken C2's 8/8 — but if the lane wants origin as well, the smallest step is a host+prefix allowlist in `provenance()` (the frozen names already fix `github.com/ggml-org/llama.cpp/releases/download/` and `huggingface.co/ggml-org/`).

### F13 (Info) — receipt-controlled server arguments

`:236` forwards `rec["ctx"]`, `rec["threads"]`, `rec["alias"]` into the server argv (`str(rec.get("ctx") or 256)`; no type or range check). A hostile receipt can request an arbitrary KV-cache size; what that costs then depends on the model. [The pass-through is measured; the allocation behaviour is `[INFERENCE]` from llama.cpp's `-c` semantics — no server was started.]

---

## 6. Proposed fixes (all verified)

`proposed-verify.diff` (live tool) and `proposed-replay.diff` (replay), full texts `proposed_verify.py` and `kama-live-replay-fixed.py`.

| fix | verification |
|---|---|
| `verify_archive_member`: `S_ISREG` + size cap + single descriptor + streaming index + entry cap + sparse/size refusal | 6/6 type refusals unchanged; sparse 1 GiB refused in 0.000 s (was 0.578 s + 1 GiB read); 20k entries refused in 0.054 s (was a full index); FIFO refused in 0.000 s (was a hang, rc 124); last-occurrence duplicate semantics preserved |
| drop-in safety | lane-shaped copy of the tree (`tools/` + `registry/`): tip `--selftest` → `selftest: ok`; patched `--selftest` → `selftest: ok` |
| replay: strict projection + `projection:unreadable` + `RecursionError`/`MemoryError` on the read path | deep nesting → exit 2 `could-not-read`; the two `TypeError` cases → exit 1 with a named mismatch (was exit 1 + traceback); the two silent-drop cases now name their reason; malformed-vs-malformed → exit 1 (was a vacuous match); identical + the three real round-48 receipts → exit 0; `--selftest` 21/21 |

Note: the live tool's `--selftest` needs its `registry/` sibling (`refused_ports()` reads `LANE/registry/endpoint-consumers.tsv`), so a bare copy of `tools/kama-llamacpp-live.py` fails `--selftest` with `SetupError` — an artefact of copying one file, not a lane defect. Reproduce with a lane-shaped copy as in `evidence.txt`.

## Coordination

`git status` in the lane shows `M tools/kama-live-replay.py`, worktree sha256 `7be002a1…`, +69/−26, **not** at `380bcdff`. As of my read it already gates `file://` behind `allow_file` (covers F8), adds `provenance.verified` digest checks and a v5 rerun-verification leg, and adds `TypeError`/`AttributeError` to `replay()`'s handler. It does **not** cover:

- F5's `RecursionError`/`MemoryError` (`--compare`'s read block, and `json.load` of the receipt at `:209`/`:409`);
- F6: a dict-valued `data` is still coerced to `[]` (`data = body.get("data") if isinstance(body.get("data"), list) else []`), so two different malformed receipts still compare equal;
- any of F1–F4 (the live tool is untouched).

`proposed-replay.diff` is against the tip and will conflict textually; the hunks to fold are the strict-projection one and the two exception tuples.

## Impact on the frozen claims

None of this falsifies C1 (7/7, untouched by this seat) or C2 (8/8): the v5 claim is *"the archive is hashed, its member is hashed, and they match the recorded digests before the server starts"*, and that is exactly what happens. F1/F2/F3/F10 are re-derived costs paid **before** those checks conclude, F5/F6 are contract/robustness defects on a tool that C2 also grades, F11 is a documentation defect in the frozen counter, and F12 says what the provenance block does *not* mean.

## Reproduction & artefacts

`out/Sen2Live/`: `repro_all.py` (driver), `evidence.txt` (its full log), `kama-llamacpp-live.py` + `kama-live-replay.py` (pinned reviewed bytes, `reviewed-bytes.txt`), `probe_archive.py`, `compare_probe.py`, `passthrough_probe.py`, `urlgate_probe.py`, `pax_sparse_probe.py`, `sparse_bounded_probe.py`, `sparse_rate_probe.py`, `extract_bomb_probe.py`, `proposed_verify.py`, `compare_fix_check.py`, `fake_live.py`, `proposed-verify.diff`, `proposed-replay.diff`, `kama-live-replay-fixed.py`.

Scratch `/fast/scratch/hyaku/kama-r48/Sen2Live` was removed after the run; no `/tmp` path is cited. No tool was installed (`RULES.md` tooling authorisation not used; the host-wide pacman pause was irrelevant), no service was started or stopped, no subagent, no `agent://all`.
