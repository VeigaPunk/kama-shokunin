VERDICT: Across 55 `/proc/` matches in 6 lane tools, 7 distinct `/proc/<pid>/<file>` targets and 1 `/proc` directory scan are read; 2 are backed by SOURCES rows (`/proc/<pid>/exe` via S499/S495 and `/proc/<pid>/maps` via S496), while 5 (`stat`, `fd`, `environ`, `cmdline`, `cwd`) plus the `/proc` directory scan are unbacked; all 6 corresponding man pages were fetched from man7.org (`man-pages 6.19`), and 6 formal registry rows (S500–S505) are proposed with strictly located quotes ($\le 25$ words), verified verbatim against fetched copies, and validated with 0 append-only violations.

# N4Sources — Cross-Source Consistency of Lane `/proc` Usage

## 1. Godspeed Posture & Axes

- **Axis Served:** **Operability (C1)**. Grounding the lane's process inspection, ancestry tracking, and socket-correlation interfaces eliminates ungrounded assumptions in server liveness verification, canary leak detection, and tree teardown.
- **Axis Preserved:** **Calibration (C2)**. Harms no calibration predicates; proposed rows do not alter disclosure contracts or threshold semantics.
- **Move:** Propose a unified set of six `proc_pid_*(5)` documentation sources (S500–S505) that fully close the kernel interface grounding deficit for all process observation tools in `kama`.

---

## 2. Inventory of Lane `/proc` Usage

Scanning `grep -n "/proc/" tools/*.py` and `grep -n '"/proc"' tools/*.py` yields 57 total references across 6 files. Grouped by accessed resource:

| Target Resource | Mapped Man Page | Status in `corpus/SOURCES.md` | Callsites (File:Line) | What it Grounds in the Lane |
|---|---|---|---|---|
| `/proc/<pid>/exe` | `proc_pid_exe(5)` | **BACKED** (`S499`, `S495`) | `kama-live-replay.py:55,357`<br>`kama-llamacpp-live.py:331,733,738,740,741,2038`<br>`round49-replay-witness-audit.py:40,260`<br>`round50-replay-bind-audit.py:40,345`<br>`round51-replay-exe-audit.py:32,45,320,352,355` | Opens and hashes running binary image (`fstat` dev+inode, SHA-256) |
| `/proc/<pid>/maps` | `proc_pid_maps(5)` | **BACKED** (`S496`) | `kama-live-replay.py:53`<br>`kama-llamacpp-live.py:681,689,2035`<br>`round50-replay-bind-audit.py:52,313`<br>`round51-replay-exe-audit.py:288` | Verifies file-backed model mapping (`dev`, `inode`, `pathname`) |
| `/proc/<pid>/stat` | `proc_pid_stat(5)` | **UNBACKED** (Proposed `S500`) | `kama-context-capacity.py:231`<br>`round49-replay-witness-audit.py:231`<br>`round50-replay-bind-audit.py:62,212,235,237`<br>`round51-replay-exe-audit.py:210,212` | Reads process state (zombie `Z`), parent PID (`ppid`), start time (`starttime`) |
| `/proc/<pid>/fd` (`/proc/<pid>/fd/<fd>`) | `proc_pid_fd(5)` | **UNBACKED** (Proposed `S501`) | `kama-llamacpp-live.py:650,652,1605`<br>`round49-replay-witness-audit.py:42,217,219`<br>`round50-replay-bind-audit.py:42,222,224`<br>`round51-replay-exe-audit.py:197,199` | Enumerates open file descriptors; matches `socket:[<inode>]` symlinks |
| `/proc/<pid>/environ` | `proc_pid_environ(5)` | **UNBACKED** (Proposed `S502`) | `round50-replay-bind-audit.py:48,273`<br>`round51-replay-exe-audit.py:248` | Verifies canary environment variables (`KAMA_R50_CANARY`) do not leak |
| `/proc/<pid>/cmdline` | `proc_pid_cmdline(5)` | **UNBACKED** (Proposed `S503`) | `round49-replay-witness-audit.py:43,267` | Extracts `-m <model>` argument from running server |
| `/proc/<pid>/cwd` | `proc_pid_cwd(5)` | **UNBACKED** (Proposed `S504`) | `round49-replay-witness-audit.py:271` | Resolves relative model path against server's current working directory |
| `/proc` (directory scan) | `proc_pid(5)` / `proc(5)` | **UNBACKED** (Proposed `S505`) | `round50-replay-bind-audit.py:282`<br>`round51-replay-exe-audit.py:257` | Enumerates numeric directory names to discover active host processes |
| `/proc/net/tcp`, `/proc/net/tcp6` | `proc_net_tcp.rst` / kernel source | **BACKED** (`S048`, `S049`) | `kama-llamacpp-live.py:627,1589,1612,1620`<br>`round49-replay-witness-audit.py:41,195`<br>`round50-replay-bind-audit.py:200`<br>`round51-replay-exe-audit.py:175` | Reads loopback listener sockets and their inodes |

