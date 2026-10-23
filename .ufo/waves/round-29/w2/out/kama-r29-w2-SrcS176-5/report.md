# SrcS176 — git-grep / gitglossary verification

Seat: `kama-r29-w2-SrcS176-5`. Lane file under check: `/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md` line 188 (uncommitted attempt-1 row). No lane file was edited.

**Verdict:** the four semantic claims hold against the live manuals. Two Gate fragments are verbatim. The short labels ("fixed string", "quiet exit status", "long form 'exclude'") and the SOURCES `teaches` cell are paraphrases. The token `:(exclude)` is not written on either page.

**Access (UTC):** latest pages `2026-10-23T18:30:32Z` (HTTP `Date: Fri, 23 Oct 2026 18:30:32 GMT`). Pinned pages `2026-10-23T18:31:36Z`–`2026-10-23T18:31:53Z`. Installed Git `2.56.0` (`git --version`). No tools installed.

## Verbatim vs paraphrase

### 1. git-grep searches blobs in given trees — holds; a verbatim sentence exists

Page: `https://git-scm.com/docs/git-grep`, saved at `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-29/w2/out/kama-r29-w2-SrcS176-5/git-grep.html`.

**Verbatim** (OPTIONS `<tree>...`, lines 2517–2518; substring `blobs in the given trees.` at source offset 76971):

> Instead of searching tracked files in the working tree, search blobs in the given trees.

15 words. This is the Gate quote in `corpus/lessons/round-29.md` line 102 and in `.ufo/waves/round-29/w1/out/ScribeSrcGitGrep/quote.txt`. It matches the saved HTML exactly.

**Also verbatim** (DESCRIPTION, lines 2190–2191; offset 45661): "blobs in given tree objects" inside "Look for specified patterns in the tracked files in the work tree, blobs registered in the index file, or blobs in given tree objects."

**Paraphrase:** the SOURCES `teaches` cell says "the given tree" (singular). The manual says "trees" / "tree objects" (`<tree>...`, one or more). Singular matches the counter's one-tree use, not the manual's wording.

Not this claim: `--cached` uses a parallel sentence, "search blobs registered in the index file" (the shared prefix starts at offset 46263).

### 2. `-F` fixed string — holds as paraphrase

**Verbatim** synopsis pairing: `-F` | `--fixed-strings` (`--fixed-strings` at offset 42021).

**Verbatim** body (lines 2334–2335, offset 58672):

> Use fixed strings for patterns (don’t interpret pattern as a regex).

The apostrophe is U+2019 (`&#8217;`), not ASCII `'`.

"fixed string" (singular) and the `teaches` wording "literal span" are paraphrases of "fixed strings" plus "don’t interpret pattern as a regex."

### 3. `-q` quiet exit status — holds as paraphrase

**Verbatim** synopsis pairing: `-q` | `--quiet` (`--quiet` at offset 43047).

**Verbatim** body (lines 2512–2513, offset 76467):

> Do not output matched lines; instead, exit with status 0 when there is a match and with non-zero status when there isn’t.

Again U+2019 in "isn’t".

"quiet exit status" and the `teaches` phrase "reports a match through exit status" compress that sentence. They keep the status channel and drop "Do not output matched lines" and the specific codes (0 vs non-zero).

### 4. Pathspec exclude, long form `exclude` — holds as a compositional reading, not a verbatim phrase

Page: `https://git-scm.com/docs/gitglossary`, saved at `.../out/kama-r29-w2-SrcS176-5/gitglossary.html`.

**Verbatim** long-form rule (lines 2807–2810, offset 77343):

> In the long form, the leading colon : is followed by an open parenthesis (, a comma-separated list of zero or more "magic words", and a close parentheses ), and the remainder is the pattern to match against the path.

**Verbatim** magic-word heading `exclude` (line 2908; source `>exclude <` at offset 82419; id `Documentation/gitglossary.txt-exclude`).

**Verbatim** body (lines 2910–2914; fragment at offset 82659):

> After a path matches any non-exclude pathspec, it will be run through all exclude pathspecs (magic signature: ! or its synonym ^). If it matches, the path is ignored. When there is no non-exclude pathspec, the exclusion is applied to the result set as if invoked without any pathspec.

