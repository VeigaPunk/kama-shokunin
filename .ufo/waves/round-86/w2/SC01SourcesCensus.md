# SC01SourcesCensus — round-86 source-row re-grade and census falsification (kama r86 w2)

Seat: scout (author-side advisory). No claim admission, no edit to production files, no commit,
no integration; the L1 is the sole committer and the non-author closure is the admission rule.

Measured revisions: frozen base `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`; committed master tip
at dispatch `67eddac89f44e768b670301ea0feff06e766f32d`; freeze `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`.
The worktree `corpus/SOURCES.md` is byte-identical to the tip blob
(`git -C /home/vgpnk/Projects/shokunin/kama-shokunin diff --quiet 67eddac8 -- corpus/SOURCES.md` → identical),
so the census run below measured the tip's registry bytes, not a dirty file.

Receipts in `.ufo/waves/round-86/w2/out/SC01SourcesCensus/receipts/`. Scratch
`/fast/scratch/hyaku/kama-r86/SC01SourcesCensus/` removed on exit.

No tooling was installed or updated (nothing was needed; `curl`, `git`, `python3`, `gawk` were
already present). No pacman transaction was attempted — the host-wide pacman pause was respected.

---

## 1. The census run the seat was asked to perform

```
$ /home/vgpnk/Projects/shokunin/scripts/sources-census.sh validate --root /home/vgpnk/Projects/shokunin kama
kama	W04	S031 duplicate url docs.ollama.com/api/tags across scopes
… 112 further W04 lines …
kama	W04	S578 duplicate url spec.commonmark.org/0.31.2 across scopes
kama	W04	S579 duplicate url spec.commonmark.org/0.31.2 across scopes
kama	ok	/home/vgpnk/Projects/shokunin/kama-shokunin/corpus/SOURCES.md
$ echo $?
0
```

**Exit code 0. Row count 319. Zero E-code findings. 116 warnings: 115 × `W04`, 1 × `W01`.**

Every warning, verbatim and complete, is in `receipts/01-census-validate-tip.out` (117 lines).
The warning population is:

| code | count | what it says | verdict on the round's rows |
|---|---|---|---|
| `W04` | 115 | `duplicate url <u> across scopes` | 113 pre-existing at base; **2 added by round-86: `S578` and `S579`**, both `duplicate url spec.commonmark.org/0.31.2 across scopes`. Full id list in `receipts/01`. |
| `W01` | 1 | `S481 tierC mined used-by=…` | pre-existing (identical at base and tip), unrelated to the CommonMark rows. |
| `E01`–`E12` | 0 | — | no malformed row, no enum violation, no tier inflation, no dangling used-by, no row outside `## Registry`. |

`W04` is warning-only and does not change the exit code, but it is a **new** warning introduced by
this round's two rows. The lesson discloses the mechanism correctly: the census's `url_of()`
strips the fragment (`sub(/#[^ ]*$/,"",u)`, `scripts/sources-census.sh:602`), so the four CommonMark
rows `S498`/`S576`/`S578`/`S579` normalise to one URL while their scopes differ. I confirmed the
strip is real (the script line above) and that the four rows do carry four distinct scope cells.

**Rows count, before → after.** Base 317 → tip 319 (the two new rows). Independently confirmed three ways
(`receipts/03`, `receipts/11`): the census tool's own `census` mode on a `git archive` copy of each
revision, the frozen contract's `awk` recipe over the committed blobs, and the `--file` run of the
whole tree as a mirror.

**Tier + status histogram (counted from `status=` cells and `tier=` cells; two independent counters):**

| | rows | tier.A | tier.B | tier.C | status.mined | status.queued | status.rejected |
|---|---|---|---|---|---|---|---|
| base `3ff23da3` | 317 | 302 | 11 | 4 | 284 | 8 | 25 |
| tip `67eddac8` | 319 | **304** | 11 | 4 | **286** | 8 | 25 |

Both new rows are tier A and mined; nothing else moved. No `tier.invalid`, no `status.invalid`,
no `missing`. The census `census` mode and the frozen contract `awk` recipe agree exactly on every
cell. `scripts/sources-census.sh census --root … kama` → `FLEET rows 319`, exit 0.

---

## 2. Row-by-row re-grade of S576, S578, S579

