# SC01SourceOpen — CommonMark 0.31.2 source opening (round-87 C1, calibration)

## Scope

Seat SC01SourceOpen opens the two public CommonMark 0.31.2 sections that round-87 claim C1
(rule R1) rests on, locates and verifies a ≤25-word verbatim quote in each, re-checks the
freshness of the stored row S578 quote, and proposes the candidate SOURCES row for §5.2.
It proposes a row as text only — `corpus/SOURCES.md` is **not** edited. It does not touch
`tools/`, `plans/`, `corpus/`, `SCORECARD.md`, `LOG.md`, or any tracked lane file.

Frozen revision measured: freeze commit `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659`
(base `362b0d4a241520c9bc79b204c042d9fcefbb06ea`), confirmed with
`git -C /home/vgpnk/Projects/shokunin/kama-shokunin rev-parse` (both resolve; HEAD = freeze).

Access date from the system clock: **2026-11-05** (`date -u +%Y-%m-%d` → `2026-11-05`;
local clock `Thu 05 Nov 2026 05:07:44 AM -03`).

## Commands and outputs (exit codes)

1. `curl -sS -L -o cm-4.5.html 'https://spec.commonmark.org/0.31.2/#fenced-code-blocks' -w 'url4.5 http=%{http_code} size=%{size_download}\n'`
   → `url4.5 http=200 size=514698`, exit 0. Second fetch of `.../#list-items` →
   `url5.2 http=200 size=514698`, exit 0 (both anchors resolve to the same document).
   sha256 of the fetched document: `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`
   (recorded in `fetched-commonmark-0.31.2.html.sha256`).
2. `python3 extract.py cm-4.5.html fenced-code-blocks fetched-4.5.txt` → `wrote fetched-4.5.txt lines: 328`, exit 0.
   `python3 extract.py cm-4.5.html list-items fetched-5.2.txt` → `wrote fetched-5.2.txt lines: 819`, exit 0.
3. `python3 verify.py cm-4.5.html <outdir>` → `wrote quotes.md and checks.txt`, exit 0. Every
   count in `quotes.md` / `checks.txt` is computed by this script; none is hand-asserted.
4. `bash census-check.sh /home/vgpnk/Projects/shokunin/kama-shokunin <scratch>/census-run`
   → exit 0; full output in `census-check.out`. Measured:
   - baseline `validate` → `exit=0`; baseline `census` → `exit=0`, `FLEET rows=319 tier.A=304 status.mined=286`.
   - S580 with `used-by=round-87 C1`: `validate` → `exit=1`, finding `file E11 S580 missing used-by round-87 C1`;
     `census` → `exit=0`, `FLEET rows=320 tier.A=305 status.mined=287`.
   - S580 with `used-by=corpus/lessons/round-87.md`: `validate` → `exit=0` (only `W04`); `census` → `exit=0`.
   - `W04` (same URL across scopes) is emitted for S580 because S576/S578/S579 already carry
     `spec.commonmark.org/0.31.2`; W-codes are warnings and do not change the exit status.
5. Web-reader cross-check (a second, independent fetch path): `grep` over the reader rendering
   located every quote — §4.5 closing fence at reader lines 2281-2282; fence character/length at
   2272-2275; §5.2 list-item block at 5017 (Example 263 at 5019); S578 sentence at 2262.

No tools were installed or upgraded: the seat needed only `curl`, `python3` (stdlib), `bash`,
and the repo's own `scripts/sources-census.sh`, all already present. No pacman transaction was run.

## Findings

**F1 — §4.5 closing-fence rule located (23 words, ≤25), verbatim, in-section.**
Quote: *"The closing code fence may be preceded by up to three spaces of indentation, and may be
followed only by spaces or tabs"*. `grep -c -F` → 1 in `fetched-4.5.txt`, 1 in the whole-document
text; 1 inside the `#fenced-code-blocks` h2 span, 0 hits in every other h2 section of the same
document. This is the indentation + trailing-character half of R1's closer rule. Two supporting
quotes cover the other half of R1: *"a closing code fence of the same type as the code block
began with (backticks or tildes)"* (17 words) and *"with at least as many backticks or tildes as
the opening code fence"* (13 words), both 1/1 and in-section.
Evidence: `quotes.md` §4.5 blocks; `checks.txt`; `fetched-4.5.txt:4` (closing fence), `:3`
(character/length).

