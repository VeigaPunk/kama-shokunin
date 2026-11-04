# SCR01Sources — round 74 w1: os-release(5) source row + knowledge entry (C3 frontier step)

Seat: SCR01Sources (sourced-claim seat, C3). Round-74 claims freeze read in full first
(`plans/round-74-claims.md`); the freeze was not edited and no frozen tool was touched.
All writes stayed inside `kama-shokunin/` (only the seat's wave paths) and
`/fast/scratch/hyaku/kama-r74/SCR01Sources/`. No git/jj mutations anywhere. No tools
installed this seat.

## Axes

- **Expansion (judged):** one new registry row S546 (os-release(5)) + one new knowledge
  entry (`host-block-base-revision.md`) drafted, mirror-census-gated exit 0, staged for L1
  append.
- **Calibration / operability:** the census gate ran before any append (routed defect 6 /
  round-74 lesson mistake 2's order) — mirror gate exit 0 is the receipt the L1 needs.
- **Freshness:** access date 2026-11-04, sha256-pinned retained bytes, 180d recheck.

## Step 1 — id-reuse check (lane registry has no os-release row)

Command and output (verbatim, exit 1 = no match):

    $ grep -i 'os-release' /home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
    (no output)

A row-scoped check of the Registry table finds no `S###` mentioning os-release (the only
`os-release` strings in the file are the `ID=` field references inside existing rows'
scope/teaches cells — e.g. S544's scope text names `/etc/os-release` as the field source,
which is the companion uname(1) row, not an os-release(5) row). No STOP condition.

## Step 2 — live fetch, retained bytes, access date, located quote

    $ curl -sSfL https://man7.org/linux/man-pages/man5/os-release.5.html \
        -o .ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html
    $ sha256sum .ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html
    c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e  .../os-release.5.html
    $ ls -lh .../os-release.5.html
    -rw-r--r-- 1 vgpnk vgpnk 45K Nov  4 00:45 .../os-release.5.html

- Access date: **2026-11-04** (today; fetch succeeded 200, 45,239 bytes).
- Retained at: `.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html`
  (path relative to `kama-shokunin/`).
- Located quote (16 words, ≤25), grounds the `ID=` field semantics — §OPTIONS,
  "General information identifying the operating system", `ID=` entry, retained HTML
  lines 187–194 (line 187 is the `<i>ID=</i>` anchor; the sentence runs lines 188–191):

  > "A lower-case string … identifying the operating system, excluding any version
  > information and suitable for processing by scripts"

  (Ellipsis elides the parenthetical character-set "(no spaces or other characters
  outside of 0–9, a–z, ".", "_" and "-")" — 10 words — to fit the 25-word cap; the
  elided text is quoted in full in the row's anchor cell.)

## Step 3 — id derivation (next id after registry maximum)

Parse of the live Registry table (delimited rows between `## Registry` at line 9 and the
next `## ` heading at line 302):

    Total rows in registry: 285
    Max id: S545 number: 545
    Last row in file: S545

Derivation: `corpus/SOURCES.md` lines 13…297 carry rows S001…S545; the maximum parsed
numeric id is **S545** (`| S545 | Git gitmodules manual …`, line 297). Cross-checks:
`grep -rn 'S546' corpus/` returns nothing (no dangling citation of the next id); the
row uses **S546**.

Drafted row (queued per spec — the L1 flips status to `mined` once the knowledge entry
cites it at integration; full text at
`drafts/SOURCES-S546-row.md`):

    | S546 | Linux os-release(5) manual page — https://man7.org/linux/man-pages/man5/os-release.5.html | docs | A | the `ID=` field of `/etc/os-release` as the distribution component of the host-identity triple C3 records; fixes the field's semantics, not that the triple identifies a host | §OPTIONS, `ID=` entry, lines 187-194 of the retained HTML ("A lower-case string ... identifying the operating system, excluding any version information and suitable for processing by scripts"); fetched bytes sha256 c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e retained at `.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html` (accessed 2026-11-04) | `ID=` identifies the operating system, excluding any version information, suitable for processing by scripts or generated filenames; unlike optional `ID_LIKE`, it defaults to "linux" when unset | queued | 2026-11-04 | 180d | corpus/knowledge/host-block-base-revision.md |

Field-shape check: 13 pipe-delimited fields (NF=13 per SOURCES-CONTRACT-v1), kind `docs`,
tier `A`, status `queued`, opened `2026-11-04`, recheck `180d`, used-by
`corpus/knowledge/host-block-base-revision.md` — exactly as the seat spec freezes.

## Step 4 — knowledge entry draft

`drafts/host-block-base-revision.md` opens with the provenance trio:

    source: S546 — Linux os-release(5), https://man7.org/linux/man-pages/man5/os-release.5.html
    (docs, tier A, queued→mined on this entry, accessed 2026-11-04; row in corpus/SOURCES.md):
    §OPTIONS `ID=` — "A lower-case string … identifying the operating system, excluding
    any version information and suitable for processing by scripts".
    verified-at: 2026-11-04 — plan plans/round-74-claims.md §C3 read; page fetched live
    (sha256 c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e); r73 counter
    read as the frozen base leg. No counter run is claimed here.
    recheck: 180d — curl the page; re-locate the §OPTIONS `ID=` entry.

Body documents the v2 block grammar per the frozen C3 predicate: the `recorded at <rev>`
token; base-revision preservation (block text with the token sentence stripped must be
byte-identical at `<rev>` and at the tip — the strip convention is the one the lane's
Round-73 block already states in its own text at `PROVINCE.md:310`; an edited block is a
finding even when it matches the live triple); the honest host-move answer (append, never
edit); and the os-release `ID=` grounding for the triple's third component (version-free
distribution identity, `ID_LIKE` explicitly unread).

## Step 5 — scratch-mirror census gate (before any append)

Mirror: `/fast/scratch/hyaku/kama-r74/SCR01Sources/mirror-lane/` — a byte copy of the
lane's `corpus/` plus the repo-root used-by targets the registry references
(`SCORECARD.md`, `SKILL.md`, `tools/`, `registry/`, `tests/`, `.ufo/waves/round-29/`).
A corpus-only mirror was tried first and cannot exit 0: pre-existing mined rows cite
repo-root paths (E11 `missing used-by SCORECARD.md` etc.), so the mirror must resolve
those paths for the gate to be meaningful. The real lane registry validates exit 0 today
(receipt below), so the mirror aims to reproduce that.

Baseline mirror (no S546): exit 0, sole non-warning line
`file	ok	…/mirror-lane/corpus/SOURCES.md`.

After inserting the S546 row after the S545 line and copying the knowledge draft into
the mirror's `corpus/knowledge/`:

    $ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate \
        --file /fast/scratch/hyaku/kama-r74/SCR01Sources/mirror-lane/corpus/SOURCES.md
    EXIT=0
    file	ok	/fast/scratch/hyaku/kama-r74/SCR01Sources/mirror-lane/corpus/SOURCES.md

Diff vs baseline: non-warning output **identical** (`ok` line only); warning-set diff
**empty** — S546 adds no E-codes and no W-codes. Gate requirement (exit 0) met; the L1
can append. Full validate transcript retained at scratch
`mirror-validate-final.out` (scratch deleted at yield; the command above is reproducible
verbatim by the L1 against its own mirror).

Control — the live registry still passes today (unchanged by this seat):

    $ scripts/sources-census.sh validate --file kama-shokunin/corpus/SOURCES.md
    → exit 0 (warnings only: pre-existing W01 x1, W04 x108; final line
      `file	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md`)

## Step 6 — drafts staged for L1

- `.ufo/waves/round-74/w1/SCR01Sources/drafts/SOURCES-S546-row.md` — the row, one line,
  append-ready (insert after the S545 line, before the blank lines ending the Registry
  table).
- `.ufo/waves/round-74/w1/SCR01Sources/drafts/host-block-base-revision.md` — the knowledge
  entry, append-ready at `corpus/knowledge/host-block-base-revision.md`.
- `.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html` — retained bytes,
  sha256 c7ba68ea45180c33bad72a3b47cf09e3d6d34d0a5313a5acf73a14fc64f8a74e.

The real `corpus/SOURCES.md` and `corpus/knowledge/` were **not** touched.

## Findings / limits

- No disagreement with the freeze. One observation, not a disagreement: the frozen C3
  predicate says "byte-identical block text at `<rev>` and at the worktree tip", while the
  Round-73 block's own parenthetical (`PROVINCE.md:310`) and this entry implement the
  comparison with the `recorded at` token sentence stripped — otherwise a token added by a
  later commit could never compare equal at `<rev>`. The draft follows the block's stated
  convention; EX03HostDrift's counter owns the exact leg.
- The quote's ellipsis is disclosed in the row and here; the anchor cell carries the
  full sentence.
- No counter runs are claimed by this seat (the entry's `verified-at` says so explicitly).

## Artifacts

| Artifact | Path (relative to `kama-shokunin/`) |
|---|---|
| Report | `.ufo/waves/round-74/w1/SCR01Sources/report.md` |
| Seat summary (Report: trailer path) | `.ufo/waves/round-74/w1/SCR01Sources.md` |
| Retained source bytes (sha256 c7ba68e…8a74e) | `.ufo/waves/round-74/w1/SCR01Sources/source/os-release.5.html` |
| Registry row draft | `.ufo/waves/round-74/w1/SCR01Sources/drafts/SOURCES-S546-row.md` |
| Knowledge entry draft | `.ufo/waves/round-74/w1/SCR01Sources/drafts/host-block-base-revision.md` |
