# RV01ClaimsReview — round-86 C1 (rendered-cell identity) review

Seat: RV01ClaimsReview (reviewer, leaf). Judged on: calibration. Milestone: kama r86 w1.
Revisions measured (committed bytes, read-only git): base `3ff23da3f291ce8abf7bf5c54f9abacec67e3e8d`;
freeze `c07e1f909414aafb2d8de5605a81fd3bd4e3550e`; lane HEAD `f4c7acaa0563d1cf813fff90e4b927494a88091f`
(HEAD = freeze + dispatch commit; `tools/round86-rendered-cells.py` sha256 `e038b2c0…bddcf` in worktree and at freeze).
Report path note: the seat line names `.ufo/waves/round-86/w1/RV01ClaimsReview.md`; the contract confines writes to
the seat's out dir, so this report lives at `.ufo/waves/round-86/w1/out/RV01ClaimsReview/RV01ClaimsReview.md`. L1 to confirm.

## Verdict

- The frozen C1 counter is **not yet a sound closure gate**. At the freeze it correctly reports the stale cells
  (`mismatches=3`, exit 1). But it also **passes cells that violate the frozen predicate**: its gate fact never reads
  the named receipt at the named revision (fixtures f1, f4 below). Its selftest has no arm that can catch this.
- The counter also **misses one live stale pointer** in the calibration row (`test -f … round-84 …`, f6).
- My independent re-derivation agrees with the counter on all three facts at both committed revisions, and on all
  fixtures except the two revision-binding cases and the extra pointer.
- Round-number resolution of the newest closure is the right key for the row's meaning. The round-69 date ordering
  is only consistent with it inside its `--since-round 63` scope; unscoped it refuses (exit 2).

## Commands and exits (all in `receipts/EXITS.txt`; outputs in `receipts/`)

| Command (lane `L=/home/vgpnk/Projects/shokunin/kama-shokunin`) | Exit |
|---|---|
| `python3 $L/.ufo/waves/round-86/count.py c1 --repo $L --rev 3ff23da3… --work <scratch>/work-base` | 1 |
| `python3 $L/.ufo/waves/round-86/count.py c1 --repo $L --rev c07e1f90… --work <scratch>/work-freeze` | 1 |
| `python3 rc-freeze.py --selftest` (copy of freeze instrument, sha256 `e038b2c0…`) | 0 (`pass=11 fail=0`) |
| `python3 tools/round69-newest-closure-counter.py --repo $L --rev c07e1f90…` | 2 (`COULD_NOT_EVALUATE closure round-10-verifier-spotcheck.md carries no parsable ISO date`) |
| same with `--since-round 63`, at freeze and at base | 1 (`NEWEST_CLOSURE … round=85 row_names=…round-84…`) |
| my `rv01_c1_check.py --repo $L --rev {3ff23da3,c07e1f90,f4c7acaa}` | 1, 1, 1 |
| frozen instrument in-process (`run_instrument.py`) at same three revs | 1, 1, 1 |
| fixtures f1–f8, p1 through both checkers (see table) | see below |

Before receipts match my runs: `measured/before/c1.out` (`facts=3 mismatches=3 … newest_gate=85 newest_closure=85`, exit 1)
and `c1-selftest.out` (pass=11) reproduce byte-for-byte in substance.

## Independent re-derivation vs frozen instrument

Mine (`scripts/rv01_c1_check.py`): own HTML-comment/fence stripper (CommonMark backtick-info rule), column-0 cell
selection, ancestry via `merge-base --is-ancestor`, and the receipt read with `git show R:path` at the **named** R.

| Case (graded rev c07e1f90 unless noted) | Mine gate/closure/disp | Frozen gate/closure/disp | Agree? |
|---|---|---|---|
| base 3ff23da3 (do-nothing) | 0/0/0 | 0/0/0 | yes |
| freeze c07e1f90 (do-nothing) | 0/0/0 | 0/0/0 | yes |
| lane HEAD f4c7acaa | 0/0/0 | 0/0/0 | yes |
| f1: head repaired, R = `948dec78` (round-85 measured rev, no receipt there) | **0**/0/0 | **1**/0/0 | **NO** |
| f2: head repaired, R = `6abaf0a8` (receipt committed here) | 1/0/0 | 1/0/0 | yes |
| f3: head repaired, R = `3ff23da3` (receipt present) | 1/0/0 | 1/0/0 | yes |
| f4: token/cmd/receipt swapped 84→85, R left at `b53cd336` (no round-85 receipt) | **0**/0/0 | **1**/0/0 | **NO** |
| f5: row repaired only | 0/1/1 | 0/1/1 | yes |
| f6: row repaired, `test -f …round-84…` left in row | 1/1/1 + **extra stale pointer round-84** (exit 1) | 1/1/1, exit 0 | **NO** (extra) |
| f7: row + `test -f` repaired, head only R=6abaf0a8 | 1/1/1, exit 0 | 1/1/1, exit 0 | yes |
| f8: head R = graded freeze, row repaired | 1/1/1, exit 0 | 1/1/1, exit 0 | yes |
| p1: f7 with a leading line `` ```x``` inline note `` | 1/1/1, exit 0 | **exit 2** (could-not-evaluate) | verdict class differs, fail-closed |