**F2 — §5.2 list-item block-content rule located (9 words, ≤25), verbatim, in-section.**
Quote: *"A list item may contain any kind of block:"*. `grep -c -F` → 1 in `fetched-5.2.txt`,
1 in the whole-document text; 1 inside the `#list-items` h2 span, 0 hits in any other h2 section.
Corroborating in-section quote (15 words): *"then blocks must be indented five spaces in order to
fall under the list item."* — 1/1, in-section. Together these state that a list item's content is
block content nested in that item, which is what makes a list-marker-prefixed fence line content
rather than a closer of an enclosing fence (R1).
Evidence: `quotes.md` §5.2 blocks; `fetched-5.2.txt:158` (the list-item block sentence);
`fetched-5.2.txt:5` (rule #1, "*Bs* as its contents").

**F3 — structural evidence for probe P-A, inside §5.2.** Example 263
(`fetched-5.2.txt:158-168`) shows list item `1. foo` containing a fenced block
` ``` / bar / ``` ` whose closing fence closes that *nested* block — the fence pair is scoped to
the list item, not to any enclosing fence. Same shape as P-A's `- ``` ` shadow line.
Evidence: `quotes.md` "Structural evidence" section; `fetched-5.2.txt:158-168`.

**F4 — S578 freshness re-check: PASS.** The stored S578 quote *"A fenced code block begins with a
code fence, preceded by up to three spaces of indentation."* occurs **1** time in
`fetched-4.5.txt` and **1** time in the whole document on 2026-11-05. S578 still matches the live
page; it needs no correction. (In the HTML the sentence is split by the `<a>fenced code block</a>`
link tag; the plain-text form is what SOURCES.md stores and what the reader renders.)
Evidence: `quotes.md` "Freshness re-check of stored row S578"; `checks.txt`.

**F5 — the seat's `used-by=round-87 C1` would turn the round's census `validate` red.**
The seat spec names `used-by=round-87 C1` for the proposed row, but `scripts/sources-census.sh`
requires a `mined` row's `used-by` cell to be a path that exists on disk under the lane root
(`usedby_findings` → `E11`, `scripts/sources-census.sh:567`). Measured on a scratch copy of the
lane registry: `validate` exits **1** with `file E11 S580 missing used-by round-87 C1`, against a
clean baseline of exit **0**. `census` mode (row/tier/status counts) exits 0 in both variants and
is unaffected — `E11` is a `validate`-mode finding only. The round's plan requires the census to
exit 0 at round end.
Recommendation to the L1: land S580 with `used-by=corpus/lessons/round-87.md` (the file the
round-87 `## Mistakes` obligation creates) — measured `validate` exit **0**, `census` exit **0**,
counts `rows=320 tier.A=305 status.mined=287`. The row as literally specified is kept verbatim in
`quotes.md` so the L1 can choose with the consequence in front of it.
Evidence: `census-check.out`; `quotes.md` "Census conformance"; `census-check.sh`.

**F6 — a chapter-5 sentence that must not be cited as a §5.2 quote.** *"A container block is a
block that has other blocks as its contents. There are two basic kinds of container blocks: block
quotes and list items."* sits in the chapter-5 preamble (`<h1 id="container-blocks">`), i.e. the
`#blank-lines` h2 span of the HTML, **outside** §5.2's span. It is recorded in `quotes.md` as
orientation only and is explicitly not the row's quote.
Evidence: `quotes.md` "Adjacent context"; HTML offset 189072 vs. `#list-items` h2 at 208884.

**F7 — lane tree left clean.** `git -C …/kama-shokunin status --porcelain` shows no tracked
modification and no untracked file outside `.ufo/`. One self-inflicted write occurred and was
undone: an earlier `census-check.sh` draft followed the `corpus/lessons` symlink and created a
placeholder `corpus/lessons/round-87.md` in the lane; it was deleted, the script now copies with
`cp -rL` after removing the symlink, and a re-run leaves the lane clean.

## Deliverables

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-87/w1/out/SC01SourceOpen/`:

- `fetched-4.5.txt` — §4.5 section text (328 lines), prose normalised one sentence per line.
- `fetched-5.2.txt` — §5.2 section text (819 lines), same normalisation.
- `quotes.md` — URL, access date, quote, word count, verbatim check (grep count), section-span
  check per quote; reader cross-check; Example 263 evidence; S578 freshness; census conformance;
  the proposed S580 row as text.
- `checks.txt` — the raw per-quote check output (counts and word counts).
- `extract.py`, `verify.py` — the extractor and the checker that produced the above.
- `census-check.sh`, `census-check.out` — the reproducible census conformance run.
- `fetched-commonmark-0.31.2.html.sha256` — digest of the fetched document.

Report: `.ufo/waves/round-87/w1/SC01SourceOpen.md` (this file). Scratch
`/fast/scratch/hyaku/kama-r87/SC01SourceOpen/` is removed on yield.

## Remaining unknowns

- Whether the L1 lands S580 with `used-by=round-87 C1` (red `validate`, F5) or with a real path
  (green). The row text for both is in `quotes.md`; the L1 owns the choice and the integration.
- `corpus/lessons/round-87.md` does not yet exist in the lane, so `used-by=corpus/lessons/round-87.md`
  becomes valid only once the round's `## Mistakes` obligation lands that file (a sibling seat's work).

VERDICT: Both §4.5 and §5.2 quotes located, verbatim (1/1) and inside their h2 section spans, ≤25 words; S578 freshness re-check PASSES; the proposed S580 row is drafted — with a measured census caveat: `used-by=round-87 C1` trips E11 and turns `validate` red, so the L1 should land `used-by=corpus/lessons/round-87.md`.
