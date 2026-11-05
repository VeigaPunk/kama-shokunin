# SC01SourceOpen — CommonMark 0.31.2 quotes (round-87 C1 calibration)

Access date (system clock): **2026-11-05** (local, 2026-11-05T05:08:00-03:00).
Fetch: `curl -sS -L -o cm-4.5.html https://spec.commonmark.org/0.31.2/#fenced-code-blocks` → HTTP 200, 514698 bytes; `.../#list-items` → same document (HTTP 200, 514698 bytes).
Section text extracted with `extract.py` (stdlib html.parser, prose paragraphs whitespace-normalised to one line each, `<pre>` blocks kept line-by-line, inline `<a>`/`<code>` markup stripped keeping text).

Verbatim check = `grep -c -F` of the quote in the section extract and in the whole-page text; section-span check = the quote occurs inside the h2 section span only (count in the section span, and count in every other h2 section of the same document).

## §4.5 Fenced code blocks — primary

- URL: https://spec.commonmark.org/0.31.2/#fenced-code-blocks
- Section anchor: `#fenced-code-blocks`  (h2 span: `fetched-4.5.txt`, 1 in-section hit)
- Access date: 2026-11-05
- Quote (23 words, limit 25):

  > The closing code fence may be preceded by up to three spaces of indentation, and may be followed only by spaces or tabs

- Verbatim check: `grep -c -F` → **1** in `fetched-4.5.txt`; **1** in the whole document text.
- Section-span check: **1** inside the h2 span of `#fenced-code-blocks`; other h2 sections of the same document: 0 hits.
- Why: closing-fence indentation and trailing-character rule (C1 rule R1)

## §5.2 List items — primary

- URL: https://spec.commonmark.org/0.31.2/#list-items
- Section anchor: `#list-items`  (h2 span: `fetched-5.2.txt`, 1 in-section hit)
- Access date: 2026-11-05
- Quote (9 words, limit 25):

  > A list item may contain any kind of block:

- Verbatim check: `grep -c -F` → **1** in `fetched-5.2.txt`; **1** in the whole document text.
- Section-span check: **1** inside the h2 span of `#list-items`; other h2 sections of the same document: 0 hits.
- Why: content of a list item is block content (C1 rule R1)

## §5.2 List items — corroborating

- URL: https://spec.commonmark.org/0.31.2/#list-items
- Section anchor: `#list-items`  (h2 span: `fetched-5.2.txt`, 1 in-section hit)
- Access date: 2026-11-05
- Quote (15 words, limit 25):

  > then blocks must be indented five spaces in order to fall under the list item.

- Verbatim check: `grep -c -F` → **1** in `fetched-5.2.txt`; **1** in the whole document text.
- Section-span check: **1** inside the h2 span of `#list-items`; other h2 sections of the same document: 0 hits.
- Why: block content sits nested under the list item (C1 rule R1)

## §4.5 Fenced code blocks — supporting (closing-fence character)

- URL: https://spec.commonmark.org/0.31.2/#fenced-code-blocks
- Section anchor: `#fenced-code-blocks`  (h2 span: `fetched-4.5.txt`, 1 in-section hit)
- Access date: 2026-11-05
- Quote (17 words, limit 25):

  > a closing code fence of the same type as the code block began with (backticks or tildes)

- Verbatim check: `grep -c -F` → **1** in `fetched-4.5.txt`; **1** in the whole document text.
- Section-span check: **1** inside the h2 span of `#fenced-code-blocks`; other h2 sections of the same document: 0 hits.
- Why: the closing fence must use the opener's fence character (C1 rule R1)

## §4.5 Fenced code blocks — supporting (closing-fence length)

- URL: https://spec.commonmark.org/0.31.2/#fenced-code-blocks
- Section anchor: `#fenced-code-blocks`  (h2 span: `fetched-4.5.txt`, 1 in-section hit)
- Access date: 2026-11-05
- Quote (13 words, limit 25):

  > with at least as many backticks or tildes as the opening code fence

- Verbatim check: `grep -c -F` → **1** in `fetched-4.5.txt`; **1** in the whole document text.
- Section-span check: **1** inside the h2 span of `#fenced-code-blocks`; other h2 sections of the same document: 0 hits.
- Why: the closing fence must be at least as long as the opener (C1 rule R1)

## §4.5 Fenced code blocks — freshness-recheck of stored row S578

- URL: https://spec.commonmark.org/0.31.2/#fenced-code-blocks
- Section anchor: `#fenced-code-blocks`  (h2 span: `fetched-4.5.txt`, 1 in-section hit)
- Access date: 2026-11-05
- Quote (17 words, limit 25):

  > A fenced code block begins with a code fence, preceded by up to three spaces of indentation.

- Verbatim check: `grep -c -F` → **1** in `fetched-4.5.txt`; **1** in the whole document text.
- Section-span check: **1** inside the h2 span of `#fenced-code-blocks`; other h2 sections of the same document: 0 hits.
- Why: stored S578 quote must still match the live page

## Independent cross-check: the web reader rendering