Method: read-only GET of `https://spec.commonmark.org/0.31.2/` (514 698 bytes,
sha256 `c85f56cc2101f761cc94215c677cd2c7c1ecca9c47be016479fdfe718af60f0d`), parsed the three
sections the rows cite, and checked each quoted string against the section body. The fetched page
is byte-identical to the lane's own committed copies
(`.ufo/waves/round-76/w1/SCR01Sources/commonmark-0.31.2.html` and
`.ufo/waves/round-85/w1/out/SCR01Frontier/commonmark.html`, same sha256), and to the full-page
digest recorded in the round-50 stored copy `.ufo/waves/round-50/c2/commonmark-0.31.2-s4.5.txt`
("full page sha256 c85f56cc…"), so the row quotes are checked against the same bytes the lane has
held since 2026-10-27. Receipts `04`, `08`, `09`.

| row | URL + anchor | anchor resolves? | section named by the row | spec section | quote | ≤25 words? | quote occurs at the anchor? |
|---|---|---|---|---|---|---|---|
| S576 | `spec.commonmark.org/0.31.2/#atx-headings` | `id="atx-headings"` present | §4.2 ATX headings | §4.2 ATX headings ✓ | "The opening # character may be preceded by up to three spaces of indentation." | 14 ✓ | **yes** |
| S578 | `…/#fenced-code-blocks` | `id="fenced-code-blocks"` present | §4.5 Fenced code blocks | §4.5 Fenced code blocks ✓ | "A fenced code block begins with a code fence, preceded by up to three spaces of indentation." | 17 ✓ | **yes** |
| S579 | `…/#indented-code-blocks` | `id="indented-code-blocks"` present | §4.4 Indented code blocks | §4.4 Indented code blocks ✓ | "An indented chunk is a sequence of non-blank lines, each preceded by four or more spaces of indentation." | 18 ✓ | **yes** |

All three anchors resolve; all three section numbers in the anchor cells are correct (I checked the
`<span class="number">` headings in the live HTML); all three quotes are ≤25 words and all three
occur at their anchor in the section body. **No fabrication-class row among S576/S578/S579.**
The quotes are tag-stripped renderings of the spec prose (the raw HTML wraps `#` in `<code>` and
the terms in `<a class="definition">`), which is the lane's established convention for this
document — the round-50 stored copy is labelled "tags stripped" — and the row quotes drop no word.

**status / opened / recheck cells the census accepts.** All three rows carry
`status=mined`, `opened=2026-11-04`, `recheck=on-release`:
`E07` (status enum) silent, `E08` (opened not in the future) silent, `E09` (recheck) silent —
`on-release` matches the census's `symbolic()` pattern, and `overdue` mode reports the three rows as
`cadence … recheck=on-release`, never overdue (`receipts/10`). Re-running validate with
`--today 2026-11-04` also exits 0. Note for the record: with `--today 2026-11-03` the same run
exits 1 (E08 on `opened=2026-11-04`), i.e. these rows are valid only from 2026-11-04 onward; that
is expected and not a defect.

