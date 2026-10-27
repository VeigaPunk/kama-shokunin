# Cross-Claim Pattern: From Reference to Object in Lane Kama (Rounds 46–52)

## 1. Executive Thesis: The Reference vs. Object Dynamic

Across rounds 46 through 52 of lane `kama`, both declared claims—**Operability** (runtime serving, execution witnessing, process binding) and **Calibration** (self-description audit, commit history verification, append-only accounting)—have evolved along a singular, isomorphic architectural vector:

> **Both claims systematically replace an external reference or surrogate token (which can be occupied, forged, or diverted by an imposter) with the immutable object itself.**

In Round 52, this dynamic reached its definitive conceptual expression:
- **Claim C1 (Operability, 8 → 8):** Replaces an on-disk filesystem path (`<work>/server/<member>`) and filesystem-level inode identity with an **anonymous, sealed in-memory image** (`memfd_create(2)`, `MFD_ALLOW_SEALING`, `F_ADD_SEALS = F_SEAL_WRITE | F_SEAL_SHRINK | F_SEAL_GROW | F_SEAL_SEAL`). Because the running server image has no directory entry (`st_nlink == 0`) and resolves only to `/memfd:llama-server (deleted)`, it cannot be duplicated, copied-over, hardlinked, or substituted via filesystem namespace operations. The executed image *is* the verified archive member stream itself.
- **Claim C2 (Calibration, 7 → 7):** Replaces external surrogate ledger rows in `registry/append-only-disclosures.tsv` (which merely *asserted* where and why 155 historical lines were deleted) with the **verbatim historical lines themselves**, re-appended into the tails of 18 affected files under `## Restored lines (round 52)` inside five-backtick fences. The document no longer relies on an external registry to excuse a missing invariant; the physical text *is* held in the document again.

This document traces this progression through SCORECARD round sections (R46–R52) and QUALITY criteria (KQ76–KQ88), and rigorously evaluates the next architectural frontiers where a path or pointer still stands in for the object.

---

## 2. Historical Trace Across Rounds 46–52

### Round 46: Aggregate Thresholds and External Ledgers
- **Operability (C1):** Release re-verification at b11906 (`registry/release-recheck-b11906.tsv`, S486, S487) compared tabular claims against upstream commits. Verification was bounded to textual rows rather than a live executing runtime.
- **Calibration (C2):** `append-only-audit` v1 introduced Git history analysis against a coarse threshold: commits deleting $\ge 20$ lines.
  - *Reference surrogate:* The $\ge 20$-line threshold stood in for "append-only."
  - *Failure mode:* In-place deletions under 20 lines (such as the loss of `LOG.md` text at `ed135b3c`) were hidden behind the threshold surrogate.

### Round 47: URL Provenance and Declaring-Line Pointers
- **Operability (C2):** Live receipt replay at b11909 (`tools/kama-live-replay.py`, schema v4) re-acquired archives and models from recorded URLs.
  - *Reference surrogate:* The recorded provenance URL and check pass/fail booleans stood in for actual execution.
  - *Failure mode (Wave attacks):* Seat `K2Cheat` demonstrated a replay that copied host-cached bytes without network access, fabricated 0-byte placeholders, and forged timestamps. The counter trusted the rerun receipt's self-reported contents.
- **Calibration (C1):** `append-only-audit` v2 introduced `registry/append-only-contract.tsv` pointing at declaring lines (`declared_at`).
  - *Reference surrogate:* A line of text matching the pattern `append` stood in for a binding contract declaration.
  - *Failure mode:* Seat `V1Ctr` showed any line mentioning "append" bound the contract, even sentences containing negation ("not append-only").

### Round 48: Pinned Revisions and Title-Based Carve-Outs
- **Operability (C2):** Schema v5 live receipts pinned the Hugging Face model URL to a 40-hex commit hash (`resolve/<sha>/...`) and verified provenance digests at record time.
  - *Reference surrogate:* Verified digests in the receipt stood in for live execution.
  - *Failure mode:* Seats `K2Cheat` and `K2Urlswap` demonstrated that a replay could download bytes, verify digests, and then write a rerun receipt that copied the original's captures without ever launching a server, or serve requests from a host install.
