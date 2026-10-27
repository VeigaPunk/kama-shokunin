# V02StaleLesson — round-55 §Mistakes row 1 re-derived from its named receipts; round-56 correction graded for append-only

Seat: leaf revenger, round 56 w1 (kama). Revisions: base `e10b6d39af450e8d652be9ac2986768b531fe13f`,
freeze `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`, round-55 build `8abadfed`, round-55
integration `c2c05e30`, round-53 counter freeze `d01b2b6d`. Lane tree read-only; nothing in
the lane, its index or jj state was written. No counter, server or fixture was run.

## Verdict

**Row 1's conclusion survives; three of its evidence assertions do not.** The vacuity finding
(round-53 C2's `dropped` leg read `SCORECARD.md` only, so hiding dead `SKILL.md` citations met
the frozen counter) re-derives from the committed round-53 receipts and the frozen counter
source. Of the six artifacts row 1 names, two no longer exist and never existed at the round-56
base or freeze tip, one is misquoted, and one quotation is attributed to a file that does not
contain those words.

**The round-56 correction is appended in content but not append-only in effect.** It does not
rewrite the round-55 lesson this round (blob `d21ed1ac85eb` at base and freeze), and its row is
appended under `## Mistakes` after `## Gate`. But it is not committed anywhere (absent from the
freeze commit and from `git log --all`), the KQ67 instrument for the "append-only" claim it
makes exits 1 with a 33-line undisclosed in-place rewrite of `corpus/lessons/round-55.md` at
`c2c05e30`, and the "round-55 wording" it preserves as history is that rewrite — the freeze-time
text survives only in git history at `9c60eae6`.

## Method (all read-only; exact commands)

```
python3 tools/append-only-audit.py --repo . --to efc6b3ec6fb6ea308c15855e9b8b62856f4255b7 --json   # exit 1
git show <rev>:<path> | git cat-file -e <rev>:<path> | git log -S <str> -- <path> | git diff --stat
python3 .ufo/waves/round-56/w1/out/V02StaleLesson/row1-recheck.py                                    # exit 1
```

`row1-recheck.py` is the replayable driver behind every check id below; its JSON output is
beside it. `lsp` is not the instrument here (the subject is committed text and git history, not
code definitions); the semantic tools would answer nothing grep does not.

## Findings

### F1 — MAJOR (calibration): row 1's "the battery also holds …" receipts do not exist, and the sentence and their deletion are the same commit
`corpus/lessons/round-55.md:97-100` states the battery "also holds one declared vector analysis
(m-ldaudit-foreign, `met=True` …) and two further receipts that print `met=True`
(m-ldaudit-writable, m-extra-in-tree)".

* `missing@tip` and `missing@base`: check A2 — `test -e` misses both paths in the worktree, and
  `git cat-file -e e10b6d3:<path>` reports both absent at the round-56 base. So the statement was
  already false when round 56 started, not only after some later cleanup.
* `met=True` is true only in history: at `8abadfed`, `m-ldaudit-writable.out` prints
  `… envnames=3/3 hostlibs=3/3 … met=True` and `m-extra-in-tree.out` prints `… met=True`
  (`round56-correction-evidence.txt` §3). `git diff --stat 8abadfed c2c05e30 -- …/battery/`
  shows exactly those two files, 48 deleted lines (§4).
