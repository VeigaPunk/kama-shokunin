# SC01ProcFd — Round 64 wave b — reopen S529 (Linux proc_pid_fd(5))

Seat: SC01ProcFd (leaf, no subagents). Axis served: operability (C1 sourcing) + calibration (row-vs-page fidelity).
Source item: independently re-open https://man7.org/linux/man-pages/man5/proc_pid_fd.5.html and decide whether
`corpus/SOURCES.md` row S529 states only what the page says; record access date, man-pages version line, the
≤25-word quote backing `teaches` with location; flag overreach; locate the hidepid / ptrace-access-mode caveat
for reading another process's fd table on this page or on proc(5) and quote it.

## Access record

- Access date: **2026-10-28** (raw HTML fetched via `curl` into my scratch; same page also read through the
  reader view earlier the same day).
- Version line (page footer): **`Linux man-pages 6.19            2026-02-08                 proc_pid_fd(5)`**
  Colophon: page obtained from `man-pages-6.19.tar.gz` (mirrors.edge.kernel.org) on 2026-09-09; HTML rendering
  created 2026-09-09.
- Byte pin verified: live fetch sha256
  `3a50ddef6f2f3a4f1139dcef3299a5eadf8fc96514df9fcb329a3bffd47ff27e` = the sha the row's anchor pins, and
  byte-identical to the retained snapshot
  `.ufo/waves/round-64/source/proc_pid_fd.html` (same hash). Row anchored to live bytes, 2026-10-28.
- proc(5) (fetched for the caveat check): footer `Linux man-pages 6.19 2026-02-08 proc(5)`; live sha256
  `b197c5fa64577269f992d50f60acfd5e0cc3df756644ddd8bd19a02591272a97` (no pin claimed by any row I checked).

## What the live page says (§DESCRIPTION, /proc/pid/fd/)

- One entry per open file, named by fd, a symbolic link to the actual file (0/1/2 = stdin/stdout/stderr).
- Pipes and sockets: symlink content is `type:[inode]`, e.g. `socket:[2248868]`; a `readlink(2)` call returns
  that string.
- "For sockets, that inode can be used to find more information in one of the files under `/proc/net/`."
- Inode-less fds (bpf, epoll, eventfd, inotify, perf_event, signalfd, timerfd, userfaultfd): symlink content
  `anon_inode:file-type`, often bracketed (e.g. `anon_inode:[eventpoll]`).
- Multithreaded process: directory contents unavailable if the main thread has terminated.
- `/proc/self/fd/N` ≈ `/dev/fd/N`; `/dev/stdin|stdout|stderr` symlink to 0/1/2.
- Access-control sentence (see §Caveats below).
- Pipe/socket inodes keep their own permission bits and ownership, which may differ from the process's
  ids; unprivileged processes may be unable to open them (`sudo -u nobody cat /proc/self/fd/0` →
  `Permission denied` example).
- SEE ALSO: `proc(5)`.

## Teaches quote (≤25 words, 22 words)

> "For file descriptors for pipes and sockets, the entries will be symbolic links whose content is the
> file type with the inode."

Location: §DESCRIPTION, `/proc/pid/fd/` subsection, second paragraph (the `readlink(2)` format paragraph),
Linux man-pages 6.19 (2026-02-08). The very next sentences give the `socket:[2248868]` example and the
/proc/net pointer.

## Row S529 as written vs the page (column-by-column)

Row (registry columns `id|source|kind|tier|scope|anchor|teaches|status|opened|recheck|used-by`):

- **scope**: "how a process's open socket reads under `/proc/<pid>/fd/<n>` so a listener inode from
  `/proc/net/tcp` can be joined to every process that holds it; Linux only; not an access-control model
  (an unreadable fd table is an observation limit, not an absence)"
- **anchor**: "§DESCRIPTION, Linux man-pages 6.19 (2026-02-08); fetched bytes sha256 3a50ddef…f27e retained
  at `.ufo/waves/round-64/source/proc_pid_fd.html`"
- **teaches**: "A socket fd links as `socket:[inode]`, so the counter can list every holder of the run-port
  listener from procfs without trusting a pid the tool reports"

Field check:

