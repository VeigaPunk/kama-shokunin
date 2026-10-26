# Proposed append for `corpus/README.md` — **delta only** (drafted by seat X1Doc)

**Why this file is a delta.** After I measured at the build, the lane's working tree gained a scribe section
`## Frontier disposition — round 48` (`corpus/README.md`, drafted by seat S9Readme at `380bcdff`, with an
"Integration addendum (round-48 L1)" naming the tenth contract row and 90 files). That section already carries the v3
numbers I measured (89 files at the build, the region semantics, `regressed`, 98 events at `--threshold 1`, the edges
list). Restating them would duplicate a landed correction. What the landed section does **not** say, and what a
reader of the round-46/47 blocks still needs, is (a) that the round-47 block's instrument statements are superseded
and by what, and (b) that one of its cited commands no longer runs at all. That is all this draft appends.

Anchor: end of the round-48 disposition block (after its "Integration addendum"), i.e. EOF of `corpus/README.md` at
the integration tip. `corpus/README.md` is contract row 4 (`A-corr`, region `*`); append, never rewrite. If the L1
prefers to fold this into the landed block, the two paragraphs below are the whole content.

All figures here name the build `380bcdff9c8af06997c482f6eb03db926a794a2b`; the build's contract is nine rows,
sha256 `ca0618e50fadc4b0d53b0d8a61868b0ea7fbf33b3429c125a0d5643022a77075`, tool sha256
`ec9c6d206fccfd9b9b04526b54da34207c48ab9f0768c3285128cd59fcf60f72`.

---

### Supersession map for the round-46 and round-47 blocks (`:759-826`, `:895-898`)

The `## Frontier disposition — round 48` block above supersedes the instrument statements of the two earlier blocks
by appending, as round 47 superseded the round-46 paragraph the same way. Read it as follows; the earlier text stays
as written and is not to be cited as current.

- `:759-761` ("the five files the lane treats as append-only") — superseded: seven rows in round 47, nine at the
  build, ten after integration.
- `:776` (`append-only-audit v2`), `:782` ("schema `append-only-audit/v2`"), `:783` ("seven rows"), `:788` ("expands
  to 85 files"), `:803-806` (round-47 counter `files=85 … met=True`) — superseded by the v3 numbers in the block
  above; the round-47 counter still meets its predicate only at its own build tip (`--tip 3a09a1d9`: `met=True`,
  exit 0) and reads `selftest=1 contract=0 lane=0 fixture=0 stable=0 met=False`, exit 1, at the v3 build.
- `:807-810` ("the tool … never reads its `rule`, `declared_at` or `note` cell (`tools/append-only-audit.py:184`)") —
  superseded: v3 reads `declared_at` and `region`; `:184` is inside `row_token()` at the build, not the expansion.
- `:811-814` ("(1) The `SCORECARD.md` carve-out is declared but not applied … a signal to read, not a verdict") and
  `:815-821` ("(2) … no contract row covers `corpus/knowledge/*.md`") — superseded: both carve-outs are applied and
  the tool exits 0 at the build. `corpus/knowledge/context-capacity.md:245` (`## Errata — round 26`) remains
  uncovered because its heading does not carry the word, so a round citing it must still disposition it under KQ71.
- `:821-826` ("91 events — 12 restored, 8 partial, 71 unrestored … 26 across 15 lesson files") — superseded: 98
  events at the build (14 restored, 4 partial, 62 unrestored, 18 ungraded, 186 ungraded lines) and 96 at the cited
  `3a09a1d9` with the v3 contract; the per-file counts, and the reason they moved, are in the block above.
- `:895-898` ("The instrument's edges") — three of its four items are closed or renumbered by the block above; the
  last clause stands unchanged: a lane file declared append-only with no contract row is still not detected by the
  tool (`unmatched_patterns` reports the inverse case), and the detection stays with a round's KQ71 census.

### The round-47 block's own command no longer runs (`:790`)

`python3 tools/append-only-audit.py --repo <clone> --to 3a09a1d9` exits **2**:

```
could-not-evaluate: contract header is not path<TAB>rule<TAB>declared_at<TAB>region<TAB>note
```

The default contract is read from `<to>` (`tools/append-only-audit.py:87`), and `3a09a1d9` still holds the four-cell
file. The same tip with the v3 contract passed explicitly reads `commits=303 files=87 events=5 restored=5 partial=0
unrestored=0 ungraded=0 ungraded_lines=89 regressed=1`, exit 1; the build reads `commits=311 files=89 … regressed=0`,
exit 0. A reader re-running the `:790` line must add `--contract registry/append-only-contract.tsv` (and then read
87/89 paths, not 85).
