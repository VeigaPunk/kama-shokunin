# S176 git-grep source findings

## Behavior
Proposed one S176 row in `row.md` using the existing 11-column SOURCES shape. It limits the source claim to Git's tree-object blob search, `-F` literal matching, `-q` match status, and pathspec exclusion mechanics. The frozen C1 counter's Q check at `count-c1.py:260` invokes `git grep -F -q -e <span> W -- .` and uses `:(exclude)` pathspecs from lines 67–68. The row's `used-by` is the knowledge-entry path supplied by its author, `.ufo/waves/round-29/w1/out/ScribeKnowledgeEntry/self-assessment-at-writing.md`.

## Gates and evidence
- Fetched `https://git-scm.com/docs/git-grep` with `curl -sSfL --max-time 35` under `timeout 45s`; recorded UTC before/after `2026-10-23T12:02:41Z`; downloaded bytes SHA-256 `33803f943da8f3e6285e07422e2302a92ac7250df286a85a09ccaa7485236e5c`.
- Fetched `https://git-scm.com/docs/gitglossary` with the same curl/max-time and timeout bounds; recorded UTC before/after `2026-10-23T12:02:57Z`; downloaded bytes SHA-256 `3fa08dfd1ee99c6196e7b86f3fc11ebb47625879e2b05821384ccfc2e3d00262`.
- `git --version` returned `git version 2.56.0`. Web page metadata identifies git-grep as last updated in 2.55.0 with 2.56.0 marked no changes; gitglossary is last updated in 2.56.0. The captured local man pages have footers `Git 2.56.0` dated 2026-09-27.
- Read local `git-grep` and `gitglossary` manuals. The relevant local clauses match the fetched documentation: tree blobs, fixed strings, quiet match/no-match status, and pathspec exclusion behavior. The local glossary gives the short exclusion signatures `!`/`^` and explains that matched paths are ignored; the long-form `:(exclude)` is the corresponding magic word form.
- Gate quotes and their section locations are in `quote.txt` and `row.md`; each quote is verbatim from its saved HTML source and is under 25 words.

Exact commands and observed outcomes:

```sh
timeout 45s sh -c 'mkdir -p /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitGrep && date -u +"before=%Y-%m-%dT%H:%M:%SZ" && curl -sSfL --max-time 35 https://git-scm.com/docs/git-grep -o /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitGrep/page.html && date -u +"after=%Y-%m-%dT%H:%M:%SZ" && sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitGrep/page.html'
```
Observed: before/after `2026-10-23T12:02:41Z`; hash above.

```sh
timeout 45s sh -c 'date -u +"before=%Y-%m-%dT%H:%M:%SZ" && curl -sSfL --max-time 35 https://git-scm.com/docs/gitglossary -o /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitGrep/gitglossary.html && date -u +"after=%Y-%m-%dT%H:%M:%SZ" && sha256sum /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitGrep/gitglossary.html'
```
Observed: before/after `2026-10-23T12:02:57Z`; hash above.

```sh
timeout 15s git --version && timeout 20s sh -c 'man -P cat git-git-grep'
```
Observed `git version 2.56.0`; requested page name `git-git-grep` was not installed (`No manual entry for git-git-grep`, exit 16). The installed page is named `git-grep`.

```sh
timeout 25s sh -c 'man -P cat git-grep > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitGrep/installed-git-grep.man.txt'
timeout 25s sh -c 'man -P cat gitglossary > /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitGrep/installed-gitglossary.man.txt'
```
Both local manual outputs were read; the relevant local footers say `Git 2.56.0 2026-09-27`. Also observed `timeout 15s git --version && timeout 20s man -P cat git-grep` output `git version 2.56.0` followed by the installed git-grep manual.

## Touched surfaces
Created in the assigned output directory: `page.html`, `gitglossary.html`, `installed-git-grep.man.txt`, `installed-gitglossary.man.txt`, `row.md`, `quote.txt`, and this report. Created the requested advice report at `.ufo/waves/round-29/w1/advice/ScribeSrcGitGrep.md`. Read-only source inputs: `CORPUS.md`, `corpus/SOURCES.md`, and `.ufo/waves/round-29/count-c1.py`.

## Out of scope and limits
No tracked lane file was edited; S176 is a proposal for L1 integration, not an edit to `corpus/SOURCES.md`. No counter execution, tests, build, server, install, or commit was performed. Documentation here establishes Git command semantics only; it does not establish git-blame writing attribution, the counter's correctness, or the resulting C1 claim. The `used-by` path was supplied by the knowledge-entry author and is proposed, not represented as an already-integrated lane source row.