* The round-56 lesson's class is right but too weak: `git log -S 'm-extra-in-tree' --
  corpus/lessons/round-55.md` returns `c2c05e30` — the integration commit **wrote the sentence
  and deleted the receipts it names** (check B5). "Deleted at the same round's integration" is
  literally true only because the integration is where the claim was authored.

Round 56 names this defect (its correction row, check B2 pass). It does not name the stronger
fact, and the correction row does not exist in any commit (F4).

### F2 — MEDIUM (calibration): row 1 misquotes a receipt field (`code=0/3`)
Row 1: "m-text-flip (`code=0/3`)". Receipt
`.ufo/waves/round-55/c1/battery/m-text-flip.out:2`:

```
bind=0 sealed=1 code=0 teardown=1 newrow=1 bound=0/3 sealedruns=3/3 coderuns=0/3 envnames=3/3 hostlibs=3/3 anon=0 twopass=3/3 rehash=3 met=False
```

`code=0`; `0/3` is `coderuns=0/3`. The lesson transcribed the seat shorthand
(`.ufo/waves/round-55/w1/out/J5EnvNames.md:229` writes `code=0/3 hostlibs=0/3`) instead of the
receipt field. `met=False` and the leg failure are unaffected, but the parenthetical is presented
as a receipt quote and is not one (check A1-m-text-flip). The same receipt's `bind=0` /
`bound=0/3` leg failure is omitted from the "three live kills" list.

### F3 — MEDIUM (calibration): a quotation attributed to the outside closure is the lane's own SCORECARD wording
Row 1 (`:83-85`) attributes, in quotation marks, to
`corpus/lessons/round-53-verifier-spotcheck.md` C2 row: "J12Hide hides dead SKILL.md citations and
removes their ledger rows while the frozen counter still returns met=True".

* verbatim in that closure file: **no** (check A6). The closure's C2 row
  (`corpus/lessons/round-53-verifier-spotcheck.md:17`) says: "Committed J12Hide shows hide variants
  still yield `met=True`, falsifying the claim's stated kill rule; J11BadFixed also passes wrong
  upstream bytes."
* verbatim in `SCORECARD.md:3042` (round-53 section, `met=True` in backticks): **yes**.

The substance is corroborated independently (check A3: `J12Hide/c2-frozen-v_a_skill.out` prints
`dropped=0 met=True`; check A4: `tools/round53-cited-path-check.py@d01b2b6d` compares only
`SCORECARD.md` blobs for `dropped`), so this is a provenance defect, not a wrong conclusion.

### F4 — MAJOR (append-only): the round-56 correction is not committed
Check B1: `git ls-files corpus/lessons/round-56.md` is empty; `git cat-file -e
efc6b3e:corpus/lessons/round-56.md` fails; `git log --all -- corpus/lessons/round-56.md` is
empty. The file exists only in the worktree (mtime `2026-10-27 13:06`), while the round-55
precedent committed its lesson in its own freeze commit (`9c60eae6`, first-add of
`corpus/lessons/round-55.md`). Consequences at this tip: the correction is invisible to every
instrument that reads commits (append-only audit, cited-path counters, a fresh clone), and it is
destroyed by any worktree reset. Everything the correction asserts is therefore unfiled as of
`efc6b3e`.

### F5 — MAJOR (append-only): the KQ67 instrument on the population exits 1, with an unrestored 33-line rewrite of the very lesson being corrected
`tools/append-only-audit.py` (definition v6) to the freeze tip, exit **1**:

```
summary {"commits":375,"files":105,"events":119,"restored":69,"partial":0,"unrestored":3,
         "ungraded":42,"disclosed":5,"permitted_lines":59,"disclosed_lines":10,
         "bad_disclosures":0,"ungraded_lines":223,"regressed":0,"vanished":0,
         "unmatched":0,"binary":0,"bad_declarations":0}
