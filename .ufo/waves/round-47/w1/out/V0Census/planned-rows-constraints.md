# V0Census — constraints for the round-47 planned SOURCES appends

Registry baseline at build `3a09a1d93dcc16799cf6c4b48786e6440af134c4`: 228 rows
(min `S001`, max `S487`), 11 columns, contract header
(id source kind tier scope anchor teaches status opened recheck used-by).
`corpus/SOURCES.md` is byte-identical between the freeze base `172b8ad0…`
and the build `3a09a1d…` (`git diff 172b8ad0 3a09a1d9 -- corpus/SOURCES.md`
is empty): the round has not appended yet; the C2 `newrow` leg lands at
integration.

## Planned appends (this round, `S4NN` ids assigned by the L1)

Source: `.ufo/waves/round-47/w1/dispatch.json` (S1Rows item; S1Numstat item).

1. S1Rows (a) — llama.cpp release b11909 Linux x64 CPU binary:
   asset `https://github.com/ggml-org/llama.cpp/releases/download/b11909/llama-b11909-bin-ubuntu-x64.tar.gz`,
   record `https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b11909`,
   tag commit `caa8191df159f764fb0160e3d2fc6be008948aee`,
   digest `sha256:bf94332a3001f3ee0b032cda37259f68460e28732ef9a579bfb1b918197e695b`;
   kind docs, tier A, scope release identity + the commit its tag names.
2. S1Rows (b) — kama live lifecycle receipts at b11909 with provenance and
   replay (own-work, tier A; anchor `.ufo/waves/round-47/c2/live/receipt-1..3.json`).
3. S1Rows (c) — stories260K model artifact at
   `https://huggingface.co/ggml-org/models-moved/resolve/main/tinyllamas/stories260K.gguf`,
   sha256 `270cba1bd5109f42d03350f60406024560464db173c0e387d91f0426d3bd256d`,
   scope artifact identity only.
4. S1Numstat — git `diff --numstat` / `\ No newline at end of file` docs row
   (C1 ground-truth source; compare model row S475).

## Constraints for `sources-census.sh validate` exit 0 (per-row, E-codes)

- Row inside the `## Registry` section (rows elsewhere are E12);
  NF=13 (leading/trailing pipe + 11 cells); id `S[0-9]{3,}` and unique (E02/E03).
- kind/tier/status enum values (E05/E06/E07); community never tier A (E10).
- opened = past/present ISO date (E08); recheck ISO/NNd/symbolic (E09).
- Mined rows: used-by paths must exist on disk (E11); tier-C mined with
  non-`—` used-by is W01 (warning only).
- New (URL, scope) pairs must not duplicate an existing pair without a
  supersedes note (E04). Duplicates across *different* scopes are W04
  (warnings do not change exit).
- W-codes (W01-W04) never flip exit 0 -> 1.

## Constraints for `tools/sources-append-only.py` exit 0 (SOURCES-CONTRACT-v1 rule 2)

- No existing row removed; every base id present in the target.
- Immutable cells `{source, kind, tier, scope, anchor, teaches, opened}`
  byte-equal after whitespace strip for every existing id; only
  `{status, recheck, used-by}` may change.
- New rows must parse: well-formed 11-cell `| ... |` row, unique id,
  no second `## Registry` heading, no malformed width/separator/header.
- No new row-like (`| S0NN |`) lines outside the Registry section (the guard
  treats them as parse errors — see blocker below).

## BLOCKER — exit 0 is currently unreachable for any append

The frozen guard `tools/sources-append-only.py` exits **2** on this exact pair:
- forward: `python3 tools/sources-append-only.py --from 172b8ad0… --to 3a09a1d9…`
  -> exit 2:
  `error: 172b8ad040d51ce8c011238c1408d4e0b6aa9595:corpus/SOURCES.md:516: row-like line outside the parsed registry table; refusing to drop it`
- reversed (3a09a1d9… -> 172b8ad0…) -> exit 2, same shape at line 516.

Both blobs contain 27 row-like lines outside the `## Registry` section
(first at line 516: Row-45 re-verification appendix row `| `S010` | …`);
these were introduced by the round-44/45 appendix sections (commits
`ef76777e`, `052cb1e9`). Because the guard parses **both** blobs before
comparing, no append can turn this exit 2 into exit 0 — the row-like scan
must be scoped to the registry section (proposed unified diff:
`proposed-fix-sources-append-only.diff`; patched tool passes its selftest
43/43 and reports `no append-only violations` / `violations: []` on the pair).

Without that fix, C2's planned `newrow` lands with no append-only gate
verification at integration time.
