source: S529 — Linux proc_pid_fd(5), https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html; S530 — Linux proc_pid_stat(5), https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html; S531 — Linux proc_pid_environ(5), https://man7.org/linux/man-pages/man5/proc_pid_environ.5.html; S532 — Linux proc_pid_cmdline(5), https://man7.org/linux/man-pages/man5/proc_pid_cmdline.5.html; S533 — Linux proc_pid_status(5), https://man7.org/linux/man-pages/man5/proc_pid_status.5.html (added by this revision: the `bind_trace` / `bind_state` observations); S534 — Linux namespaces(7), https://man7.org/linux/man-pages/man7/namespaces.7.html (added by this revision: the `bind_ns` observation); held: S049 — Linux kernel Documentation/networking/proc_net_tcp.rst @ v7.2, https://github.com/torvalds/linux/blob/v7.2/Documentation/networking/proc_net_tcp.rst (its raw bytes: https://raw.githubusercontent.com/torvalds/linux/v7.2/Documentation/networking/proc_net_tcp.rst); S495 — Linux proc_pid_exe(5), https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html; S496 — Linux proc_pid_maps(5), https://man7.org/linux/man-pages/man5/proc_pid_maps.5.html; S499 — Linux proc_pid_exe(5) (same page as S495, recheck 360d).
verified-at: 23b3fdb1a925129a9961cf551f6d40bf251602cb (2026-10-30) — every man page re-fetched with curl on 2026-10-30 (man-pages 6.19, footer date 2026-02-08) and every quote checked by `recheck-quotes.py` (31/31 OK: 23 man-page quotes, 2 namespaces(7) quotes, 2 S049 quotes from the raw kernel doc, 4 held text copies of S495/S496 read at this commit); fetched bytes also under `.ufo/waves/round-64/source/` (see "Fetched bytes"). The counter and the tool were read with `git show` at this commit; `tools/kama-completion-live.py` is byte-identical to the freeze commit (sha256 a0c26e14184d664bef75013aac6f1c2a7bb47881eb4bf372b5bb70a26861423c at 23b3fdb1 and at f6a4ea9a). Every counter line number below was re-derived at this commit by the `recheck:` command. The one live counter run cited below is the only counter result this entry records; the round's verdict is not this entry's.
recheck: on-release, and every 90 days. `python3 .ufo/waves/round-64/f/out/SB04KnowledgeRevise/recheck-quotes.py` must print `quotes OK=31/31`; `git show 23b3fdb1a925129a9961cf551f6d40bf251602cb:tools/round64-c1-counter.py | grep -n -E '^def (listeners|holder_pids|holder_record|collect|grade_binding|witness_run|score|reference_run)'` must print the line numbers cited below (250, 270, 391, 434, 470, 760, 932, 999, in the order the command prints them; it also prints `score_run` at 1869, because the pattern's `score` is a prefix of it). A changed quote or moved line restarts this entry.

# Process-bound listener: which process answers on a port (Linux)

## Claim

A port number says nothing about who answers on it. A verifier that wants to write "the process answering on port P is the pinned `llama-server` at digest D" needs these observations, each read from `/proc` on Linux:

1. the listening socket's inode, from `/proc/net/tcp` and `/proc/net/tcp6` (S049) — step 1;
2. every *readable* process holding that inode, from `/proc/<pid>/fd/*` (S529), and every process whose fd table could *not* be read (S529's permission clause), of any uid — step 2; the unreadable tables of processes that started **before** the tool are counted but not graded (step 2), so the holder claim covers the readable holder set plus the unreadable tables of processes the tool started, not an unconditional every-process guarantee;
3. for each holder, the executable (`/proc/<pid>/exe`, S495/S499) — step 3;
4. the exact argv (`/proc/<pid>/cmdline`, S532), the environment (`/proc/<pid>/environ`, S531), the namespaces (`/proc/<pid>/ns/*`, S534), the trace and run state (`/proc/<pid>/status`, S533) and the mapped files (`/proc/<pid>/maps`, S496) — step 4;
5. the holder's parent and start time (`/proc/<pid>/stat` fields 4 and 22, S530), to order it after the tool that claims to have started it — step 5;
6. the holder's exit, observed by the verifier after the verifier itself releases the hold — step 6;
7. agreement of the held process's answers with a second pinned server, which the verifier starts itself — step 7;
8. the receipt's own request and answer, equal to the request the verifier drew for this run and to that server's answer to it — step 8.

Steps 1–6 are the binding. Step 7 is a behaviour check and binds nothing (see its limits). Step 8 binds the *receipt* to *this run*.

*Opinion:* no single observation is enough. Each one can be satisfied by a forged process in some way (the limits below), so the verdict has to be the conjunction, and each conjunct should be read with its limit beside it.

## Why the binding exists: the round-63 failure

Round 63 bound the socket, not the process. Its counter bound the socket the tool reported, took the pid from the tool's own `hold.json`, and loaded its ownership helper from the tree under judgment. Two forged tools passed at 44/44:

- `forge-A-realchild.patch`: a canned answerer serves the run port from an inherited listener fd while the real child is also running;
- `forge-B-sleeper-delta.patch`: a sleeper process with no `llama-server` at all.

Evidence: `.ufo/waves/round-63/w1/out/MT15C1FakeConsistent/forge.out` and `sleeper.out`; each prints `met=True` on line 1 with `controls_targeted=44/44 eval_selftest=3/3 errors=0`. Commands: `git show f6a4ea9a8b5a876d685b08e7e582ec0723412a4a:.ufo/waves/round-63/w1/out/MT15C1FakeConsistent/forge.out | grep -n 'met='` and the same command with `sleeper.out`. The same failure is in `corpus/lessons/round-63-verifier-spotcheck.md` (section 6, C1).

## Step 1 — the listener inode

**Procfs.** `/proc/net/tcp` and `/proc/net/tcp6` list one socket per line; field 2 is the local address, field 4 the state, field 10 the inode. S049 (intro, lines 4-12) says these interfaces "are deprecated in favor of tcp_diag" and that the entry format is `46: 010310AC:9C4C 030310AC:1770 01` (its example, line 18). S049's row excludes state codes and IPv6 byte order, and the page states neither the state values nor the IPv4 byte order. The state `0A` (LISTEN) is what the counter uses and what the demo below observed. The IPv4 byte order is stated in code, not on the page (`tools/kama-llamacpp-live.py:619-626`, docstring: "IPv4 addresses use little-endian byte order").

**Kama reading.** `listeners()` (`tools/round64-c1-counter.py:250-268`) keeps every `0A` row whose port equals the run port, from both tables, and records whether the address is loopback (`_hex_loopback`, 240-248). `bind_listener` (counter 480-481) then requires every such listener to be loopback.

**Observed** (`procfs-demo.run1.out`, run on this host): a socket bound to a random loopback port produced one inode and was found in the `0A` state.

**Limits.**
- The reader is the file that S049 calls deprecated in favour of tcp_diag. A netlink reader would be a new source; none is held (S536 was rejected in `corpus/lessons/round-64.md`).
- Two readers, two address policies. The counter's `listeners()` keeps wildcard listeners and then fails `bind_listener`. The tool's `_listen_inodes()` (`tools/kama-llamacpp-live.py:619-639`) skips wildcard addresses on purpose ("fail-closed" in its docstring). A wildcard listener is therefore visible to the counter and invisible to the tool. Only the counter's view decides the verdict.
- Point in time. Listeners and holders are read separately and at different moments. The counter reads the whole snapshot twice (`raw_a`, `raw_b`, counter 1049 and 1054) and requires equal holder signatures (`bind_stable`, counter 846). The second read narrows the window; it does not close it.

## Step 2 — the holders, and the tables that could not be read

**Procfs.** `readlink /proc/<pid>/fd/<n>` on a socket returns `type:[inode]`, and "For sockets, that inode can be used to find more information in one of the files under /proc/net/." (S529, DESCRIPTION). Holders are every pid with an fd whose link equals `socket:[<inode>]`.

**Kama reading.** `holder_pids()` (counter 270-316) walks `/proc`, lists each `fd` directory and compares links to the wanted inodes. A `PermissionError` on the fd table is *recorded*, of **any uid** (counter 283-284): `scan()` returns `None` for an unreadable table regardless of owner. An unreadable table is re-read 4 times, 50 ms apart (counter 305-316), because a process in the middle of `execve` is briefly unreadable; only a table that stays unreadable is left in the set. `collect()` (counter 434-457) then splits the set: `unreadable_own` (452-454) keeps the pids whose start ticks are **at or after the tool's** — the name is a leftover from the pre-amendment code, which filtered by uid; the filter now is the start time — and `unreadable_old` (455) is the plain count of everything unreadable. `bind_holders` (483-486) fails when `unreadable_own` is non-empty.

**Observed** (`procfs-demo.run1.out`): before a fork, the listener had one holder (the reader). After `os.fork()` the child appeared as a second holder, with the same executable digest, because a child inherits a listening fd. This is the mechanism behind forgery A.

**Limits.**
- Permission. S529: "Permission to dereference or read (readlink(2)) the symbolic links in this directory is governed by a ptrace access mode PTRACE_MODE_READ_FSCREDS check". An fd table the reader cannot read is an observation limit, not an absence.
- **The pre-existing non-dumpable helper.** An own-uid helper that existed *before* the tool and holds a duplicate of the listener lands in `unreadable_old`, which is recorded and never graded (`grade_binding` reads only `unreadable_own`). Wave-b MT01 O3/O4 and MT08 f2 forged exactly that and were accepted at the freeze tip; the amended counter still filters on start time, so the case is not closed (`.ufo/waves/round-64/b/MT01DumpableHide.md`, `.ufo/waves/round-64/b/MT08HoldWindow.md` §2; acknowledged in `controls/freeze.txt` AMENDMENT 1, "Survivors acknowledged and NOT fixed"). *Inference from the code at this commit:* the amendment widened the recording to any uid but kept the start-time filter, so a pre-existing helper of any uid is still only counted.
- "In a multithreaded process, the contents of this directory are not available if the main thread has already terminated" (S529, DESCRIPTION). A read can fail for that reason too.
- The tool's own `_proc_holders()` (`tools/kama-completion-live.py:190-223`) silently skips any table it cannot read (`except OSError: continue`). Its `listener_holders` list can therefore be incomplete; the counter compares the tool's list with its own (`bind_claim`, counter 854).
- A holder set of exactly `{hold pid}` rules out a second *visible* holder. It says nothing about what that holder executes; that is steps 3-4.

## Step 3 — the executable and its digest

**Procfs.** "This symbolic link can be dereferenced normally; attempting to open it will open the executable." (S495, DESCRIPTION; S499 carries the same sentence). An unlinked executable reads with a suffix: "If the pathname has been unlinked, the symbolic link will contain the string ' (deleted)' appended to the original pathname." (S495). Reading the link is governed by "a ptrace access mode PTRACE_MODE_READ_FSCREDS check" (S495, S499).

**Kama reading.** `holder_record()` (counter 391-431) reads the link text (395) and hashes `/proc/<pid>/exe` itself (396); on any `OSError` both fields become `None` (397-398). `sha256_path()` (counter 180-191) hashes afresh on every call — the `cache` argument is accepted and ignored, the wave-b RV02 D9 path-keyed cache is gone. `bind_exe` (487-489) requires the link text to equal the server path the counter chose and the digest to equal `SERVER_SHA` (`b6a31a8e…`, counter 57).

**Why hash through the link.** S495 says opening the link opens the executable. The hash therefore covers the image the process runs, not whatever is at the path it was started from. (The "therefore" is kama's reading of that sentence.)

**Observed** (`procfs-demo.run1.out`): the python process's `exe` hashed to `375532f8…`, which is the digest of `/usr/bin/python3.14` (`sha256sum /usr/bin/python3.14`). Any holder that is not the pinned binary fails `bind_exe` by its digest, whatever its path or name.

**Limits.**
- A wrapper that `exec`s `llama-server` is judged as `llama-server`, because the wrapper is gone after `exec`. A wrapper that forks is judged by its child. Ancestry (step 5) is what separates the two cases.
- *Inference, not in S495:* for a script, the executable is the interpreter, so the digest names the interpreter.
- An unreadable link gives `None`, which fails `bind_exe`. That is fail-closed, and the same limit as step 2 applies.
- The digest pins the file on disk. It does not pin the bytes the process is executing from memory: a write into the live server's own mapping through `/proc/<pid>/mem` changes the served `system_fingerprint` without changing any file (wave-b MT05 F2, `.ufo/waves/round-64/b/MT05EnvInject.md` §2). Nothing in the counter reads `/proc/<pid>/mem`; the freeze lists this as an acknowledged, unfixed limit.

## Step 4 — argv, environment, namespaces, trace and run state, mapped files

These are weaker than step 3 because the process can change what they show. The amended counter (AMENDMENT 1, 2026-10-28) tightened all of them after wave-b findings.

**argv (S532).** "processes have the freedom to override the memory region and break assumptions about the contents or format of the /proc/pid/cmdline file." And: "Think of this file as the command line that the process wants you to see." Kama reading: `holder_record()` splits the file on NUL and drops empty arguments (counter 400-404), then `bind_argv` (496) requires the **whole list to equal** `expected_argv()` (553-558): `[server_path, '--model', model_path, '--alias', ALIAS, '--port', str(port), '--host', '127.0.0.1', '-c', '512', '-t', '1']` — the exact list the tool builds (`tools/kama-completion-live.py:301-304`, whose `--ctx`/`--threads` defaults are 512/1 at 646-647). The model's digest is checked in the same conjunct (`sha256_path(model_path) == MODEL_SHA`, counter 56). The earlier four-flag check was replaced by this exact comparison after wave-b MT04 and RV02 D2 (a trailing `-m` copy, `--load-mode none`, extra flags all passed).

*Opinion:* argv is corroborating, never identity. `argv[0]` is the first thing a rewrite changes, so `bind_exe` carries the identity; the exact-list rule makes argv a *shape* check, not an identity check.

*Limits.* The comparison is against the list the counter believes the tool used, so a tool that changed its default flags would fail `bind_argv` (a false reject, not a false pass). A process that rewrites its own argv area is still the pinned binary by `bind_exe`; wave-b MT04 A3 passed the old check on that route and is now refused only by `bind_exe`/`bind_maps`, not by `bind_argv`.

**Environment (S531).** "This file contains the initial environment that was set when the currently executing program was started via execve(2)." And: "If, after an execve(2), the process modifies its environment (e.g., by calling functions such as putenv(3) or modifying the environ(7) variable directly), this file will not reflect those changes." Kama reading: `holder_record()` parses the file into a key/value dict (405-415); `bind_env` (503-504) is now an **allowlist with values**: every key the holder shows must be one of the counter's own `PATH`, `HOME`, `LANG`, `LC_ALL` values (`TOOL_CHILD_ENV`, 162; `expect_env`, counter 449-450) *and carry the same value*. The old denylist (`LD_*`, `GLIBC_TUNABLES`) is gone; wave-b MT05 F3 (an extra non-`LD_` key) and RV02 D2 (an `LLAMA_ARG_*` override) passed it.

*Limits.* Only the initial environment is visible (S531): a `putenv` after `execve` that relocates the block is not in the file, so a runtime-added variable is outside the allowlist check. Wave-b MT05 §3(d) measured the converse: the file is live memory, so a *same-length in-place* rewrite of the block does show (their F4 was killed by `bind_env`); a value-only edit (F5) passed the old key-only check and is now caught by the value comparison. *Inference from the code:* an empty environment would satisfy `bind_env` vacuously (`all()` over no keys). The tool's own filter also allows `LD_LIBRARY_PATH`, `LLAMA_ARG_THREADS` and `XDG_CACHE_HOME` (`tools/kama-completion-live.py:322-323`), but the counter hands the tool only `PATH`, `HOME`, `LANG`, `LC_ALL`, `TMPDIR` (`_TOOL_ENV_KEYS`, 159; used at 1013), so the child inherits only the four.

**Namespaces (S534).** "If two processes are in the same namespace, then the device IDs and inode numbers of their /proc/pid/ns/xxx symbolic links will be the same" (S534, §The /proc/pid/ns/ directory); "Each process has a /proc/pid/ns/ subdirectory containing one entry" (same section). Kama reading: `ns_of()` (382-389) reads the six links `mnt`, `pid`, `net`, `user`, `ipc`, `uts` (`NS_NAMES`, 379) of a pid; `collect()` takes the counter's own six (`self_ns`, 448); `bind_ns` (505-506) requires the holder's six to equal the counter's. This closed wave-b MT05 F1/F8 (a private mount namespace and a user namespace with its own `/etc` and `ld.so.preload`).

*Limit.* The check is "same as the counter", not "the pinned namespace". A process that unshares into a copy of the counter's namespaces is equal to it. *Inference:* the check cannot see namespace contents, only identity.

**Trace and run state (S533).** "TracerPid  PID of process tracing this process (0 if not being traced)." and "State Current state of the process. One of "R (running)", "S (sleeping)", "D (disk sleep)", "T (stopped)", "t (tracing stop)", "Z (zombie)", or "X (dead)"." (S533, §DESCRIPTION). Kama reading: `holder_record()` reads `/proc/<pid>/status` and parses `State:` and `TracerPid:` (416-424); `bind_trace` (507-508) requires `TracerPid == 0`; `bind_state` (509-510) requires the state letter to be one of `S`, `R`, `D`. Both are re-graded on the second snapshot (`score`, 841-844). This closed wave-b MT05 F6 (a `PTRACE_SEIZE` tracer) and MT03 (c) (a `SIGSTOP`ped real child).

*Limits.* A tracer that has already detached, or a `SIGSTOP`ped process resumed between the two snapshots, is not seen: the state is a letter at two instants, not a history. A process stopped and resumed inside the window passes. *Inference from the code:* `bind_state` accepts `D` (disk sleep) and `R` (running) besides `S`.

**Mapped files (S496).** "dev is the device (major:minor); inode is the inode on that device." And: "The pathname field will usually be the file that is backing the mapping." Kama reading: `read_maps()` (341-367) keeps each distinct pathname with its `dev` and `inode` columns, and hashes the file only when its realpath lies under the server directory (361-364). `maps_ok()` (512-535, graded at 536) rejects any `(deleted)` mapping (518-519), skips pseudo-paths (`[heap]`, `[vdso]`) and anonymous mappings (520-523), skips `/usr/lib/`, `/lib/`, `/usr/lib64/`, `/lib64/` and `/etc/ld.so.cache` by path (`SYSTEM_PREFIXES` and `SYSTEM_FILES`, 150-151, used at 524-525), accepts the model path itself (527-528), and requires every other file under the server directory to match `LIBS` by basename and digest (530-532).

**Reference-file identity (new, AMENDMENT 1a).** Path plus digest was not enough: wave-b seat MT06MapsLib (result in `.ufo/waves/round-64/b/b-results.json`; that seat wrote no report file) had **6 of 9** library/model forgeries pass the freeze-tip counter — a1 a model path bind-mounted with other bytes inside the server's mount namespace, a2 the model swapped on disk (new inode), a4 a byte-identical copy of the model at a new inode, b2 the model rewritten in place after load with neutral bytes, c `libllama-cli-impl.so` (a `LIBS` member the pinned server never loads) dlopen-injected, and d a `/usr/lib` file shadowed by a bind mount. The amended counter adds `bind_ref_files` (`score`, 835-840): the held child's file-backed mappings, as the sorted set of `(path, dev, inode)` (`file_set()`, 373-377), must equal the set the **counter's own reference server** maps (`REF_FILES`, captured from that server's `/proc/<pid>/maps` at `reference_run`, 957). A swapped, shadowed, copied or extra mapping differs in `dev`/`inode` even when its bytes are identical.

*Limits.* The comparison is with the counter's own reference server, so it pins the *file identities of the pinned build*, not the contents the process may have patched in memory (step 3's `/proc/<pid>/mem` limit): an in-place content change under an unchanged inode is not an identity difference. It is an equality of sets, so a mapping the held child has and the reference does not (or the reverse) fails — strict by design; *inference:* the two sets could differ for reasons unrelated to forgery (a lazily loaded library), which would fail a genuine run; the L1's three pre-wave-f receipts (`controls/c1-final-prewave-runs.txt`) and this seat's own run at this commit did not hit that. The reference is not an independent authority: it is another process of the same host, so a system-wide change that both processes see is outside the comparison.

**Limits of the maps check.**
- "will usually be" is a hint, not an identity; `bind_ref_files` is what closes the identity gap, and only for the file's path/dev/inode triple.
- System prefixes are trusted by path, not by digest (counter 150, 524-525) — wave-b RV02 D7, acknowledged and not fixed in the freeze. *At this commit* the shadowing case wave-b MT06 d measured is caught by `bind_ref_files` instead (the shadowed `/usr/lib` mapping differs from the reference's in `dev`/`inode`); what the exemption still leaves open is an **in-place content change** of a system-prefixed file, because such a file is not hashed and its inode does not change.
- S496: "0 indicates that no inode is associated with the memory region" — the anonymous case is the blank pathname; `maps_ok` skips it (counter 522-523).

## Step 5 — parentage and start time

**Procfs.** `/proc/<pid>/stat` fields are numbered in S530. Field (4) is ppid: "The PID of the parent of this process." Field (22) is starttime: "The time the process started after system boot." and "Since Linux 2.6, the value is expressed in clock ticks (divide by sysconf(_SC_CLK_TCK))." S530 marks some fields `[PT]` (fields 26-30, 35, 45-52 in the page) and says of them: "If the check denies access, then the field value is displayed as 0." Fields 4 and 22 are not `[PT]` in S530.

**Kama reading.** `stat_fields()` (counter 319-326) splits after the last `)`, so the list index is the field number minus three: `rest[1]` is field 4 and `rest[19]` is field 22. `ppid_chain()` (329-339) walks at most 8 parents. `bind_ancestry` (538-539) requires the tool's pid in every holder's chain. `hold_fresh` (544-549) requires the holder's starttime at or after the tool's (547-548, `>=`), the hold file's mtime later than the counter's own start time (545-546), an **upper** mtime bound of one second after the snapshot (546), and schema `kama-completion-hold/v1` (549). `pid_gone()` (971-987) treats a pid whose starttime differs, or whose state is `Z` or `X`, as gone; an unknown starttime is **not** gone (977-978: fail closed).

**Clock tick.** `getconf CLK_TCK` prints `100` on this host, so one tick is 10 ms.

**Observed** (`procfs-demo.run{1,2,3}.out`, run 2026-10-30, command `python3 .ufo/waves/round-64/f/out/SB04KnowledgeRevise/procfs-demo.py`): 60 `sleep 3` children started within a fraction of a second had 2, 2 and 1 distinct starttime values. The largest single group in one saved run was all 60 children in one tick. A variable set in the running python process with `os.environ[...] =` is not visible in `/proc/self/environ` (`runtime-set var visible in /proc/self/environ: False`, all three runs).

**Limits.**
- Resolution. Two processes started in the same tick have equal starttime and cannot be ordered by it. `hold_fresh` accepts equal values (`>=`, 547-548), so a holder started in the same tick as the tool passes the order check. *Opinion:* the ancestry check (`bind_ancestry`) is the order fact that does not depend on ticks; the tick comparison is weak, supporting evidence.
- Identity over time. Identity is the pair (pid, starttime), not the pid. `pid_gone()` reads a reused pid with a different starttime as gone. *Inference:* a reused pid with an equal starttime in the same tick cannot be told apart by these fields.
- Reparenting. *Inference from kernel reparenting, not in S530:* a holder whose tool has exited is reparented, so ancestry fails. That is a failure to observe, not proof of a detached process.

## Step 6 — teardown, observed by the verifier, and killing what it saw

The counter takes the hold: it writes `release` into the hold directory it created (counter 1071), then polls for 30 seconds (1075) until every recorded holder is gone (`pid_gone`) and `listeners(port)` is empty; the result is the `teardown_observed` check (857). The release file and the poll are kama's design; S529-S532 do not describe them.

**Kill on exit (new).** Every holder the counter saw is killed on the way out — `kill_if_same()` (989-997) sends `SIGKILL` only while the pid still carries the observed start ticks — and the tool's whole process group is killed with `os.killpg` (1097). The tool is started with `start_new_session=True` (1027) so the group is its own. This closes wave-b RV02 D5 (forged tools leaked pinned `llama-server` processes; the freeze records the leak and the fix).

*Limits.* The port check counts `LISTEN` sockets only, so a connection in another state does not count as holding the port. A zombie counts as gone (state `Z`), on the reading that a process's descriptors are released when it exits (*inference*, not on the held pages). A new listener on the same port that appears during the window makes the port look open, so the check fails rather than passing. **A holder that exists only after the release is invisible**: the two binding snapshots are taken strictly before the release (1049, 1054) and the teardown check is "the recorded holders are gone and the port closes"; wave-b CR03 §3.4 measured that case (K5) passing at the freeze tip, and the freeze lists it as an acknowledged, unfixed survivor. *Inference from the code at this commit:* the release/teardown ordering is unchanged, so the coverage boundary is the same.

## Step 7 — reference agreement (not a binding)

The counter starts its own copy of the pinned server on a free loopback port, with the same model, alias and flags (`reference_run()`, counter 932-968; `--model`, `--alias`, `--port`, `--host 127.0.0.1`, `-c 512`, `-t 1` at 937-939). It sends the same two probe requests to the held child and to the reference; `probe_fails()` (714-758) compares each answer, and `score()` (776-788) requires the two probes to differ from each other in `n_predict`/prompt (785-788).

**Probes.** `draw_requests()` (875-890) draws three requests per run — two outside probes for the held child and the request the counter tells the tool to send — each with a random prompt length, `n_predict` and seed, every prompt carrying the run nonce. The counter redraws (up to 8 times, 1819-1826) until the three reference answers are non-empty and pairwise distinct; that is the fix for the wave-b X08 flake (two probes drawing identical reference text).

**Limits.** Agreement shows the answers match a pinned server. It does not show that the answering process is that server. A forwarding proxy that relays to the reference would agree on every answer, which is why binding (steps 1-6) is a separate verdict. The counter's proxy control is credited to `bind_holders` (counter 1990). *Opinion:* the exact-body check `{"status":"ok"}` on `/health` (counter 947-948) is a shape check. **The sample is finite**: two outside probes plus the tool's own request, drawn from one generator — not an exhaustive agreement over prompts. Wave-b MT13 §1/§4 measured that the draw distribution, the status shape and the fingerprint shape have their own survivors (freeze-era results against the freeze-tip instrument, re-measured by nobody here); its 1,210 fuzz runs never exercised an end-of-sequence or stop answer.

## Step 8 — the receipt's own request and answer (new)

**Kama reading.** The counter tells the tool what to send: `witness_run()` passes `--prompt/--n-predict/--seed` to the tool (1022-1024) from the request it drew, and the tool's captured `request_body` must equal that request — `receipt_req` (811-815: prompt, `n_predict` and seed). The receipt's captured answer must equal the reference server's answer to the same request — `receipt_ref_text` (819-821) — and its usage must equal the reference's — `receipt_ref_usage` (823-826). The three names are the `RECEIPT_BIND` set (88).

This closes wave-b RV02 D1 and MT13: a genuine pinned child that replays an earlier run's receipt passed the freeze-tip counter 76/76, because the receipt's answers were never bound to this run.

*Limits.* The reference answers the counter's request, not the receipt's: if the tool altered the request on the wire, `receipt_req` fails and the run is rejected, which is the intended reading. The comparison is on text and token counts, not on the raw bytes; a receipt whose answer differs from the reference in whitespace is rejected (the check is exact equality).

## What the join cannot establish

- That the pinned binary behaves correctly. Digests pin bytes, not behaviour.
- Anything about a process the reader cannot read. An unreadable holder is an observation limit — and, for a holder that predates the tool, an ungraded one (step 2).
- Anything about the **bytes the pinned process is running**, only the bytes on disk: a write into the live server's memory through `/proc/<pid>/mem` is invisible to every check (wave-b MT05 F2; acknowledged in the freeze).
- Anything at an instant other than the snapshot, and nothing about the window between the counter's release and its teardown poll (step 6).
- Anything about files under the system prefixes, which are trusted by path (step 4).
- Anything about the environment the process changed for itself after `execve` (S531; step 4).
- That the tool's own bookkeeping is honest: the tool-side holder list is compared with the counter's (`bind_claim`), not graded as an artifact. Under the amended kill rule this is deliberate.

## Numbers and the command that produced each

Each value is printed by the command shown; the first block is `recheck-quotes.py`, which the `recheck:` line cites.

```
python3 .ufo/waves/round-64/f/out/SB04KnowledgeRevise/recheck-quotes.py
  -> quotes OK=31/31
  -> man-page digests (fetched 2026-10-30): fd 3a50ddef…, stat 0f04d789…, environ 93394d9e…,
     cmdline 1fc68168…, status 1596cd27…, exe 8c9bf02f…, maps 3a339496…, namespaces.7 f8e08716…
  -> S049 raw digest a4da3f43… (matches the row); S049 line of 'deprecated in favor' [8],
     'tcp6_seq_show()' [12], '46: 010310AC:9C4C' [18]
  -> counter declares controls=91 families=30
  -> counter line anchors at 23b3fdb1: listeners 250, holder_pids 270, stat_fields 319, ppid_chain 329,
     read_maps 341, file_set 373, ns_of 382, holder_record 391, collect 434, grade_binding 470,
     expected_argv 553, holders_signature 565, probe_fails 714, score 760, free_port 863,
     draw_requests 875, probe 892, reference_run 932, pid_gone 971, kill_if_same 989, witness_run 999
  -> check anchors: bind_listener 480, bind_holders 483, bind_exe 487, bind_argv 496, bind_env 503,
     bind_ns 505, bind_trace 507, bind_state 509, bind_maps 536, bind_ancestry 538, hold_fresh 544,
     receipt_req 815, receipt_ref_text 821, receipt_ref_usage 826, bind_ref_files 840,
     bind_stable 846, bind_claim 854, teardown_observed 857
getconf CLK_TCK                                  -> 100 (one tick = 10 ms)
sha256sum /usr/bin/python3.14                    -> 375532f8… (the demo's holder digest)
git show 23b3fdb1a925129a9961cf551f6d40bf251602cb:tools/round64-c1-counter.py | sed -n 56,57p
  -> MODEL_SHA 270cba1b…, SERVER_SHA b6a31a8e…
python3 .ufo/waves/round-64/f/out/SB04KnowledgeRevise/procfs-demo.py
  -> 60 sleep children: distinct starttime ticks 2, 2, 1 (procfs-demo.run{1,2,3}.out)
  -> runtime-set variable visible in /proc/self/environ: False (all three saved runs)
```

The one live counter run this entry cites (clone of the lane at 23b3fdb, unmodified counter, fresh `--work`):

```
cd <clone>/tools && python3 round64-c1-counter.py --repo <clone> --tip 23b3fdb1a925129a9961cf551f6d40bf251602cb --work <fresh scratch>
  -> tool_present=1 live_ok=1/1 controls_targeted=91/91 of 91 families_exact=1 missing_families=[]
     eval_selftest=8/8 errors=0 met=True families[bind=30/30 … receiptbind=4/4 … replay=1/1 …]
  -> exit 0, 75.52 s, empty stderr
```

## Fetched bytes

Fetched 2026-10-30 with `curl -sS -A 'kama-recheck/1'`, sha256 as in the block above; deposited under `.ufo/waves/round-64/source/` (`proc_pid_exe.5.html`, `proc_pid_maps.5.html`, `proc_net_tcp.v7.2.rst` are new there; `proc_pid_fd.html`, `proc_pid_stat.html`, `proc_pid_environ.html`, `proc_pid_cmdline.html`, `proc_pid_status_5.html`, `namespaces_7.html` were already present with identical digests). The same bytes are in `.ufo/waves/round-64/f/out/SB04KnowledgeRevise/source/` with `SHA256SUMS`.

## Opinion (marked where it appears)

- No single observation identifies a process; the conjunction of steps 1-6, with each limit read beside its check, is the binding.
- argv is corroborating, not identifying; the exact-list rule makes it a shape check.
- The tick comparison in `hold_fresh` is weak support; ancestry carries the ordering.
- The environment allowlist is only as good as the initial-environment view: a runtime `putenv` is outside it.
- `bind_ref_files` pins file identities of the pinned build, not the bytes the process is running from memory; comparing the maps line's `dev:inode` with a `stat` of the path is *not* a drop-in improvement — wave-b MT06 found `st_dev` ≠ the maps `dev` on this host's btrfs, which is why the implemented check compares the holder's set with the counter's own reference server's set instead.
- The recheck is a *membership* check: each quote is looked for in the whitespace-normalised text of the fetched page, the S049 line anchors and the counter line anchors are printed for the reader to compare, and the exit status follows the quotes only. A page that keeps the sentence but moves it would still pass.

## Round-64 wave-f addendum (2026-10-30) — every limit above was realized by a live forgery

The falsify wave attacked the amended counter at `23b3fdb1` with live forged tools; the
unmutated counter still printed `met=True` `91/91` in each case below. Each row is one
limit of this entry, demonstrated rather than inferred:

| Wave seat | Forgery | Which limit it realizes |
|---|---|---|
| `b/MT01`+`b/MT08`, re-realized `f/MT30` F3 | a pre-existing non-dumpable helper holds a `pidfd_getfd` duplicate of the child's LISTEN socket (`SCM_RIGHTS`) | Step 2: `unreadable_old` is recorded, never graded — "the case is not closed" |
| `f/MT22` b3 | a **root** daemon pre-started before the tool holds a second `::1:<runport>` listener; the counter's own snapshot prints TWO listeners on the run port and passes | Step 1: `bind_listener` requires loopback but not *oneness*; a second visible listener is not rejected |
| `f/MT22` (f) | the serving listener lives inside a user+net namespace the tool created; the counter's procfs tables are per-namespace and see nothing | Step 1: every `/proc/net/tcp*` observation is namespace-local |
| `f/MT23` (d) | the tool sends seed `4242` on the wire but writes the drawn seed into the receipt; temperature 0 makes the text seed-independent | Step 8: `receipt_req` grades the receipt's *self-report* of the request, not the wire bytes |
| `f/MT25` D_gap600 | the model is mapped lazily, so at both snapshots it is not file-backed in `/proc/<pid>/maps` | Step 4: `bind_ref_files` compares file-backed mappings only; a lazily-faulted mapping is invisible |

Also wave-f (amended counter): `f/RV08` — cleanup kills every holder of a tool-named port
(identity-checked, not ownership-checked) and `pid_gone` still conflates an unreadable
`/proc/<pid>/stat` with a vanished pid; `f/X11` — `bind_holders` flaked on 4 of 8 runs under
~40-seat host load (fails closed, `met=False`); `f/SB06` — counter mutants `m_live_status`
and `m_finish_gate` survive (dropping either failure from `probe_fails` keeps `met=True`),
so some named failures are not load-bearing in the verdict.

The binding steps 1-6 remain the right *shape*; the wave's lesson is that each step's
implementation is one observable short of its sentence, and the next instrument must
observe the wire (request bytes), the namespace set, and second-listener oneness
independently of the tool's receipt.
