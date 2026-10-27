# Cross-Round Pattern: The Decoy Line and Verification Limits in Kama

**Author**: Seat `N3Pattern` (UFO-FSD connector)  
**Round**: 51  
**Target**: Lane `kama` (local model serving and endpoint health)  
**Deliverable**: `.ufo/waves/round-51/a2w1/out/N3Pattern/pattern.md`  
**Date**: 2026-10-27  

---

## 1. Executive Summary: The Fundamental Verification Asymmetry

Across Rounds 47 through 51, the `kama` lane has pursued two core verification goals under the assigned axes of **operability** (reproducing serving evidence from first principles) and **calibration** (ensuring repository self-descriptions faithfully reflect git history).

Every round followed a strict cycle:
1. An empirical capability or auditor was implemented.
2. A frozen counter was written to grade the capability.
3. An adversarial wave probed the counter to find shortcuts, stubs, and decoys that achieved `met=True` without satisfying the intended real-world property.
4. The subsequent round closed the identified shortcut by adding new observer checks.

A critical pattern emerges across this trajectory: **the recurring divergence between extensional verification (inspecting properties of resulting static artifacts) and intensional verification (proving causal execution ancestry).**

Whenever a counter inspects static outputs—whether JSON receipt fields, files residing on disk, listening network ports, memory-mapped files, or even `/proc/<pid>/exe` device and inode tuples—an adversary can craft a **decoy** that places the expected artifacts in the expected locations without executing the intended causal pipeline (e.g., re-acquiring the release archive from GitHub, verifying its archive digest, extracting the member, and executing that freshly extracted member).

The Round 51 C1 `own` leg was specifically designed to close Round 50's `J4Decoy` (a decoy replay that directly executed the host's existing `llama-server` binary at `/home/vgpnk/.local/opt/llama-b11909/llama-server`). While the `own` leg successfully catches that direct execution (`00:38:238037577` vs `103:05:*`), **it does NOT end the decoy line.** A **copy decoy**—which copies the host's binary into `<work>/server/<member>` via `shutil.copyfile` before execution—satisfies the `own` leg completely (`bind=1 own=1 teardown=1 newrow=1 met=True`, verified empirically by seats `J3CopyDecoy`, `K1Cheat3`, and `J4Hardlink`).

This document provides a comprehensive cross-round taxonomy of all decoy and shortcut classes identified from Round 47 to Round 50, analyzes why static file/process checks cannot defeat the copy decoy, and identifies the exact architectural observation that terminates the decoy line.

---

## 2. Complete Taxonomy of Decoy and Shortcut Classes (Rounds 47–50)

Based on the `What met=True does not show` sections of `SCORECARD.md` (Rounds 47–50), the non-author verifier spot-checks (`corpus/lessons/round-48-verifier-spotcheck.md`, `round-49-verifier-spotcheck.md`, `round-50-verifier-spotcheck.md`), and the corresponding round lessons, all shortcuts that met a frozen counter fall into eight distinct classes:

