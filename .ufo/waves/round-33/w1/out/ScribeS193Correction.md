# ScribeS193Correction — SOURCES contract-v1-safe correction for S193's quote location/count

- Round / wave: 33 / w1. Role: scribe (leaf; no subagents, no dispatch).
- Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`, read-only throughout.
- Read at lane tip `7c35289da5f4b94e062cd900eb086919e5094003` (branch `master`).
- Assignment: read the opened gate docstring at `c4c46ad5` and the round-32 lesson `## Gate`; state
  the exact anchor, verbatim quote, word count, and the append-only replacement-row requirements.
- Tools installed or upgraded: **none** (no install was needed; all work used git, coreutils, awk and python3 stdlib).

## Verdict

The round-32 `## Gate` record is false in two checkable fields at its own writing revision and
non-verbatim in a third:

| field as filed in round 32 | actual at the writing revision | class |
|---|---|---|
| location `line 22` | sentence spans **lines 15–16**; line 22 is the `empty-entry` defect bullet | false |
| count `16 words` | **17** whitespace-delimited words | false |
| quote `A path is registered …` | source reads `A path is ``registered`` …` (double-backtick inline-literal markup) | not byte-verbatim |

The contract-v1-safe correction is **not an edit to S193**. Under `SOURCES-CONTRACT-v1` rule 2 the
only permitted repair for a row's `anchor`/`teaches` is a **new row** whose `teaches` opens
`supersedes S193 —`, plus an **appended** round-lesson `## Gate` record (rule 1). That shape is what
the landed S194 row realizes; the exact anchor, quote, count and the full requirement checklist are
below.

## 1. Opened source and exact anchor