The same document was read a second time through the web reader (a different fetch path from
`curl`), and each quote was located there as well:

- §4.5 primary — reader line 2281 (`The closing code fence may be preceded by up to three spaces of indentation, and`)
  continued on reader line 2282 (`may be followed only by spaces or tabs, which are ignored.`)
- §4.5 supporting (character / length) — reader lines 2272-2275 (`The content of the code block consists of all subsequent lines, until a closing code fence of the same type as the code block began with (backticks or tildes), and with at least as many backticks or tildes as the opening code fence.`)
- §5.2 primary — reader line 5017 (`A list item may contain any kind of block:`), example 263 at reader line 5019
- §4.5 S578 freshness — reader line 2262 (`A [fenced code block](#fenced-code-block) begins with a code fence, preceded by up to three spaces of indentation.`)

Wrapping note: the fetched HTML hard-wraps prose at the source line width, so a sentence can straddle
two source lines (the §5.2 corroborating quote `then blocks must be indented five spaces in order to fall
under the list item.` wraps at reader lines 4853-4855). The verbatim check is therefore run against
whitespace-normalised text, which is the same sentence, not a different wording — the count for each
quote in the whitespace-normalised whole document is exactly 1.

## Adjacent context (NOT inside §5.2 — do not cite as a §5.2 quote)

The chapter-5 preamble (`<h1 id="container-blocks">`, reader lines 4257-4259) carries the general
container rule: *A container block is a block that has other blocks as its contents. There are two
basic kinds of container blocks: block quotes and list items.*

It is the §5 preamble, not the §5.2 h2 span, so it is recorded here for orientation only. The §5.2
quote used for the row is *A list item may contain any kind of block:*, which is inside §5.2.

## Structural evidence: a fenced block nested inside a list item (Example 263)

`fetched-5.2.txt` lines 158-168 — the §5.2 sentence *A list item may contain any kind of block:* and its markdown example:
(Example 263): the list item `1. foo` contains a fenced code block ` ``` / bar / ``` ` whose closing
fence closes that *nested* block, inside the list item — the list marker line is content, and the
fence pair is scoped to the list item rather than to any enclosing fence. This is the shape of
probe P-A (`- ``` `): a list-marker-prefixed fence line is list-item content, never a closer of an
enclosing fenced block.

```
A list item may contain any kind of block:
1. foo

 ```
 bar
 ```

 baz

 > bam
```

## Freshness re-check of stored row S578

Stored S578 quote: "A fenced code block begins with a code fence, preceded by up to three spaces of indentation."
Live page match: **1** occurrence in `fetched-4.5.txt` (whole document: 1) → the stored quote still matches the live page on 2026-11-05; S578 needs no re-opening correction.

Note on markup: in the fetched HTML the stored S578 sentence is interrupted by the `<a>fenced code block</a>` link tag; the plain-text form above is the sentence as the reader renders it, which is the form SOURCES.md already stores.

## Candidate SOURCES row for §5.2 (proposal only — corpus/SOURCES.md not edited)

```
| S580 | CommonMark0.31.2 list items — https://spec.commonmark.org/0.31.2/#list-items | spec | A | List-item container rule in kama rendered-cell selection (round-87 C1 rule R1) | Version0.31.2 (2024-01-28), section5.2 List items, opening definition of list-item content, opened2026-11-05: "A list item may contain any kind of block:" | The content of a list item is block content nested in that item, so a line beginning with a list marker is never a closing fence of an enclosing fenced block | mined | 2026-11-05 | on-release | round-87 C1 |
```

### Census conformance of the proposed row (measured, `scripts/sources-census.sh`)

The proposed row was appended to a scratch copy of the lane's `corpus/SOURCES.md` (lane tree
untouched) and validated with the fleet's own census tool:

- `validate` on the unmodified registry copy → exit **0** (baseline, no findings).
- `validate` with S580 appended and `used-by=round-87 C1` → exit **1**, one finding:
  `file E11 S580 missing used-by round-87 C1`. The `used-by` cell of a `mined` row must be a path
  that exists on disk under the lane root (`E11` in `scripts/sources-census.sh`, `usedby_findings`).
- `census` mode (row/tier/status counts) with S580 appended → exit **0** in both variants;
  `census` counts rows/tiers/statuses and does not run the `used-by` path check, so `E11` is a
  `validate`-mode finding only.
- `validate` with S580 appended and `used-by=corpus/lessons/round-87.md` (a path the round-87
  lesson file creates, per the round's `## Mistakes` obligation) → exit **0**; the row then
  moves the counts to `rows=320 tier.A=305 status.mined=287`.

`W04` (same URL across scopes) is emitted for S580 because S576/S578/S579 already carry
`spec.commonmark.org/0.31.2`; W-codes are warnings and do not change the exit status.

Recommendation to the L1: land the row with `used-by=corpus/lessons/round-87.md` (the file the
round-87 lesson obligation creates) rather than the literal string `round-87 C1`, which trips
`E11` and turns the round's `validate` census red. The seat's `used-by=round-87 C1` value is
recorded here as specified, with the measured consequence attached.
