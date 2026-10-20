# AttackSourceCuration — S032 sourcing for C1: tier A scope vs circular self-endorsement

Critic seat, author advisor (not independent closure). Static reads, two public manual pages
opened 2026-10-20, and read-only git/sha256 hash facts. I ran no fidelity, reproduce,
selftest or census command and edited nothing outside this file. Tools installed/updated:
none.

Axes: **calibration** (C1), **discernment** (registry vs admission), **coverage/expansion**
(masquerade risk), and **provenance safety** (false authority).

**Plan change (parent message):** the planned own-work S032 is superseded. S032 is now
docs/A, the Git git-show manual (`SOURCES.md:44`, `lessons/round-12.md:37-46,98-118`).
The own-work analysis is kept below only as the reason for that change.

## Verdict

- The docs/A S032 removes the circularity for the method citation. I agree with the change.
- Three wording/scope defects remain (R2–R4), plus one carried from the earlier analysis
  (R6). R5 is resolved in the landed `fidelity.py` (static read, unrun). None blocks the
  plan, and all can be fixed inside the round without touching immutable cells.

## Facts observed this pass

| Fact | Value / where |
|---|---|
| git-show manual DESCRIPTION, opened 2026-10-20 | "For plain blobs, it shows the plain contents." Verbatim, matching `round-12.md:39,103`; page says "git-show last updated in 2.56.0", dated 2026-09-28 |
| git-show manual, `--textconv` | "textconv filters are enabled by default only for git-diff[1] and git-log[1], but not for git-format-patch[1] or diff plumbing commands." |
| git-cat-file manual §OUTPUT (2.56.0, 2026-09-28) | "If `<type>` is specified, the raw (though uncompressed) contents of the `<object>` will be returned." |
| comparator read path | `fidelity.py:264-265` and `:431` use `git cat-file blob`, not `git show` |
| capture path | `advice/Fidelity.md:27,109`: one-shot `git show` generation; `git show` and `cat-file` bytes identical (author-observed) |
| new snapshot `frozen/corpus/SOURCES.md` | sha256 `9dc40d25…093a`; `git hash-object --no-filters` gives `7de1360655eadada356fe110813c6e1338142551`, equal to `git rev-parse 2f7303c…:corpus/SOURCES.md` |
| old snapshot `round-11/frozen/before/corpus/SOURCES.md` | sha256 `52665cf2…42fa1`, `hash-object` `e03f233b…` (≠ source) |
| origin of non-author digest | `round-11-verifier-spotcheck.md:102-103`, commit `79fa2577…` by `protocol-shokunin` |
| attributes on `corpus/SOURCES.md` | `git check-attr -a` gives none |

The two snapshot-hash rows are correspondence measured **without `fidelity.py`**. They are
static facts, not a gate run.

## R1 — circularity: resolved for the method, still open for the outcome

**Earlier counterexample (why own-work S032 was circular).**
`round-11/frozen/expected.json:15` is a lane-authored pin of `52665cf2…`. It matched its
snapshot, so integrity was green, while the snapshot was not the source blob (D1). An
own-work S032 would have had one author writing the judge, pin, subject, row, quote and
claim, which is the same structure.

**Docs/A S032 is the right shape.** The lesson already limits it correctly: it cites S032
"for capture method, not as proof of observed snapshot outcome" (`round-12.md:41-42,104-106`).

The **outcome** (old ≠ source, new = source) still rests on author-run evidence. It becomes
non-circular through two authorities the round-12 author did not write:
- the content-addressed blob OID `7de13606…` in commit `2f7303c` (2026-10-19);
- the non-author digest `9dc40d25…` at spotcheck:102-103.

`fidelity.py` pins both as constants. The Gate should name where each constant came from,
and non-author closure is still pending (`round-12.md:50-53`, correct as written).

## R2 (medium, fixable) — S032 sources the capture command, not the comparator

`round-12.md:12-13` says: "The same command compares both against `git show 2f7303c…`".
`fidelity.py` actually compares against `git cat-file blob` (`:264`, `:431`). `git show` was
used only for the one-shot capture (`Fidelity.md:27,109`). As worded, C1 binds its
correspondence method to a manual for a command the comparator does not run.