| Class ID | Decoy / Shortcut Class | Manifestation in Rounds 47–50 | Closing Round & Mechanism | Status at Round 51 |
|:---|:---|:---|:---|:---|
| **Class 1** | **Receipt Fabrication & Output Playback** | • R47 C1 (`K1Cheat`): Tool recognizes fixture shape, plays back lane's 5 events, print-only selftest stub.<br>• R47 C2 (`K2Cheat`): Replay outputs fabricated rerun receipt with 0-byte placeholders and forged `started_utc`; counter blindly trusted receipt contents.<br>• R48 C2 (`K2Cheat`): 19-line replay script re-acquires inputs, but skips server lifecycle and copies original receipt checks/captures with rewritten paths.<br>• R49 C1 (`K1Cheat`): Decoy replay writes `ready.json`, copies original receipt with `witness.released: true` and fake `child_pid`. | **Progressively Closed**:<br>• R48 added counter-side input hashing and stable projection diffing (`--compare`).<br>• R49 added independent execution witness (`POST /tokenize` nonce round-trip against counter-decoded vocabulary).<br>• R50 added `child_pid` join and process tree descent (`descends_from`). | **Closed** against pure simulation. Rerun receipts cannot be fabricated without a real listening process answering nonces. |
| **Class 2** | **Host-Binary Execution & Cache Hijack** | • R47 C2 (`K2Cheat`): Replay copies host-cache bytes without network download; passes with network dead.<br>• R48 C2 (`K2Urlswap`): Replay serves from host bytes, uses hardcoded table to reject swapped URLs; passes offline.<br>• R49 C1 (Disclosed limit / `K1Cheat`): Execution witness confirms frozen binary listens and answers nonces, but binary is host's install at `/home/vgpnk/.local/opt/llama-b11909/llama-server`, not extracted from archive.<br>• R50 C1 (`J4Decoy`): Replay process executes host install directly; meets `bind=1 teardown=1 newrow=1 met=True` because `/proc/<pid>/exe` digest matches `SERVER_SHA`. | **Partially Closed in R51**:<br>• R51 added `own` leg comparing `/proc/<pid>/exe` `fstat()` `(dev, inode)` against `os.stat(<work>/server/<member>)`.<br>• Catches direct execution of host install (`J2DecoyHost` fails `owned=0/3`).<br>• **Bypassed by Copy Decoy** (see Section 3). | **OPEN** to Copy Decoy (`J3CopyDecoy`, `K1Cheat3`, `J4Hardlink`). |
| **Class 3** | **Execution Context & Environment Hijacking** | • R49 C1 (`K1Cheat`): Counter passed inherited environment to replay invoker; planting `PYTHONPATH`/`sitecustomize.py` intercepted python calls in pristine build tree.<br>• R50 C1 (`Sen1Env`): Live tool handed `PATH` and `HOME` to `tools/kama-probe.sh`, which executed `python3` without `-I` and unquoted tools, enabling arbitrary code execution inside replay. | **Partially Closed in R50**:<br>• R50 isolated replay invoker (`python3 -I`), used strict allow-list (`PATH, HOME, LANG, LC_ALL, TMPDIR`), planted canaries (`KAMA_R50_CANARY`, sitecustomize marker).<br>• Live child executed with isolated environment. | **Carried Limit** in R51: probe script `PATH` execution remains open (prereg limit 42). |
| **Class 4** | **Semantic Smuggling & Syntax Laundering** | • R48 C1 (`K1Regions`): Dated-section deletion laundered by moving text under exempt `## ` heading while section line count was sustained; audit exited 0 with lines `ungraded`.<br>• R49 C2 (`K2Origin`): Fake `## ` heading inside CommonMark fenced code block treated as heading, masking dated deletions; CRLF line-ending mutations bypassed key lookup. | **Closed in R49 & R50**:<br>• R49 C2 added line origin requirement (text must be born in an exempt section).<br>• R50 C2 added CommonMark 0.31.2 §4.5 fence-aware parser (`S498`) and CR-normalized origin keys. | **Closed**. CommonMark code fences and CR normalizations are strictly checked by 12 constructed fixtures. |
| **Class 5** | **Traversal Sensitivity & Graph Order Dependence** | • R49 C2 (`K2Origin`): Line origin determined by first appearance in `git rev-list --topo-order`; merge sibling order (which parent is traversed first) flipped birth section and changed audit outcome. | **Closed in R50**:<br>• R50 C2 redefined origin as a property of the commit graph DAG: the union of section titles across *every birth* of a key (commits holding the key where no parent holds it). Invariant under rev-list order. | **Closed**. Order-independence verified by fixture `order-b`. |
| **Class 6** | **Threshold Masking (Sub-Threshold Blindness)** | • R47–R50 C2 (`L1Lowthr`, `X13Threshold`, R50 Spot-check R6): The default 20-line deletion threshold concealed 97+ deletion events, including a real 6-line deletion in `LOG.md` at `ed135b3c` and 22 unrestored events in `corpus/lessons/*.md`.<br>• R47 C1 (`X1Stable`): Window maximum kept restored-then-re-deleted event as `restored`. | **Closed in R48 & R51**:<br>• R48 C1 surfaced `regressed` (held at tip vs held at window max) in exit code.<br>• R51 C2 lowered default threshold from 20 to 1 (all deletions graded), permitted A-row metadata updates, and mandated explicit disclosures in `registry/append-only-disclosures.tsv`. | **Closed**. Threshold 1 grades every deletion; 166 lines disclosed in 51 events, 58 permitted lines. |
| **Class 7** | **Oracle Duplication & Shallow Verification** | • R47 C1 (`V1Ctr`): Contract leg accepted any line containing `append`; stable leg vacuous when base and tip coincided.<br>• R48 C1 (`K1Binding`): Token matched substrings (`log` in `catalog`); wildcard row bound to covered file's self-declaration.<br>• R49/R50 C2 (`V2Ctr`, `N3Pattern2`): Counter binder copied tool's implementation; counter bounded tool's self-reported `ungraded` count rather than independently calculating ground truth. | **Closed in R49 & R51**:<br>• R49 C2 added whole-word token matching, 3-word negation window, and directory-bound wildcards.<br>• R51 C2 counter independently recomputes -U0 diffs, numstat, and multiset of lost keys directly from git graph. | **Closed**. C2 counter recomputes lost keys key-for-key on all whole-file-graded files. |
| **Class 8** | **Incomplete Teardown & Process Leaks** | • R49 C1 (`Sen2Replay`, `X1Kill`): Killing replay or counter left `llama-server` process running as an orphan in background.<br>• R50 C1 Base: `PR_SET_PDEATHSIG` set only on live tool -> server link, leaving 3 descendants alive after killing invoker. | **Closed in R50**:<br>• R50 C1 set `PR_SET_PDEATHSIG` on both links (replay -> live tool and live tool -> server).<br>• Teardown leg verifies SIGKILL of invoker terminates whole tree and port refuses in < 30 s (measured 0.10 s). Kept in R51 C1. | **Closed**. Process group teardown verified on every run; no processes survive. |