---

## 3. Analysis of Unbacked Uses

### 1. `/proc/<pid>/stat` $\rightarrow$ `proc_pid_stat(5)`
- **Tools/Lines:**
  - `tools/kama-context-capacity.py:231`: `stat = Path(f'/proc/{pid}/stat').read_text()`; splits after `)`, checks `fields[0] == 'Z'` to identify zombies during child cleanup.
  - `tools/round49-replay-witness-audit.py:231`: `pid_alive()` checks `state not in ("Z", "X")`.
  - `tools/round50-replay-bind-audit.py:237` & `tools/round51-replay-exe-audit.py:212`: `stat_fields(pid)` extracts `(rest[0], int(rest[1]), int(rest[19]))` corresponding to `(state, ppid, starttime)` (fields 3, 4, and 22). Used in `descendants(root)` to construct process ancestry and ensure no process survives teardown or suffers PID reuse.
- **Man Page Documentation:** `proc_pid_stat(5)` specifies field order and format:
  - Paragraph (3): `state %c` ("One of the following characters, indicating process state: ... Z Zombie").
  - Paragraph (4): `ppid %d` ("The PID of the parent of this process.").
  - Paragraph (22): `starttime %llu` ("The time the process started after system boot.").
- **Located Quote ($\le 25$ words):**
  `"The PID of the parent of this process."` (8 words) and `"The time the process started after system boot."` (8 words).
- **What it Grounds:** Reading process state to filter zombies, parent PID to walk ancestry trees, and start time to detect PID reuse across SIGKILL teardown windows.

### 2. `/proc/<pid>/fd` $\rightarrow$ `proc_pid_fd(5)`
- **Tools/Lines:**
  - `tools/kama-llamacpp-live.py:650-652`: `os.listdir(f'/proc/{pid}/fd')` and `os.readlink(f'/proc/{pid}/fd/{fd}')` in `_child_owns_port()`.
  - `tools/kama-llamacpp-live.py:1605`: `os.readlink(f'/proc/self/fd/{listener.fileno()}')` in selftest `_selftest_live_tcp6()`.
  - `tools/round49-replay-witness-audit.py:217-219`: `pid_socket_inodes(pid)`.
  - `tools/round50-replay-bind-audit.py:222-224` & `tools/round51-replay-exe-audit.py:197-199`: `pid_socket_inodes(pid)` and `proc_sockets(pid)`.
- **Man Page Documentation:** `proc_pid_fd(5)` §DESCRIPTION ¶2 states:
  "For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode. A readlink(2) call on this file returns a string in the format: type:[inode] ... For sockets, that inode can be used to find more information in one of the files under /proc/net/."
- **Located Quote ($\le 25$ words):**
  `"For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode."` (22 words).
- **What it Grounds:** Resolving open file descriptors to socket inodes (`socket:[<inode>]`) to correlate process ownership with `/proc/net/tcp{,6}` listener entries.

### 3. `/proc/<pid>/environ` $\rightarrow$ `proc_pid_environ(5)`
- **Tools/Lines:**
  - `tools/round50-replay-bind-audit.py:273` & `tools/round51-replay-exe-audit.py:248`:
    `with open(f"/proc/{pid}/environ", "rb") as fh: return {e.split(b"=", 1)[0].decode("utf-8", "replace") for e in fh.read().split(b"\0") if e}`.
- **Man Page Documentation:** `proc_pid_environ(5)` §DESCRIPTION ¶1 documents that this file contains the initial environment set at `execve(2)` with null-byte-separated entries.
- **Located Quote ($\le 25$ words):**
  `"This file contains the initial environment that was set when the currently executing program was started via execve(2)."` (18 words).
- **What it Grounds:** Extracting the environment variable keys of running processes to confirm absence of canary variables (`KAMA_R50_CANARY`).

### 4. `/proc/<pid>/cmdline` $\rightarrow$ `proc_pid_cmdline(5)`
- **Tools/Lines:**
  - `tools/round49-replay-witness-audit.py:267`:
    `with open(f"/proc/{pid}/cmdline", "rb") as fh: argv = [a.decode("utf-8", "replace") for a in fh.read().split(b"\0")]`.
