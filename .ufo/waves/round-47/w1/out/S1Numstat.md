# S1Numstat — round 47 source for C1's numstat ground truth

**Verdict:** one `mined` tier-A row (S489, git `--numstat`) drafted and gated clean — `sources-census.sh validate` prints `file ok`, exit 0, zero E codes, no new finding — and the opened pages **do** support C1's deleted-equals-numstat rule and **do** support skipping binary files, but **neither page documents the `\ No newline at end of file` marker**, so the item's premise is half supported.

## Behaviour

Two documentation pages opened 2026-10-26, text extracted, quote located:

| page | version (page text) | bytes | sha256 |
|---|---|---|---|
| https://git-scm.com/docs/git-diff | "git-diff last updated in 2.56.0" (text line 1279) | 229155 | `5ae80d1deee5dc2c1acafff5491c5ba019629b9a785e6781a3e8a411cf9e22ed` |
| https://git-scm.com/docs/diff-format | "diff-format last updated in 2.55.0" (text line 1233) | 63322 | `a486a5f8aa7c75fa7f114547af55a976baf026e5e387f287127e6c6656e2b078` |

Located text (git-diff rendered lines 3419-3425):

```
--numstat
Similar to --stat, but shows number of added and
deleted lines in decimal notation and pathname without
abbreviation, to make it more machine friendly.  For
binary files, outputs two - instead of saying
0 0.
```

Row quote (20 words, verified substring of the whitespace-normalized page): *"shows number of added and deleted lines in decimal notation and pathname without abbreviation, to make it more machine friendly"*. Second locator: diff-format §other diff formats, rendered lines 2315-2345 (`Documentation/diff-format.adoc` lines 145-160 at git v2.56.0), where the entry fields are listed as "the number of added lines; a tab; the number of deleted lines; a tab; pathname".

Row: id `S489`, kind `docs`, tier `A`, status `mined`, opened `2026-10-26`, recheck `on-release`, used-by `tools/append-only-audit.py, tools/round47-append-audit-v2-check.py, registry/append-only-contract.tsv` (all three exist at tip `3a09a1d9`, `git ls-tree` shown in `S1Numstat/checks.txt` §7). Full row text: `S1Numstat/row.md`. The id is the next free one: `S001`-`S487` are in the registry and `S488` is the L1's b11909 release row (`.ufo/waves/round-47/w1/out/U2Pins.md:27`); renumber on integration if another seat claims `S489`.

## Gates

| command | exit | output |
|---|---|---|
| `sources-census.sh validate --file <S>/mini/corpus/SOURCES.md --today 2026-10-26` (header + the row only) | 0 | `file	ok	<path>` |
| `sources-census.sh validate --file <S>/fullbase/corpus/SOURCES.md --today 2026-10-26` (lane registry unchanged) | 0 | 95 lines: 93 W04, 1 W01 (S481), `ok` |
| `sources-census.sh validate --file <S>/full/corpus/SOURCES.md --today 2026-10-26` (lane registry + S489 after S487) | 0 | 95 lines, **identical finding set**, no line mentions S489, 0 E codes |
| `sources-census.sh census --file <S>/full…` vs `…fullbase…` | 0 | rows 228 → 229; tier.A 217 → 218 |

Scratch mirrors (`$S/mini`, `$S/fullbase`, `$S/full`) symlink every lane top-level entry *including the dotfile `.ufo`* and every `corpus/` child except `SOURCES.md`, so `used-by` paths resolve exactly as in the lane. A first pass without `.ufo` produced four bogus `E11` lines for S174-S177; those were mirror artefacts, not lane findings, and disappeared once `.ufo` was linked — the lane's `.ufo/waves/round-29/count-c1.py` exists.

## What the page supports, cell by cell

- **deleted = numstat deletions — supported** (text files): git-diff 3419-3425 plus diff-format 2315-2345.
- **binary skipped — supported as the only consistent reading**: "For binary files, outputs two - instead of saying 0 0" (git-diff 3424-3425); there is no numeric deletion count to compare, and `tools/append-only-audit.py:170` guards with `parts[1].isdigit()` exactly there. The page documents output shape; skipping is the instrument's policy, not a documented rule.
- **`--no-renames` per-path records — supported** (git-diff rendered line 3710).
- **deleted count equals the hunk-header `-` count — NOT documented.** The page never states numstat's counting algorithm; the equality the tool asserts at `tools/append-only-audit.py:203` (`len(dl) != ns[f]` → `AuditError`) is implementation-derived. My fixture (scratch, `git 2.56.0`, text file rewritten to one line) printed `0	2	text.md` and the hunk count is 2 — consistent, but one case, not a contract.
- **CRLF inside a line, and a final segment without newline counting as a line — NOT documented.** These are v2's own definitions (`tools/append-only-audit.py:27-29`), grounded by C1's fixture, not by git docs.
- **pathnames printed verbatim — NO.** diff-format rendered 2057-2060 and git-diff rendered 3500-3512: without `-z`, pathnames with "unusual" characters are quoted per `core.quotePath`; `-z` terminates fields with NUL and prints the filename verbatim.