| field | value |
|---|---|
| source | `tools/gate-registry-check.py` (own-work, tier A candidate) |
| revision evaluated | `c4c46ad5b87d8b63f03e200a7b13eb8eeff46279` |
| git blob | `0183e55cb8243b1b87833a62123d0fa4352a596b`, mode `100755`, 15140 bytes |
| sha256 of blob | `e07cf8d753560cd34b5945c89f4dc3f19122ca87d19f8e85844e3b1ae4e0506b` |
| byte-identical at | `dc4258bdb08d658f1c5b15abc8378461659bd155` (the round-32 lesson's writing revision), `967d88528c1d83535563f971863f7855f76b4849` (round-33 C2 gate source), `c4c46ad5…`, and `HEAD` `7c35289…` — same sha256 at all four |
| section | module docstring; docstring opens at file line 2 (`"""gate-registry-check.py -- …`), the `Contract:` bullet block starts at file line 10 (the file contains exactly one `^Contract:` line), docstring closes at file line 55 |
| sentence line span | **15–16** — minimal span; the sentence starts mid-line 15 and ends mid-line 16 |
| start | line 15, column 27 (1-based), byte offset 780 |
| end | line 16, column 27 (the period of `table.`); exclusive end column 28; byte offset 860 |
| byte length in source | 80 (includes the wrap: one newline + six-space indent) |
| immediate context | line 15 is preceded by `evaluated revision. `; line 16 is followed by ` A prose mention (a wave-artifact paragraph, a` |
| uniqueness | `grep -n "A path is"` at the pinned revision → one hit, line 15 |

Source lines, verbatim (leading indentation included):

```
L15:       evaluated revision. A path is ``registered`` iff it occurs in a cell of
L16:       a row of such a table. A prose mention (a wave-artifact paragraph, a
```

The sentence occupies `L15[26:]` and `L16[:28]`; the six-space indentation on line 16 is not part
of the sentence.

Line 22 at the same revision — the location the round-32 lesson names — is:

```
        * ``empty-entry``     the Kind / entry command cell is empty;
```

i.e. a defect bullet in the docstring's `Meaning, graded per registered row` list, not the
registration sentence.

## 2. Verbatim quote

With the source's own markup:

```
A path is ``registered`` iff it occurs in a cell of a row of such a table.
```

- `registered` is wrapped in **double backticks** in the source (RST inline literal); the round-32
  lesson and the S193 row both render it as bare `registered`, which is why neither quote is
  byte-verbatim.
- Terminal punctuation is a single period after `table.`; no other punctuation occurs inside the
  sentence.
- **Normalization that must be declared:** the sentence is wrapped across two source lines
  (`… cell of` + newline + six spaces + `a row …`). Any single-line presentation collapses
  `\n` + six spaces to one space. Source form is 80 bytes; the single-line form is 74 bytes.
  17-word count is invariant under this normalization; byte identity is not.

## 3. Word count

**17 whitespace-delimited words**, identical whether the double-backtick markup is retained or
stripped:

```
A(1) path(2) is(3) ``registered``(4) iff(5) it(6) occurs(7) in(8) a(9) cell(10)
of(11) a(12) row(13) of(14) such(15) a(16) table.(17)
```

Reproduced two ways: `python3` `split()` on the extracted sentence → 17; `wc -w` on the single-line
quote with and without the markup → 17 and 17. **16 is unreachable by any whitespace rule applied to
the filed sentence**: the sentence has exactly 17 whitespace-separated tokens, so 16 requires
dropping precisely one token (e.g. `iff` or `A`) with no stated rule. The filed `(16 words.)` is an
arithmetic/location slip, not a different tokenization.

## 4. The superseded statement, named verbatim

Filed in `corpus/lessons/round-32.md` lines 27–28 (single commit `dc4258bdb`, unchanged since):

```
Located quote (docstring, "Contract" section, line 22): "`A path is registered iff it occurs in
a cell of a row of such a table.`" (16 words.)
```

Two related imprecisions sit in the S193 row itself (they are imprecise, not false — which is why
they also need a superseding row rather than an in-place fix):

- `anchor` cell: `docstring "Contract" section, read 2026-10-24 at c4c46ad5…` — no line span,
  against the contract's `anchor — exact section / heading / page / line plus revision`.
- `teaches` cell quote drops the double-backtick markup, so the row's own quote is not byte-verbatim.

A third record, `corpus/lessons/round-32-verifier-spotcheck.md:65,81`, names the start line only
(“source at c4c46ad5 has it at line 15”) and 17 words; it is correct as far as it goes but is an
incomplete span. Filed bytes stay; the correction should name it so the three records do not read as
contradictory.

## 5. Append-only replacement-row requirements (`SOURCES-CONTRACT-v1`)

Each requirement is keyed to the frozen contract (`/home/vgpnk/Projects/shokunin/.ufo/waves/kaika/SOURCES-CONTRACT-v1.md`)
and to the census block the contract prints.

1. **No in-place edit of S193.** Rule 2: only `status`, `recheck` and `used-by` change in place.
   `anchor` and `teaches` are outside that set, so S193's anchor/quote cannot be rewritten — the
   correction must ride a new row.
2. **New row, next unused id, never reused.** Shape block. A further correction after S194 would be
   S195 and must itself open `supersedes S194 —`; ids form an append-only chain and are not recycled.
3. **`teaches` opens exactly `supersedes S193 — `.** Rule 2’s literal form: the token `supersedes`,
   the old id, a space, U+2014 EM DASH, a space. (Byte-checked in the landed S194 row:
   `73 75 70 65 72 73 65 64 65 73 20 53 31 39 33 20 2014 20`.)
4. **Row shape.** 11 columns → `NF=13` under `awk -F'|'`; **no `|` inside any cell**. Any violation
   makes the contract's “malformed rows — must print 0” check fail.
5. **Enums.** `kind` = `own-work` here; `tier` = `A` is permitted for “the lane's own re-runnable gate
   output”; `community` is never A; `status` ∈ {queued, mined, rejected}.
6. **Anchor names section + line span + full 40-hex revision**, never a bare path or homepage:
   `docstring "Contract", lines 15–16 (…) @ c4c46ad5b87d8b63f03e200a7b13eb8eeff46279`.
7. **Quote in the row is ≤25 words** (rule 1 states the bound for the lesson record; the row should
   carry the same located quote) — here 17 — and the row or lesson must **declare the wrap
   normalization** (§2), otherwise a byte-comparing verifier is entitled to call it non-verbatim.
8. **`status: mined` requires a citing path.** `mined` means “cited by ≥1 path in `used-by`”, and the
   contract's census resolves every `used-by` path with `[ -e "$p" ]`. The citing lesson must exist at
   the evaluated revision — land the row in the same commit as its lesson (or later). Observed: the
   round-33 lesson exists at the S194-add commit `88331197a7de5fcc171bc7290fdd7beb43487a63` and the
   used-by existence sweep prints nothing.
9. **Rule 1 companion record.** The correction is only half-done with a row: the round lesson's
   `## Gate` must record, for the new row, the repo path (own-work), the access date, and the
   ≤25-word quote with its location grounding `teaches`. This is the paragraph that must name the
   superseded sentence verbatim (§4).
10. **Rule 5 search log.** The bounded search that produced the row gets one prose note in
    `corpus/SOURCES.md` §Search log (question/where/date/identified–screened–included–excluded/stop).
    Observed: the 2026-10-24 note records 2 identified, 2 screened, 1 included (S194), 0 excluded.
11. **Frozen bytes stay frozen.** The round-32 lesson remains byte-identical at `dc4258bdb`
    (`git log -- corpus/lessons/round-32.md` → exactly that one commit), the filed round-32 report is
    not rewritten, and S193's row is not touched. Corrections **append** and **name** the superseded
    statement; they never silently delete it.
12. **One-directional supersession, no status change.** There is no `superseded` status enum, so S193
    stays `mined`; only the new row names the old one. Rule 6 also applies: no credential material,
    no session/private URLs, no `op://` references.
13. **Census after insertion.** The contract's block must stay clean: rows 194, malformed 0, duplicate
    ids none, tier A/B/C 189/2/3, status mined/queued/rejected 175/8/11, used-by paths all existing;
    `validate` exit 0.

## 6. Draft correction text (append-only, paste-ready)

### 6a. Replacement row — contract-compliant form

This is the canonical text for the correction. It is realized by the landed S194; the parenthetical
column anchors and the normalization clause are the two strengthenings the landed row leaves implicit
(see §7, F2/F3).

```
| S194 | Gate registry check v2 — kama lane instrument — tools/gate-registry-check.py | own-work | A | the exact meaning of gate registration in the v2 contract docstring; not endpoint health or proof that another registered instrument is correct | docstring "Contract", lines 15–16 (sentence starts line 15 col 27 after `evaluated revision. `; ends line 16 col 27 at the period; the wrapped line break + 6-space indent renders as one space) @ c4c46ad5b87d8b63f03e200a7b13eb8eeff46279, opened 2026-10-24 | supersedes S193 — the registration sentence is at lines 15–16 and reads `A path is ``registered`` iff it occurs in a cell of a row of such a table.` (17 whitespace-delimited words); the scope stays the five-column registry table | mined | 2026-10-24 | on-release | corpus/lessons/round-33.md, SKILL.md |
```

Checks run mentally against §5: 11 columns, no `|` in cells, enums valid, `supersedes S193 — `
verbatim, quote 17 ≤ 25, `mined` with two existing `used-by` paths.

### 6b. Append candidate for the round-33 lesson `## Gate` (never the round-32 lesson)

```
**S193 quote correction — appended 2026-10-24, superseding the round-32 §Gate parenthetical.**
The round-32 Gate record reads, verbatim: `Located quote (docstring, "Contract" section, line 22):
"`A path is registered iff it occurs in a cell of a row of such a table.`" (16 words.)` Re-opened at
that lesson's own writing revision `dc4258bdb08d658f1c5b15abc8378461659bd155` (blob
`0183e55cb8243b1b87833a62123d0fa4352a596b`, sha256 `e07cf8d7…e0506b`, byte-identical at
`c4c46ad5…`), the sentence is at lines 15–16: it begins on line 15 at column 27 after
`evaluated revision. `, and ends on line 16 at the period of `table.`; line 22 is the `empty-entry`
defect bullet. It reads `A path is ``registered`` iff it occurs in a cell of a row of such a table.`
— 17 whitespace-delimited words, with `registered` wrapped in double backticks in the source; every
single-line presentation collapses the source's line break plus six-space indent to one space.
S194 appends the corrected anchor and quote; S193 and the round-32 lesson remain unchanged.
`corpus/lessons/round-32-verifier-spotcheck.md` names the start line only (line 15) and the same
17-word count; this record states the full span rather than contradicting it.
```

## 7. Compliance of the landed correction, and open residuals

Observed at `HEAD` `7c35289…` (S194 first added by `88331197a7de5fcc171bc7290fdd7beb43487a63`; the
row is byte-identical between that commit and HEAD — `git diff 8833119 HEAD -- corpus/SOURCES.md`
prints nothing).

| §5 req | landed evidence | status |
|---|---|---|
| 1 | S193 row byte-identical base `cc469803…` → HEAD (`diff` of the row → identical) | PASS |
| 2–4 | rows 194, malformed 0, duplicate ids none, S194 appended after S193, NF=13 | PASS |
| 3 | `teaches` opens `supersedes S193 — ` with U+2014 | PASS |
| 6 | anchor `docstring "Contract", lines 15–16 @ c4c46ad5…` | PASS; column anchors absent |
| 7 | quote retains ` ``registered`` `, 17 words ≤ 25 | PASS; wrap normalization unstated |
| 8 | round-33 lesson exists at the add commit; used-by sweep prints nothing | PASS |
| 9 | round-33 lesson `## Gate` line 14 records path, revision, access date, 17-word quote, lines 15–16 | PASS |
| 10 | `corpus/SOURCES.md` 2026-10-24 search-log note (2/2/1/0) | PASS |
| 11 | round-32 lesson: one commit `dc4258bdb`, untouched | PASS |
| 12 | S193 still `mined`; no superseded enum introduced | PASS |
| 13 | `sources-end-count.out` rows 194 / A 189 / B 2 / C 3 / mined 175 / queued 8 / rejected 11, `EXIT_CODE=0`; `census-end.out` `kama ok … EXIT_CODE=0` | PASS |

Residual findings for the L1 integration owner (report only — nothing here was edited):

- **F1 (defect, corrected).** Round-32 §Gate `line 22` + `16 words` are false at the lesson's own
  writing revision `dc4258bdb`; the gate blob is byte-identical there, so this is a write-time error,
  not later drift. Corrected by S194 + the round-33 lesson.
- **F2 (open, minor).** The **markup drift** — round-32 and S193 both render `registered` without the
  double backticks — is not named in the round-33 mistakes row 3, which describes only
  “location/count”. One clause in the appended record (§6b) closes it; the row already carries the
  markup correctly.
- **F3 (open, minor).** The wrap normalization is unstated everywhere: the source quote is 80 bytes
  over two lines, the presented quote 74 bytes on one. Safe today (no byte-comparing verifier of this
  quote exists), but it is the precise reason a future verifier could call the quote non-verbatim.
- **F4 (pointer).** `SKILL.md:1325` still ends “row semantics row S193”, while `SKILL.md:1336–1338`
  already cites S194. The SKILL registry table is not a SOURCES row, so rule 2 does not forbid a
  pointer edit; it is a live pointer to the superseded row and is the L1's call.
- **F5 (pointer, no action).** `corpus/README.md:520` (“S193 quote location/count … corrected by
  append-only records”) is consistent with this correction; `SCORECARD.md:1861–1866` likewise states
  lines 15–16 / 17 words and that S193 and the round-32 lesson stay unchanged.
- **F6 (structural).** S193's `anchor` cell still has no line span (contract: anchor must name a line).
  It cannot be fixed in place; S194 is the only permitted carrier, and S193 remains valid for its
  scope. No further row is warranted unless a verifier demands a byte-identical quote, in which case
  it would be S195 (`supersedes S194 —`).

## 8. Verification log (all read-only)

| # | command | observed |
|---|---|---|
| 1 | `git show c4c46ad5…:tools/gate-registry-check.py` | 15140 bytes; blob `0183e55c…`; sha256 `e07cf8d7…e0506b` |
| 2 | `git ls-tree c4c46ad5… tools/gate-registry-check.py` | `100755 blob 0183e55cb8243b1b87833a62123d0fa4352a596b` |
| 3 | `git diff --stat dc4258bdb c4c46ad5 -- tools/gate-registry-check.py` | empty (no change) |
| 4 | `sha256sum` of the blob at `dc4258bdb`, `967d88528c1d`, `c4c46ad5`, `HEAD` | `e07cf8d7…e0506b` at all four |
| 5 | `awk 'NR==15||NR==16'` / `NR==22` at `dc4258bdb` | lines 15–16 as quoted; line 22 = `* ``empty-entry``     the Kind / entry command cell is empty;` |
| 6 | python extraction of `L15[26:] + L16[:28]` | 80 bytes, byte offsets 780–860, 17 `split()` tokens, no tabs, no NBSP |
| 7 | `printf '%s\n' <quote> \| wc -w` (with and without ` `` `) | `17`, `17` |
| 8 | python `len()` on the single-line quote | 74 chars, 17 words |
| 9 | `grep -n "A path is"` at pinned rev | one hit, line 15 (anchor unique) |
| 10 | `grep -c "^Contract:"` at pinned rev | 1 |
| 11 | `awk` row-shape/dup/used-by checks on `corpus/SOURCES.md` | `S193 NF=13`, `S194 NF=13`, malformed 0, rows 194, duplicate ids none, used-by sweep silent |
| 12 | `diff` S193 row at `cc469803…` vs `HEAD` | identical |
| 13 | `git diff 8833119 HEAD -- corpus/SOURCES.md` | empty (S194 byte-stable since add) |
| 14 | `git cat-file -e 8833119:corpus/lessons/round-33.md` | exists (rule-1/`mined` timing satisfied at add) |
| 15 | `git log --format='%h %s' -- corpus/lessons/round-32.md` | one commit: `dc4258b round-32: docs — …` |
| 16 | `git log --format='%h %s' -- corpus/SOURCES.md` | `8833119` (S194), `dc4258b` (S193), `c16fe3e` (S192) |
| 17 | `cat .ufo/waves/round-33/sources-{start,end}-count.out` | 193→194 rows, A 188→189, B 2, C 3, mined 174→175, queued 8, rejected 11, both `EXIT_CODE=0` |
| 18 | `tail -3 .ufo/waves/round-33/census-{start,end}.out` | `kama ok …/corpus/SOURCES.md`, `EXIT_CODE=0` both |

No file in the lane was modified, added, staged or committed; no jj or git mutating command was run;
the filed round-32 lesson and report bytes were read only.

## 9. Limits

- This is evidence about **one own-work instrument docstring** at one pinned blob. It says nothing
  about endpoint health, model quality, service restoration, current registered-consumer health, or
  any other registered instrument's correctness.
- The verbatim quote exists only in wrapped form in the source; the 74-byte single-line rendering is a
  declared normalization (17-word count is normalization-invariant). No byte-identical single-line
  quote exists in the blob.
- Counts and census figures are **read from the committed round-33 evidence files** and from
  re-running the contract's own read-only `awk` checks; the lane's `sources-census.sh` / `validate`
  were not re-run by this seat, and no counter was re-executed.
- S194's landing state is reported as observed at `HEAD 7c35289…`; the row is byte-stable from
  `8833119`, so no later in-place edit occurred.
- The draft row and append paragraph are **proposals for the L1 integration owner**; this seat wrote
  only this report. No `agent://` broadcast was sent and no subagent was dispatched.