- **Calibration (C1):** `append-only-audit` v3 introduced region carve-outs (`exempt=<## title>` and `only=<## prefix>`).
  - *Reference surrogate:* Section title strings stood in for whether content was legitimately re-derived.
  - *Failure mode:* Seat `K1Regions` showed title-based carve-outs were content-blind: a dated-section deletion could be laundered by moving text under an exempt title while sustaining the section's line count.

### Round 49: The Execution Witness and Line Origin
- **Operability (C1):** Replay execution witness (KQ76, KQ80) required an outside observer to verify a listening port, check `/proc/<pid>/exe` digest, and round-trip a nonce through `/tokenize` and `/detokenize`.
  - *Reference surrogate:* Checking that `/proc/<pid>/exe` hashed to the expected digest stood in for verifying the specific replay binary.
  - *Failure mode:* Seats `K1Cheat` and `R0Controls` launched the host's existing binary at `/home/vgpnk/.local/opt/llama-b11909/llama-server`. Because the counter only verified the digest of `/proc/<pid>/exe` and never checked `child_pid == observed_pid`, the host install passed all witness checks.
- **Calibration (C2):** `append-only-audit` v4 introduced line origin tracking (`origin(l)`).
  - *Reference surrogate:* Traversal order in `git rev-list` stood in for commit history.
  - *Failure mode:* Seat `K2Origin` showed sibling order in `git rev-list` could flip verdicts, and fenced code blocks could introduce fake `## ` headings.

### Round 50: Process-Tree Binding and Birth-DAG Origin
- **Operability (C1):** Process-bound replay witness (KQ81, KQ82) bound `child_pid == observed_pid`, traced the `/proc` PPID ancestry up to 64 hops, checked environment canaries, and inspected `/proc/<pid>/maps` for model mapping via `O_NOFOLLOW` fstat and hash.
  - *Reference surrogate:* The server was still executed from a filesystem path `<work>/server/<member>`, and its identity was checked via path/inode.
  - *Failure mode:* While the process tree was bound, the executable on disk remained a regular file with a filesystem link.
- **Calibration (C2):** `append-only-audit` v5 (KQ83, KQ84) resolved origin across all birth commits in the Git DAG, ignored fenced code blocks, and enforced `graded + ungraded == deleted`.
  - *Reference surrogate:* The $\ge 20$-line threshold remained the gating surrogate for grading events.

### Round 51: Filesystem Dev/Inode Binding and the Disclosure Ledger
- **Operability (C1):** Replay's own server image (KQ85, S499). The live tool recorded `server_exe` via `/proc/<pid>/exe` (dev, inode, digest), and the replay required `server_exe` to match the extracted member `<work>/server/<member>`.
  - *Reference surrogate:* A filesystem node at `<work>/server/<member>` stood in for the verified member.
  - *Failure mode:* Seat `J3CopyDecoy` proved that a byte-identical host file copied over `<work>/server/<member>` satisfied the counter. Seat `J4Hardlink` proved that hardlinking the host binary to `<work>/server/<member>` satisfied the counter because it shared dev and inode!
- **Calibration (C2):** `append-only-audit` v6 (KQ86, KQ87, KQ88) eliminated the 20-line threshold (threshold 1: every deletion graded) and introduced `registry/append-only-disclosures.tsv`.
  - *Reference surrogate:* A disclosure ledger row (commit, file, key sha256, count, class) stood in for the lost line.
  - *Failure mode:* The disclosure ledger made `exit 0` cheap. An unheld line was simply excused by an external ledger row rather than being restored. The file remained missing its declared text.

### Round 52: Convergence on the Object Itself
- **Operability (C1):** Replaces `<work>/server/<member>` on disk with an **anonymous sealed memfd** (`memfd_create(2)`).
  - *The Object:* The executed image is streamed directly from the tar archive into RAM, sealed (`F_SEAL_WRITE | SHRINK | GROW | SEAL`), and executed via `/proc/<pid>/fd/<n>`. The running image has `st_nlink == 0`, resolves to `/memfd:llama-server (deleted)`, and has no filesystem directory entry. Hardlinks, copies, and rename-overs are structurally impossible.
