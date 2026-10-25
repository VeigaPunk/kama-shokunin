# ExecS193Quote — S193 quote location and word count at the pinned gate revision

Read-only static measurement of one blob at one revision. This report is the only write; no lane
file, index, or jj state was touched.

## Verdict

| item | measured value |
|---|---|
| pinned commit | `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279` (full; `^{commit}` resolves to itself) |
| source path | `tools/gate-registry-check.py` |
| quote start | line **15**, column **27** (1-based); byte offset **780** (0-based) |
| quote end | line **16**, column **28** inclusive (last character `.`); exclusive boundary column 29 / byte offset **860** |
| source lines occupied | **15 and 16 only**; no other line contains any character of the quote |
| quoted characters | 80 (ASCII; 51 on line 15 + LF + 6 continuation spaces + 22 on line 16) |
| word count | **17** under the stated whitespace rule, corroborated as 17 by three other rules |
| round-32 lesson Gate | says "line 22" and "16 words" — **both contradicted** by the pinned bytes |
| S194 correction row | "lines 15–16", "17 whitespace-delimited words" — **matches** this measurement exactly |

## Pinned identity and retained provenance

| property | value |
|---|---|
| commit | `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279`, `2026-10-24 03:08:04 -0300` |
| commit subject | `round-32: C2 — gate-registry-check v2 (registry-row meaning: table-row presence, cell/exit-map checks, cited-path existence) + selftest + control/mutation receipts` |
| git blob id | `0183e55cb8243b1b87833a62123d0fa4352a596b` |
| blob size | 15140 bytes |
| blob sha256 | `e07cf8d753560cd34b5945c89f4dc3f19122ca87d19f8e85844e3b1ae4e0506b` |
| line count | 380 lines, LF endings, trailing LF, ASCII only |
| occurrences of raw quoted span | exactly 1 |
| occurrences of `A path` in the blob | exactly 1 (at this span) |
| HEAD comparison | lane `HEAD` blob for this path is also `0183e55c…`; worktree bytes hash to the same sha256 |

The only two commits touching this path are `e49b4cf77046024551ba83d490ef83d9dee061ed` (round-28,
v1) and `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279` (round-32, v2). The v1 sentence is a different
text (13 words, beginning at line 12), so neither stale number below is inherited from the
immediate predecessor's wording of this phrase.

## Exact quoted span

Byte-exact raw span (80 bytes). `\n` and the six continuation spaces are literal; the file has no
tabs and no trailing whitespace on either line:

```text
A path is ``registered`` iff it occurs in a cell of\n      a row of such a table.
```

Source view with line, raw content (`repr`), quote segment, and columns:

| line | raw content | quote segment | quote columns | tokens |
|---|---|---|---|---|
| 15 | `      evaluated revision. A path is ``registered`` iff it occurs in a cell of` | `A path is ``registered`` iff it occurs in a cell of` | 27–77 | 1–11 |
| 16 | `      a row of such a table. A prose mention (a wave-artifact paragraph, a` | `a row of such a table.` | 7–28 | 12–17 |

Boundary detail:

- Line 15 is 77 characters; its first 26 columns are the prefix `      evaluated revision. `, so
  the quote starts at column 27 and runs to end of line (column 77, after `of`).
- Line 16 is 74 characters; columns 1–6 are continuation indentation, the quote resumes at column 7
  and ends at column 28 (the final `.`). Column 29 is the single separating space; the next
  sentence starts at column 30 (`A prose mention …`).
- The line break and the six-space indent between `of` and `a row` are whitespace separators only;
  they contribute no word.
- Context lines 13–18 belong to the same `- Registry:` bullet and its following sentences, but
  only lines 15–16 carry the quote. Line 22 of the pinned file is unrelated:
  `        * ``empty-entry``     the Kind / entry command cell is empty;`

### Markup fidelity (relevant to "verbatim")

- The raw source contains RST inline-literal markup: `` ``registered`` `` (four backtick characters
  around `registered`), columns 37–50 of line 15.
- The S193 `corpus/SOURCES.md` row and the round-32 lesson quote the **rendered** form
  `A path is registered iff it occurs in a cell of a row of such a table.` (markup interpreted
  away). That rendered string is **not** a byte-contiguous substring of the blob; it is obtained
  by deleting the four backticks.
- The raw one-line form with the docstring wrap collapsed (LF + six spaces → one space) equals the
  S194 row quote exactly: `A path is ``registered`` iff it occurs in a cell of a row of such a table.`
  The markup-stripped one-line form equals the S193 row quote exactly. A one-line quotation of a
  wrapped docstring necessarily normalizes the wrap; the token sequence is unchanged.

## Tokenization rule and count

**Rule W (primary).** Take the raw span exactly,
`A path is ``registered`` iff it occurs in a cell of\n      a row of such a table.`; strip leading
and trailing whitespace; split on maximal runs of ASCII whitespace (U+0020 space, U+000A newline —
the span contains one newline and 21 spaces: 10 separators on line 15, and on line 16 six
continuation-indent spaces plus 5 separators, forming 16 maximal whitespace runs); count
each non-empty item as one word. Punctuation and RST markup stay attached to their token and
neither create nor remove tokens. **Result: 17 words.** Line 15 contributes tokens 1–11, line 16
tokens 12–17.