event c2c05e30b80e corpus/lessons/round-55.md unrestored deleted=33 undisclosed=33 restored_at_tip=null
event e81d90e64b04 SCORECARD.md                 unrestored deleted=3  (pre-existing, outside this slice)
event 4bd7521a704e SCORECARD.md                 unrestored deleted=3  (pre-existing, outside this slice)
events at the round-56 freeze commit efc6b3e: 0
```

All 33 deleted lines are unheld at the tip and undisclosed (`lost-lines-c2c05e30.txt` lists each
with its parent line number). They are not reflow: they include the C1/C2 claim sentences
(`:19`, `:21`, `:25`), the rejected-source rationale (`:47-51`), the S510 Gate sentence (`:56`),
row 1's own fix evidence (`:73-76` — the freeze-time text asserting every battery mutant fails),
row 3's fix clause and the census "after" bullet (`:94-96`, `:101`), and all four `considerthese`
disposition rows (`:105-113`).

The mechanism is exact: the filed lesson at the tip is **byte-identical** to the seat proposal
`.ufo/waves/round-55/w1/out/Sc1Lesson/round-55.proposed.md`
(`sha256 47c398fee93829cf…` both, diff empty). The integration overlaid a wave-1 proposal onto a
filed lesson — the `A-corr` rule for `corpus/lessons/*.md` (`registry/append-only-contract.tsv:7`,
declared at `corpus/README.md:1239`) allows appended corrections that name the superseded text,
not wholesale replacement.

Repair constraint (tool docstring, v6): the disclosure ledger exists since `b6bed925` (round 51),
which is an ancestor of `c2c05e30`, and "a deletion made once the ledger existed is restored by
append, never disclosed" — a `registry/append-only-disclosures.tsv` row for `c2c05e30` would be a
bad disclosure (exit 1). The only valid repair is an append restoring the superseded text.

Round 56's correction claims append-only but reports no audit at all (`grep -c
append-only-audit corpus/lessons/round-56.md` = 0), and its scope covers only the two deleted
receipts, not this event.

### F6 — MEDIUM (stale): the same rewrite left a second statement the tip tree contradicts
`corpus/lessons/round-55.md:130` says `.ufo/waves/round-55/census/end.out` "does not exist yet
(`census/` holds `start.out` only …)", and `:138` says it is "(absent at this lesson's write
time …)". The receipt exists at the freeze tip and was added by `c2c05e30` — the commit that
wrote those lines and that states "census end (exit 0)" in its subject (check C1). The freeze-time
version said the round "ends with census exit 0 (receipt `.ufo/waves/round-55/census/end.out`)";
the rewrite moved it backwards to a pre-end state. Round 56 does not correct it.

### F7 — INFO: everything else in row 1 re-derives exactly
| row-1 assertion | evidence | check |
|---|---|---|
| round-53 C2 counter printed `met=True` at its build | `.ufo/waves/round-53/measured/c2-build.out` `… dropped=0 met=True` | A7 |
| hide-a-SKILL-citation control also met `met=True` | `J12Hide/c2-frozen-v_a_skill.out` `dropped=0 met=True` | A3 |
| the dropped leg read `SCORECARD.md` only | `tools/round53-cited-path-check.py@d01b2b6d`, dropped loop on `SCORECARD.md` blobs | A4 |
| base control is the red-before state (`dropped=1` → `met=False`) | `.ufo/waves/round-55/controls/base.c2.out` | A5 |
| m-ldpreload `envnames=0/3`, `met=False` | `m-ldpreload.out:2` | A1 pass |
| m-member-flip `rehash=3`, `met=False` | `m-member-flip.out:2` | A1 pass |
| m-ldaudit-foreign `met=True` (declared vector analysis) | `m-ldaudit-foreign.out:2` | A1 pass |

The round-55 lesson is also untouched between base and freeze (check B0, blob `d21ed1ac85eb`
both), so round 56 wrote nothing into it.

## Proposed fixes (append-only; none applied — lane is read-only for this seat)

1. **F4** — commit `corpus/lessons/round-56.md` with the w1 integration commit and record its
   digest in the round report. If the lane deliberately files lessons only at integration, say
   so in the correction row and cite `9c60eae6` as the preserved round-55 text; do not let the
   round end with the correction uncommitted.
2. **F5** — append to `corpus/lessons/round-55.md` an erratum that quotes the 33 superseded lines
   (source: `lost-lines-c2c05e30.txt`, event `c2c05e30`, `deleted=33 undisclosed=33`) and names
   the superseding commit; then re-run `tools/append-only-audit.py --to <tip>` and report its
   summary and exit. Do **not** add a disclosure-ledger row: the ledger predates `c2c05e30`, so
   v6 grades such a row bad.
3. **F2** — append an erratum row for row 1: `code=0/3` → `code=0` (`coderuns=0/3`), naming
   `bind=0`/`bound=0/3` as m-text-flip's second failing leg, so the three-kill list matches the
   receipts field for field.
4. **F3** — cite `SCORECARD.md:3042` verbatim for the J12Hide sentence and quote the closure's own
   wording ("Committed J12Hide shows hide variants still yield `met=True`, falsifying the claim's
   stated kill rule") as the closure's verdict.
5. **F6** — append an erratum for `:130`/`:138`: the census `end.out` receipt was committed at
   `c2c05e30`; the lesson's "does not exist yet" describes the pre-integration state.
6. **F1 (residual)** — the two deleted receipts' bytes should be preserved, not left to git
   history: `8abadfed:{m-ldaudit-writable,m-extra-in-tree}.out` into
   `.ufo/waves/round-55/c1/battery/first-composition/` with the one-line README S7Pointers already
   proposed (`.ufo/waves/round-55/w1/out/S7Pointers/proposed-fix.patch`, never applied). The
   correction row's KQ26 disclosure otherwise rests on an object that no clone-without-history can
   read.
7. **Standing gap the correction names as "captured-by: none"** — I found no `corpus/QUALITY.md`
   row that binds a lesson's named artifact to its existence at the tip: the round-56 C2 checker
   reads only the battery roster, and the cited-path counters' `SURFACES` are
   `(SCORECARD.md, SHONEN.md, SKILL.md)`. The correction's claim is therefore accurate; the
   KQ67-style check it lacks (fix 2/5) is the one that would have caught the `c2c05e30` rewrite.

## What would falsify these findings

- A commit before the wave closes that adds `corpus/lessons/round-56.md` with unchanged content
  narrows F4 to "absent at the freeze tip" (still a divergence from `9c60eae6`).
- A later commit restoring the 33 superseded lines turns F5's `unrestored` into `restored`; the
  finding then becomes "the rewrite was undisclosed until round N".
- If `git log -S 'm-extra-in-tree'` gains a commit later than `c2c05e30`, F1's same-commit claim
  falls back to the round-56 lesson's weaker "deleted at integration" form.
- If `m-text-flip.out` is ever regenerated with a `code=0/3` field, F2 must be re-read; the field
  set is fixed by the round-55 counter's output contract.

## Limits and confidence

- High confidence on F1/F2/F4/F5/F6/F7: each rests on committed bytes or on the lane's own tool
  output, reproduced here with exit codes. Medium-high on F3's severity (the quotation's substance
  is independently verified; only its attribution is wrong).
- I did not re-run any round-55 counter, start a server, or reach the fleet or siblings; the
  round-53/55 counters are cited as frozen bytes only.
- The audit's exit 1 is whole-population. Only the `corpus/lessons/round-55.md` event is in this
  slice; the two `SCORECARD.md` unrestored events (`e81d90e6`, `4bd7521a`) are pre-existing and
  named here for completeness, not graded by me.
- No tools installed (no pacman, uv, npm, cargo); scratch
  `/fast/scratch/hyaku/kama-r56/V02StaleLesson/` removed after copying the receipts below.

## Receipts in this seat's directory (`.ufo/waves/round-56/w1/out/V02StaleLesson/`)

| file | content |
|---|---|
| `row1-recheck.py` | replayable driver for checks A0-A7, B0-B5, C1 (read-only git) |
| `row1-recheck.json` | its output, `all_ok=false`, 11/19 checks pass, exit 1 |
| `append-only-audit.json` | `tools/append-only-audit.py --to efc6b3e --json`, full output |
| `append-only-audit.txt` | same run's summary, unrestored events and the round-56 event count |
| `round56-correction-evidence.txt` | missing-receipt check in worktree and at base, deleted receipts' `met=True` at `8abadfed`, deletion diff, `git log -S` attribution |
| `lost-lines-c2c05e30.txt` | the 33 superseded lines with parent line numbers |
