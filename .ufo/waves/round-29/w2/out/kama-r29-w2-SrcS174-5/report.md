# kama round-29 w2 — SrcS174: git-blame quote vs live manual

Seat: kama-r29-w2-SrcS174-5 · access 2026-10-23T18:30:41Z · Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin` (branch `master`, HEAD `513eba3ba51a142c9936553e3a85918345eb5c4c`, read-only). No lane file outside this seat's output was edited. No tools installed.

## Verdict

| check | result |
|---|---|
| fragment 1 verbatim on https://git-scm.com/docs/git-blame | **fail** |
| fragment 2 verbatim on that page | **fail** |
| each named fragment ≤25 words | **pass** (12 and 7) |
| anchor `DESCRIPTION`; `OPTIONS --line-porcelain` | **pass** (right sections; the cell text is not copied from them) |

The S174 `teaches` cell is a paraphrase of two real manual sentences. It is not a located verbatim quote. The whole cell is 28 words, so it also misses a single ≤25-word quote even though the two fragments the item names are each under 25.

## Row under test

Working tree only. `git grep -e '| S174 |' HEAD -- corpus/SOURCES.md` exits 1 (absent at `513eba3`). `git diff --numstat -- corpus/SOURCES.md` is `4 0` (four added lines, zero deletions). Row text, `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md:186`:

```
| S174 | Git git-blame manual — https://git-scm.com/docs/git-blame | docs | A | git blame's per-line last-modifying revision and --line-porcelain commit metadata for C1; not validation of C1's checks | §DESCRIPTION; OPTIONS §--line-porcelain; live manual opened 2026-10-23 (local Git 2.56.0; installed git-blame(1) has the same text) | git blame annotates each line using the revision that last modified it; --line-porcelain outputs commit information for each line, not only on the first reference to a commit. | mined | 2026-10-23 | on-release | corpus/knowledge/self-assessment-at-writing.md, .ufo/waves/round-29/count-c1.py |
```

Named fragments, whitespace-split:

1. `git blame annotates each line using the revision that last modified it` — 12 words.
2. `--line-porcelain outputs commit information for each line` — 7 words.

Full `teaches` cell (the text between those two bars): 28 words.

Wave-1's saved gate line was different and shorter. `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w1/out/ScribeSrcGitBlame/quote.txt`:

```
“last modified the line” (§DESCRIPTION) … “commit information for each line, not just the first time a commit is referenced” (OPTIONS, §--line-porcelain).
```

Those two spans do occur on the page. The integrated `teaches` cell does not reuse them.

## Page fetch

- Command: `curl -fsSL -D headers.txt -o page.html -w '...' https://git-scm.com/docs/git-blame`
- Local clock immediately before curl: `2026-10-23T18:30:41Z` (`date -u +%Y-%m-%dT%H:%M:%SZ`)
- Response: `HTTP/2 200`; `date: Fri, 23 Oct 2026 18:30:41 GMT`; `content-type: text/html; charset=utf-8`; `last-modified: Fri, 23 Oct 2026 13:46:13 GMT`; body 82635 bytes
- SHA-256 of saved body: `9395727d7a1cf9a827d1521ab98fba435e78969307fbd272a7a257969dbb0d7c`
- Banner on the page: `git-blame last updated in 2.56.0` (version list entry `2.56.0` / `2026-09-28`)
- Saved: `.ufo/waves/round-29/w2/out/kama-r29-w2-SrcS174-5/page.html`, `headers.txt`, `page.txt` (visible text)

Search of the raw HTML and of whitespace-normalized visible text (and the same text casefolded): count 0 for fragment 1, fragment 2, and the full `teaches` sentence. Substring probes in the normalized visible text:

| needle | offset |
|---|---|
| `git blame annotates each line using the revision that last modified it` | absent |
| `--line-porcelain outputs commit information for each line` | absent |
| `outputs commit information for each line` | absent |
| `using the revision` | absent |
| `revision that last modified` | absent |
| `Annotates each line in the given file` | present |
| `revision which last modified` | present |
| `output commit information for each line` | present (`output`, not `outputs`) |
| `not just the first time a commit is referenced` | present |
| `not only on the first reference` | absent |

## What the page actually says (anchors)

DESCRIPTION, `page.html:2143` `<h2 id="_description">`, first paragraph `page.html:2146-2147`:

> Annotates each line in the given file with information from the revision which last modified the line. Optionally, start annotating from the given revision.

That is the section the first fragment points at. It is not the fragment. Differences: no leading `git blame`; `with information from the revision which` rather than `using the revision that`; `the line` rather than `it`; extra `in the given file`.

OPTIONS, `page.html:2183` `<h2 id="_options">`. The option is a definition term under that list, `page.html:2289-2293`, anchor `id="Documentation/git-blame.txt---line-porcelain"`:

> `--line-porcelain`
> Show the porcelain format, but output commit information for each line, not just the first time a commit is referenced. Implies `--porcelain`.

That is the section the second fragment points at. It is not the fragment. The option name is the heading, not the start of the sentence; the verb is `output`, not `--line-porcelain outputs`; the row's continuation `not only on the first reference to a commit` does not occur. A later sentence under THE PORCELAIN FORMAT (`page.txt` line 479) says the `--line-porcelain` option can be used to output full commit information for each line. That is also not fragment 2.

So the anchor cell's locators (`§DESCRIPTION`; `OPTIONS §--line-porcelain`) are the right headings for the claims. The `teaches` wording is a rewrite of those two passages.

## Local manual (row parenthetical only)

`git --version` → `git version 2.56.0`. `man -P cat git-blame` DESCRIPTION and `--line-porcelain` carry the same sentences as the page (groff wraps and hyphenates; the words match, including `Implies --porcelain`). The row's claim that installed `git-blame(1)` has the same text holds for these two passages. It does not make the `teaches` cell verbatim.

## Defect to leave for the L1

Do not treat S174's `teaches` cell as a ≤25-word verbatim quote of the git-blame manual. Either put the page's own spans back (the wave-1 quote file already has two that sit inside DESCRIPTION and OPTIONS `--line-porcelain`), or label the cell as a paraphrase. No other lane file was changed by this seat.