**Smallest correction:** reword the lesson to say "captured once with `git show` (S032);
compared with `git cat-file blob` against pinned OID/sha256". Then choose one:
- (a) open and register git-cat-file §OUTPUT. Its 15-word quote "If `<type>` is specified,
  the raw (though uncompressed) contents of the `<object>` will be returned" sources the
  comparator's raw-bytes read.
- (b) state that the comparator's method needs no documentation authority, because
  correspondence is checked by recomputing the content-addressed OID.

Either way, do not let S032 imply it documents the comparator.

## R3 (low) — "byte-preserving" goes beyond the S032 quote

The S032 scope says "Byte-preserving historical blob retrieval". The quote says only "plain
contents". The git-show page's one textconv statement says textconv is on by default for
`git-diff`/`git-log` (git show is log-family). The page never states that blob display
bypasses textconv or filters, so "byte-preserving" is **[INFERENCE]** from that page.

In this repo the inference holds empirically: no attributes on the path, author-observed
show = cat-file bytes, and the snapshot's `hash-object` equals the blob OID. That support
is local observation, not S032 content. The git-cat-file "raw (though uncompressed)
contents" sentence is the documentation that actually states raw bytes.

**Fix:** label "byte-preserving" as inference in the lesson's S032 paragraph, or ground it
in the cat-file quote from R2(a). `SOURCES.md:44` cells are now committed row text, so
correct them by appended prose, not by editing the cell, unless the row is still
uncommitted this round.

## R4 (low) — revision pin

The anchor gives "manual last updated in Git 2.56.0 (2026-09-28)" against the unversioned
`/docs/git-show` URL, which follows the latest release. The page lists a versioned URL,
`https://git-scm.com/docs/git-show/2.56.0`. Citing it in the lesson Gate makes the quote
reproducible after the next release (KQ6 revision requirement). This is optional, and
`on-release` recheck already covers drift.

## R5 — the C1 counter (resolved in source; static read, not run)

Earlier defect, read at tag `A0B6`/`439F`: `mismatches` mixed the pin, anchor and
correspondence checks. A blob that failed the anchor was reported as `source_mismatch`.

Fixed in landed `fidelity.py` (read at tag `0D0E`):
- `:323`: `mismatches = int(source_matches is False and anchor_matches is True)`.
- `:283-292`: if the retrieved blob fails the pinned OID, sha256 or byte count, the
  finding is `source_unavailable` (exit 2).
- `:330-347`: integrity is reported separately as `integrity_result` and
  `snapshot_pin_matches`.
- The selftest assertions (`:486-521`) encode the coherent-mutation case as
  `mismatches: 1` with `integrity_result: match`, and the unavailable case as
  `mismatches: 0`.

Note: the selftest tamper case asserts `mismatches: 1` (`:505`). That is correct, because
the mutant snapshot also differs from the source. Its exit (2, `snapshot_tampered`) comes
from finding precedence, not from the counter.

My earlier counterexample is now a selftest fixture (tag `3B0B`, `:507-514`,
`pin-only-corruption-exact-snapshot`). It pairs a byte-exact snapshot with a wrong pin.
The fixture expects exit 2 `snapshot_tampered`, `integrity_result: mismatch`,
`source_matches: true` and `mismatches: 0`. The selftest has 11 fixtures; I have not
run it.

Remaining obligation for the Gate, also recorded in Fidelity's report: quote `finding`,
`mismatches`, `source_anchor_matches` and `source_matches` from the committed receipt for
both snapshots.

**Ownership:** R2, R3, R4 and R6 are wording in the lesson and SOURCES, and the L1 lesson
owner fixes them. None requires a `fidelity.py` change. Fidelity's own report already
separates `git show` capture from `git cat-file blob` comparison (`Fidelity.md:27,78-79`).
It also makes no byte-preserving claim and names the two files behind the 1→0 count. The
defects are in `round-12.md:12-13,10-12,129` and the `SOURCES.md:44` scope wording.

