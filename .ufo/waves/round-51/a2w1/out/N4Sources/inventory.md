# Inventory of Lane `/proc` Usage and Man Page Cross-Mapping

## 1. Executive Summary

A comprehensive scan of all Python tools under `kama-shokunin/tools/*.py` (`grep -n "/proc/" tools/*.py` and `grep -n '"/proc"' tools/*.py`) identifies **57 references** across **6 files**:
- `tools/kama-context-capacity.py` (1 reference)
- `tools/kama-live-replay.py` (3 references)
- `tools/kama-llamacpp-live.py` (14 references)
- `tools/round49-replay-witness-audit.py` (11 references)
- `tools/round50-replay-bind-audit.py` (14 references)
- `tools/round51-replay-exe-audit.py` (14 references)

These references resolve to **7 distinct `/proc/<pid>/<file>` paths**, **1 `/proc` directory scan**, and **2 `/proc/net/` network tables**:

| Target Path | Mapped Man Page | Status in `corpus/SOURCES.md` | Primary Function in Lane Tools |
|---|---|---|---|
| `/proc/<pid>/exe` | `proc_pid_exe(5)` | **BACKED** (`S499`, `S495`) | Opens and hashes running binary image (`fstat` dev+inode, SHA-256) |
| `/proc/<pid>/maps` | `proc_pid_maps(5)` | **BACKED** (`S496`) | Verifies file-backed model mapping (`dev`, `inode`, `pathname`) |
| `/proc/<pid>/stat` | `proc_pid_stat(5)` | **UNBACKED** | Reads process state (zombie `Z`), parent PID (`ppid`), start time (`starttime`) |
| `/proc/<pid>/fd` (`/proc/<pid>/fd/<fd>`) | `proc_pid_fd(5)` | **UNBACKED** | Enumerates open file descriptors; matches `socket:[<inode>]` symlinks |
| `/proc/<pid>/environ` | `proc_pid_environ(5)` | **UNBACKED** | Verifies canary environment variables (`KAMA_R50_CANARY`) do not leak |
| `/proc/<pid>/cmdline` | `proc_pid_cmdline(5)` | **UNBACKED** | Extracts `-m <model>` argument from running server |
| `/proc/<pid>/cwd` | `proc_pid_cwd(5)` | **UNBACKED** | Resolves relative model path against server's current working directory |
| `/proc` (directory scan) | `proc_pid(5)` / `proc(5)` | **UNBACKED** | Enumerates numeric directory names to discover all host processes |
| `/proc/net/tcp`, `/proc/net/tcp6` | `proc_net_tcp.rst` / `proc_pid_net(5)` | **BACKED** (`S048`, `S049`) | Finds LISTEN sockets on loopback and correlates socket inodes |

---

## 2. Detailed Breakdown by Target

### A. `/proc/<pid>/exe` (BACKED by S499, S495)
- **Mapped Page:** `proc_pid_exe(5)` (URL: `https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html`)
- **SOURCES Row:** `S499` (admitted round 51 build `b6bed925`, supersedes `S495`).
- **Quote in S499:** `"This symbolic link can be dereferenced normally; attempting to open it will open the executable."` (15 words)
- **Callsites:**
  - `tools/kama-live-replay.py:55`: docstring noting `server_exe` opened through `/proc/<pid>/exe (proc_pid_exe(5))`.
  - `tools/kama-live-replay.py:357`: comment describing running image comparison against `<work>/server/<member>`.
  - `tools/kama-llamacpp-live.py:331`: witness docstring noting observer reads `/proc/<pid>/exe`.
  - `tools/kama-llamacpp-live.py:733, 738, 740, 741`: `server_exe(pid)` opens `/proc/{pid}/exe` via `os.open(link, os.O_RDONLY)` and verifies file type, size, dev/inode, and SHA-256 digest.
  - `tools/kama-llamacpp-live.py:2038`: comment in receipt generator recording `server_exe`.
  - `tools/round49-replay-witness-audit.py:40, 260`: `sha_file(f"/proc/{pid}/exe") == SERVER_SHA`.
  - `tools/round50-replay-bind-audit.py:40, 345`: `sha_file(f"/proc/{pid}/exe") == SERVER_SHA`.
  - `tools/round51-replay-exe-audit.py:32, 45, 320`: `sha_file(f"/proc/{pid}/exe") == SERVER_SHA`.
  - `tools/round51-replay-exe-audit.py:352, 355`: `own_exe(pid, member_path, probs)` opens `/proc/{pid}/exe` with `os.O_RDONLY`, `os.fstat(fd)`, and compares with extracted member.

### B. `/proc/<pid>/maps` (BACKED by S496)
- **Mapped Page:** `proc_pid_maps(5)` (URL: `https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html`)
- **SOURCES Row:** `S496` (admitted round 50).
- **Quote in S496:** `"dev is the device (major:minor); inode is the inode on that device" and "The pathname field will usually be the file that is backing the mapping."` (22 words)
- **Callsites:**
  - `tools/kama-live-replay.py:53`: docstring on model-mapping read from `/proc/<pid>/maps`.
  - `tools/kama-llamacpp-live.py:681, 689`: `model_mapping(pid, model_path)` reads `/proc/{pid}/maps` to locate file-backed mapping of `--model`.
  - `tools/kama-llamacpp-live.py:2035`: comment recording `model_mapping`.
  - `tools/round50-replay-bind-audit.py:52, 313`: `witness_server(pid, port, probs)` reads `/proc/{pid}/maps` to verify model mapping.
  - `tools/round51-replay-exe-audit.py:288`: `witness_server` reads `/proc/{pid}/maps`.