| Row claim | Page support | Verdict |
|---|---|---|
| "a process's open socket reads under `/proc/<pid>/fd/<n>`" | readlink returns `socket:[inode]` | stated |
| "a listener inode from `/proc/net/tcp` can be joined to every process that holds it" | page states the join key (same inode in the fd symlink and under `/proc/net/`) and per-process fd listings, but only the **forward** direction: "that inode can be used to find more information in one of the files under `/proc/net/`" | join key stated; reverse-join + enumeration **inferred**, see Flag 1 |
| "Linux only" | Linux man-pages describing Linux procfs | stated |
| "not an access-control model (an unreadable fd table is an observation limit, not an absence)" | page's PTRACE_MODE_READ_FSCREDS sentence + inode-permission example show the table can be unreadable; page teaches no access-control model | correctly bounded; consistent |
| anchor "§DESCRIPTION, Linux man-pages 6.19 (2026-02-08)" | matches footer verbatim | stated |
| anchor sha256 | recomputed today from live bytes; matches pin and retained copy | verified |
| teaches "A socket fd links as `socket:[inode]`" | page verbatim (format + example) | stated |
| teaches "the counter can list every holder … without trusting a pid the tool reports" | application clause; enumeration is the counter's construction, not page text — permitted by this table's `teaches` convention (S530–S532 likewise embed counter use), and it does not claim the page says it | inference, bounded; see Flags 1–2 |

## Overreach flags

- **Flag 1 (direction + enumeration).** The page gives fd → `/proc/net` ("that inode can be used to find
  more information in one of the files under `/proc/net/`"); the row uses the same key in reverse
  (`/proc/net/tcp` listener inode → every holding process). The reverse join follows from the page's
  structure (every process's fd dir is listed the same way) but is nowhere stated, and "every holder" is
  the counter's procedure. Severity: mild — the `teaches` column attributes the enumeration to the counter,
  and the scope's own caveat covers its failure mode. Page-only wording would be "joined to holders via
  each process's fd listing".
- **Flag 2 ("every" is conditional).** Completeness of "every holder" presupposes a readable fd table for
  each candidate pid; both pages document conditions where it is not (§Caveats). The row already carries
  this as "an unreadable fd table is an observation limit, not an absence" — accurate, no change needed.
- No other overreach found: the row claims no timing semantics, no hidepid mechanics, no permission model
  beyond the disclaim, nothing the page contradicts.

## Caveats for reading another process's fd table (as asked)

- **On proc_pid_fd(5) itself** (§DESCRIPTION, after the `/dev/stdin` paragraphs; raw lines 136–138):
  > "Permission to dereference or read (readlink(2)) the symbolic links in this directory is governed by a
  > ptrace access mode PTRACE_MODE_READ_FSCREDS check; see ptrace(2)."

  (23 words.) This is the ptrace-access-mode caveat: reading another process's fd symlinks is
  capability/credential-gated per ptrace(2)'s PTRACE_MODE_READ_FSCREDS.
- Complementary, same page: pipe/socket inodes keep their own ownership and permission bits, "and that the
  owner may differ from the user and group IDs of the process. An unprivileged process may lack permissions
  to open them" — with the `sudo -u nobody cat /proc/self/fd/0` → `Permission denied` example.
- **On proc(5)** (§Mount options, man-pages 6.19 2026-02-08): the hidepid caveat, **not** on the fd page:
  > "hidepid=n (since Linux 3.3) — This option controls who can access the information in /proc/pid
  > directories."

  hidepid=1: "Users may not access files and subdirectories inside any /proc/pid directories but their
  own"; hidepid=2: other users' `/proc/pid` directories "become invisible"; `gid=` members "behave as
  though /proc was mounted with hidepid=0".
- Net: the fd page states the per-symlink ptrace gate; proc(5) states the mount-wide hidepid gate. The row
  carries a one-line disclaim instead of citing either, which is faithful; if the lane ever wants the
  mechanism named in the row, the ptrace sentence is the one on this exact page.

## Verification exercised

- Live raw fetch of both pages (curl, 2026-10-28); sha256 of fd page recomputed and matched to the row pin
  and the retained snapshot; hashes above. Reader-view read of the fd page matched the raw bytes' text.
- No code run against the lane; no clone needed (no counter, no commit). No tools installed (curl,
  sha256sum, coreutils preexisting); pacman untouched.
- Receipts: raw HTML copies at `.ufo/waves/round-64/b/out/SC01ProcFd/proc_pid_fd.html` and `proc.5.html`.

## Unresolved

- None material to the item. The fd page's ptrace sentence delegates the access-mode definition to
  ptrace(2); not opened — the caveat the item asked for is fully stated on the two named pages.
- Observation (out of scope, one line): row S529 `used-by` is `—` while the round-64 freeze says C1 "rests
  on S529-S532"; the column may be filled at integration.

Confidence: high (byte-pinned page, all row clauses checked against fetched text).