## R6 (carried, low) — "1 → 0" is two objects; "denominator one file" conflicts

The old snapshot remains mismatched by design. The 0 is a different, new file. Two places
read as repairing one file: `round-12.md:10-12` ("reduces the source-mismatch count from
one to zero") and `:129` ("fixed denominator is one file").

**Suggested wording:** "of the two SOURCES snapshots of `2f7303c` (round-11 copy, round-12
corrective copy): 1 non-corresponding before; the corrective copy corresponds and the old
copy remains non-corresponding, erratum-labelled". The scalar stays 7 → 7 (already stated).

## Resolved since the earlier draft

- D2 recurrence: `SOURCES.md:70` appends that S032 was opened in round 12, with S001–S031
  cells intact.
- Expansion masquerade: S032 used-by is `corpus/lessons/round-12.md`, which is not a
  knowledge entry, and the lesson states knowledge/frontier added = 0 (`round-12.md:123-125`).
  Contract rule 4 (knowledge entries citing `mined` rows count toward expansion) is
  therefore not triggered. [INFERENCE] that the contract permits a lesson as `used-by` for
  `mined`: census E11 checks path existence only (round-11 `ReviewContract.md:31`), but the
  contract text is outside this seat's path bounds.

## Gate, quote, access and used-by constraints (docs/A S032)

| Item | Requirement | Status |
|---|---|---|
| URL | the opened page | met: `https://git-scm.com/docs/git-show` |
| access date | actual UTC open date | met: 2026-10-20 |
| quote | ≤25 words, verbatim, located section | met: 9 words, DESCRIPTION; verified this pass |
| revision | documented version/date | met by "2.56.0 (2026-09-28)"; versioned URL optional (R4) |
| scope | narrow enough that the quote supports it | partial (R2/R3): the quote covers `git show` plain blob display, not the `cat-file` comparator or literal byte preservation |
| used-by | existing path; no `corpus/knowledge/*.md`; no knowledge `source: S032` | met; L1 confirms by grep |

## Registry vs admission

`SOURCES.md:3-4`: "Claim admission stays in `QUALITY.md`; this file records where claims
come from". S032 is a provenance row. **It admits nothing.**

- **Admission of C1:** the `round-12.md` Gate decision row (`:24`) under:
  - KQ14/KQ15: correspondence separate from integrity;
  - KQ3: old bytes preserved;
  - KQ10: read-only git plus temporary writes;
  - KQ12: fixed denominator; row growth is not knowledge.

  It also needs the committed red-before/green-after receipt and non-author closure.
- **Census:** after the row lands, the delta (rows 31→32, tier.A 28→29, mined 21→22) is
  bookkeeping. The lesson's "expansion unchanged" is the right reading.

## Checks for L1 (named, not run here)

1. Confirm `git -C <lane> hash-object --no-filters .ufo/waves/round-12/frozen/corpus/SOURCES.md`
   equals `git -C <lane> rev-parse 2f7303c242319c1dc96c6bcf7702ac18b3ca1aad:corpus/SOURCES.md`
   (`7de13606…`), and that the old copy gives `e03f233b…` (≠).
2. `grep -n "git show" corpus/lessons/round-12.md`: wording should say capture-only after
   the R2 fix. `grep -n "cat-file" .ufo/waves/round-12/fidelity.py` is the comparator.
3. Re-open `https://git-scm.com/docs/git-show/2.56.0` §DESCRIPTION, then `grep -F` the quote.
4. Coupling: `grep -l 'S032' corpus/knowledge/*.md` should give none.
   `grep -c '^| S032 ' corpus/SOURCES.md` should give 1.
5. Run `sources-census.sh validate`/`census` after the change and record the delta as
   bookkeeping.
6. The reproduce receipt should show the C1 fields from R5 for both snapshots, with
   `source_sha256 == 9dc40d25…`.
7. `git diff --exit-code 79fa2577… -- .ufo/waves/round-11/frozen` should show the old
   receipt untouched.
8. Read `SOURCES-CONTRACT-v1.md` status definitions to confirm that `mined` with a lesson
   `used-by` is allowed.
