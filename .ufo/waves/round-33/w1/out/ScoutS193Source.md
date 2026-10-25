# ScoutS193Source — S193 gate source at pinned revision

## Observed (source blob)

- Blob: `tools/gate-registry-check.py` @ `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279`
  (git blob `0183e55cb8243b1b87833a62123d0fa4352a596b`, mode 100755).
- Identical bytes at the C2 input gate-source revision
  `967d88528c1d83535563f971863f7855f76b4849` (lines 15–16 verified equal).

### Quoted sentence

Line span: **file lines 15–16**, inside the docstring `Contract:` section (docstring
opens at file line 2). The sentence begins mid-line and ends mid-line:

```
L15 col 27 →  "A path is ``registered`` iff it occurs in a cell of"
L16 col 28 ←  "a row of such a table."
```

- L15: `      evaluated revision. A path is ``registered`` iff it occurs in a cell of`
- L16: `      a row of such a table. A prose mention (a wave-artifact paragraph, a`

Verbatim bytes (joining across the line break):

```
A path is ``registered`` iff it occurs in a cell of a row of such a table.
```

### Visible punctuation/markup

- `registered` is wrapped in **double backticks** — reStructuredText inline-literal
  markup: `` ``registered`` ``.
- Single terminal period after `table`.
- No other punctuation inside the sentence. It is preceded on L15 by
  `evaluated revision. ` and followed on L16 by ` A prose mention (...)`.

### Word count

**17 whitespace-delimited words**, identical whether the `` `` `` markup is retained
(attaches to the `registered` token) or stripped:

`A(1) path(2) is(3) registered(4) iff(5) it(6) occurs(7) in(8) a(9) cell(10)
of(11) a(12) row(13) of(14) such(15) a(16) table.(17)`

## Comparison

| record | states | vs. source |
|---|---|---|
| `corpus/lessons/round-32.md` §Gate | "line 22", quote renders bare `registered`, "(16 words.)" | line wrong (sentence spans 15–16; L22 is the `empty-entry` defect bullet), quote drops `` `` `` markup, count wrong (17, not 16) |
| `corpus/SOURCES.md` S193 row | anchor `docstring "Contract" section, read 2026-10-24 at c4c46ad5b87d…`, quote `` `A path is registered iff it occurs in a cell of a row of such a table.` `` | anchor has no line span (imprecise, not false); quote drops `` `` `` markup — not byte-verbatim |
| `corpus/SOURCES.md` S194 row (committed `8833119`) | `lines 15–16`, quote with `` ``registered`` ``, "17 whitespace-delimited words" | exact match to source |
| `corpus/lessons/round-32-verifier-spotcheck.md` L65 | "line 15" (start line), flags lesson's "line 22" as defect 3 | consistent — sentence starts on L15 |

## Confidence

High — byte-level extraction from the pinned blob, two independent revisions
checked, all three discrepancies reproduced.

## Remaining unknowns

None within scope. Tokenization rule stated; no reasonable whitespace rule yields
16 (16 would require excluding `iff` as a word).