- **Man Page Documentation:** `proc_pid_cmdline(5)` §DESCRIPTION ¶1 documents that this read-only file holds the command line as null-byte-separated strings unless the process is a zombie.
- **Located Quote ($\le 25$ words):**
  `"This read-only file holds the complete command line for the process, unless the process is a zombie."` (17 words).
- **What it Grounds:** Extracting CLI flags (specifically `-m <model>`) from running server processes.

### 5. `/proc/<pid>/cwd` $\rightarrow$ `proc_pid_cwd(5)`
- **Tools/Lines:**
  - `tools/round49-replay-witness-audit.py:271`:
    `mpath = os.path.join(os.readlink(f"/proc/{pid}/cwd"), mpath)`.
- **Man Page Documentation:** `proc_pid_cwd(5)` §DESCRIPTION ¶1 documents that `/proc/pid/cwd` is a symbolic link to the process's current working directory.
- **Located Quote ($\le 25$ words):**
  `"This is a symbolic link to the current working directory of the process."` (13 words).
- **What it Grounds:** Resolving relative argument paths against the process's working directory.

### 6. `/proc` Directory Scan $\rightarrow$ `proc_pid(5)`
- **Tools/Lines:**
  - `tools/round50-replay-bind-audit.py:282` & `tools/round51-replay-exe-audit.py:257`:
    `for name in os.listdir("/proc"): if not name.isdigit(): continue`.
- **Man Page Documentation:** `proc_pid(5)` §DESCRIPTION ¶1 documents that `/proc` contains a numerical subdirectory for each running process, named by its process ID.
- **Located Quote ($\le 25$ words):**
  `"There is a numerical subdirectory for each running process; the subdirectory is named by the process ID."` (17 words).
- **What it Grounds:** Discovering all active host processes via numeric subdirectory names in `/proc`.

---

## 4. Proposed SOURCES Rows

The six proposed rows strictly follow SOURCES-CONTRACT-v1:

