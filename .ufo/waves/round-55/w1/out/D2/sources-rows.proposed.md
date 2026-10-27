# Source rows the proposed entry would cite

No new `S###` row is opened by this proposal. Every mechanism statement in
`counter-hardening-legs.proposal.md` maps to a row already in `corpus/SOURCES.md`
at the lane tip (`8abadfed`), open with a committed copy beside its round, tier A or B.
KQ6 requires engine/spec + revision + section + opened row; each line below names the
section used and where the copy is.

| Row | Tier | Section / anchor used | Opened copy | Used for |
|---|---|---|---|---|
| S506 | A | `proc_pid_mem(5)` §DESCRIPTION, man-pages 6.19, page dated 2026-02-08 | `.ufo/waves/round-53/c1/proc_pid_mem.5.txt` | the memory read that makes the `code` leg compare running bytes, not a file at a path |
| S507 | A | `ptrace(2)` §/proc/sys/kernel/yama/ptrace_scope value 1, man-pages 6.19, page dated 2026-06-05 | `.ufo/waves/round-53/c1/ptrace.2.txt` | why the counter (the replay's ancestor) may open `/proc/<pid>/mem`, and why a non-descendant observer may not; scope 2/3 fails closed |
| S508 | A (rejected) | `proc_pid_map_files(5)` §DESCRIPTION | `.ufo/waves/round-53/c1/proc_pid_map_files.5.txt` | cited only as the *refused* alternative means of reading each mapped file (needs CAP_SYS_ADMIN/CAP_CHECKPOINT_RESTORE) — the entry must not present it as a method |
| S500 | A | `memfd_create(2)` §DESCRIPTION, §HISTORY | `.ufo/waves/round-52/c1/memfd_create.2.txt` | the sealed image that `code_observe` admits as the server's own (a `/memfd:` link, no path) |
| S501 | A | `F_GET_SEALS(2const)` §DESCRIPTION | `.ufo/waves/round-52/c1/F_GET_SEALS.2const.txt` | seals are an inode property, so the observer's own open sees the seals the replay set |
| S502 | A | kernel `mfd_noexec` §Sysctl (linux-next next-20261026) | `.ufo/waves/round-52/c1/mfd_noexec.txt` | the host limit: at `vm.memfd_noexec=2` a replay cannot run a memfd server at all |
| S509 | A (code) | `ggml/src/ggml-backend-reg.cpp` @ tag b11909, lines 401 / 480 / 488-489 / 491 | `.ufo/waves/round-53/c1/ggml-backend-reg.cpp.b11909` | libraries/backends load by path from the executable's directory and the current directory, so a frozen host-library set and a by-basename binding are needed (and bounded) |
| S510 | B | `git(1)` §Documentation/git.txt `codeGITDIRcode` | `.ufo/waves/round-54/sources/git-docs-git.html` | `GIT_DIR` names a foreign repository and turns off discovery — why every git call is env-stripped |
| S511 | B | `git-config(1)` §GIT_CONFIG_COUNT | `.ufo/waves/round-55/sources/git-docs-git-config.html` | `GIT_CONFIG_COUNT`/`KEY_n`/`VALUE_n` inject runtime config (e.g. `core.hooksPath`) into the counter's own `git commit` |

Boundary notes for the corpus reviewer:

- S505 and S503/S504 are **not** cited: S505 is the superseded anchor (S509 carries
  the correction) and S503/S504 are rejected records for `fexecve`/`execveat`; none
  grounds a leg in this entry.
- The battery's `LD_AUDIT` result (the vector is void on this glibc, so no live kill
  exists for the `hostlibs` leg) is a **host observation with a receipt**
  (`.ufo/waves/round-55/c1/battery/m-ldaudit-foreign.out`), not a documented
  behaviour of any engine. If the lane later wants a row for glibc's audit interface,
  it must be opened and quoted like any other; the entry must not be read as citing
  one.
- All rows above were last re-read at their committed copies during this proposal; no
  live fetch was made and none is needed (KQ10: no census/probe for this entry).
