# Lesson Gate entries — draft for `corpus/lessons/round-49.md` §Gate (seat S1Rows)

Drop-in replacement for the two table rows already in `corpus/lessons/round-49.md:21-22`. Both filed quotes are
verbatim; these rows add the S494 `/detokenize` caveat (defect F1 in `rows.md`) and the S495 hard-wrap note.
Columns match the existing table: `Row | Decision | URL | Opened (UTC) | Located quote (≤ 25 words) | Why`.

| Row | Decision | URL | Opened (UTC) | Located quote (≤ 25 words) | Why |
|---|---|---|---|---|---|
| S494 | admit (tier A, mined) | https://raw.githubusercontent.com/ggml-org/llama.cpp/caa8191df159f764fb0160e3d2fc6be008948aee/tools/server/README.md | 2026-10-26T23:11:45Z (copy `.ufo/waves/round-49/c1/server-README-caa8191d.md`, 2523 lines, sha256 `009af291…ac0c` = the live raw fetched again on 2026-10-26) | "The `tokens` array contains either just token IDs or objects with `id` and `piece` fields, depending on the `with_pieces` parameter." (§POST `/tokenize` → Response, line 700; 20 words) | the documented surface the witness challenges — `/tokenize` request **and** response. The README documents only the **request** option of `/detokenize` (lines 731-735), so the row's scope is narrowed to that; the response body the counter reads (`tools/round49-replay-witness-audit.py:284`) is in the same commit's `server-context.cpp:6293-6305`, not in this README. Pinned to b11909 = commit `caa8191d…` (`refs/tags/b11909` checked). The README's own example uses `tinyllama/stories260k` |
| S495 | admit (tier A, mined) | https://man7.org/linux/man-pages/man5/proc_pid_exe.5.html | 2026-10-26T23:11:45Z (text copy `.ufo/waves/round-49/c1/proc_pid_exe.5.txt`; man-pages 6.19, page dated 2026-02-08, colophon tarball `man-pages-6.19.tar.gz`) | "This symbolic link can be dereferenced normally; attempting to open it will open the executable." (§DESCRIPTION ¶1, copy lines 75-76; the page's hard wrap splits the sentence after "attempting"; 15 words) | grounds hashing `/proc/<pid>/exe` as the identity of the binary a listener runs, whatever wrapper or path started it — and, via the " (deleted)" clause at 78-80, after the path has been replaced. The scope leaves the ptrace access-mode paragraph (¶2) out |

Rejects: unchanged from the filed table. Both entries were re-opened live by seat S1Rows on 2026-10-26
(`rows.md` §1): raw README 200/126663 B sha256 `009af291…ac0c`; blob view 200; man page 200/8377 B; the man page's
footline reads `Linux man-pages 6.19  2026-02-08  proc_pid_exe(5)`.
