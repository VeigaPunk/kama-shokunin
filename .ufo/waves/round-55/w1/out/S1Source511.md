# S1Source511 — S511 re-open: git-config(1) GIT_CONFIG_COUNT row verification

Verdict: **AGREE — every cell checks out** (live page byte-identical to the committed copy; quote verbatim modulo one typographic apostrophe U+2019→U+0027, 18 words ≤ 25, located at the named anchor; scope and override-order claims confirmed verbatim on the page).

Seat item: re-open S511 — fetch https://git-scm.com/docs/git-config live, verify the row's quote (verbatim, ≤25 words, at the named anchor), check scope/teaches claims (override order: env pairs override config files, overridden by `git -c`), compare live page with the committed copy (sha256 both, diff), verdict agree/disagree per cell.

Date: 2026-10-27. Live fetch: `curl -sSL https://git-scm.com/docs/git-config` (exit 0, 830605 bytes). All work in scratch `/fast/scratch/hyaku/kama-r55/w1/S1Source511` (TMPDIR set); scratch removed after the report.

## Row under test

`kama-shokunin/corpus/SOURCES.md:264` (table header line 11):

```
| S511 | git-config(1) environment: GIT_CONFIG_COUNT / GIT_CONFIG_KEY_<n> / GIT_CONFIG_VALUE_<n> —
https://git-scm.com/docs/git-config#Documentation/git-config.txt-GITCONFIGCOUNT | docs | B |
which environment variables inject runtime configuration into every git call a counter makes:
GIT_CONFIG_COUNT pairs GIT_CONFIG_KEY_<n> with GIT_CONFIG_VALUE_<n> into the process's runtime
configuration, overriding config files (e.g. core.hooksPath reaches an attacker hook) |
§GIT_CONFIG_COUNT (HTML copy `.ufo/waves/round-55/sources/git-docs-git-config.html`); opened
2026-10-27 by the L1 | "all environment pairs GIT_CONFIG_KEY_<n> and GIT_CONFIG_VALUE_<n> up to
that number will be added to the process's runtime configuration" — so both round-55 counters
strip GIT_* from every git call, grounding the hermetic-git method in the exact injection
mechanism | mined | 2026-10-27 | 360d | corpus/lessons/round-55.md |
```

## Cell-by-cell verdicts

1. **Source URL / anchor** — AGREE. The live page (and the committed copy) contains
   `id="Documentation/git-config.txt-GITCONFIGCOUNT"` (grep count 2: the `dt` id and its inner
   `<a class="anchor" href=...>`). It is the `<dt>` heading `GIT_CONFIG_COUNT` of the ENVIRONMENT
   section definition list (out/S1Source511/gitconfigcount-section.txt line 1). The fragment
   `#Documentation/git-config.txt-GITCONFIGCOUNT` therefore resolves.
2. **Quote verbatim** — AGREE (one typographic normalization). Page sentence: "If GIT_CONFIG_COUNT
   is set to a positive number, all environment pairs GIT_CONFIG_KEY_<n> and
   GIT_CONFIG_VALUE_<n> up to that number will be added to the process's runtime configuration."
   The row's quoted substring matches every character after tag/entity stripping **except** the
   apostrophe: the HTML source is `process&#8217;s` (U+2019 RIGHT SINGLE QUOTATION MARK), the row
   uses ASCII `'` (U+0027). Verbatim-modulo-U+2019 confirmed programmatically (`verbatim-modulo-
   apostrophe: True`). Given the corpus stores quotes as plain ASCII, this is a rendering
   normalization, not a wording error. No defect raised.
3. **Quote ≤ 25 words** — AGREE. 18 words by `len(quote.split())`, both for the row text and the
   page text (`row quote words: 18`, `page quote words: 18`).
4. **Quote at the named anchor** — AGREE. The sentence is the first paragraph of the `<dd>` of the
   definition list whose `<dt>` carries `id="Documentation/git-config.txt-GITCONFIGCOUNT"`
   (extract lines 1–6 of out/S1Source511/gitconfigcount-section.txt).
5. **Scope claim "overriding config files"** — AGREE, verbatim basis on the page: "These
   environment variables will override values in configuration files" (extract lines 9–10).
6. **Scope parenthetical "(e.g. core.hooksPath reaches an attacker hook)"** — [INFERENCE] AGREE.
   Not page text; it is the lane's attack scenario, corroborated in-fleet by the C2 counter's own
   comment `tools/round54-cited-path-check.py:201` ("GIT_CONFIG_COUNT reached core.hooksPath and
   executed an attacker hook"). Consistent with the page mechanism (arbitrary keys injectable).
7. **Override order (seat check): env pairs override config files, overridden by `git -c`** —
   AGREE, exact: "These environment variables will override values in configuration files, but
   will be overridden by any explicit options passed via `git -c`." (extract lines 9–11).
8. **Teaches tail "so both round-55 counters strip GIT_* from every git call"** — AGREE, verified
   in source: `tools/round54-replay-code-audit.py:170` and `tools/round54-cited-path-check.py:202`
   both build the git-call environment as
   `env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}`.
9. **Live vs committed copy** — AGREE (copies identical). sha256 of both the live fetch and
   `.ufo/waves/round-55/sources/git-docs-git-config.html` is
   `706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a`; `cmp` reports the two files
   byte-identical, `diff -q` reports no differences. Evidence: out/S1Source511/sha256-and-diff.txt;
   the live fetch itself is preserved at out/S1Source511/git-config-live-2026-10-27.html.

## Commands and outputs (key)

```
$ curl -sSL -o git-config-live.html https://git-scm.com/docs/git-config   # exit 0, 830605 bytes
$ sha256sum git-config-live.html .ufo/waves/round-55/sources/git-docs-git-config.html
706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a  git-config-live.html
706b1566467e9cd8c6cdda853a5fc82118a48fde3119777d18cefc014bcd3d5a  .../sources/git-docs-git-config.html
$ cmp git-config-live.html .../sources/git-docs-git-config.html && echo identical   # identical
$ grep -c 'id="Documentation/git-config.txt-GITCONFIGCOUNT"' page → present (dt + anchor a)
```

Section text extracted (whitespace-normalized) at out/S1Source511/gitconfigcount-section.txt; raw
HTML source around the quote shows `added to the process&#8217;s runtime configuration`.

## Defects

None. One observation recorded for the corpus maintainers (not a defect): the row's straight
apostrophe vs the page's U+2019 in "process's"; also the recheck TTL is 360d against a live page
that can change at any time (the row already carries an HTML copy as mitigation).

## Evidence index (this seat's out dir)

- `out/S1Source511/sha256-and-diff.txt` — hashes and cmp result
- `out/S1Source511/git-config-live-2026-10-27.html` — the fetched live page (copy cited)
- `out/S1Source511/gitconfigcount-section.txt` — normalized section extract with the quote,
  override-order sentence, and the GIT_CONFIG_COUNT/GIT_CONFIG_KEY_<n>/GIT_CONFIG_VALUE_<n> dts

No lane files were modified; no tools installed; no services started. Scratch
`/fast/scratch/hyaku/kama-r55/w1/S1Source511` removed after writing this report.
