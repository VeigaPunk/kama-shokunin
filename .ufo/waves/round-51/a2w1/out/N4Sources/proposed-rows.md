# Proposed `corpus/SOURCES.md` Rows for Unbacked `/proc` Interfaces

The lane's `/proc` usage across `tools/*.py` currently includes five unbacked `/proc/<pid>/<file>` targets and one unbacked `/proc` directory scan. Below are the proposed registry rows, formatted strictly according to SOURCES-CONTRACT-v1 (11 columns, immutable column set, quote limit $\le 25$ words, negative scope boundaries, and local text copy references).

## 1. Candidate Registry Table Rows

```markdown
| S500 | Linux proc_pid_stat(5) — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | docs | A | what `/proc/<pid>/stat` fields report: (3) `state`, (4) `ppid` and (22) `starttime` (clock ticks after boot); Linux only; not other platforms, not thread stat | §DESCRIPTION, paragraphs (3),(4),(22); man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_stat.5.txt`) | "The PID of the parent of this process." and "The time the process started after system boot." — so tools can trace descendant process trees and detect process exit without PID-reuse races | mined | 2026-10-27 | 360d | tools/kama-context-capacity.py, tools/round49-replay-witness-audit.py, tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |
| S501 | Linux proc_pid_fd(5) — https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html | docs | A | what `/proc/<pid>/fd/` entries are: symbolic links named by file descriptor, resolving for sockets to `socket:[<inode>]`; Linux only; not other platforms, not fd permissions | §DESCRIPTION ¶2; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_fd.5.txt`) | "For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode." — so the live tool and audit counters can match open socket inodes against `/proc/net/tcp{,6}` listeners | mined | 2026-10-27 | 360d | tools/kama-llamacpp-live.py, tools/round49-replay-witness-audit.py, tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |
| S502 | Linux proc_pid_environ(5) — https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html | docs | A | what `/proc/<pid>/environ` contains: initial environment set when the program was started via execve(2), with null-byte-separated entries; Linux only; not post-exec modifications | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_environ.5.txt`) | "This file contains the initial environment that was set when the currently executing program was started via execve(2)." — so audit counters can check for canary environment leakage in child processes | mined | 2026-10-27 | 360d | tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |
| S503 | Linux proc_pid_cmdline(5) — https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html | docs | A | what `/proc/<pid>/cmdline` holds: complete command line for the process as null-byte-separated strings; Linux only; not zombie processes | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_cmdline.5.txt`) | "This read-only file holds the complete command line for the process, unless the process is a zombie." — so audit counters can extract command-line arguments like `-m <model>` from a running server | mined | 2026-10-27 | 360d | tools/round49-replay-witness-audit.py |
| S504 | Linux proc_pid_cwd(5) — https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html | docs | A | what `/proc/<pid>/cwd` is: a symbolic link to the current working directory of the process; Linux only; not terminated main thread | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid_cwd.5.txt`) | "This is a symbolic link to the current working directory of the process." — so audit counters can resolve relative path arguments against the server process working directory | mined | 2026-10-27 | 360d | tools/round49-replay-witness-audit.py |
| S505 | Linux proc_pid(5) — https://man7.org/linux/man-pages/man5/proc_pid.5.html | docs | A | what numerical subdirectories under `/proc` are: per-process directories named by process ID; Linux only; not thread subdirectories | §DESCRIPTION ¶1; man-pages 6.19, page dated 2026-02-08 (text copy `.ufo/waves/round-51/a2w1/out/N4Sources/proc_pid.5.txt`) | "There is a numerical subdirectory for each running process; the subdirectory is named by the process ID." — so descendant scanning can enumerate active host processes via `/proc` directory listing | mined | 2026-10-27 | 360d | tools/round50-replay-bind-audit.py, tools/round51-replay-exe-audit.py |
```

---

## 2. Row-by-Row Rationale and Grounding Analysis

### 1. S500: `proc_pid_stat(5)`
- **URL:** `https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html`
- **Location:** `man-pages 6.19`, page dated 2026-02-08, §DESCRIPTION paragraphs on fields (3) `state`, (4) `ppid`, and (22) `starttime`.
- **Quote (16 words):** `"The PID of the parent of this process."` (8 words) and `"The time the process started after system boot."` (8 words).
- **What it grounds:**
  1. `tools/kama-context-capacity.py:231`: Zombie detection (`fields[0] == 'Z'`) to avoid blocking on defunct processes during test cleanup.
  2. `tools/round49-replay-witness-audit.py:231`: Process liveness check (`state not in ("Z", "X")`).
  3. `tools/round50-replay-bind-audit.py:237` & `tools/round51-replay-exe-audit.py:212`: Construction of the parent-child ancestry tree in `descendants(root)` using `ppid` (field 4), and anti-PID-reuse verification using `starttime` (field 22) during teardown verification.

### 2. S501: `proc_pid_fd(5)`
- **URL:** `https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html`
- **Location:** `man-pages 6.19`, page dated 2026-02-08, §DESCRIPTION ¶2.
- **Quote (22 words):** `"For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the file type with the inode."`
- **What it grounds:**
  1. `tools/kama-llamacpp-live.py:650-652`: Live port ownership check `_child_owns_port()`, reading `/proc/{pid}/fd/{fd}` via `os.readlink()` and matching `socket:[<inode>]`.
  2. `tools/kama-llamacpp-live.py:1605`: Listener socket inode resolution in selftest `_selftest_live_tcp6()`.
  3. `tools/round49-replay-witness-audit.py:217-219`: `pid_socket_inodes(pid)`.
  4. `tools/round50-replay-bind-audit.py:222-224` & `tools/round51-replay-exe-audit.py:197-199`: `pid_socket_inodes(pid)` and `proc_sockets(pid)`.
  This bridges the gap between `/proc/net/tcp{,6}` listener tables and process ownership.

### 3. S502: `proc_pid_environ(5)`
- **URL:** `https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html`
- **Location:** `man-pages 6.19`, page dated 2026-02-08, §DESCRIPTION ¶1.
- **Quote (18 words):** `"This file contains the initial environment that was set when the currently executing program was started via execve(2)."`
- **What it grounds:**
  1. `tools/round50-replay-bind-audit.py:273` & `tools/round51-replay-exe-audit.py:248`: `environ_keys(pid)`, which parses `/proc/{pid}/environ` by splitting on `\0` and extracting variable keys before `=`. Grounds the `env` canary check asserting `KAMA_R50_CANARY` is absent from server and parent environments.

### 4. S503: `proc_pid_cmdline(5)`
- **URL:** `https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html`
- **Location:** `man-pages 6.19`, page dated 2026-02-08, §DESCRIPTION ¶1.
- **Quote (17 words):** `"This read-only file holds the complete command line for the process, unless the process is a zombie."`
- **What it grounds:**
  1. `tools/round49-replay-witness-audit.py:267`: Reading `/proc/{pid}/cmdline` to recover the `-m <model>` argument passed to `llama-server`.

### 5. S504: `proc_pid_cwd(5)`
- **URL:** `https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html`
- **Location:** `man-pages 6.19`, page dated 2026-02-08, §DESCRIPTION ¶1.
- **Quote (13 words):** `"This is a symbolic link to the current working directory of the process."`
- **What it grounds:**
  1. `tools/round49-replay-witness-audit.py:271`: Resolving relative `-m` path arguments against `os.readlink(f"/proc/{pid}/cwd")` to check whether the targeted file matches `MODEL_SHA`.

### 6. S505: `proc_pid(5)`
- **URL:** `https://man7.org/linux/man-pages/man5/proc_pid.5.html`
- **Location:** `man-pages 6.19`, page dated 2026-02-08, §DESCRIPTION ¶1.
- **Quote (17 words):** `"There is a numerical subdirectory for each running process; the subdirectory is named by the process ID."`
- **What it grounds:**
  1. `tools/round50-replay-bind-audit.py:282` & `tools/round51-replay-exe-audit.py:257`: Directory scanning of `/proc` via `os.listdir("/proc")` filtered by `name.isdigit()` to enumerate all running processes for descendant tree construction.
