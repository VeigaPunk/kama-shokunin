# ScribeSrcGitBlame

## Finding
The opened first-party git-blame manual says a line is annotated with information from the revision that last modified it. Its `--line-porcelain` option outputs commit information for every line (not only the first time a commit is referenced) and implies `--porcelain`. The frozen C1 counter docstring independently identifies W as the commit named by `git blame --line-porcelain <base> -- <file>` for the line (count-c1.py lines 7–10). This supports that narrow attribution contract; it does not validate C1's class checks or results.

## Source proposal
See `row.md` for the single proposed S174 row and Gate line; `quote.txt` preserves the two verbatim fragments, together 18 words. Access was 2026-10-23 at 12:02:48 UTC. The saved page SHA-256 is `c78da5c9b809721d7c32966f6b4127a5956923cdbef69f47a5c57fc22ed1ed0d`.

## Local manual and version
`git --version` reported `git version 2.56.0`. The requested `man -P cat git-git-blame` name produced `No manual entry for git-git-blame` and command exit 16. The alternate installed page `man -P cat git-blame` exists; its DESCRIPTION and OPTIONS §`--line-porcelain` contain the same relevant statements. The alternate manual output does not itself state a version; the local Git command reports 2.56.0. `/usr/share/doc/git` was not found.

## Exact commands and outcomes
1. `timeout 5 mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitBlame && timeout 30 curl -sSfL https://git-scm.com/docs/git-blame -o /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitBlame/page.html && timeout 5 sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitBlame/page.html && timeout 5 date -u +%Y-%m-%dT%H:%M:%SZ && timeout 5 git --version && timeout 20 sh -c 'man -P cat git-git-blame > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitBlame/installed-man.txt'` — fetch succeeded; SHA and timestamp above; Git 2.56.0; requested man name absent (exit 16).
2. `timeout 15 sh -c 'man -P cat git-blame > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitBlame/installed-man-alternate.txt'; timeout 5 git --version` — installed alternate man output captured; Git 2.56.0.

## Provenance, limits, contract note
Read `/home/vgpnk/Projects/shokunin/CORPUS.md` §“SOURCES.md — where a shokunin learns”, `kama-shokunin/corpus/SOURCES.md` header and S173, the round preregistration, C1 counter docstring, saved HTML, and captured local manual. The row follows the existing 11-column shape. The knowledge-entry draft `.ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md` is present and cites S174; it remains a wave output pending L1 integration. `used-by` lists that draft plus the explicitly requested direct C1 consumer `.ufo/waves/round-29/count-c1.py`; the latter is outside `CORPUS.md` §Shape's knowledge-entry/lesson path definition, so L1 should decide whether to retain it in the final row. The live online manual is not version-pinned; no row was integrated into tracked SOURCES.md. No C1 counter execution, rescore, tests, build, or product edits were performed. No tools were installed.

## Artifacts
`page.html`, `installed-man.txt` (empty after the absent-man error), `installed-man-alternate.txt`, `row.md`, `quote.txt`, and this report are under `.ufo/waves/round-29/w1/out/ScribeSrcGitBlame/`. Scoped handoff: `.ufo/waves/round-29/w1/advice/ScribeSrcGitBlame.md`.