**Verbatim fragment (Gate quote, 7 words):** "If it matches, the path is ignored." The pronoun is a path that matched an exclude pathspec, under the preconditions in the same paragraph. The fragment alone drops those preconditions.

**Not on either page:** the token `:(exclude)` (searched both latest HTML files; absent). The signatures written beside `exclude` are the short forms `!` and `^`. git-grep EXAMPLES (lines 2558–2560) shows the short form `git grep solution -- :^Documentation` ("Looks for solution, excluding files in Documentation."), not `:(exclude)`.

Calling `exclude` the long-form magic word is the section's structure: long form = magic words; the `top` entry says "The magic word `top` (magic signature: `/`)" explicitly, while the `exclude` entry gives only the signature. `:(exclude)` in the SOURCES `teaches` cell is that composition, plus the counter's argv, not a copied token.

Different feature, not this claim: git-grep `--exclude-standard` / `--no-exclude-standard` are `.gitignore` switches (lines 2225–2234).

## Version lines in the row (verbatim chrome)

On the latest git-grep page: "git-grep last updated in 2.55.0" (offset 17228); "2.56.0 no changes" (offset 17491). On the latest glossary page: "gitglossary last updated in 2.56.0" (offset 17973). These match the S176 anchor cell.

Supporting fetches, same day:

- `GET https://git-scm.com/docs/git-grep/2.56.0` returned a 593-byte HTML document (sha256 `dbd184dc1f2f4d81844af6fab21fca46f5cb4d24e08401d815b7778431e12b28`) whose canonical href is `http://git-scm.com/docs/git-grep/2.55.0` (client-side redirect). A separate `HEAD` of that URL returned `301` to `https://git-scm.com/docs/git-grep/2.56.0/`; the trailing-slash URL was not fetched.
- `GET https://git-scm.com/docs/git-grep/2.55.0` (sha256 `d8bb1ca54b3342f09a871cea8ff1aa438a43a5736dae8bfc6b69b5636737138e`, 87297 bytes): the four git-grep paragraphs above are equal to latest.
- `GET https://git-scm.com/docs/gitglossary/2.56.0` (sha256 `be37eb0249be1d45151dde761980ad6f1d91e5569359cc4aad1f2967034f33f2`, 109772 bytes): the long-form paragraph and the exclude paragraph are equal to latest.

Full-page bytes are not equal to the unversioned latest HTML. Installed `man git-grep` and `man gitglossary` (footers `Git 2.56.0` / `2026-09-27`, captured in this seat's out dir) contain the same clauses.

## Page identity

| URL | sha256 | bytes | Last-Modified |
|---|---|---|---|
| https://git-scm.com/docs/git-grep | `c7812f8f522c396164151dc215cda790aaa17b088a51cdd2cb8a1aef34803962` | 87426 | Fri, 23 Oct 2026 13:46:12 GMT |
| https://git-scm.com/docs/gitglossary | `eb521ce9552c3ffa8606fb4798c0585f124ecb492312cdd0e490e10aeaf0c835` | 109901 | Fri, 23 Oct 2026 13:46:14 GMT |

The wave-1 capture (2026-10-23T12:02:41Z / 12:02:57Z, sha256 `33803f943da8f3e6285e07422e2302a92ac7250df286a85a09ccaa7485236e5c` / `3fa08dfd1ee99c6196e7b86f3fc11ebb47625879e2b05821384ccfc2e3d00262`) is an earlier generation: Last-Modified is after 12:02Z and the full-page hashes differ. The cited `<p>` texts are equal between that capture and this fetch.

## Where the row says it

- `corpus/SOURCES.md:188` `teaches` cell is one paraphrase: `` `git grep -F -q -e <span> <tree> -- . :(exclude)...` searches blobs in the given tree for a literal span, reports a match through exit status, and omits paths matched by exclusion pathspecs. `` "Omits paths" paraphrases "the path is ignored" and drops the non-exclude precondition.
- Gate quotes in `corpus/lessons/round-29.md:102` and `.ufo/waves/round-29/w1/out/ScribeSrcGitGrep/row.md` are the two verbatim fragments above.
- `corpus/knowledge/self-assessment-at-writing.md:16` ("S176 documents tree-object blob search, these options, and pathspec exclusion") is a consistent paraphrase, not a quote.

## Not done

No `count-c1.py` run. Local man text was not an execution test of `git grep`. No package installs.

Confidence: high.
