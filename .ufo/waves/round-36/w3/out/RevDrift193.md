# RevDrift193 — S193 quote vs tools/gate-registry-check.py @ c4c46ad5b87d8b63f03e200a7b13eb8eeff46279

Scope: registry row S193 (corpus/SOURCES.md, working tree, line 205) and its
pinned quote target. No registry or tool file was edited. Read-only git only.

## Measured results

Blob resolution: `git show c4c46ad5b87d8b63f03e200a7b13eb8eeff46279:tools/gate-registry-check.py`
resolves; 15,140 bytes, sha256 `e07cf8d753560cd34b5945c89f4dc3f19122ca87d19f8e85844e3b1ae4e0506b`.

Location of the quoted sentence (module docstring, `Contract:` section):
- Line 15: `      evaluated revision. A path is ``registered`` iff it occurs in a cell of`
- Line 16: `      a row of such a table. A prose mention (a wave-artifact paragraph, a`

Exact sentence bytes (80 bytes, spanning the source line wrap):
`A path is ``registered`` iff it occurs in a cell of\n      a row of such a table.`

Uniqueness: the stem `iff it occurs in a cell` occurs exactly once in the blob
(byte offset 805, line 15). The citation is unambiguous.

## Findings by severity

**None (no actionable defect).**

Verdict on the row's quote: **normalized, not byte-exact.** Evidence:
- The source sentence carries RST literal markup — double backticks around
  `registered` (` ``registered`` `) — which the S193 quote strips.
- The source sentence wraps across lines 15–16 with `\n` + 6 spaces of
  indentation inside it; the S193 quote is a single line.
- The S193 quote string is not a contiguous byte span of the blob (full-blob
  search returns no match); nor is the markup-stripped single-line form.
- After normalization (strip all ``` ` `` marks, collapse the line-wrap
  whitespace to one space), the source sentence equals the S193 quote
  byte-for-byte. Word count is preserved: 17 whitespace-delimited words on
  both sides. Zero content drift; only markup and line-wrap are normalized.

Cross-check: the superseding row S194 (corpus/SOURCES.md:206) already states
the sentence is at lines 15–16 with the markup intact — independently
confirmed by this measurement. The corpus itself already documents the exact
bytes, so S193's normalization is a known, self-corrected rendition.

## Residual risk

- Any downstream byte-exactness checker that greps the pinned blob for the
  S193 quote bytes will fail to find them (markup + wrap). Mitigated: S194
  carries the byte-faithful form and supersedes S193.

## Verification gaps

- None material for the assigned question. Not verified (out of scope):
  provenance/commit history of the SOURCES.md row itself; no tool execution
  was required to answer the quote-fidelity question.