Mismatch sub-checks in mine are finer-grained than the frozen three-fact count (e.g. base shows 5 finding lines for 3
facts); the fact-level verdicts are what is compared.

## Questions

**(1) A fact a do-nothing tree satisfies.** On committed bytes, the do-nothing tree (base and freeze) satisfies **none**
of the three facts (gate=0 closure=0 disposition=0). But the frozen gate fact is satisfiable **without binding the
receipt to the revision**:
- `instrument rc-freeze.py:267-274`: for each R that is an ancestor of the graded revision, it reads the receipt via
  `tree.blob(path)`, i.e. at the **graded** revision, never at R. R's bytes are not checked.
- Consequence: f4 is a three-token edit (84→85 in token, command, receipt path) that leaves the stale revision
  `b53cd336…` in place and passes the frozen gate fact. f1 does the same with the measured revision `948dec78…`,
  which the round-85 closure text names as the terminal measurement and which does not contain the receipt.
- The round-84 cell already violates this leg today: `.ufo/waves/round-84/measured/after/gate-final-green.out` does not
  exist at its named revision `b53cd336…` (`git cat-file` fatal), so "receipt bytes at R" is false for the current head
  while the instrument (at HEAD) reports only the round mismatch.
- Closure and disposition facts are pointer-name checks (satisfiable by text naming). That is what they claim to be, so
  I do not count them as defects.

**(2) Universal clauses.**
- "newest **terminal** gate receipt": `terminal` is never implemented. `newest_gate` (lines 203-218) takes the maximum round
  over every `.ufo/waves/round-N/measured/**/*.out` containing a `PRE_REPORT round=` line, including `before/` controls
  (e.g. `.ufo/waves/round-84/measured/before/ctl-gate.out`). A committed before-control at a higher round would become
  the required head token. Code-derived; not executed.
- "receipt's bytes **at R**" / "R names it": the coupling is existential over R in the paragraph but the bytes are read at
  the graded revision (see (1)). This is the one universal clause the instrument does not implement.
- "exact token": `token.group(0).strip("`") in text` (line 273) is a substring test, not a whole-line match. Not exercised
  on live bytes; code-derived.
- "word must occur in the closure body": `disposition_of` (lines 234-238) returns the **first** word in fixed order
  (`rejected-harmed`, `rejected-honest-stop`, `admitted`) found **anywhere** in the body. One quoted `rejected-harmed` in a
  future closure would force that word onto the row. Latent: round-84 and round-85 bodies contain no `rejected-harmed`
  (grep). Today's disposition is `rejected-honest-stop` for round 85 on both checkers.
- "fence-free (CommonMark 0.31.2 §4.4/§4.5)": the selector treats a column-0 line such as `` ```x``` `` as a fence opener
  (FENCE regex, line 63). CommonMark forbids backticks in a backtick fence's info string. Demonstrated by p1: the frozen
  instrument hides everything to EOF and returns exit 2. That is a fail-closed false refusal, not a false green.

**(3) Mismatches reported that are not real stale cells.** None at the freeze. Each finding matches committed bytes:
- `gate declared round=84 newest terminal receipt round=85 (.ufo/waves/round-85/measured/after/gate.out)`: head line 6
  carries `PRE_REPORT round=84` and the round-85 receipt exists at 3ff23da3, 6abaf0a8 and the freeze.
- `closure row names round-84 newest committed closure is round-85`: row line 18 names round-84.
- `disposition row does not name round85 rejected-honest-stop`: true, but **derivative** of the closure finding (one stale
  row produces two counted mismatches).