- **Calibration (C2):** Replaces disclosure ledger rows with **fenced verbatim re-appends** (`## Restored lines (round 52)`).
  - *The Object:* The 151 unheld lines across 18 files are restored byte-for-byte in history order at the file tails. The disclosure rows are deleted from `registry/append-only-disclosures.tsv`. The file itself holds the object again.

---

## 3. Detailed Trace of QUALITY Criteria (KQ76–KQ88)

The quality bar codified in `corpus/QUALITY.md` documents this step-by-step transition:

| ID | Title / Focus | The Surrogate Reference (What was Rejected) | The Concrete Object (What was Required) |
|---|---|---|---|
| **KQ76** | Outside Replay Witness | Replay self-reports, recorded receipts, and static digests. | A live outside observer checking active socket listening, recorded binary execution, `-m` matching, and dynamic nonce tokenization round-trip. |
| **KQ77** | Origin-Bound Exemptions | Section title strings as blankets for moved lines. | Line origin tracking: a line's text must have been born in an exempt section at its initial Git introduction. |
| **KQ78** | Word-Bound Contract Binding | Loose substring matching (`log` in `catalog`) or negated statements. | Exact whole-word token matching without preceding negations within three words. |
| **KQ79** | Report Immutability & Census Completeness | In-place report edits and selective census quoting. | Single-commit report landing; subsequent corrections only via appended errata; census quoted whole with zero-counts. |
| **KQ80** | Multi-Fact Outside Observation | Trusting receipt `argv` or self-reported state. | Four independent facts derived by the observer: socket listening inode, PPID tree descent (up to 64 hops), live GGUF nonce round-trip, and clean process death. |
| **KQ81** | Process-Bound Evidence & Model Mapping | Trusting PID claims or untracked memory. | `child_pid == observed_pid`, and model file mapping extracted from `/proc/<pid>/maps` re-opened `O_NOFOLLOW`, fstat-checked, and hashed. |
| **KQ82** | Process-Tree Teardown | Assertions of process exit or single-process kill. | Observer kills the replay parent and verifies all snapshot descendants exit within 30s and port refuses. |
| **KQ83** | Graph-Bound Origin & Fence Awareness | `git rev-list` traversal order and naive `## ` regex matching. | Origin defined over the commit DAG birth set; fenced code blocks stripped; trailing CRs normalized. |
| **KQ84** | Exhaustive Line Accounting | Self-reported ungraded counts or unverified sums. | `graded + ungraded == deleted` for every event, strictly matching `git diff --numstat` first-parent deletions. |
| **KQ85** | Replay-Owned Server Image | Executable digest alone or `readlink` path string. | Running image opened via `/proc/<pid>/exe` (S499) matching dev:inode of the extracted member; digests verify *bytes*, dev:inode verifies *file identity*. |
| **KQ86** | Elimination of Deletion Thresholds | 20-line event threshold hiding in-place edits. | Threshold 1: every deletion event graded, exposing 101 previously hidden deletion events. |
| **KQ87** | Permitted A-Row Registry Mutations | Blanket immutability or arbitrary cell edits. | Strict adherence to declared cell rules: only status, recheck, and used-by may change in A-row files; all other deletions graded. |
| **KQ88** | Disclosure Ledger Discipline | Unheld lines excused by unverified ledger entries. | A disclosure row must name exact commit, file, key hash, count, and mechanical class; restored lines require ledger row deletion. |

---

## 4. Evaluation of Next Candidate Sites

Where in lane `kama` does a path or pointer still stand in for the object? We examine the three primary candidates:

### Candidate 1: Shared Library Paths (`LD_LIBRARY_PATH`)

#### Architectural Anatomy
In Round 52, C1 executed `llama-server` from an anonymous sealed memfd. However:
1. `llama-server` is an ELF dynamically linked executable:
   ```
   llama-server size: 17,864 bytes (17.45 KB)
   ```
