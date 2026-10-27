# Proposed SOURCES.md rows for round 51 (seat N5Sources2)

Full proposed registry-row text. IDs S499/S500 suggested; renumber at integration.
Each was verified live 2026-10-26 (HTTP 200, quotes below fetched from the pages).

## P1

| S499 | Linux proc_pid_stat(5) — https://man7.org/linux/man-pages/man5/proc_pid_stat.5.html | docs | A | the ordered `/proc/<pid>/stat` fields a ppid-chain or liveness read relies on: (3) `state` (one char, includes Z zombie), (4) `ppid`, (22) `starttime` (clock ticks since boot); whether fields display valid information is governed by a ptrace access-mode check; Linux only; not other platforms, not a permission model | §DESCRIPTION, field list entries (3) state, (4) ppid, (22) starttime and the PTRACE_MODE_READ_VISIBILITY note; man-pages 6.19, page dated 2026-02-08 | "The fields, in order, with their proper scanf(3) format specifiers, are listed below." — so `state`, `ppid` and `starttime` have documented positions a counter can parse, grounding the tree-descent, liveness and pid-reuse checks of round-50 C1 |

Grounds: C1 `tree` (ppid chain), `env` parent lookup, `descendants`/`teardown` liveness and starttime reuse guard (round50-replay-bind-audit.py:234-306, 497-526).

## P2

| S500 | Linux inode(7) — https://man7.org/linux/man-pages/man7/inode.7.html | docs | A | what identifies a file to stat(2)/statx(2): `st_dev` names the filesystem's device (major+minor IDs), `st_ino` is unique only within a filesystem, so dev and inode together identify a file; Linux only; not a hardlink/NFS-renumber caveat catalog | §DESCRIPTION, `st_dev` and `st_ino` paragraphs; man-pages 6.19, page dated 2026-02-08 | "Each file in a filesystem has a unique inode number. Inode numbers are guaranteed to be unique only within a filesystem." — so a (dev, inode) match between a maps row and a stat() result proves same-file, which is the join round-50 C1's `mapped` check and the live tool's `model_mapping` rely on |

Grounds: C1 `mapped` check's stat()-side join (round50-replay-bind-audit.py:328-338) and the tool's O_NOFOLLOW fstat comparison (kama-llamacpp-live.py:704-713).

## Runner-ups recorded for the next source seat (not proposed)

- listen check: `proc_net_tcp(5)` does NOT exist on man7.org (404 verified). Nearest man page is proc_pid_net(5) (man5/proc_net.5.html — names tcp's `st` column only; no 0A code list, no tcp inode column, no tcp6, no `/proc/<pid>/fd` socket links). Full grounding needs kernel tcp4_seq_show (net/ipv4/tcp_ipv4.c, S048 precedent) plus proc_pid_fd(5) — two rows.
- open(2) O_NOFOLLOW (man2/open.2.html, 200) — grounds the tool-side symlink guard only.
- proc_pid_environ(5) (200) + Python `-I`/sitecustomize docs — grounds the env canary leg.
- git-rev-list(1) `--parents` output grammar — grounds C2's parent lists (counter:417-418).
