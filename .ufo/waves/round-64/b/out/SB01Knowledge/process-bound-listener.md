source: S529 — Linux proc_pid_fd(5), https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html; S530 — Linux proc_pid_stat(5), https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html; S531 — Linux proc_pid_environ(5), https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html; S532 — Linux proc_pid_cmdline(5), https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html; held: S049 — Linux kernel Documentation/networking/proc_net_tcp.rst @ v7.2, https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst (its raw bytes: https://raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst); S495 — Linux proc_pid_exe(5), https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html; S496 — Linux proc_pid_maps(5), https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html; S499 — Linux proc_pid_exe(5), https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html (second row for the same page). Code read at the verified-at commit: tools/round64-c1-counter.py, tools/kama-completion-live.py (v3), tools/kama-llamacpp-live.py.
verified-at: f6a4ea9a8b5a876d685b08e7e582ec0723412a4a (2026-10-28) — man pages re-fetched with curl on 2026-10-28 (man-pages 6.19, footer date 2026-02-08) and quotes checked by `recheck-quotes.py` (27/27 OK: 21 man-page quotes, 2 S049 quotes from the raw kernel doc, 4 held text copies of S495/S496 read at this commit); S049 raw digest checked against the row; counter and tool read with `git show` at this commit. Nothing here records a counter run: the live result belongs to the round's verdict, not to this entry.
recheck: on-release, and every 90 days. `python3 .ufo/waves/round-64/b/out/SB01Knowledge/recheck-quotes.py` must print `quotes OK=27/27`; `git show f6a4ea9a8b5a876d685b08e7e582ec0723412a4a:tools/round64-c1-counter.py | grep -n -E '^def (listeners|holder_pids|stat_fields|read_maps|holder_record|grade_binding|pid_gone|reference_run)'` must print the line numbers cited below (238, 258, 289, 311, 339, 400, 843, 806). A changed quote or moved line restarts this entry.

# Process-bound listener: which process answers on a port (Linux)

## Claim

A port number says nothing about who answers on it. A verifier that wants to write "the process answering on port P is the pinned `llama-server` at digest D" needs six observations, each read from `/proc` on Linux:

1. the listening socket's inode, from `/proc/net/tcp` and `/proc/net/tcp6` (S049);
2. every process holding that inode, from `/proc/<pid>/fd/*` (S529);
3. for each holder, the executable (`/proc/<pid>/exe`, S495/S499), argv (`/proc/<pid>/cmdline`, S532), initial environment (`/proc/<pid>/environ`, S531) and mapped files (`/proc/<pid>/maps`, S496);
4. the holder's parent and start time (`/proc/<pid>/stat` fields 4 and 22, S530), to order it after the tool that claims to have started it;
5. the holder's exit, observed by the verifier after the verifier itself releases the hold;
6. agreement of the held process's answers with a second pinned server, which the verifier starts itself.

Steps 1-5 are the binding. Step 6 is a behaviour check and does not bind anything (see step 7).

*Opinion:* no single observation is enough. Each one can be satisfied by a forged process in some way (the limits below), so the verdict has to be the conjunction, and each conjunct should be read with its limit beside it.

## Why the binding exists: the round-63 failure

Round 63 bound the socket, not the process. Its counter bound the socket the tool reported, took the pid from the tool's own `hold.json`, and loaded its ownership helper from the tree under judgment. Two forged tools passed at 44/44:

- `forge-A-realchild.patch`: a canned answerer serves the run port from an inherited listener fd while the real child is also running;
- `forge-B-sleeper-delta.patch`: a sleeper process with no `llama-server` at all.

Evidence: `.ufo/waves/round-63/w1/out/MT15C1FakeConsistent/forge.out` and `sleeper.out`; each prints `met=True` on line 1 with `controls_targeted=44/44 eval_selftest=3/3 errors=0`. Command: `git show f6a4ea9a8b5a876d685b08e7e582ec0723412a4a:.ufo/waves/round-63/w1/out/MT15C1FakeConsistent/forge.out | grep -n 'met='`. The same failure is in `corpus/lessons/round-63-verifier-spotcheck.md` (section 6, C1).

## Step 1 — the listener inode

**Procfs.** `/proc/net/tcp` and `/proc/net/tcp6` list one socket per line; field 2 is the local address, field 4 the state, field 10 the inode. S049 (intro, lines 4-12) says these interfaces "are deprecated in favor of tcp_diag" and that the entry format is `46: 010310AC:9C4C 030310AC:1770 01` (its example, line 18). S049's row excludes state codes and IPv6 byte order, and the page states neither the state values nor the IPv4 byte order. The state `0A` (LISTEN) is what the counter uses and what the demo below observed. The IPv4 byte order is stated in code, not on the page (`tools/kama-llamacpp-live.py:619-626`, docstring: "IPv4 addresses use little-endian byte order").

**Kama reading.** `listeners()` (`tools/round64-c1-counter.py:238-255`) keeps every `0A` row whose port equals the run port, from both tables, and records whether the address is loopback. `bind_listener` (counter line 410) then requires every such listener to be loopback.

**Observed** (`procfs-demo.run1.out`, run on this host): a socket bound to a random loopback port produced one inode and was found in the `0A` state.

**Limits.**
- The reader is the file that S049 calls deprecated in favour of tcp_diag. A netlink reader would be a new source; none is held.
- Two readers, two address policies. The counter's `listeners()` keeps wildcard listeners and then fails `bind_listener`. The tool's `_listen_inodes()` (`tools/kama-llamacpp-live.py:619-638`) skips wildcard addresses on purpose ("fail-closed" in its docstring). A wildcard listener is therefore visible to the counter and invisible to the tool. Only the counter's view decides the verdict.
- Point in time. Listeners and holders are read separately and at different moments. The counter reads the whole snapshot twice (`raw_a`, `raw_b`, counter lines 898-902) and requires equal holder signatures (`bind_stable`, counter line 722). The second read narrows the window; it does not close it.
- *Inference, not tested here:* `/proc/net/tcp` shows sockets of the reader's network namespace only. S049 does not say so.

## Step 2 — the holders

**Procfs.** `readlink /proc/<pid>/fd/<n>` on a socket returns `type:[inode]`, and "For sockets, that inode can be used to find more information in one of the files under /proc/net/." (S529, DESCRIPTION). Holders are every pid with an fd whose link equals `socket:[<inode>]`.

**Kama reading.** `holder_pids()` (counter lines 258-286) walks `/proc`, lists each `fd` directory and compares links to the wanted inodes.

**Observed** (`procfs-demo.run1.out`): before a fork, the listener had one holder (the reader). After `os.fork()` the child appeared as a second holder, with the same executable digest, because a child inherits a listening fd. This is the mechanism behind forgery A.

**Limits.**
- Permission. S529: "Permission to dereference or read (readlink(2)) the symbolic links in this directory is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check". An fd table the reader cannot read is an observation limit, not an absence. (The S529 row says the same thing in its own words; that reading is kama's, not the man page's.)
- The counter fails closed only for unreadable tables owned by its own uid (`holder_pids`, lines 270-276). Unreadable tables of other uids are skipped without a record.
- The counter also drops unreadable own-uid tables of processes that started before the tool from the failing set: collect() keeps `unreadable_own` only for start ticks at or after the tool's (counter lines 382-384); the older ones are counted in `unreadable_old` (line 385), and grade_binding() never reads `unreadable_old`. *Inference from code:* an older, non-dumpable process of the same uid could hold the listener unseen by the grade.
- The tool's own `_proc_holders()` (`tools/kama-completion-live.py:190-223`) silently skips any table it cannot read (`except OSError: continue`). Its `listener_holders` list can therefore be incomplete; the counter compares the tool's list with its own (`bind_claim`, counter line 730).
- "In a multithreaded process, the contents of this directory are not available if the main thread has already terminated" (S529, DESCRIPTION). A read can fail for that reason too.
- A holder set of exactly `{hold pid}` rules out a second holder. It says nothing about what that holder executes; that is steps 3-4.

## Step 3 — the executable and its digest

**Procfs.** "This symbolic link can be dereferenced normally; attempting to open it will open the executable." (S495, DESCRIPTION; S499 carries the same sentence). An unlinked executable reads with a suffix: "If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname." (S495). Reading the link is governed by "a ptrace access mode PTRACE_MODE_READ_FSCREDS check" (S495, S499).

**Kama reading.** `holder_record()` (counter lines 339-346) reads the link text and hashes `/proc/<pid>/exe` itself, uncached (`cache=False`, line 344); on any `OSError` both fields become `None`. `bind_exe` (lines 417-419) requires the link text to equal the server path the counter chose and the digest to equal `SERVER_SHA` (`b6a31a8e97615a2a1445aeba51e6411e7b02f0a5fa554559347239ee860cd804`, line 49).

**Why hash through the link.** S495 says opening the link opens the executable. The hash therefore covers the image the process runs, not whatever is at the path it was started from. (The "therefore" is kama's reading of that sentence.)

**Observed** (`procfs-demo.run1.out`): the python process's `exe` hashed to `375532f8…`, which is the digest of `/usr/bin/python3.14` (`sha256sum /usr/bin/python3.14`). Any holder that is not the pinned binary fails `bind_exe` by its digest, whatever its path or name.

**Limits.**
- A wrapper that `exec`s `llama-server` is judged as `llama-server`, because the wrapper is gone after `exec`. A wrapper that forks is judged by its child. Ancestry (step 5) is what separates the two cases.
- *Inference, not in S495:* for a script, the executable is the interpreter, so the digest names the interpreter.
- An unreadable link gives `None`, which fails `bind_exe`. That is fail-closed, and the same limit as step 2 applies.

## Step 4 — argv, initial environment, mapped files

These three are weaker than step 3 because the process can change what they show.

**argv (S532).** "processes have the freedom to override the memory region and break assumptions about the contents or format of the /proc/pid/cmdline file." And: "Think of this file as the command line that the process wants you to see." Kama reading: the counter splits on NUL and drops empty arguments (`holder_record`, lines 348-352), then checks `realpath(argv[0])`, `--port`, `--host 127.0.0.1`, `--alias` and `--model` (with the model's digest) by flag-value pairs (`argv_ok`, lines 421-433). Dropping empty arguments means positions shift, so the check reads pairs, not positions.

*Opinion:* argv is a corroborating observation. `argv[0]` is the first thing a rewrite changes, so it should never stand alone as the identity; `bind_exe` carries the identity.

**Initial environment (S531).** "This file contains the initial environment that was set when the currently executing program was started via execve(2)." And: "If, after an execve(2), the process modifies its environment (e.g., by calling functions such as putenv(3) or modifying the environ(7) variable directly), this file will not reflect those changes." Kama reading: only the key names are kept (lines 354-359); a key beginning `LD_` or `GLIBC_TUNABLES` fails `bind_env` (lines 434-437).

**Observed** (`procfs-demo.run1.out`): a variable set in the running python process with `os.environ[...]=` is not visible in `/proc/self/environ` (`runtime-set var visible in /proc/self/environ: False`, three runs).

**Limits.**
- Only the initial environment is visible. S531 adds that a process may move the region with `prctl(2)` operations such as `PR_SET_MM_ENV_START`.
- Values are never recorded, only key names.
- *Inference from the counter's code, not exercised by any control:* a system-wide preload file (`/etc/ld.so.preload`) is not in any environment and no key names it, so `bind_env` cannot see it.

**Mapped files (S496).** "dev is the device (major:minor); inode is the inode on that device." And: "The pathname field will usually be the file that is backing the mapping." Kama reading: `read_maps()` (lines 311-336) keeps each distinct pathname, and hashes only files that realpath under the server directory, using the realpath at check time (line 334). `maps_ok()` (lines 439-462) rejects any `(deleted)` mapping, skips pseudo-paths (`[heap]`, `[vdso]`) and anonymous mappings, skips `/usr/lib/`, `/lib/`, `/usr/lib64/`, `/lib64/` and `/etc/ld.so.cache` by path (`SYSTEM_PREFIXES` and `SYSTEM_FILES`, lines 140-141, check at line 451), requires a file under the server directory to match `LIBS` by basename and digest (lines 456-458), and rejects anything else.

S496 also says that for a deleted file-backed mapping "the string " (deleted)" is appended to the pathname. Note that this is ambiguous too." `maps_ok` rejects any such mapping (counter line 445).

**Limits.**
- "will usually be" is a hint, not an identity. The counter does not compare the `dev` and `inode` columns of the maps line with the file it hashes. It hashes whatever the path names at check time. *Inference from line 334:* a file replaced at the same path after the process loaded it hashes as the new file. *Opinion:* the stronger check compares the mapped `dev:inode` with `stat` of the path. That is not implemented here, and this entry holds no source for `/proc/<pid>/map_files`.
- System prefixes are trusted by path, not by digest (counter line 140, check line 451). A library under `/usr/lib/` that the pinned binary loads would pass `bind_maps` unchecked. *Inference:* no control exercises this.
- S496: "0 indicates that no inode is associated with the memory region" — the anonymous case is the blank pathname; `maps_ok` skips it (counter line 449).

## Step 5 — parentage and start time

**Procfs.** `/proc/<pid>/stat` fields are numbered in S530. Field (4) is ppid: "The PID of the parent of this process." Field (22) is starttime: "The time the process started after system boot." and "Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK))." S530 marks some fields `[PT]` (fields 26-30, 35, 45-52 in the page) and says of them: "If the check denies access, then the field value is displayed as 0." Fields 4 and 22 are not `[PT]` in S530.

**Kama reading.** `stat_fields()` (counter lines 289-296) splits after the last `)`, so the list index is the field number minus three: `rest[1]` is field 4 and `rest[19]` is field 22. `ppid_chain()` (lines 299-308) walks at most 8 parents. `bind_ancestry` (lines 465-466) requires the tool's pid in every holder's chain. `hold_fresh` (lines 469-476) requires the holder's starttime at or after the tool's (`>=`, line 472), the hold file's mtime later than the counter's own start time, and schema `kama-completion-hold/v1`. `pid_gone()` (lines 843-855) treats a pid whose starttime differs, or whose state is `Z` or `X`, as gone.

**Clock tick.** `getconf CLK_TCK` prints `100` on this host, so one tick is 10 ms.

**Observed** (`procfs-demo.run{1,2,3}.out`, command `python3 procfs-demo.py`): 60 `sleep 3` children started within a fraction of a second had 2, 1 and 2 distinct starttime values. Three unsaved runs in the seat transcript gave 3, 2 and 3. The largest single group in one saved run was all 60 children in one tick.

**Limits.**
- Resolution. Two processes started in the same tick have equal starttime and cannot be ordered by it. `hold_fresh` accepts equal values (`>=`, line 472), so a holder started in the same tick as the tool passes the order check. *Opinion:* the ancestry check (`bind_ancestry`) is the order fact that does not depend on ticks; the tick comparison should be read as a weak, supporting check.
- Identity over time. Identity is the pair (pid, starttime), not the pid. `pid_gone()` reads a reused pid with a different starttime as gone. *Inference:* a reused pid with an equal starttime in the same tick cannot be told apart by these fields.
- Reparenting. *Inference from kernel reparenting, not in S530:* a holder whose tool has exited is reparented, so ancestry fails. That is a failure to observe, not proof of a detached process. (The detach control in the counter is credited to `bind_ancestry`, counter line 1592.)

## Step 6 — teardown, observed by the verifier

The counter takes the hold: it writes `release` into the hold directory it created (counter line 916), then polls for 30 seconds until every holder is gone (`pid_gone`, line 922) and `listeners(port)` is empty (line 924). The release file and the poll are kama's design; S529-S532 do not describe them.

**Limits.** The port check counts `LISTEN` sockets only, so a connection in another state does not count as holding the port. A zombie counts as gone (state `Z`), on the reading that a process's descriptors are released when it exits (*inference*, not on the held pages). A new listener on the same port that appears during the window makes the port look open, so the check fails rather than passing.

## Step 7 — reference agreement (not a binding)

The counter starts its own copy of the pinned server on a free loopback port, with the same model, alias and flags (`--model`, `--alias`, `--port`, `--host 127.0.0.1`, `-c 512`, `-t 1`; `reference_run()`, lines 806-840). It sends the same two probe requests to the held child and to the reference; `probe_fails()` (line 631) compares each answer. The probes are drawn per run from a generator seeded with `os.urandom` (`draw_probes()`, lines 751-765; seed at line 1481).

**Limits.** Agreement shows the answers match a pinned server. It does not show that the answering process is that server. A forwarding proxy that relays to the reference would agree on every answer, which is why binding (steps 1-5) is a separate verdict. The round-64 counter credits its proxy control to `bind_holders` (counter line 1593). *Opinion:* the exact-body check `{"status":"ok"}` on `/health` (line 822) is a shape check.

## What the join cannot establish

- That the pinned binary behaves correctly. Digests pin bytes, not behaviour.
- Anything about a process the reader cannot read. An unreadable holder is an observation limit.
- Anything outside the reader's pid and network namespaces (*inference*: the held pages do not discuss namespaces).
- Anything at an instant other than the snapshot. The counter's two reads narrow the window; they do not remove it.
- The model. The llama-server digest does not pin the model file or the build's flags; the counter pins the model separately (`MODEL_SHA`, counter line 48; argv `--model` checked against it in `argv_ok`).

## Numbers and the command that produced each

Each value is printed by the command shown; the first block is `recheck-quotes.py`, which the `recheck:` line cites.

```
python3 .ufo/waves/round-64/b/out/SB01Knowledge/recheck-quotes.py
  -> quotes OK=27/27
  -> man-page digests (fetched 2026-10-28): fd 3a50ddef…, stat 0f04d789…, environ 93394d9e…, cmdline 1fc68168…, exe 8c9bf02f…, maps 3a339496…
  -> S049 raw digest a4da3f43… (matches the row); S049 line of 'deprecated in favor' [8], 'tcp6_seq_show()' [12], '46: 010310AC:9C4C' [18]
  -> S049 blob page: 205095 bytes, HTML (the row URL is the blob page, not the .rst; an earlier fetch gave 202667 bytes, so the page renders dynamically)
  -> counter declares controls=76 families=28
getconf CLK_TCK                                  -> 100 (one tick = 10 ms)
sha256sum /usr/bin/python3.14                    -> 375532f8… (the demo's holder digest)
git show f6a4ea9a8b5a876d685b08e7e582ec0723412a4a:tools/round64-c1-counter.py | sed -n 48,49p
  -> MODEL_SHA 270cba1b…, SERVER_SHA b6a31a8e…
git show f6a4ea9a8b5a876d685b08e7e582ec0723412a4a:tools/round64-c1-counter.py | sed -n 289,296p
  -> rest[1] is field 4 (ppid), rest[19] is field 22 (starttime)
python3 .ufo/waves/round-64/b/out/SB01Knowledge/procfs-demo.py
  -> 60 sleep children: distinct starttime ticks 2, 1, 2 (procfs-demo.run{1,2,3}.out); 3, 2, 3 in unsaved runs of the same script
  -> runtime-set variable visible in /proc/self/environ: False (all three saved runs)
```

## Opinion (marked where it appears)

- No single observation identifies a process; the conjunction of steps 1-5, with each limit read beside its check, is the binding.
- argv is corroborating, not identifying.
- The tick comparison in `hold_fresh` should be read as weak support; ancestry carries the ordering.
- A stronger mapped-file check compares `dev:inode` from the maps line with a stat of the path.
