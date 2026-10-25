# RevDrift174 — S174 quote check vs live git-scm.com/docs/git-blame

Checked 2026-10-24. One fetch (`curl -sL`), 82,635 bytes saved to
`.ufo/waves/round-36/w3/out/RevDrift174/git-blame.html`. Registry not edited.

## Measured (from fetched bytes)

- Pattern `Annotates each line` occurs exactly once in the page (§DESCRIPTION, first paragraph).
- Live sentence (≤25-word quote, 19 words):

  > "Annotates each line in the given file with information from the revision which last modified the line."

  Followed in the same paragraph by: "Optionally, start annotating from the given revision."

- Row S174 (corpus/SOURCES.md line 186, `teaches` cell, first quote, 18 words):

  > "Annotates each line in the file with information from the revision which last modified the line"

## Verdict: NOT byte-exact

Word-for-word difference: the row's quote **omits the word "given"** — the page reads
"in the given file", the row reads "in the file". That is the only difference; all 18
shared words match in order, punctuation aside (row quote has no terminal period).

## Inference / context (not measured here)

- corpus/SOURCES.md lines 435–443 already carry a round-30 append-only correction record
  ("Round-30 source correction — S174 and S176") that documents this exact "given" omission
  and instructs reading the cell's first phrase as a paraphrase, not a quote. The row body
  itself still carries the "(§DESCRIPTION, verbatim)" label with the truncated text, so the
  drift persists at the row level; the correction is metadata-only. Consistent with the
  append-only policy; no action taken (out of scope).
- Row's provenance cell ("live manual opened 2026-10-23") is compatible with today's page content.

## Residual risk / gaps

- Only the sentence beginning "Annotates each line" was verified; the row's second quote
  (§OPTIONS `--line-porcelain`) was not compared against the fetched page (out of scope).
- Page version drift vs the row's "local Git 2.56.0" note was not independently pinned
  (page carries no visible version header in the saved bytes); fetch is a single snapshot.
