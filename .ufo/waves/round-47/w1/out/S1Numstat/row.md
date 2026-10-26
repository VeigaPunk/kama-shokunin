# S489 — git `--numstat` (registry row, ready to paste)

Verdict: one `mined`, tier-A row for the `git diff --numstat` contract; `sources-census.sh validate`
reports `file ok` with exit 0 and adds no E/W finding. The page supports "deleted = numstat
deletions" and "binary skipped"; it does **not** document the `\ No newline at end of file` marker.

## Row (single line, 11 cells, NF=13 — paste after S487)

```
| S489 | git-diff manual, `--numstat` — https://git-scm.com/docs/git-diff | docs | A | what `git diff --numstat` prints per path: added and deleted line counts, and `-` in place of both for a binary file; not the line-splitting algorithm, not CRLF or final-line identity, and not the `\ No newline at end of file` patch marker | §OPTIONS `--numstat`, rendered lines 3419-3425 (git-diff 2.56.0, page bytes SHA-256 5ae80d1deee5dc2c1acafff5491c5ba019629b9a785e6781a3e8a411cf9e22ed) and §other diff formats, rendered lines 2315-2345 (diff-format 2.55.0, page bytes SHA-256 a486a5f8aa7c75fa7f114547af55a976baf026e5e387f287127e6c6656e2b078); unusual-pathname quoting rule at diff-format rendered lines 2057-2060; neither page contains the newline marker (grep count 0); opened 2026-10-26 | Quote (20 words): "shows number of added and deleted lines in decimal notation and pathname without abbreviation, to make it more machine friendly"; for binary files it "outputs two - instead of saying 0 0"; diff-format names the third entry field "the number of deleted lines" and warns an unusual pathname is quoted unless `-z` | mined | 2026-10-26 | on-release | tools/append-only-audit.py, tools/round47-append-audit-v2-check.py, registry/append-only-contract.tsv |
```

## Cells

| field | value |
|---|---|
| id | S489 |
| source | git-diff manual, `--numstat` — https://git-scm.com/docs/git-diff |
| kind | docs |
| tier | A |
| scope | what `git diff --numstat` prints per path: added and deleted line counts, and `-` in place of both for a binary file; not the line-splitting algorithm, not CRLF or final-line identity, and not the `\ No newline at end of file` patch marker |
| anchor | §OPTIONS `--numstat`, rendered lines 3419-3425 (git-diff 2.56.0, page bytes SHA-256 5ae80d1deee5dc2c1acafff5491c5ba019629b9a785e6781a3e8a411cf9e22ed) and §other diff formats, rendered lines 2315-2345 (diff-format 2.55.0, page bytes SHA-256 a486a5f8aa7c75fa7f114547af55a976baf026e5e387f287127e6c6656e2b078); unusual-pathname quoting rule at diff-format rendered lines 2057-2060; neither page contains the newline marker (grep count 0); opened 2026-10-26 |
| teaches | Quote (20 words): "shows number of added and deleted lines in decimal notation and pathname without abbreviation, to make it more machine friendly"; for binary files it "outputs two - instead of saying 0 0"; diff-format names the third entry field "the number of deleted lines" and warns an unusual pathname is quoted unless `-z` |
| status | mined |
| opened | 2026-10-26 |
| recheck | on-release |
| used-by | tools/append-only-audit.py, tools/round47-append-audit-v2-check.py, registry/append-only-contract.tsv |

## Gate

`<scratch>` below is `/fast/scratch/hyaku/kama-r47/S1Numstat`, removed at close; the transcripts are
copied verbatim as `validate-mini.out`, `fullbase.validate.out`, `full.validate.out` in this
directory. Each mirror symlinks every lane top-level entry (including the dotfile `.ufo`) and every
`corpus/` child except `SOURCES.md`, so `used-by` paths resolve as in the lane.

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file <scratch>/mini/corpus/SOURCES.md --today 2026-10-26
file	ok	<scratch>/mini/corpus/SOURCES.md
exit 0

$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
    --file <scratch>/full/corpus/SOURCES.md --today 2026-10-26     # lane registry + this row
exit 0, 95 lines, 0 E codes, finding set identical to the unchanged base copy, no S489 line

$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file <scratch>/full/corpus/SOURCES.md
file	rows	229          (base copy: 228)
file	tier.A	218        (base copy: 217)
```

## Does the page support the C1 counter's rule?

| C1 rule | supported? | located evidence |
|---|---|---|
| deleted count = numstat deletions | yes, for text files | git-diff §OPTIONS `--numstat`, rendered 3419-3425: "shows number of added and deleted lines in decimal notation"; diff-format §other diff formats, rendered 2315-2345: entry field "the number of deleted lines" |
| binary files are skipped | yes, as the only consistent reading | git-diff rendered 3424-3425: "For binary files, outputs two - instead of saying 0 0" — no numeric deletion count exists to compare; the counter's `parts[1].isdigit()` guard (`tools/append-only-audit.py:170`) skips exactly those records. The page states the output shape, not the consumer policy |
| per-path records with `--no-renames` | yes | git-diff rendered 3710 `--no-renames`; rendered 3419-3425 pathname is the third field |
| deleted count equals hunk-header `-` count | **not documented** | the page gives the entry shape, not the counting algorithm; the equality the tool asserts (`tools/append-only-audit.py:203`) is implementation-derived (fixture: 2 == 2) |
| CRLF kept in the line; final segment without newline is a line | **not documented** | the page is silent on line splitting; this is the tool's own definition, sourced by the C1 fixture |
| pathnames are printed verbatim | **no, and this bites** | diff-format rendered 2057-2060 and git-diff rendered 3500-3512: without `-z`, unusual pathnames are quoted per `core.quotePath`; both `numstat()` parsers key on the tab-split path |
| `\ No newline at end of file` marker | **not on either page** | `grep -c` = 0 on both fetched pages; the literal is `diff.c:1868` at git v2.56.0 |

## Notes

- Page versions: git-diff 2.56.0 (page text line 1279), diff-format 2.55.0 (line 1233); page bytes
  SHA-256 5ae80d1d… / a486a5f8…, copies in this directory.
- `mined` with three used-by paths that all exist at lane tip 3a09a1d9
  (`tools/append-only-audit.py`, `tools/round47-append-audit-v2-check.py`,
  `registry/append-only-contract.tsv`).
- Row id S489: S001-S487 exist in the lane registry and S488 is taken by the L1's b11909 release row
  (`.ufo/waves/round-47/w1/out/U2Pins.md:27`); S489 is the next free id. Renumber on integration if
  another seat claims it.
- "rendered lines N" means line N of this seat's text extraction of the fetched page bytes:
  strip `<script>`/`<style>`, strip tags, `html.unescape`, collapse runs of 3+ blank lines to one.
  The page sha256 in the anchor pins the bytes; the extraction is reproducible from them.
- The scope cell deliberately excludes the newline marker: no page support exists, so the row must not
  be read as sourcing it. If the round needs that claim, its source is the code literal
  (`diff.c:1868`), kind `code`, not these documentation pages.
