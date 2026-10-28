# Planned SOURCES.md flips (seat SB03LessonGate, wave b) — NOT APPLIED

Not applied. `corpus/knowledge/process-bound-listener.md` does not exist at draft time (checked: `ls corpus/knowledge/process-bound-listener.md` → no such file). The L1 applies these only after that file exists and cites the rows. Per KQ22 only the `status`, `recheck` and `used-by` cells may change; every other cell stays byte-identical, so `opened`, `teaches`, `anchor` and `source` are not touched.

| Row | Column | Old | New | Condition |
|---|---|---|---|---|
| S529 | status | queued | mined | knowledge file exists and cites S529 |
| S529 | used-by | — | corpus/knowledge/process-bound-listener.md, corpus/lessons/round-64.md | same |
| S530 | status | queued | mined | same |
| S530 | used-by | — | corpus/knowledge/process-bound-listener.md, corpus/lessons/round-64.md | same |
| S531 | status | queued | mined | same |
| S531 | used-by | — | corpus/knowledge/process-bound-listener.md, corpus/lessons/round-64.md | same |
| S532 | status | queued | mined | same |
| S532 | used-by | — | corpus/knowledge/process-bound-listener.md, corpus/lessons/round-64.md | same |
| S529-S532 | recheck | 180d | 180d (unchanged) | — |
| S508 | status | rejected | rejected (unchanged) | — |
| S508 | used-by | corpus/lessons/round-53.md | corpus/lessons/round-53.md, corpus/lessons/round-64.md | the round-64 gate restates the rejection |
| S049 | used-by | corpus/knowledge/loopback-listener-ownership.md, corpus/lessons/round-18.md | + corpus/knowledge/process-bound-listener.md | only if that file cites S049 (C1 names it as a held row) |
| S495 | used-by | corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-49.md | + corpus/knowledge/process-bound-listener.md | only if that file cites S495 |
| S496 | used-by | corpus/knowledge/llamacpp-loading-lifecycle.md, corpus/lessons/round-50.md | + corpus/knowledge/process-bound-listener.md | only if that file cites S496 |

Proposed new rows (L1 decides; not written here). Ids S533-S535 are the first free ids (last row S532). Each: `status rejected`, tier A, kind `docs`, `opened 2026-10-28` (local), `recheck` 360d, `used-by corpus/lessons/round-64.md`.

| Proposed id | Source | Teaches (rejection reason) |
|---|---|---|
| S533 | Linux proc_stat(5) — https://man7.org/linux/man-pages/man5/proc_stat.5.html | rejected: `btime` wall-clock conversion; no round-64 check uses it |
| S534 | Linux proc_pid_status(5) — https://man7.org/linux/man-pages/man5/proc_pid_status.5.html | rejected: PPid/CapEff/Uid not read by any round-64 tool or predicate conjunct |
| S535 | Linux sock_diag(7) — https://man7.org/linux/man-pages/man7/sock_diag.7.html | rejected: netlink listing not used; `/proc/net/tcp*` stays the counter's inode table (S049 deprecation is the stated limit) |

Not proposed: a row for candidate 5 (`proc_pid_cmdline` as identity). It is a claim, not a source; it is refused in the Gate's admit/reject table (candidate 5) and is excluded from S532's teaches column.

Check after applying: `python3 tools/sources-append-only.py --from <base> --to <tip>` over every commit that touches `corpus/SOURCES.md` in the round (KQ22), exit 0. Not run by this seat.