2. The actual serving logic, HTTP engine, prompt processing, and CPU tensor kernels reside entirely in dynamically loaded shared libraries:
   - `libllama-server-impl.so`: 7,923,736 bytes (7.56 MB)
   - `libllama.so.0.7.0`: 5,275,808 bytes (5.03 MB)
   - `libllama-common.so.0.7.0`: 6,699,720 bytes (6.39 MB)
   - `libmtmd.so.0.7.0`: 2,047,208 bytes (1.95 MB)
   - `libggml-base.so.0.27.0`: 906,112 bytes (0.86 MB)
   - `libggml-cpu-x64.so`: 954,888 bytes (0.91 MB)
   - `libggml-cpu-alderlake.so`: 1,420,688 bytes (1.35 MB)
   *Total shared library code sampled:* 25,279,200 bytes (24.11 MB).
3. **The Disproportion:** The launcher represents **0.071%** of the executable code. The shared libraries represent **99.929%** of the executable code! (Empirically verified in receipt `library-sizes-proof.txt`).
4. **The Pointer:** Because an anonymous memfd has no filesystem directory, `$ORIGIN` dynamic linking fails. `tools/kama-llamacpp-live.py:1957` sets:
   ```python
   child_env['LD_LIBRARY_PATH'] = os.path.dirname(server_real)
   ```
   `LD_LIBRARY_PATH` is a directory path pointing to the temporary extracted directory `<work>/server/llama-b11909` on disk.
5. **The Vulnerability:** The libraries on disk are regular, unsealed filesystem files. An attacker or hostile fixture can modify, swap, or hardlink a decoy `libllama-server-impl.so` on disk after extraction. The server starts from the sealed memfd, but `ld.so` loads the compromised library from disk. The counter inspects `/proc/<pid>/exe`, sees the sealed memfd, and reports `sealed=1 met=True`! The C1 counter currently checks *zero* shared libraries.

### Candidate 2: Model Path After Mapping (`--model <path>`)

#### Architectural Anatomy
1. In `kama-llamacpp-live.py:1936-1961`, the model is passed via a filesystem path argument:
   ```python
   server_argv[2] = os.path.abspath(args.model)
   ```
2. In `tools/round52-replay-memfd-audit.py:313-323`, the counter checks model mapping:
   ```python
   for dev, ino, path in cands:
       st = os.stat(path)
       if sha_file(path) == MODEL_SHA:
           return dev, ino
   ```
3. **The Pointer:** The counter inspects `/proc/<pid>/maps`, extracts the `path` string, and calls `os.stat(path)` and `sha_file(path)`. The path on disk stands in for the mapped memory pages.
4. **The Vulnerability:**
   - If the model file is modified after mapping, or if the process maps memory pages from an alternate source (or modifies private pages), statting and hashing the file by path on disk verifies the on-disk file, not the server's mapped virtual memory.
   - If the model file is unlinked after load, `path` becomes `/path/to/model.gguf (deleted)`, causing `os.stat` to fail.
5. **Empirical Breakthrough (Receipt `memfd-model-proof.txt`):**
   In this investigation, we tested whether `llama-server` can load a model directly from an anonymous sealed memfd via `/proc/self/fd/<fd>`.
   - Result: **100% SUCCESS.**
   - Command: `llama-server -m /proc/self/fd/3` (where fd 3 was created via `os.memfd_create("stories260K.gguf", MFD_CLOEXEC | MFD_ALLOW_SEALING)` and sealed with `F_ADD_SEALS = 15`).
   - Server log:
     ```
     0.00.028.090 I srv load_model: loading model '/proc/self/fd/3'
     0.00.035.620 I srv server_run_i: model loaded
     0.00.035.646 I srv server_on_li: listening on http://127.0.0.1:36815
     ```
   - Inspection of `/proc/<pid>/maps`:
     ```
     7f8e902cf000-7f8e903ee000 r--s 00003000 00:01 182445 /memfd:stories260K.gguf (deleted)
     ```
   The model mapping is an anonymous, sealed memfd (`00:01`, `nlink=0`, `seals=15`), completely eliminating on-disk model path tampering!

