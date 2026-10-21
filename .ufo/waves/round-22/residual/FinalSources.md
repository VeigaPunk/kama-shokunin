# FinalSources — round-22 residual source audit (S075–S086)

Seat: KamaR22.FinalSources. Pinned master `971d4549dff78e93327fbebaf1498e1c47db6661`
(scratch clone `FinalSources/clone`, removed after review; file digests in
`FinalSources/cmd/source-digests.txt`, production copy of `corpus/SOURCES.md`
byte-identical). All twelve rows reopened 2026-10-21 ~13:27 UTC, not a sample.
No production edit, no install, no delegation. Machine receipts:
`.ufo/waves/round-22/residual/FinalSources/receipts.json` (100 files, sha256 each).

## Verdict

**Twelve rows hold; no row needs a superseding correction.** All 19 lesson
quotes are verbatim in the live pages (`cmd/quote-locate.json`, 19/19), each
≤25 words (max 21). Every named section exists, and every revision label comes
from page content, not the URL. The S078–S086 `teaches` cells each begin
`supersedes S0NN —` (U+2014) naming the right predecessor, and each URL equals
its predecessor's (`cmd/row-audit.json`). `tools/sources-append-only.py --from
10271460 --to 971d4549 --json` exited 0: 0 violations, 12 added rows
(`cmd/append-only.out`). No scope inflation was found across the twelve rows.

There are two actionable record findings. Neither invalidates a quote.

- **F1 `used-by` gap (mutable cell, low).** `corpus/knowledge/llamacpp-loading-lifecycle.md`
  cites S075/S076/S077 in its `source:` line (l.375) and S077 again at l.393. Its
  round-22 correction paragraph (l.409–413) says current readings use S078/S079/S080.
  Rows S075–S080 still list only `corpus/lessons/round-22.md`. The precedent is
  S064–S068, which list the knowledge file they ground. The fix is to append
  that path to `used-by` for S075–S080. KQ22 allows this, and it needs no new row.
- **F2 Python alias drift (recheck trigger, low).** The `docs.python.org/3.14/`
  URL is a 3.14-series alias. At build time it carried the title "Python 3.14.8
  documentation" (footer 10:01 UTC; recorded in `build/advice/SrcOpen.md`,
  `SrcOsLstat.md` and `SourceReject.md`). It now renders "3.14.9 documentation"
  (footer "Last updated on Oct 21, 2026 (13:17 UTC)"). The S075–S077 quotes are
  unchanged on the 3.14.9 render. The host interpreter is still
  `Python 3.14.8` (`cmd/python-version.json`). The 3.14.8 label was correctly
  taken from page content and not guessed from the URL. However, the anchor
  wording "versioned 3.14.8 page" overstates the pin: the URL is versioned only
  to 3.14. No row change is needed. The SOURCES addendum MAY record "alias now
  renders 3.14.9, identical quoted text" the way R21 did for Nix 2.34.9.
  `[INFERENCE]` The page change probably reflects a 3.14.9 docs rebuild. I did
  not verify a CPython release.

## Per-row audit

| Row | URL (HTTP) | Revision evidence (from content) | Anchor located | Quote (words) | Status / used-by | Prefix / scope |
|---|---|---|---|---|---|---|
| S075 | builtins/functions.html#open (200; `library/functions.html` redirects here) | title now 3.14.9; build-time title 3.14.8 (F2) | Built-in Functions, `open()` entry ¶1 | "If the file cannot be opened, an OSError is raised." (10) ✓ | mined; F1 | no prefix (new row) ✓; "caller policy" correctly marked as own-work |
| S076 | library/os.html (200) | same as S075 (F2) | module-intro Note; os.listdir l.2338 and os.lstat l.2431 under Files and Directories | Note (21) ✓; "does not follow symbolic links" (5) ✓ | mined; F1 | ✓. The "so an intentional link skip differs…" clause is own inference. It is consistent with the lesson's Gate framing, so no action. |
| S077 | os.html#os.access (200) | same as S075 (F2) | the access section has two Notes (l.2049, l.2072); the quote is in the **second** ✓ | (12) ✓ | rejected; F1 | ✓ rejects the remedy, not the documentation |
| S078 | man7 ldconfig.8 (200) | footer "Linux man-pages 6.19 2026-08-03"; tarball man-pages-6.19 | DESCRIPTION chain example | (12) ✓; chain `libfoo.so -> libfoo.so.1 -> libfoo.so.1.12` and "compatibility issues after an upgrade" present | mined; F1 | `supersedes S066 —` ✓. "ldconfig expects" matches the page; the earlier R21 prose said "maintains". |
| S079 | man7 ld.so.8 (200) | "Linux man-pages 6.19 2026-08-03" | slash-less preamble; steps (1)–(5) at l.55–79; step (4) is the cache | (16) ✓; `symlink\|symbolic` sweep: 0 matches | mined; F1 | `supersedes S067 —` ✓. Steps 1–3 and 5 are directory searches and only step 4 uses the cache. The row says only that step 4 is not a directory walk, which is correct. |
| S080 | nix.dev 2.34 nix-archive (200) | title "Nix 2.34.9 Reference Manual" (supports "2.34-series"; same render already noted in R21 prose) | EBNF symlink production | `symlink = str("target"), str(target);` ✓ | mined; F1 | `supersedes S068 —` ✓. The scope wording matches the page's "serialize file system objects". |
| S081 | go.googlesource v0.42.0 hash.go (200, `?format=TEXT`) | tag in URL is a real revision pin | HashDir l.75–78; Hash1 loop l.48–63 | l.76 `os.Open(...)` ✓. The decode is byte-identical to `.ufo/waves/round-22/sources/dirhash-v0.42.0.go` (sha256 `24de6a73…cb297`). | mined | `supersedes S069 —` ✓. Hash1 writes only `%x  name`, with no target text. DirFiles (`filepath.Walk`) lists non-directory entries. |
| S082 | git-scm gitrevisions (200) | "gitrevisions last updated in 2.56.0"; `/2.56.0` pin has both quotes; host git 2.56.0 | SPECIFYING REVISIONS: `<sha1>` and `<rev>^{<type>}` | (9) ✓; peel text "…recursively until an object of type <type> is found…(in which case, barf)" | mined | `supersedes S070 —` ✓. "Commit-only is kama policy" is correctly marked. |
| S083 | git-scm git-cat-file (200) | "last updated in 2.56.0"; `/2.56.0` pin ✓ | BATCH OUTPUT (l.740–880); missing l.823; ambiguous l.832 | "an ambiguous short sha" (4) ✓; `<object> SP ambiguous LF` ✓ | mined | `supersedes S071 —` ✓. It drops R21's peel nuance and marks it as own-work. |
| S084 | docs.jj-vcs.dev/latest cli-reference (200) | the page shows **no** version string (regex over the HTML: none). The row correctly claims no pin. | `jj metaedit` description | (13) ✓. Installed `jj 0.45.1` `metaedit --help` has the identical sentence; this is corroboration only and not cited by the row. | mined | `supersedes S072 —` ✓. Author-time invariance is marked as own-work. |
| S085 | git-scm git-log (200) | "last updated in 2.56.0"; `/2.56.0` pin ✓ | PRETTY FORMATS `%at`/`%ct`; `--diff-filter` "Added (A)" | (4)+(4) ✓ | mined | `supersedes S073 —` ✓. The cutoff choice is marked as lane policy. |
| S086 | tldp shared-libraries.html (200) | "version 1.20, 11 April 2003" is on the guide's `index.html` title page, **not** on the anchor page (receipt `cmd/tldp-index.curl.out`). It is content-derived, not taken from the URL. | 3.1.1 Shared Library Names (`AEN49` present) | (16) ✓. The context reads "ldconfig makes no assumptions… so installers must…". | queued; `—` (same convention as S074) | `supersedes S074 —` ✓, tier B ✓ |

## Scope-inflation check (all twelve)

- Counts are consistent: there are 12 new rows, C1's S075–S077 plus 9
  correction rows. This appears in the SOURCES R22 addenda, the lesson
  (l.145–147), LOG (l.1285–1288) and the residual inventory ("12 source rows").
- Neither SOURCES nor the lesson counts S078–S086 as capability, knowledge
  surfaces or score. SOURCES says "not nine new knowledge surfaces". SCORECARD
  credits only S075/S076/S077 to C1 (l.1052).
- Every correction row narrows its predecessor. None adds a page claim. The
  own-work boundaries (digest consequence, author-time cutoff, commit-only
  policy, peel nuance, same-bytes retarget) are labelled in each `teaches`
  cell. The lesson Gate supplement (l.130–140) agrees with each row cell for
  cell.
- Unresolved: I could not reobserve R21's prose claim that `latest` jj "serves
  v0.46.0", because the current HTML has no version string. That claim is R21
  prose, outside these twelve rows, and S084 does not depend on it.

## Checks for main

The main agent could append `corpus/knowledge/llamacpp-loading-lifecycle.md` to
the `used-by` cells of S075–S080 (F1), then rerun
`python3 tools/sources-append-only.py --from 10271460cc575fc2280aa831e442726385fc2319 --to <new> --json`.
Optionally, record the F2 alias drift in the SOURCES R22 addendum.