---

## 3. Deep Analysis: Is the C1 `own` Leg the End of the Decoy Line?

### 3.1 The C1 `own` Leg Design and its Target
In Round 50, seat `J4Decoy` bypassed the witness counter by executing the host's existing `b11909` installation (`/home/vgpnk/.local/opt/llama-b11909/llama-server`). Because the counter only verified that `/proc/<pid>/exe` hashed to `SERVER_SHA`, and the host installation had the exact same bytes, the check passed.

Round 51 introduced Claim C1 (sourced on `proc_pid_exe(5)`, `S499`):
1. `tools/kama-llamacpp-live.py` implements `server_exe(pid)`, which opens `/proc/<pid>/exe`, performs `fstat()`, captures `(dev, inode)`, hashes the file descriptor, and records `receipt['server_exe']`.
2. `tools/kama-live-replay.py` asserts that `receipt['server_exe']` matches `os.stat(<work>/server/<member>)` by `(dev, inode)` and records `own_server`.
3. `tools/round51-replay-exe-audit.py` executes `own_exe()`, independently opening `/proc/<pid>/exe` during the witness hold, checking `fstat()` device and inode against `os.stat(<work>/server/<member>)`, and verifying that the rerun receipt and replay JSON reflect those values.

Seat `J2DecoyHost` confirmed that this mechanism successfully catches a direct execution of `/home/vgpnk/.local/opt/llama-b11909/llama-server`:
- Running image: dev `00:38` (device 56, `/home`), inode `238037577`.
- Extracted member: dev `103:05` (device 66309, `/fast`), inode `1753616769`.
- Result: `own: running image dev:inode 00:38:238037577 is not the replay's extracted member ... (103:05:1753616769)`. `owned=0/3`, `met=False` (exit 1).

### 3.2 The Copy Decoy Counterexample
The assumption behind the `own` leg was that checking `(dev, inode)` proves that the running binary is the *file extracted from the archive*. 

However, as demonstrated during the Round 51 wave by seats `J3CopyDecoy`, `K1Cheat3`, and `J4Hardlink`, **the `own` leg does NOT prove that the bytes originated from the downloaded archive.**

Consider the **Copy Decoy**:
Instead of executing the host binary directly from its host path, the decoy replay does:
```python
# In tools/kama-live-replay.py before exec:
shutil.copyfile("/home/vgpnk/.local/opt/llama-b11909/llama-server", server_member_path)
```
Or, even more aggressively (skipping network download and extraction entirely):
```python
# Stage host binary directly into the expected member path:
os.makedirs(os.path.dirname(server_member_path), exist_ok=True)
shutil.copyfile("/home/vgpnk/.local/opt/llama-b11909/llama-server", server_member_path)
os.chmod(server_member_path, 0o755)
```

When this file is executed:
1. `<work>/server/<member>` is a regular file on device `103:05` with inode $I_{copy}$.
2. The server process executes `<work>/server/<member>`.
3. The kernel link `/proc/<pid>/exe` points to `<work>/server/<member>`.
4. `fstat(/proc/<pid>/exe)` reports device `103:05` and inode $I_{copy}$.
5. `os.stat(<work>/server/<member>)` reports device `103:05` and inode $I_{copy}$.
6. `fstat(/proc/<pid>/exe)` bytes hash to `SERVER_SHA`.
7. `own_exe()` observes: `got == want` ($103:05:I_{copy} == 103:05:I_{copy}$).
8. `rerun_receipt['server_exe']` and `res['own_server']` record $103:05:I_{copy}$.
9. **Outcome**: The frozen counter reports `bind=1 own=1 teardown=1 newrow=1 bound=3/3 owned=3/3 met=True`! (Empirical receipt: `.ufo/waves/round-51/a2w1/out/J3CopyDecoy/j3-copydecoy.c1.out`).