## Findings

**F1 — the `\ No newline at end of file` marker is on neither opened page (item premise unsupported).**
`grep -c "No newline at end of file" git-diff.html diff-format.html` → `0`, `0`. The literal exists in code, not docs: `git v2.56.0 diff.c:1868 static const char nneof[] = "\\ No newline at end of file\n";`. Also absent from `Documentation/diff-format.adoc`, `Documentation/diff-generate-patch.adoc`, `Documentation/diff-options.adoc` (v2.56.0) and from every installed git man page (`zgrep -il` over `/usr/share/man/man1/git-*.1.gz`, `/usr/share/man/man5/git*.5.gz` → no match). Consequence: S489's scope cell excludes the marker; a marker claim needs a `code` row for `diff.c` (or the round must drop the marker from scope). Note the marker is a `-p` patch artefact and never appears in `--numstat`, so its absence does not weaken C1's numstat rule.
*Proposed action:* none inside the frozen counters; if the marker claim is needed, add the code row (L1 decision).

**F2 — both numstat parsers would silently miss a quoted pathname (defect, low reach today).**
`tools/append-only-audit.py:165-172` (`raw = _text(… "diff", "--numstat", "--no-renames" …)` then `parts[1].isdigit()` / `res[parts[2]]`) and the frozen counter's copy at `tools/round47-append-audit-v2-check.py:189-198` (line 193 same command, line 196 same `isdigit` guard) key on the tab-split third field. Per the pages above, a pathname with unusual characters is emitted quoted, so the key never equals the contract path and that file is never audited — with no refusal, which is the failure mode the round is trying to close. Demonstration of the output shape (page rule, not a lane repro): diff-format rendered 2057-2060.
*Reach today:* none — every contract path (`SCORECARD.md`, `LOG.md`, `corpus/QUALITY.md`, `corpus/README.md`, `corpus/SOURCES.md`, `corpus/lessons/*.md`) is ASCII, so no lane leg is affected; this is a robustness limit of the instrument, not a mis-scored claim.
*Proposed fix (not applied, counter is frozen; file is C1's subject so the edit belongs to the L1):* `S1Numstat/append-only-audit-numstat-z.proposed.patch` — add `-z`, split on NUL, read triplets (safe because `--no-renames` makes every record single-path). Residual limit after the fix: `_text()` decodes with `errors="replace"`, so non-UTF-8 path bytes still would not round-trip.

**F3 — W00 pre-existing lane warnings, unchanged by this row.** 93 `W04` duplicate-URL warnings and `W01 S481 tierC mined used-by=…` appear in the untouched base copy and are byte-identical with S489 inserted. Not mine, not repaired here (the registry is READ-ONLY for this seat).

## Touched surfaces

- Written: `.ufo/waves/round-47/w1/out/S1Numstat/` (row, report evidence, page copies, transcripts, fixture output, proposed patch) and `.ufo/waves/round-47/w1/out/S1Numstat.md` (this report).
- Read-only: lane `corpus/SOURCES.md`, `tools/append-only-audit.py`, `tools/round47-append-audit-v2-check.py`, `registry/append-only-contract.tsv`, `.ufo/waves/round-47/*`; fleet `scripts/sources-census.sh`; git-scm.com and raw.githubusercontent.com pages.
- Untouched: no lane file edited, no `git`/`jj` mutation anywhere, no fixture commit outside my scratch (the one fixture repo lives at `<S>/numstat-fixture`, toplevel asserted equal to it before the commit), no registry row inserted into the lane, no service started, no package installed (no install was needed; pacman untouched).

## Out of scope / not claimed

C1 and C2 counter runs, the lane measurement, integration of the row into `corpus/SOURCES.md`, and the b11909 row (S488, L1) were not touched. I did not re-run any counter; the row's support assessment is documentation analysis plus one scratch fixture.

## Artefacts

- `.ufo/waves/round-47/w1/out/S1Numstat.md` — this report
- `.ufo/waves/round-47/w1/out/S1Numstat/row.md` — the row, paste-ready, 11 cells, with cell table and gate
- `.ufo/waves/round-47/w1/out/S1Numstat/checks.txt` — every command, output and exit code
- `.ufo/waves/round-47/w1/out/S1Numstat/git-diff.html`, `diff-format.html` — fetched page bytes (sha256 above)
- `.ufo/waves/round-47/w1/out/S1Numstat/numstat-rendered-excerpt.txt` — rendered lines 3415-3430
- `.ufo/waves/round-47/w1/out/S1Numstat/validate-mini.out`, `fullbase.validate.out`, `full.validate.out` — gate transcripts
- `.ufo/waves/round-47/w1/out/S1Numstat/numstat-fixture.out` — scratch fixture `git diff --numstat` and `-U0` output (`-\t-\tbin.dat`, `0\t2\ttext.md`)
- `.ufo/waves/round-47/w1/out/S1Numstat/append-only-audit-numstat-z.proposed.patch` — proposed F2 fix