| # | token | line:columns | # | token | line:columns |
|---|---|---|---|---|---|
| 1 | `A` | 15:27–27 | 10 | `cell` | 15:71–74 |
| 2 | `path` | 15:29–32 | 11 | `of` | 15:76–77 |
| 3 | `is` | 15:34–35 | 12 | `a` | 16:7–7 |
| 4 | `` ``registered`` `` | 15:37–50 | 13 | `row` | 16:9–11 |
| 5 | `iff` | 15:52–54 | 14 | `of` | 16:13–14 |
| 6 | `it` | 15:56–57 | 15 | `such` | 16:16–19 |
| 7 | `occurs` | 15:59–64 | 16 | `a` | 16:21–21 |
| 8 | `in` | 15:66–67 | 17 | `table.` | 16:23–28 |
| 9 | `a` | 15:69–69 | | | |

Token statistics: 17 tokens; 14 case-sensitive token types (13 case-insensitive); `A`/`a` occurs
3 times and `of` twice.

Corroborating rules, each independently yielding **17**:

| rule | count | note |
|---|---|---|
| Rule W: raw span, maximal ASCII-whitespace runs | 17 | token 4 is `` ``registered`` `` (markup attached) |
| RST markup stripped, then Rule W | 17 | token 4 is `registered` |
| Unicode word-character runs, regex `[^\W_]+` | 17 | punctuation dropped, no token split |
| coreutils `wc -w` on the exact 80-byte slice `[780,860)` | 17 | independent of Python tokenization |

No tested rule yields 16. Reaching 16 requires deleting exactly one of the 17 tokens (for example,
dropping the leading `A`); no stated segmentation of the bytes does that. The lesson's "16 words"
is therefore not reproducible from the pinned blob.

## Comparison with the stale and corrected claims

| claim source | claim | measurement |
|---|---|---|
| `corpus/lessons/round-32.md` Gate (lines 27–28) | quote at "line 22", "(16 words.)" | quote spans lines 15–16; 17 words. Line 22 is an `empty-entry` bullet and holds no part of the quote |
| `corpus/lessons/round-32-verifier-spotcheck.md` line 65 | "line 15 of the file at that commit" | correct as the **start** line, incomplete as a span: the sentence continues through line 16 |
| `corpus/SOURCES.md` S194 row | "lines 15–16", "17 whitespace-delimited words", quote with `` ``registered`` `` markup | exact match with the raw span and Rule W |
| `corpus/SOURCES.md` S193 row | quote rendered without markup | exact match with the markup-stripped rendering; not a raw byte substring (see fidelity note) |
| `SCORECARD.md` § "S193 quote correction" | "lines 15–16 … 17 whitespace-delimited words" | matches |

## Retained evidence

Commands run from `/home/vgpnk/Projects/shokunin/kama-shokunin` (read-only git):

```text
$ git rev-parse c4c46ad5b87d8b63f03e200a7b13eb8eeff46279^{commit}
c4c46ad5b87d8b63f03e200a7b13eb8eeff46279
$ git rev-parse c4c46ad5b87d8b63f03e200a7b13eb8eeff46279:tools/gate-registry-check.py
0183e55cb8243b1b87833a62123d0fa4352a596b
$ git cat-file -s 0183e55cb8243b1b87833a62123d0fa4352a596b
15140
$ git show c4c46ad5b87d8b63f03e200a7b13eb8eeff46279:tools/gate-registry-check.py | sha256sum
e07cf8d753560cd34b5945c89f4dc3f19122ca87d19f8e85844e3b1ae4e0506b  -
$ git show c4c46ad5b87d8b63f03e200a7b13eb8eeff46279:tools/gate-registry-check.py | dd bs=1 skip=780 count=80 status=none | wc -w
17
$ git log --format='%h %H %s' -- tools/gate-registry-check.py
c4c46ad c4c46ad5b87d8b63f03e200a7b13eb8eeff46279 round-32: C2 — gate-registry-check v2 ...
e49b4cf e49b4cf77046024551ba83d490ef83d9dee061ed round-28: C1 data ...
```

Additional checks recorded in-session: `blob[780:860] ==` the raw span bytes (True);
`blob[779] == b' '` and `blob[860] == b' '` (quote is bounded by spaces); the raw span occurs
exactly once; line 15 and line 16 have no trailing whitespace; the file contains no CRLF and no
non-ASCII bytes.

## Consequence for the correction owner (advisory only)

- Use the anchor **docstring "Contract", lines 15–16** and the count **17 whitespace-delimited
  words**.
- If "verbatim quote" means raw-source exact, retain the doubled backticks around `registered`
  (as the S194 row does); if it means rendered text, S193's markup-free form is exact after
  interpreting the RST literal. In either case a one-line quotation collapses the docstring wrap
  (LF + six spaces → one space) without changing the 17-token sequence.
- The round-32 lesson's "line 22 / 16 words" should be superseded by an appended correction that
  names it; filed bytes should not be rewritten.

## Limits

- Static measurement of one blob at one pinned revision; the gate was not executed and no fixture
  was replayed here. No endpoint, service, model-quality, consumer-health, or cross-lane claim is
  made. No external source was fetched. No lane file was edited and no lane jj/Git state was
  mutated; this report is the sole write.
- Tooling: nothing installed or upgraded (no package manager, uv, or binary install was run).