### 3.3 The Theoretical Impossibility of Post-Hoc Static File Inspection
Why does the copy decoy succeed against every static inspection?

In operating systems and security theory, a regular file on a POSIX filesystem has no immutable "birth certificate" or causal memory. Once bytes are written into a file and closed, the file system metadata consists only of:
- `st_dev`, `st_ino` (spatial allocation identifiers)
- `st_mode`, `st_nlink`, `st_uid`, `st_gid`
- `st_size`
- `st_atim`, `st_mtim`, `st_ctim`

There is zero information stored in inode metadata or file content that can distinguish whether those bytes arrived via:
$$\text{Pipeline A: } \text{Network Socket} \xrightarrow{\text{urllib}} \text{Archive File} \xrightarrow{\text{tarfile}} \text{Member Path}$$
or:
$$\text{Pipeline B: } \text{Host Local Path} \xrightarrow{\text{shutil.copyfile}} \text{Member Path}$$
or:
$$\text{Pipeline C: } \text{Python Script} \xrightarrow{\text{write()}} \text{Member Path}$$

Every static inspection (reading `/proc/<pid>/exe`, statting paths, checking inodes, reading `/proc/<pid>/maps`, hashing bytes) is an **extensional query**: it tests the state of the system at time $t$. But the claim being evaluated is an **intensional property**: it asserts that the system traversed a specific causal history prior to time $t$.

Because different computational histories can terminate in the identical physical filesystem state, **the copy decoy keeps the decoy line open forever against any purely static, post-hoc file or process inspection.**

---

## 4. Evaluation of Candidate Observations: What Would End It?

To truly terminate the decoy line, the verification harness must observe properties that are strictly true for Pipeline A and strictly false for Pipeline B. We evaluate five candidate observations:

### Candidate 1: Link Count Assertion (`st_nlink == 1`)
- **Concept**: Proposed by seat `J4Hardlink` (`fix/counter-nlink.py`). Asserts that `os.stat(member_path).st_nlink == 1`.
- **Efficacy**: Catches hardlink attacks (`os.link(staged_file, member_path)` results in `st_nlink == 2`).
- **Fatal Flaw**: Completely blind to `shutil.copyfile()` or `open().write()`. A copied file allocates a new inode with `st_nlink == 1`.
- **Verdict**: **Insufficient** (does not end the copy decoy).

### Candidate 2: Inotify Write-Event Counting
- **Concept**: Proposed by seat `J3CopyDecoy` (`j3-counter-plus.diff`). An inotify watch on `<work>/server/` monitors write events on the member basename, asserting `create == 1, close_write == 1, late == 0`.
- **Efficacy**: Catches a decoy that *first* extracts from the archive and *then* overwrites the member with the host binary (`close_write == 2`).
- **Fatal Flaw**: Completely blind to a decoy that skips archive extraction entirely and writes the host binary into the member path once. Such a decoy produces `create == 1, close_write == 1`, indistinguishable from extraction.
- **Verdict**: **Insufficient** (catches only sequential overwrite, not direct copy).

### Candidate 3: Archive Header mtime Comparison
- **Concept**: Comparing `os.stat(member_path).st_mtime_ns` with the `mtime` stored in the tar header.
- **Fatal Flaw**: `mtime` is trivially forgeable in userspace via `os.utime(member_path, (tar_mtime, tar_mtime))`, as demonstrated by `j3-inotify-lab.py`.
- **Verdict**: **Insufficient** (trivially spoofable).

### Candidate 4: Network Ingress Verification (Network Namespace Egress Witness)
- **Concept**: Run the replay inside an isolated Linux network namespace (`veth` pair or dedicated accounting interface) where the counter monitors packet and byte counts.
- **Mechanism**: The counter asserts that during the replay invocation, $\ge 70\text{ MB}$ of ingress traffic crossed the network interface from GitHub's IP range.
- **Efficacy**: A local copy decoy transfers 0 bytes over the network; an honest replay downloads ~75 MB.
- **Trade-offs**: Requires setting up network namespace routing (`veth`, NAT, or user-mode networking like `slirp4netns`), which introduces substrate dependencies and fragility in containerized CI environments.
- **Verdict**: **Effective but heavyweight**.