```markdown
| S500 | Linux proc_pid_stat(5) — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | docs | A | what `/proc/<pid>/stat` fields report: (3) `state`, (4) `ppid` and (22) `starttime` (clock ticks after boot); Linux only; not other platforms, not thread stat | §DESCRIPTION, paragraphs (3),(4),(22); man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_stat.5.txt`) | "The PID of the parent of this process." and "The time the process started after system boot." — so tools can trace descendant process trees and detect process exit without PID-reuse races | mined | 2026-10-27 | 360d | tools/kama-context-capacity.py, tools/round49-replay-witness-audit.py, tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |
| S501 | Linux proc_pid_fd(5) — https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html | docs | A | what `/proc/<pid>/fd/` entries are: symbolic links named by file descriptor, resolving for sockets to `socket:[<inode>]`; Linux only; not other platforms, not fd permissions | §DESCRIPTION ¶2; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_fd.5.txt`) | "For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode." — so the live tool and audit counters can match open socket inodes against `/proc/net/tcp{,6}` listeners | mined | 2026-10-27 | 360d | tools/kama-llamacpp-live.py, tools/round49-replay-witness-audit.py, tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |
| S502 | Linux proc_pid_environ(5) — https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html | docs | A | what `/proc/<pid>/environ` contains: initial environment set when the program was started via execve(2), with null-byte-separated entries; Linux only; not post-exec modifications | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_environ.5.txt`) | "This file contains the initial environment that was set when the currently executing program was started via execve(2)." — so audit counters can check for canary environment leakage in child processes | mined | 2026-10-27 | 360d | tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |
| S503 | Linux proc_pid_cmdline(5) — https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html | docs | A | what `/proc/<pid>/cmdline` holds: complete command line for the process as null-byte-separated strings; Linux only; not zombie processes | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_cmdline.5.txt`) | "This read-only file holds the complete command line for the process, unless the process is a zombie." — so audit counters can extract command-line arguments like `-m <model>` from a running server | mined | 2026-10-27 | 360d | tools/round49-replay-witness-audit.py |
| S504 | Linux proc_pid_cwd(5) — https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html | docs | A | what `/proc/<pid>/cwd` is: a symbolic link to the current working directory of the process; Linux only; not terminated main thread | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_cwd.5.txt`) | "This is a symbolic link to the current working directory of the process." — so audit counters can resolve relative path arguments against the server process working directory | mined | 2026-10-27 | 360d | tools/round49-replay-witness-audit.py |
| S505 | Linux proc_pid(5) — https://man7.org/linux/man-pages/man5/proc_pid.5.html | docs | A | what numerical subdirectories under `/proc` are: per-process directories named by process ID; Linux only; not thread subdirectories | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid.5.txt`) | "There is a numerical subdirectory for each running process; the subdirectory is named by the process ID." — so descendant scanning can enumerate active host processes via `/proc` directory listing | mined | 2026-10-27 | 360d | tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |
```

---

## 5. Second-Order Effects & Cross-Surface Consistency

1. **Runtime Surface (`tools/kama-llamacpp-live.py`):**
   - Socket ownership `_child_owns_port()` directly relies on `/proc/{pid}/fd` resolving to `socket:[<inode>]`. Without `proc_pid_fd(5)` grounding, the correlation between `/proc/net/tcp{,6}` and process sockets lacks foundational authority.
2. **Contract Surface (`corpus/SOURCES.md` & `tools/sources-append-only.py`):**
   - Adding rows S500–S505 complies strictly with SOURCES-CONTRACT-v1 rule 2: no existing rows modified outside mutable set (`{status, recheck, used-by}`), all immutable cells populated, and all quotes strictly under 25 words.
3. **Substrate Surface (Linux procfs):**
   - Notice: `stat_fields` parses `/proc/<pid>/stat` via `rsplit(')', 1)[1].split()`. This is only robust because the process `comm` field is enclosed in parentheses, and no subsequent numerical fields contain closing parentheses. `proc_pid_stat(5)` confirms this format.
   - Notice: `/proc/net/tcp` documentation does not reside at `proc_net_tcp(5)` on man7.org (returns 404), but in `Documentation/networking/proc_net_tcp.rst` (backed by `S049`) and `proc_pid_net(5)`.
4. **Verification Surface (`tools/round51-replay-exe-audit.py`):**
   - The C1 counter already enforces that `proc_pid_exe(5)` is grounded via `newrow` (checked against `S499`). Admitting `S500`–`S505` completes the remaining ungrounded verification surfaces (`own`, `bind`, `listen`, `teardown`, and `env`).

---

## 6. Evidence Commands & Exit Codes

1. **Grepping all `/proc` usages:**
   ```bash
   grep -Hn "/proc/" /home/vgpnk/Projects/shokunin/kama-shokunin/tools/*.py
   ```
   *Result:* 55 matches in 6 files (exit code 0).
2. **Checking `/proc` directory scan:**
   ```bash
   grep -Hn '"/proc"' /home/vgpnk/Projects/shokunin/kama-shokunin/tools/*.py
   ```
   *Result:* 2 matches (`round50-replay-bind-audit.py:282`, `round51-replay-exe-audit.py:257`) (exit code 0).
3. **Live Fetch of Man Pages from man7.org (`man-pages 6.19`):**
   ```bash
   curl -sSI https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html
   ```
   *Result:* HTTP 200 OK, `Content-Length: 20647`.
   All 6 man pages fetched and saved as `.txt` files in `out/N4Sources/`.
4. **Automated Validation of Proposed Rows (`validate_proposed.py`):**
   ```bash
   python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/validate_proposed.py
   ```
   *Output:*
   ```text
   --- 1. Checking Quote Word Counts and Verbatim Presence ---
   [S500] (proc_pid_stat.5.txt): Quote 1 (8 words), Quote 2 (8 words) -> Verbatim match confirmed.
   [S501] (proc_pid_fd.5.txt): Quote (22 words) -> Verbatim match confirmed.
   [S502] (proc_pid_environ.5.txt): Quote (18 words) -> Verbatim match confirmed.
   [S503] (proc_pid_cmdline.5.txt): Quote (17 words) -> Verbatim match confirmed.
   [S504] (proc_pid_cwd.5.txt): Quote (13 words) -> Verbatim match confirmed.
   [S505] (proc_pid.5.txt): Quote (17 words) -> Verbatim match confirmed.

   --- 2. Checking SOURCES-CONTRACT-v1 Append-Only Compliance ---
   Clean append-only diff: 6 rows added (['S500', 'S501', 'S502', 'S503', 'S504', 'S505']), 0 violations.
   ALL VALIDATION CHECKS PASSED SUCCESSFULLY.
   ```
   *Exit Code:* 0.

---

## 7. Deliverables & Absolute Paths Written

1. Report:
   `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources.md`
2. Deliverable Directory:
   `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/inventory.md`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/proposed-rows.md`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/validate_proposed.py`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_stat.5.txt`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_fd.5.txt`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_environ.5.txt`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_cmdline.5.txt`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_cwd.5.txt`
   - `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid.5.txt`