**`used-by`.** S576 → `corpus/lessons/round-85.md, corpus/lessons/round-86.md`;
S578 → `corpus/lessons/round-86.md`; S579 → `corpus/lessons/round-86.md`.
All three **name `corpus/lessons/round-86.md` as required**, and every named path exists on disk
in the lane (E11 silent; the contract's own dangling-used-by `awk` recipe also prints nothing).
`corpus/lessons/round-86.md` is committed at the tip (`git ls-tree 67eddac8 corpus/lessons/` lists
`round-86.md`), so the used-by is not satisfied by an uncommitted file. The round-86 lesson cites
each of the three ids (`S576`×3, `S578`×2, `S579`×2 in `corpus/lessons/round-86.md`), so the
used-by is a real citation, not a nominal one.

**Append-only rule 2 (CORPUS.md rule 2 / KQ22).** `python3 tools/sources-append-only.py --repo .
--from 3ff23da3… --to 67eddac8…` → `added S578 (allowed) / added S579 (allowed) / no append-only
violations`, exit 0. I also diffed S576 field-by-field base→tip: the **only** cell that changed is
`used-by` (mutable); `source`, `kind`, `tier`, `scope`, `anchor`, `teaches`, `status`, `opened`,
`recheck` are byte-identical (`receipts/06`, `07`). One commit touched `corpus/SOURCES.md` in the
round, so the base→tip pair is also the consecutive-pair range KQ22 requires.

**What the census does not check — proven, not assumed.** I ran two controls against a full
`git archive` mirror of the tip tree (`receipts/05`, `receipts/11`):

* **Control A — fabricated quote.** Replacing S578's quoted sentence with a sentence that does
  **not** occur at §4.5 leaves the census at **exit 0 with no new finding**. The census validates
  row shape, enums, ids, URL/scope duplication and used-by existence; it never opens a URL and
  never compares a quote to its source. A green census is therefore **not** evidence that a row's
  quote is at its anchor — that check is KQ45's, and it is what this seat performed by fetching.
* **Control B — dangling used-by.** Adding a non-existent path to S579's used-by makes the same
  census run exit 1 with `E11 S579 missing used-by corpus/lessons/round-99.md`. So the E11 arm is
  live and discriminating; the quote arm does not exist.

---

## 3. Findings

### F1 — `S498` (pre-existing, round-50) carries a quote that is not at its anchor — fabrication class
`corpus/SOURCES.md:251`, unchanged at base and tip, so **not** one of this round's rows and not
affected by the round's change set. But the seat was told to report any row whose quote is not at
its anchor, and this one is:

* S498 `teaches` cell quotes: `"A code fence is a sequence of at least three consecutive backtick characters or tildes."`
* The actual §4.5 text is: `A code fence is a sequence of at least three consecutive backtick characters (`) or tildes (~).`
* The quoted string is absent from the tag-stripped §4.5 text (checked against the live page and
  against the round-50 stored copy the row itself cites as its anchor — **False** in both), and
  absent from the raw HTML. The quote drops the `` (`) `` and `` (~) `` code spans.
* KQ45 (`corpus/QUALITY.md:322`) makes "a row whose quote drops a word, strips markup, or sits at a
  line other than the one its anchor names" a defect, corrected by an **appended superseding row**
  (CORPUS.md rule 2), never by editing the quoted cell.
* S498 is still `status=mined` and cited by `corpus/lessons/round-50.md` and
  `corpus/knowledge/fenced-quotation-scope.md` (both exist — no dangling used-by).
* **The repair vehicle already exists and was not used.** S578 opens the *identical* URL *and* the
  identical anchor `…/#fenced-code-blocks` with an accurate quote of the same paragraph, but its
  `teaches` does not open `supersedes S498 —`. A superseding row is the contract's own remedy for
  exactly this; as landed, the defective paraphrase stays live and mined and the accurate quote
  sits beside it in a second scope.

Author-side note: this is a judgment about which row should carry which correction, and the
non-author closure decides. The observable facts above are measured; the recommendation to append a
`supersedes S498 —` row is the L1's call.