### Candidate 5: Substrate Mount Masking (Filesystem Isolation Sandbox)
- **Concept**: Instead of trying to detect whether the replay copied from the host install, **make the host install physically inaccessible to the replay process**.
- **Mechanism**: The counter executes the replay inside an unprivileged user and mount namespace:
  ```bash
  unshare -U -m --map-root-user
  ```
  Inside this namespace, before starting the replay, the harness bind-mounts an empty `tmpfs` over `/home/vgpnk/.local` and any external scratch directories, or creates a minimal pivot root containing only the repository clone, scratch `$S`, and necessary system runtime paths (`/usr`, `/lib`, `/etc`).
- **Efficacy**:
  - The replay process runs as unprivileged user `vgpnk`.
  - When the decoy attempts `shutil.copyfile("/home/vgpnk/.local/opt/llama-b11909/llama-server", ...)` or `DECOY_SERVER = "/home/vgpnk/.local/opt/..."`, the OS immediately returns `ENOENT` (`FileNotFoundError`).
  - The replay has *nowhere to copy from*. The host binary does not exist in its mount table.
  - The *only* source of the binary available to the replay is downloading it from GitHub over the network.
- **Verification on Host Substrate**:
  Verified live on Arch Linux 7.2 (`linux 7.2.11-arch1-1`):
  ```bash
  unshare -U -m --map-root-user bash -c 'mount -t tmpfs tmpfs /tmp && echo ok'
  ```
  Runs without `sudo`, without privilege, and without modifying host state.
- **Verdict**: **Definitive, clean, and robust**. It converts an intractable extensional inspection problem into a structural constraint: by removing the decoy binary from the replay's universe, any server that executes is guaranteed to have been downloaded.

---

## 5. Synthesis: The UFO-FSD Connector Move for Round 52

Synthesizing the lessons of Rounds 47–51:

1. **Axes Impacted**:
   - **Operability** (8 $\rightarrow$ 8): Elevates `live-receipt-replay` from an extensional check (which can always be fooled by placing bits on disk) to a structurally guaranteed causal replay.
   - **Calibration** (7 $\rightarrow$ 7): Closes Preregistration Limit 41 by aligning the counter's observable scope with the actual claim statement.

2. **The Non-Obvious Move**:
   **"Substrate Mount Masking for Replay Isolation"**
   In the next iteration of the replay counter (`round52-replay-provenance-audit.py`):
   - Wrap the invocation of `tools/kama-live-replay.py` in an unprivileged user/mount namespace (`unshare -U -m --map-root-user`).
   - Mount an empty read-only `tmpfs` over `/home/vgpnk/.local` and any directory outside the assigned scratch `$S` and repository clone.
   - Pass through network access.
   - Under this substrate boundary:
     - Direct exec (`J2DecoyHost`) fails with `ENOENT`.
     - Cross-device copy (`J3CopyDecoy`, `K1Cheat3`) fails with `ENOENT`.
     - Hardlink decoy (`J4Hardlink`) fails with `ENOENT`.
     - Honest replay succeeds, downloads the archive, extracts the member, and executes cleanly.

3. **Second-Order Effects**:
   - **Runtime**: Zero changes required in `tools/kama-llamacpp-live.py` or `tools/kama-live-replay.py`. The tooling remains standard Python.
   - **Contract**: Replay receipts and `server_exe` structures require no breaking schema changes.
   - **Verification**: The counter becomes immune to any future local-copy decoy variants, permanently ending the cat-and-mouse game of inode/write-event heuristics.

---

## 6. Conclusion

The progression from Round 47 to Round 51 represents an escalating dialectic:
- Round 47 checked **JSON text** $\rightarrow$ defeated by JSON fabrication.
- Round 48 checked **files on disk** $\rightarrow$ defeated by skipping execution.
- Round 49 checked **process execution & nonces** $\rightarrow$ defeated by host binary execution.
- Round 50 checked **process tree & mapping** $\rightarrow$ defeated by in-place host execution.
- Round 51 checked **image dev & inode (`own`)** $\rightarrow$ defeated by in-place host copy.

The C1 `own` leg is **not** the end of the decoy line because files on disk cannot testify to their own provenance. Trying to patch this with file metadata (`nlink`, `mtime`, or `inotify`) merely invites more sophisticated userspace decoys.

The decoy line ends only when the observation surface shifts from **inspecting the output artifact** to **constraining the execution substrate**. Substrate mount masking strips the replay of all local shortcuts, forcing it to exercise the true end-to-end re-acquisition pipeline.
