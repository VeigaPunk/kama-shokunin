# DRAFT — SCORECARD.md and LOG.md round-99 correction blocks (seat SB01Entry, round 99, lane kama)

Status: DRAFT for the committer (KamaR99). Not applied to any tracked lane file by this seat.
Targets: `SCORECARD.md` (appended after the stale wave line at `SCORECARD.md:6431`) and `LOG.md`
(appended after the stale wave line at `LOG.md:4040`).

Every number in these blocks was re-derived by this seat on 2026-11-08, not copied from the
round-98 prose:

- **12 seats, 12 results, 0 dead** — `.ufo/waves/round-98/w1-results.json`: `seats` = 12, `results`
  array length = 12, and every entry's `output` is non-empty (lengths 3876–12 367 bytes, min
  `CR01Boundary` 636 bytes) → dead = 0
  (receipt `../receipts/w1-results-derivation.out`).
- **7 attack / 5 non-attack** — derived by the counter's own role set
  (`tools/round99-record-audit.py:83`: `ATTACK_ROLES = {reviewer, critic, mutation-tester, sentinel,
  revenger}`), not by reading the stale prose. The seven attack seats are `RV01SelfAssess`
  (reviewer), `RV02BudgetCells` (reviewer), `CR01Boundary` (critic), `CR02Wording` (critic),
  `MT01Forgeries` (mutation-tester), `SN01StepFlips` (sentinel), `RV03Intent` (revenger); the five
  others are `SC01SiblingScan` (scout), `SC02SourceReopen` (scout), `EX01SelfAssessControl`
  (executor), `EX02BudgetControl` (executor), `CN01Overlap` (connector)
  (receipt `../receipts/c2-base-mismatch-detail.out` shows exactly this split at base).
- **`EX02BudgetControl` vs `SB01-equivalent`** — `LOG.md:4044` credits "SB01-equivalent prose carried
  by the lesson"; the results file names no such seat. The fifth non-attack seat is
  `EX02BudgetControl`.
- **`RV03Intent`** — the round-98 SCORECARD's attack list (`SCORECARD.md:6433-6434`) omits it; the
  results file carries it with a non-empty output.
- **Census base/tip groups** — `git show 681c80a4:corpus/SOURCES.md` → 361 rows (A 344, B 11, C 6;
  mined 324, queued 8, rejected 29); `git show 649bb2e9:corpus/SOURCES.md` → 363 rows (A 345, B 11,
  C 7; mined 325, queued 8, rejected 30). Both re-derived with
  `bash /home/vgpnk/Projects/shokunin/scripts/sources-census.sh census --file <file>`
  (receipt `../receipts/census-base-tip.out`).
