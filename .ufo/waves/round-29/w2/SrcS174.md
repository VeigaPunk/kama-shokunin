# SrcS174

**verbatim fail; length pass; anchor pass.** Access **2026-10-23T18:30:41Z**. Full write-up: `.ufo/waves/round-29/w2/out/kama-r29-w2-SrcS174-5/report.md`.

Opened `https://git-scm.com/docs/git-blame` (`curl -fsSL`, HTTP/2 200, `date: Fri, 23 Oct 2026 18:30:41 GMT`, `last-modified: Fri, 23 Oct 2026 13:46:13 GMT`, 82635 bytes, sha256 `9395727d7a1cf9a827d1521ab98fba435e78969307fbd272a7a257969dbb0d7c`). Page banner: `git-blame last updated in 2.56.0` (list entry 2026-09-28). Saved under the seat dir as `page.html`, `headers.txt`, `page.txt`.

Row: working-tree `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:186` (not in HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`; `git diff --numstat -- corpus/SOURCES.md` is `4 0`). `teaches` cell:

`git blame annotates each line using the revision that last modified it; --line-porcelain outputs commit information for each line, not only on the first reference to a commit.`

1. **Not verbatim.** Neither fragment, nor the whole cell, occurs in the raw HTML or in whitespace-normalized visible text (casefold included). Count 0.
2. **≤25 words each.** Fragment 1 is 12 words; fragment 2 is 7. The undivided `teaches` cell is 28 words.
3. **Anchor is right.** DESCRIPTION is `<h2 id="_description">` at `page.html:2143`. OPTIONS is `<h2 id="_options">` at `page.html:2183`. `--line-porcelain` is the dt at `page.html:2289` (`id="Documentation/git-blame.txt---line-porcelain"`). The cell paraphrases those two passages; it does not quote them.

Page text at those anchors:

- DESCRIPTION `page.html:2146-2147`: `Annotates each line in the given file with information from the revision which last modified the line.`
- OPTIONS `--line-porcelain` `page.html:2291-2293`: `Show the porcelain format, but output commit information for each line, not just the first time a commit is referenced. Implies --porcelain.`

Mismatches: no leading `git blame`; `with information from the revision which` / `the line` rather than `using the revision that` / `it`; verb is `output` not `--line-porcelain outputs`; `not only on the first reference to a commit` is absent (page says `not just the first time a commit is referenced`).

`git --version` is `git version 2.56.0`. Installed `man git-blame` matches those two page sentences, so the row's parenthetical is fair and still not a verbatim `teaches` cell. Wave-1 `w1/out/ScribeSrcGitBlame/quote.txt` kept shorter spans that do sit on the page (`last modified the line`; `commit information for each line, not just the first time a commit is referenced`).

Defect for the L1: S174's `teaches` cell is not a verbatim ≤25-word quote of the manual. No lane file was edited.