### Candidate 3: Receipts Cited by Path in SCORECARD

#### Architectural Anatomy
1. In `SCORECARD.md`, the Evidence column cites measurement artifacts via relative paths (e.g., `.ufo/waves/round-52/measured/c1.out`, `.ufo/waves/round-48/c2/live/receipt-1.json`). Over 45 distinct `.ufo/waves/` paths are cited across rounds (receipt `scorecard-path-evidence.txt`).
2. **The Pointer:** A markdown path string stands in for the evidence object.
3. **Historical Failure Modes:**
   - *Round 31 C2:* SCORECARD cited `.ufo/waves/round-31/c2/c2-tip.json`, which never existed (actual files were `c2-b4f3edc0.json` and `c2-bda324bb.json`).
   - *Round 37 / R38:* SCORECARD cited `tools/round37-statement-audit.py` and `CriticEntries.md` which were uncommitted in R37 and only landed in R38.
   - *Round 51 D1:* `.ufo/waves/round-51/a2w1/out/X7Regen.md` was rewritten in place (13+/13-), modifying evidence behind an existing path.
   - *Round 51 D3:* SCORECARD claimed `planned-pointer met=True` citing a receipt at `1ab1de39` that was never committed.
   - *Round 46/48/51:* Head banners in SCORECARD line 6 were replaced without preserving superseded text.
4. **The Vulnerability:** While `digest-ledger` pins citations of raw SHA-256 strings, and `hexrun-census` pins Git commit SHAs, receipt paths cited in the Evidence column are unpinned pointers. They can point to missing, modified, or contradictory files.

---

## 5. Synthesis: Naming the Next Places in the Lane

The cross-claim pattern reveals that the lane cannot rest on half-measures where a small launcher is sealed while 99.9% of executable code remains on a mutable path, or where model weights and evidence receipts remain unanchored pointers.

### The Immediate Frontier for Operability (Round 53 C1)
**Primary: Dual-Anchored Runtime Objects (Sealed Model Descriptor + Mapped Library Identity).**
1. **The Model:** Move the GGUF model into a sealed anonymous memfd (`memfd_create("model.gguf")`, `seals=15`), passed to `llama-server` as `-m /proc/self/fd/<model_fd>`. Our empirical proof confirms `llama-server` natively supports this. This eliminates the carried R50 limit of post-map on-disk model rewriting and makes the model image an anonymous, sealed object in `/proc/<pid>/maps` (`/memfd:stories260K.gguf (deleted)`).
2. **The Libraries:** Because Linux `ld.so` requires a filesystem path for `DT_NEEDED` resolution, the dynamic libraries cannot be loaded directly from anonymous descriptors without a specialized loader. Therefore, the counter and replay must bind the **mapped library objects** in `/proc/<pid>/maps`. During the witness hold, the counter must inspect `/proc/<pid>/maps`, verify that every mapped `.so` in the server address space belongs to `<work>/server/`, and check its `(dev, inode, sha256)` against an immutable extraction manifest generated directly from the verified archive tar stream.

### The Immediate Frontier for Calibration (Round 53 C2)
**Primary: Digest-Pinned Evidence Citations in SCORECARD.**
Extend the self-description audit so that every receipt cited by path in SCORECARD tables must be accompanied by its SHA-256 digest (e.g., `path:sha256` or an anchored column), verified by an automated check against Git blob history. This closes the gap identified in R51 D1 and D3 where a markdown path stands in for an uncommitted, missing, or rewritten receipt object.

---

## 6. Conclusion

Lane `kama`'s development from Round 46 to Round 52 has systematically retired surrogate representations in favor of the physical objects themselves:
- Strings $\to$ Line Origins $\to$ DAG Births $\to$ Verbatim Restored Lines.
- Release Tables $\to$ Replay Receipts $\to$ Process Trees $\to$ Inode Checks $\to$ Sealed Anonymous Memfds.

The next evolutionary move directly extends this invariant to the runtime code substrate (mapped shared libraries), the runtime model substrate (sealed memfd model loading), and the historical evidence substrate (digest-pinned receipt citations).