- **The gate's six failed arms** — from `.ufo/waves/round-98/measured/pre-report-gate.out`:
  `selfdesc`, `newest-closure`, `round-scope`, `round-clean`, `round75-instruments`,
  `round78-instruments` (the receipt's `PRE_REPORT_ARM <name> exit=<n> FAIL` lines), under the
  verdict line `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1`. The round-98 erratum named five,
  omitting `round-clean`.

---

## 1. The `SCORECARD.md` block (append at the end of `SCORECARD.md`)

```
## Round 99 correction — round-98 wave accounting (appended 2026-11-08; the round-98 entries above are not rewritten)

The round-98 wave line "10 reported, 2 dead" (`SCORECARD.md:6431`; the same sentence is `LOG.md:4040`) is wrong. `.ufo/waves/round-98/w1-results.json` at `649bb2e9` carries **12 seats** and **12 results**, every result with a non-empty output, and `corpus/lessons/round-98.md` M3 records that `RV03Intent` and `EX02BudgetControl` settled inside the same wave: **12 reported, 0 dead**. The split is **7 attack** seats — `RV01SelfAssess`, `RV02BudgetCells`, `CR01Boundary`, `CR02Wording`, `MT01Forgeries`, `SN01StepFlips`, `RV03Intent` — and **5 non-attack** seats — `SC01SiblingScan`, `SC02SourceReopen`, `EX01SelfAssessControl`, `EX02BudgetControl`, `CN01Overlap`. `LOG.md:4044` credits "SB01-equivalent prose carried by the lesson" where the fifth non-attack seat belongs; the seat is `EX02BudgetControl`. The SCORECARD line that lists the attack seats omits `RV03Intent`; the derived count is seven. The round-98 pre-report gate receipt `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1` has six failed arms — `selfdesc`, `newest-closure`, `round-scope`, `round-clean`, `round75-instruments`, `round78-instruments` — and the round-98 erratum named five, omitting `round-clean`. Re-derived by `python3 tools/round99-record-audit.py --repo . --rev <rev>` (`RECORD_AUDIT99 checks=12`).
```

## 2. The `LOG.md` block (append at the end of `LOG.md`)

```
## Round 99 correction — round-98 wave accounting (appended 2026-11-08; the entry above is not rewritten)

The round-98 wave line "10 reported, 2 dead" (`LOG.md:4040`; the SCORECARD twin is `SCORECARD.md:6431`) is wrong: `.ufo/waves/round-98/w1-results.json` carries **12 seats** and **12 results**, every result with a non-empty output, so it is **12 reported, 0 dead** (lesson M3: `RV03Intent` and `EX02BudgetControl` settled). The split is **7 attack** (`RV01SelfAssess`, `RV02BudgetCells`, `CR01Boundary`, `CR02Wording`, `MT01Forgeries`, `SN01StepFlips`, `RV03Intent`) and **5 non-attack** (`SC01SiblingScan`, `SC02SourceReopen`, `EX01SelfAssessControl`, `EX02BudgetControl`, `CN01Overlap`); the "SB01-equivalent prose" seat above is `EX02BudgetControl`. The gate receipt `PRE_REPORT round=98 arms=14 failed=6 uncommitted=1` names six failed arms (`selfdesc`, `newest-closure`, `round-scope`, `round-clean`, `round75-instruments`, `round78-instruments`), not five.
```

---

## 3. Grading of these drafts against the frozen counter

Materialised a tree under this seat's scratch containing the working-tree `SCORECARD.md` and `LOG.md`
(with these blocks), `corpus/lessons/round-98.md`, `corpus/lessons/round-99.md` (this seat's lesson
draft), `.ufo/waves/round-98/w1-results.json` and `.ufo/waves/round-98/measured/pre-report-gate.out`,
and ran:

```
python3 tools/round99-record-audit.py --repo . --tree <scratch tree> --work <scratch>
RECORD_AUDIT99 checks=12 mismatches=0 met=True rev=tree:<scratch tree>
```

exit 0 (receipt `../receipts/c2-tree-graded.out`). The same command against the freeze-commit bytes
of the counter (`git show f6e7ccc2:tools/round99-record-audit.py`) on the same tree reports
`mismatches=1` — check 8 — because that committed byte reads the two census revisions from the
materialised tree instead of from git, so it sees the tree's tip SOURCES.md for both revisions
(receipt `../receipts/c2-frozen-counter-vs-tree.out`). The working-tree counter carries the fix
(`tools/round99-record-audit.py:250-257`: "The two census revisions are historical and always come
from git, also under `--tree`"), and that fix is a change to a frozen counter's bytes — see the
report's findings section; the committer must decide whether the fix lands before M2 and whether the
plan's "counter bytes change after the freeze commit" kill rule K1 is thereby met.

## 4. The forgery control this seat ran (the plan's K4)

Materialised a second tree with the correction text forged back to "10 reported, 2 dead" and ran the
same counter with `--tree`:

```
RECORD_AUDIT99_MISMATCH 1 SCORECARD block states 12 reported, 0 dead after the stale line
RECORD_AUDIT99_MISMATCH 2 LOG block states 12 reported, 0 dead after the stale line
RECORD_AUDIT99 checks=12 mismatches=2 met=False rev=tree:<scratch forge tree>
```

exit 1 (receipt `../receipts/c2-forged-rerun.out`). The forged correction is refused, so the
counter discriminates on the correction's content and not on its presence.