- Semantic note, not a false mismatch: the newest terminal receipt is **red** (`PRE_REPORT round=85 … failed=1`, exit 1).
  The instrument treats it as the newest terminal receipt and requires the head to name it. That is honest, but "terminal"
  should be declared as "final receipt of the round, any outcome".

**(4) Stale cells the counter misses at the freeze commit.**
- `SCORECARD.md:18` (calibration row): `File-presence-only: run test -f corpus/lessons/round-84-verifier-spotcheck.md && printf present → present`.
  It is a live verification command naming the superseded closure. The counter grades only the first closure mention
  (`ROW_CLOSURE.search`, line 77). Fixture f6 is green in the frozen counter (exit 0); my extra-pointer check flags it.
- `SCORECARD.md:6` (head): the round-84 coupled assertion names `b53cd336…` but the receipt is absent there (see (1)).
  The counter reads the receipt at the graded revision, so it cannot see this.
- `SCORECARD.md:18` evidence pointer `round-83 final SELFRECORD_R82 … at 1d90dc81…` while round-84/85 receipts exist.
  Candidate only: outside the predicate population and I did not establish it as false.
- Scan of other tracked files (non-wave, non-LOG) for `latest outside closure`, `Current authority (round` and
  `| calibration |`: no other live self-assessment cell. Historical occurrences are in `LOG.md` and superseded SCORECARD
  sections only.

## Newest-closure resolution: round number vs round-69 date ordering

- Closures `round-10` … `round-85` exist (rounds 20–23 have no closure file). `round-10` carries no ISO date at all, so the round-69 counter's unscoped run exits 2 on it, the first undated closure it reaches. Its date key comes from a `date:` field, then a heading date, then the **first ISO date anywhere in the body**.
- With `--since-round 63` the counter returns `round=85 date=2026-11-04`, and rounds 73–85 all carry `2026-11-04`. Its
  `(date, round)` sort therefore reduces to round order inside that era, with round as the tie-break.
- **Round number is the right key for the row's meaning.** "Latest outside closure" means the most recently filed lane
  closure, and rounds are filed sequentially. The date key is fragile: body-sourced dates, same-day ties, and undated early
  closures. A later-round closure whose body quotes an earlier date would make the date key pick an older closure. A round
  key cannot be inverted that way. The frozen predicate already states this.

## Counter provenance caveat (not a stale cell)

`count.py` runs the instrument from the **working tree** (`pathlib.Path(args.repo).resolve() / script`), not from
`git show REV:tools/…`, although its header says "committed bytes at --rev". c3 checks committed presence; c1 and c2 do not.
The working-tree instrument equals the freeze blob today, so the measured results stand. The "before" receipt for C1 measures
the new instrument over base bytes, which is valid only because the instrument reads `--rev`'s bytes; the instrument file itself
is absent at `3ff23da3`.

## Recommended repairs (for L1; not applied, I did not edit production files)

1. `gate_fact`: read the named receipt at R (`tree.blob` bound to R), require the whole-line token there, and require the
   named receipt path to be among the newest-round receipts. Then f1 and f4 go red.
2. Add selftest arms: revision-without-receipt (must be red), CommonMark backtick-info line (must not hide the head), second stale
   closure pointer in the row (must be red), disposition body with a quoted earlier verdict word (must pick the verdict).
3. Repair the head to name **R = `6abaf0a8…` or `3ff23da3…`** (receipt committed there), not the measured `948dec78…`. Repair the
   row's `test -f` pointer with its `latest outside closure` pointer.
4. Decide "terminal" explicitly and exclude `before/` control receipts from the newest-receipt population.

## Verification gaps

- Did not run the other two legs (C2, C3) or any of the lane's gate arms.
- Fixtures are in-process over real git history with one overridden blob (`SCORECARD.md`); nothing was committed and no lane
  path was written.
- The `before/` control-receipt concern in (2) and the substring-token concern are code-derived, not fixture-proven.

## Hygiene

- Only read-only git (`rev-parse`, `show`, `log`, `ls-tree`, `grep`, `cat-file`, `merge-base`, `diff --stat`, `status --porcelain`)
  against `-C /home/vgpnk/Projects/shokunin/kama-shokunin`. No mutating git or jj command.
- No tool was installed or upgraded. No pacman/uv/npm activity.
- Scratch `/fast/scratch/hyaku/kama-r86/RV01ClaimsReview/` was used for fixtures and removed after copying scripts and receipts here.
