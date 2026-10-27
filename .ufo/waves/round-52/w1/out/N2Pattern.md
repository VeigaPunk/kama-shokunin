# N2Pattern — Round 52 Cross-Claim Pattern and Frontier Report

**Verdict:** CONFIRMED CROSS-CLAIM CONVERGENCE — Both Round 52 claims replace a vulnerable surrogate reference (an on-disk file path in C1; an external disclosure ledger row in C2) with the immutable object itself (an anonymous sealed memfd in C1; verbatim restored lines in C2); the next acute operational gap where a mutable path stands in for executable code is `LD_LIBRARY_PATH` (where 99.929% of the server's code resides in unsealed `.so` files on disk), paired with the model path after mapping (proven experimentally to load natively from a sealed memfd via `/proc/self/fd/N`), and unpinned receipt paths in SCORECARD.

---

## 1. Evidence: The Cross-Claim Pattern (Rounds 46–52)

### 1.1 Structural Convergence in Round 52
In Round 52, both declared claims arrived at the same core solution:
1. **C1 (Operability 8 → 8, memfd_create(2)):**
   - *Previous state (Round 51):* The server was executed from `<work>/server/<member>`. Identity was statted via `/proc/<pid>/exe` dev and inode. Seat `J3CopyDecoy` proved that a byte-identical host file copied over that path satisfied the counter; seat `J4Hardlink` proved that a hardlink of the host binary at that path satisfied the counter. The filesystem path `<work>/server/<member>` stood in for the verified archive member.
   - *Round 52 build (`5dacf2c70f94`):* `tools/kama-live-replay.py:222-257` (`sealed_member()`) copies the verified member straight from the archive tar stream into an anonymous sealed memfd (`memfd_create(2)`, `MFD_ALLOW_SEALING`, `F_ADD_SEALS = F_SEAL_WRITE | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL`), passes it via `--server-fd`, and execs it via `/proc/<pid>/fd/<n>`.
   - *Object invariant:* The running image has link count 0 (`st_nlink == 0`), resolves to `/memfd:llama-server (deleted)`, has no directory entry, and cannot be written or hardlinked. The executed image *is* the verified byte stream.
2. **C2 (Calibration 7 → 7, Append-Only Restoration):**
   - *Previous state (Round 51):* Threshold 1 graded every deletion event. Unheld lost lines were recorded in `registry/append-only-disclosures.tsv`. A disclosure row (commit, file, key sha256, count, mechanical class) stood in for the missing text. The ledger made `exit 0` cheap while leaving the documents mutilated.
   - *Round 52 build (`5dacf2c70f94`):* The 155 lines lost across 18 files were re-appended verbatim at the tails of those files under `## Restored lines (round 52)` inside five-backtick fences. Their disclosure rows were deleted from `registry/append-only-disclosures.tsv` (keeping only 10 rows where verbatim re-append would cause duplicate registry IDs).
   - *Object invariant:* The document physically holds the historical text again. The surrogate reference was discarded in favor of the object itself.

### 1.2 Historical Trace Through Rounds 46–52 and QUALITY (KQ76–KQ88)
Across earlier rounds, both claims progressively eliminated reference surrogates:
- **Round 46:**
  - *C1:* Tabular release note claims (`registry/release-recheck-b11906.tsv`, S486, S487) stood in for execution.
  - *C2:* A $\ge 20$-line event threshold stood in for append-only integrity, hiding in-place deletions under 20 lines (e.g. `LOG.md` at `ed135b3c`).
- **Round 47:**
  - *C2:* Provenance URLs and check pass/fail booleans in schema v4 receipts stood in for live execution; `K2Cheat` demonstrated fabricated 0-byte reruns.
  - *C1:* Declaring lines in `registry/append-only-contract.tsv` were identified by substring; `V1Ctr` showed lines containing negations bound the contract.
- **Round 48:**
  - *C2:* Schema v5 receipts pinned commit SHAs and verified provenance; `K2Cheat` and `K2Urlswap` showed a replay could verify digests without ever starting a server.
  - *C1:* Contract `region` cell (`exempt=<## title>`) used title strings as a surrogate for re-derived sections; `K1Regions` showed text could be laundered under exempt titles.
- **Round 49:**
  - *C1 (KQ76, KQ80):* Replay witness verified `/proc/<pid>/exe` digest and nonce tokenization; `K1Cheat` and `R0Controls` executed the host install binary because the observer never verified that `observed_pid == child_pid`.
  - *C2 (KQ77, KQ78):* Line origin `origin(l)` tracked birth headings, but relied on `git rev-list` traversal order; `K2Origin` showed sibling commit ordering could flip verdicts.
- **Round 50:**
  - *C1 (KQ81, KQ82):* Bound `observed_pid == child_pid`, verified PPID ancestry, canaries, and mapped model in `/proc/<pid>/maps`. Server was still an on-disk regular file.
  - *C2 (KQ83, KQ84):* Origin defined over Git commit-DAG births; complete accounting enforced `graded + ungraded == deleted`. The 20-line threshold still stood in as an event filter.
- **Round 51:**
  - *C1 (KQ85, S499):* Verified server image dev:inode via `/proc/<pid>/exe` against extracted member. `J3CopyDecoy` and `J4Hardlink` demonstrated that on-disk paths could still be substituted or hardlinked.
  - *C2 (KQ86, KQ87, KQ88):* Threshold 1 graded every deletion; `registry/append-only-disclosures.tsv` stood in as an external surrogate for unrestored lines.
- **Round 52:**
  - *C1:* Anonymous sealed memfd (`memfd_create(2)`, `seals=15`) replaces on-disk executable path.
  - *C2:* Verbatim fenced re-appends restore lost lines directly into files, deleting ledger rows.

---

## 2. Examination of Next Candidate Sites

Where in lane `kama` does a path or pointer still stand in for the object?

### Candidate 1: Shared Library Paths (`LD_LIBRARY_PATH`)
- **Evidence (`library-sizes-proof.txt`):**
  - `llama-server` binary size: **17,864 bytes** (17.45 KB, **0.071%** of executable code).
  - Sampled shared libraries (`libllama-server-impl.so`, `libllama.so`, `libllama-common.so`, `libmtmd.so`, `libggml-base.so`, `libggml-cpu-x64.so`, `libggml-cpu-alderlake.so`): **25,279,200 bytes** (24.11 MB, **99.929%** of executable code).
  - `tools/kama-llamacpp-live.py:1957` sets:
    ```python
    child_env['LD_LIBRARY_PATH'] = os.path.dirname(server_real)
    ```
- **The Gap:** The sealed memfd protects only the 17.8 KB launcher trampoline. The entire inference runtime, HTTP server, and CPU tensor kernels are dynamically loaded from an unsealed filesystem path `<work>/server/llama-b11909` via `LD_LIBRARY_PATH`. A decoy substitution of `libllama-server-impl.so` after extraction executes arbitrary code while `round52-replay-memfd-audit.py` checks only `/proc/<pid>/exe` and passes `sealed=1 met=True`.

### Candidate 2: Model Path After Mapping (`--model <path>`)
- **Evidence (`memfd-model-proof.txt`):**
  - Currently, `kama-llamacpp-live.py:1961` passes `-m <path>`.
  - In `tools/round52-replay-memfd-audit.py:313-323`, `mapped_model()` reads `/proc/<pid>/maps`, extracts the `path` string, and calls `os.stat(path)` and `sha_file(path)` from disk. The path string stands in for the mapped memory.
  - **Empirical Breakthrough:** We tested whether `llama-server` can load a model directly from an anonymous sealed memfd descriptor via `/proc/self/fd/<fd>`:
    ```
    MEMFD: fd=3 dev=00:01 ino=182445 nlink=0 seals=15
    SERVER_PID: 2234335
    MAPS_ENTRY: 7f8e902cf000-7f8e903ee000 r--s 00003000 00:01 182445 /memfd:stories260K.gguf (deleted)
    LOG: load_model: loading model '/proc/self/fd/3'
    LOG: server_run_i: model loaded; listening on http://127.0.0.1:36815
    ```
  - `llama-server` natively maps the sealed memfd directly. This proves the carried R50 limit (post-map on-disk model rewriting) can be eliminated by loading the model from a sealed memfd.

### Candidate 3: Receipts Cited by Path in SCORECARD
- **Evidence (`scorecard-path-evidence.txt`):**
  - Over 45 distinct `.ufo/waves/` receipt paths are cited across SCORECARD.md round tables.
  - Historical failures from unpinned paths:
    1. *Round 31 C2:* Cited `.ufo/waves/round-31/c2/c2-tip.json`, which never existed.
    2. *Round 37 C3:* Cited counters and reports that were never committed in R37.
    3. *Round 51 D1:* `.ufo/waves/round-51/a2w1/out/X7Regen.md` was rewritten in place (13+/13-), altering evidence at an existing path.
    4. *Round 51 D3:* Claimed `planned-pointer met=True` at tip `1ab1de39` citing a receipt at the final tip, but no receipt was committed.

---

## 3. Affected Axes
- **Operability (8 → 8):** Eliminating mutable path dependencies for 99.929% of runtime executable code (`LD_LIBRARY_PATH`) and runtime model weights (`-m`).
- **Calibration (7 → 7):** Eliminating unpinned mutable path pointers in evidence citations in SCORECARD.

---

## 4. Proposed Move: Dual-Substrate Object Binding (Round 53)

Synthesizing findings across `K2Design`, `S6Limits`, `S5Ggml`, and this seat, the recommended single bounded move for Round 53 is:

> **Extend anonymous memfd sealing to model loading (`-m /proc/self/fd/<model_fd>`) and bind `/proc/<pid>/maps` shared library mappings against an immutable extraction manifest, while requiring digest-pinned receipt citations in SCORECARD.**

### Exact Implementation Shape
1. **Model Runtime Sealing (Operability):**
   - In `tools/kama-live-replay.py`, stream the verified model from cache into `os.memfd_create("model.gguf", MFD_CLOEXEC | MFD_ALLOW_SEALING)`, seal with `F_ADD_SEALS = 15`, pass to the live tool as `--model-fd`, and invoke `llama-server -m /proc/self/fd/<model_fd>`.
   - In `round53-replay-audit.py`, verify that `/proc/<pid>/maps` model entry has `/memfd:`, `st_nlink == 0`, `seals == 15`, matching the rerun receipt's `model_fd` record.
2. **Mapped Library Verification (Operability):**
   - Since Linux `ld.so` cannot natively load shared libraries from anonymous file descriptors without a custom loader, the contradiction is resolved at the `/proc/<pid>/maps` interface:
   - Replay extracts the tar archive, records an immutable manifest of all `.so` members `(member, sha256, dev, inode)`.
   - During witness hold, counter reads `/proc/<pid>/maps`, filters executable mappings (`r-xp`) within `<work>/server/`, opens each mapped file, and verifies that its dev, inode, and SHA-256 match the immutable archive extraction manifest.
3. **Scorecard Evidence Digest Pinning (Calibration):**
   - Require that every receipt cited in SCORECARD Evidence columns include its SHA-256 digest (e.g. `path:sha256`), verified by an automated check against committed Git blobs, preventing D1 in-place rewriting and D3 missing receipt defects.

---

## 5. Risks and Second-Order Effects

1. **Runtime Surface:**
   - Passing an inherited memfd descriptor to `llama-server` requires `pass_fds` in Python `Popen`. As demonstrated in `memfd-model-proof.txt`, `llama-server` b11909 handles `/proc/self/fd/<n>` out of the box.
   - GGUF mapping via `mmap` over memfd consumes virtual address space and RAM, but for the 1.2 MB test model `stories260K.gguf`, memory overhead is negligible (~1.2 MB RAM).
2. **Contract Surface:**
   - `kama-llamacpp-live.py` receipt schema will add `server.model_fd` alongside `server.fd`.
   - `round53-replay-audit.py` will require `sealed_model=1` and `libraries_verified=1`.
3. **Substrate Surface:**
   - Both `memfd_create(2)` and `/proc/<pid>/maps` inspection remain Linux-specific. This aligns with existing preregistered limits.
4. **Explicit Contradiction:**
   - *Contradiction:* One might ask why libraries cannot be placed in sealed memfds like the launcher.
   - *Resolution:* Linux `ld.so` requires filesystem paths for dynamic resolution of `DT_NEEDED` dependencies; passing memfds to `ld.so` is unsupported by the platform dynamic linker. Therefore, the architectural solution must bind the mapped memory objects in `/proc/<pid>/maps` rather than forcing an unsupported substrate mechanism.

---

## 6. Verification Plan

1. **Sealed Model Verification:**
   - Command: `python3 -c "import fcntl; fd = ...; fcntl.fcntl(fd, 1034)"` on model fd in live tool.
   - Counter check: Assert `/proc/<pid>/maps` contains `/memfd:model.gguf (deleted)` with `seals == 15` and matching digest.
   - Ablation control: Pass a regular disk file for `--model`; counter must fail with `model_not_sealed_memfd`.
2. **Library Mapping Verification:**
   - Counter inspects `/proc/<pid>/maps` for all `r-xp` entries matching `libllama*.so` and `libggml*.so`.
   - Ablation control: Overwrite `libllama-server-impl.so` in `<work>/server/` with a modified copy after extraction; counter must fail with `library_digest_mismatch`.

---

## 7. Deliverables and Written Paths
All deliverables are committed in the lane output directory:
- Analysis document: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N2Pattern/pattern.md`
- Model memfd proof receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N2Pattern/memfd-model-proof.txt`
- Library sizes and dependency receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N2Pattern/library-sizes-proof.txt`
- Scorecard path evidence receipt: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N2Pattern/scorecard-path-evidence.txt`
- Report (this file): `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-52/w1/out/N2Pattern.md`
