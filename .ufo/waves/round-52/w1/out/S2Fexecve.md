# S2Fexecve — exec-from-descriptor source review

**Verdict: reject both pages as SOURCES rows for the precise claim that executing `/proc/<pid>/fd/<n>` of a memfd runs that file.** Both document descriptor-based exec semantics, but neither addresses the proc-fd pathname case, what `/proc/self/exe` or `AT_EXECFN` reports for it, or the close-on-exec behavior of a direct `execve` of that pathname. They are useful background, not evidence for those particulars.

## Evidence

Accessed 2026-10-27T05:11:08Z UTC.

- `https://man7.org/linux/man-pages/man3/fexecve.3.html` — fexecve(3), Linux man-pages 6.19. Located quote (17 words): “the file to be executed is specified via a file descriptor, fd, rather than via a pathname.” The page additionally says close-on-exec with a script can cause `ENOENT`, because the descriptor is closed before interpreter execution. This is specifically the `fexecve()` script case, not direct execution through `/proc/<pid>/fd/<n>`.
- `https://man7.org/linux/man-pages/man2/execveat.2.html` — execveat(2), Linux man-pages 6.19. Located quote (19 words): “If path is an empty string and the AT_EMPTY_PATH flag is specified, then the file descriptor dirfd specifies the file to be executed”. It explains the script + `O_CLOEXEC` failure (`ENOENT`) and `argv[0]` passed to a script interpreter (`/dev/fd/N` or `/dev/fd/N/P`), but not `/proc/self/exe` or `AT_EXECFN` for a memfd executable.

Observed source-row format: `corpus/SOURCES.md` table has 11 cells: `id | source | kind | tier | scope | anchor | teaches | status | opened | recheck | used-by` (header at line 11). Existing S500 is tier A but narrowly scoped to memfd creation, proc-fd link and seals (line 253); it does not establish exec path identity.

## Judgment and flip condition

**Reject; no 11-cell row proposed.** These general API manuals cannot substantiate the requested exact runtime claim or its procfs metadata implications. Flip to admit one or both only if a page explicitly documents execution of the proc-fd pathname (or the precise equivalent), including the resulting `/proc/self/exe` / `AT_EXECFN` behavior and relevant close-on-exec caveat; otherwise seek a source that does. No counter or runtime behavior was tested in this source-screening task.