### C. `/proc/<pid>/stat` (UNBACKED — Proposed S500)
- **Mapped Page:** `proc_pid_stat(5)` (URL: `https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html`)
- **Usage:**
  - `tools/kama-context-capacity.py:231`:
    ```python
    stat = Path(f'/proc/{pid}/stat').read_text()
    fields = stat.rsplit(')', 1)[1].split()
    if fields[0] == 'Z': continue
    ```
    Used during capacity test child cleanup to detect zombie processes.
  - `tools/round49-replay-witness-audit.py:231`:
    ```python
    with open(f"/proc/{pid}/stat") as fh:
        state = fh.read().rsplit(")", 1)[1].split()[0]
    return state not in ("Z", "X")
    ```
    Used in `pid_alive(pid)` to check process liveness.
  - `tools/round50-replay-bind-audit.py:212, 237`:
    ```python
    with open(f"/proc/{pid}/stat") as fh:
        rest = fh.read().rsplit(")", 1)[1].split()
    return rest[0], int(rest[1]), int(rest[19])
    ```
    Extracts `(state, ppid, starttime)`. Used in `stat_fields()`, `pid_alive()`, and `descendants()` to construct process tree and check for PID reuse via starttime.
  - `tools/round51-replay-exe-audit.py:210, 212`:
    Same `stat_fields(pid)` implementation used in `descendants()` and `teardown`.

### D. `/proc/<pid>/fd` and `/proc/<pid>/fd/<fd>` (UNBACKED — Proposed S501)
- **Mapped Page:** `proc_pid_fd(5)` (URL: `https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html`)
- **Usage:**
  - `tools/kama-llamacpp-live.py:650, 652`:
    ```python
    for fd in os.listdir(f'/proc/{pid}/fd'):
        if os.readlink(f'/proc/{pid}/fd/{fd}') in wanted:
            return True
    ```
    Matches symlink targets formatted as `socket:[<inode>]` against LISTEN socket inodes from `/proc/net/tcp{,6}`.
  - `tools/kama-llamacpp-live.py:1605`:
    `os.readlink(f'/proc/self/fd/{listener.fileno()}')` in selftest `_selftest_live_tcp6()` to extract socket inode.
  - `tools/round49-replay-witness-audit.py:217, 219`:
    `os.listdir(f"/proc/{pid}/fd")` and `os.readlink()` in `pid_socket_inodes(pid)`.
  - `tools/round50-replay-bind-audit.py:222, 224`:
    `os.listdir(f"/proc/{pid}/fd")` and `os.readlink()` in `pid_socket_inodes(pid)`.
  - `tools/round51-replay-exe-audit.py:197, 199`:
    `os.listdir(f"/proc/{pid}/fd")` and `os.readlink()` in `proc_sockets(pid)`.

### E. `/proc/<pid>/environ` (UNBACKED — Proposed S502)
- **Mapped Page:** `proc_pid_environ(5)` (URL: `https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html`)
- **Usage:**
  - `tools/round50-replay-bind-audit.py:273`:
    ```python
    def environ_keys(pid):
        with open(f"/proc/{pid}/environ", "rb") as fh:
            return {e.split(b"=", 1)[0].decode("utf-8", "replace")
                    for e in fh.read().split(b"\0") if e}
    ```
    Reads process initial environment keys to assert `KAMA_R50_CANARY` is not present in server or parent environment.
  - `tools/round51-replay-exe-audit.py:248`:
    Identical `environ_keys(pid)` check in the round-51 counter.

### F. `/proc/<pid>/cmdline` (UNBACKED — Proposed S503)
- **Mapped Page:** `proc_pid_cmdline(5)` (URL: `https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html`)
- **Usage:**
  - `tools/round49-replay-witness-audit.py:267`:
    ```python
    with open(f"/proc/{pid}/cmdline", "rb") as fh:
        argv = [a.decode("utf-8", "replace") for a in fh.read().split(b"\0")]
    mpath = argv[argv.index("-m") + 1]
    ```
    Extracts the `-m` (model path) argument from the running server process command line.

### G. `/proc/<pid>/cwd` (UNBACKED — Proposed S504)
- **Mapped Page:** `proc_pid_cwd(5)` (URL: `https://man7.org/linux/man-pages/man5/proc_pid_cwd.5.html`)
- **Usage:**
  - `tools/round49-replay-witness-audit.py:271`:
    ```python
    if not os.path.isabs(mpath):
        mpath = os.path.join(os.readlink(f"/proc/{pid}/cwd"), mpath)
    ```
    Resolves relative `-m` argument against the server process's current working directory.

### H. `/proc` Directory Scan (UNBACKED — Proposed S505)
- **Mapped Page:** `proc_pid(5)` / `proc(5)` (URL: `https://man7.org/linux/man-pages/man5/proc_pid.5.html`)
- **Usage:**
  - `tools/round50-replay-bind-audit.py:282`:
    ```python
    for name in os.listdir("/proc"):
        if not name.isdigit():
            continue
        st = stat_fields(int(name))
    ```
    Discovers all active process IDs to build the process descendant tree.
  - `tools/round51-replay-exe-audit.py:257`:
    Identical `/proc` directory scan in `descendants(root)`.