### F2 — the HTML-comment rule that C1 depends on has no registry row
The frozen plan's frontier paragraph states the round "re-opens the CommonMark 0.31.2 specification
for the fence **and comment** rules that ground C1's selector", and the C1 predicate lists "HTML
comment blocks" among the excluded constructs. The registry holds **zero** rows citing the comment
rule: `grep -c '<!--' corpus/SOURCES.md` → 0 and `grep -c 'html-blocks' corpus/SOURCES.md` → 0. The
three opened rows cover ATX headings, fences and indented code; the lesson's Gate table has three
rows and no comment row. The comment rule lives in CommonMark §4.6 (HTML blocks, type 2: "Start
condition: line begins with the string `<!--`. End condition: line contains the string `-->`"),
which is citable at `…/#html-blocks`. So one of the three exclusions C1's instrument implements is
**unsourced in the registry** while the plan's own sentence claims it was sourced.

This is a coverage observation, not a defect in S576/S578/S579 (all three of those are sound). It
matters because C1 is declared "the sourced claim" and the comment-shadow arm is one of the
instrument's eleven selftest arms.

### F3 — S579's `teaches` cell overstates the quoted rule by dropping the spec's own exception
S579 teaches: "Four-space indentation makes a line code, so a selected authority banner or axes row
must start at column zero." The quoted anchor sentence supports the first half. The spec states the
exception **in the same section, one paragraph later**: "An indented code block cannot interrupt a
paragraph, so there must be a blank line between a paragraph and a following indented code block."
A 4-space-indented line that continues a paragraph is therefore *not* code. The teaches cell's
premise is true only outside paragraph continuation, and the row's anchor cell cites §4.4's
"definition" without that caveat.

The instrument's actual behaviour is stricter than the spec in the safe direction: `AUTHORITY` and
`CALIBRATION` are anchored at column 0, so a live cell indented by 1–3 spaces is not selected at
all (measured: `indent=1,2,3` → `could-not-evaluate: no rendered top-level Current authority cell`,
exit 2 — fail-closed). The "indent-shadow" arm passes for the same reason (a 4-space-indented cell
never matches a column-0 regex), not because `rendered()` implements an indented-code-block rule —
it has none. The direction is conservative, so this is an accuracy-of-teaches observation rather
than a risk to the claim.

### F4 — two frozen-plan statements do not match the committed record
* Plan line 120: "§4.2 ATX headings, **row S576, opened this round**". S576 was **not** opened this
  round: it was landed by the round-85 integration commit `948dec784a9736b4a36d6a10d303fbee054b19c6`
  ("round-85: integrate finite controls and retain frozen false-pass findings"), which is an ancestor
  of the frozen base; the base blob already carries the S576 row. Round 86 only extended S576's
  `used-by`. The lesson states this correctly ("S576 (re-opened, used-by extended)", "opened stayed
  2026-11-04"), so the landed artifact is accurate and the plan's parenthetical is not.
* Plan lines 42 and 120 pair the section numbers with the topics as "§4.4/§4.5 fenced and indented
  code". In CommonMark 0.31.2 §4.4 is *Indented* code blocks and §4.5 is *Fenced* code blocks — the
  plan's positional order is inverted relative to the spec. The landed rows and lesson have it right
  (S578 → §4.5 fenced, S579 → §4.4 indented), so a reader who follows the plan's string literally
  would look in the wrong section.

### F5 — the round-86 lesson's Gate table drops the per-row access-date column
CORPUS rule 1: "The round lesson's `## Gate` records, for every new row, the URL, the access date,
and a ≤25-word quote with its location grounding `teaches`." The round-86 Gate table has
`Row | URL | Located quote (≤25 words) | Decision` — no access-date column; the date appears once
in the preamble ("Opened 2026-11-04 (static read of the published specification, no endpoint
sampled)"), which covers the table but is not the per-row shape round-85's Gate used
(`id | URL | access date | location and ≤25-word quote | decision and scope`). Minor shape
deviation, not a factual error; the date is stated and correct.

---

## 4. Verdict

* **Census:** exit **0**, **319** rows, **0** E-findings, **116** warnings (115 `W04` + 1 `W01`),
  of which **2 `W04` are new** this round (`S578`, `S579`) and are correctly disclosed in the lesson.
* **Tier/status histogram:** rows 317→319, tier.A 302→304, tier.B 11→11, tier.C 4→4,
  status.mined 284→286, status.queued 8→8, status.rejected 25→25 — counted twice independently, both agree.
* **S576 / S578 / S579:** URL+anchor correct and resolving; section numbers correct; quotes ≤25 words
  and **present at their anchors**; status/opened/recheck accepted by the census; `used-by` names
  `corpus/lessons/round-86.md` and every named path exists; append-only rule 2 clean. **No fabrication-class
  row and no dangling used-by among the three.**
* **Fabrication class, elsewhere in the registry:** one — the pre-existing round-50 row **S498**
  (F1). It is outside the round's change set; the correct remedy under CORPUS rule 2 is an appended
  superseding row, and S578 is the natural vehicle that was not used that way.
* **Open items for the L1:** F2 (comment rule unsourced though the plan claims it was sourced),
  F3 (S579 teaches omits §4.4's paragraph-continuation exception), F4 (two frozen-plan statements
  vs the committed record), F5 (Gate table shape). No claim admission is made here; the L1 and the
  non-author closure decide.

**Census coverage limit, stated so no green is over-read:** the census does not check quotes
(Control A: a fabricated S578 quote still exits 0) and does not open URLs. Its exit 0 therefore
certifies shape, enums, ids, URL/scope duplication and used-by existence — not that a row's quote
is at its anchor. That certification came from this seat's independent fetch, not from the census.
