# CR02ClaimC2 — falsification attempt on round-88 C2 (calibration)

## Scope

C2's frozen predicate only: `tools/round42-selfdesc-reconcile.py --tip M` `mismatches=0 met=True`,
`tools/round69-newest-closure-counter.py --rev M --since-round 63` exit 0, the three instruments
byte-identical B..M, and the moved round-85 row present verbatim at M. Plus the three ordered
attacks: (a) is this a thin/bookkeeping claim a cheap control reaches, (b) does the SCORECARD move
harm any other SCORECARD reader, (c) does any M statement contradict observed repo state.
Revisions: B `9b4c7af16fdd4bba9e4815f4615f4b003f340747`, F `fb76e7f2…`, I `68ab526e…`,
M `138a75437bcd11b72446087e970f5dfc5abf9ccd`, T `f77d2ae9f2797a19e7548989fb9e64d8f9411d3f`.
Scratch `/fast/scratch/hyaku/kama-r88/CR02ClaimC2` (one `--shared` clone + two `git init` fixture
repos, all under scratch, all removed). No tool installed, no pacman, no live router touched,
no lane file modified.

## Commands and outputs

All receipts in `.ufo/waves/round-88/w1/out/CR02ClaimC2/`; `$T` = lane `tools/`.

1. `python3 $T/round42-selfdesc-reconcile.py --repo <clone> --tip B --work $TMPDIR/w-B`
   → `r41=0 banner=0 planned=0 retired=1 saturation=1 caps=1 … closure_ptr=0 mismatches=4 maxN=86 met=False`, exit 1 (`c2-reconcile-B.out`).
   at M → `retired=0 saturation=0 caps=0 … closure_ptr=1 mismatches=0 maxN=88 met=True`, exit 0 (`c2-reconcile-M.out`); at T identical, exit 0 (`c2-reconcile-TIP.out`).
2. `python3 $T/round69-newest-closure-counter.py --repo <clone> --rev B --since-round 63`
   → `STALE_CALIBRATION row_names=…round-86… newest=…round-87…`, exit 1 (`c2-newest-B.out`);
   at M → `row_names=…round-87… row_current=true`, exit 0 (`c2-newest-M.out`); at T exit 0.
3. `python3 out/CR02ClaimC2/check-c2.py --repo <clone>` → `RESULT fail=0`, exit 0 (`check-c2.out`):
   seven instruments (`r42`, `r41`, `r69`, `r74`, `r86-rendered-cells`, `r84`, `r72-round-scope`)
   sha256-identical at B, F, I, M, T (`H ok` ×7); both B calibration rows found verbatim exactly
   once at M (len 1127 and 1377); live axes table 7 rows → 6, 2 calibration rows in the
   `### Superseded calibration rows` subsection under its own table header (M:SCORECARD.md:24-28).
4. Attack (b), five named readers, same command at B and at M (`instruments-B.out` / `instruments-M.out`):
   - `round41-scorecard-reconcile.py --repo . --tip <rev>` → `axes=6 facts=26 hash_bad=0 … mismatches=0 met=True` exit 0 at **both**.
   - `round74-selfdesc-canon.py --repo .` → exit 0 at both (`canon_round=86 canon_rows=52` → `canon_round=88 canon_rows=55 total=55 invisible=0`).
   - `round86-rendered-cells.py --repo . --rev <rev>` → exit 1 at both: B `mismatches=3 gate=0 closure=0 disposition=0`, M `mismatches=2 gate=0 closure=1 disposition=0` (closure fact red→ok; no ok→red).
   - `round84-selfrecord-round83.py --repo .` → exit 1 at both, identical `claims=8 mismatches=1 corrected=5 unbacked=1` (F8 stale).
   - `round72-round-scope.py --repo . --round 88 --tip <rev>` → B exit 1 only because `plans/round-88-claims.md status=absent` at B (the plan lands at F, not a C2 effect); M exit 0. Control: `--round 87` exit 0 at B **and** at M.
5. Extra readers (`other-scorecard-readers.out`): `round43-registry-audit.py --tip` prints the
   identical three `detail:` lines (pins/selftest/spot) exit 1 at B and M; `round73-round-scope-cases.py --round 87|88 --tip` exit 0 at M; `round64-c2-counter.py --tip` **improves**:
   B `closure: own=closure-norow ptr=None newest=87 planted_ok=False mismatches={}` vs
   M `own=closure ptr=87 newest=87 planted_ok=True mismatches={'fixed': 0, 'stale': 1}` (exit 1 both,
   on unrelated arms) — the duplicate row was *blocking* r64's planted closure control at B.
6. Attack (a), destructive cheat from the B tree in a `git init` fixture (`cheat-fixture.out`):
   three edits only — delete the round-85 calibration row, delete the `gate-round86-instruments`
   row from the head Capabilities table, re-point the live row's `latest outside closure` to 87 —
   then `round42 … --tip HEAD` → `mismatches=0 met=True` **exit 0**; `round69 …` → `row_current=true` exit 0;
   `capability-repertoire-audit.py` → `listed 52 observed 52 missing 0 met True` exit 0. The deleted
   capability is gone: `git show HEAD~1:SCORECARD.md | grep -c 'round-85 terminal'` → `0`.
   Blanking control on top (`cheat B`, Retired+Saturation bodies emptied) → `mismatches=5 met=False` exit 1.
7. Attack (c), independent content checks (`check-c2.out`, all `C ok`): 6 unique axes rows and the
   vector `operability 8, freshness 8, depth 7, coverage 9, calibration 7, adjacency 7` (same cells as B);
   `canon round=88 rows=55 unique=55`, head table 55 = canon, 55 = B's 52 + {gate-round86-instruments,
   router-mode-readiness, pinned-fixture-restore} with no removals; first-working rounds = 31 entries
   incl. 87 and 88 and present in Saturation; `Retired` `6 axes` / `55 capabilities`;
   `### Planned (round 89)` followed by `1. …`; live `SKILL.md` anchor `6b378d50…` (1778 lines) and
   `cross-lane-scope` anchor `c45318b5…` (148 lines) match the M blobs byte-for-byte.
   Planned item 1's `bad_rows=19` is corroborated by `.ufo/waves/round-87/measured/gate-tip.out:8`
   and `.ufo/waves/round-88/measured/gate.out:9`.
8. Append-debt attribution (`append-debt-attribution.out`): `round81-append-debt.py --repo . --round 88`
   B exit 2 (base), I `pending=0`, M `pending=1` with `bad_rows=19 unaccepted=11` unchanged.

## Findings

**C2 corroborated, not falsified.**
- NOTE — every predicate conjunct re-derives: mismatches 4→0 and r69 1→0 at M and at T; seven
  instruments byte-identical across B, F, I, M, T; both B calibration rows present verbatim once
  at M; live table back to one row per axis. `c2-reconcile-M.out`, `c2-newest-M.out`, `check-c2.out`.
- NOTE (c) — no M statement contradicts observed state on the four named surfaces (vector, 55,
  firsts, Planned 89) or on the two hash anchors the edits changed (`SKILL.md`, `cross-lane-scope.md`);
  the 55 is B's 52 plus three additions, each with an evidence token that exists at M. `check-c2.out`.
- NOTE (b) — no SCORECARD reader regressed: five named tools show no ok→red transition; r86 went
  3→2, r64's planted closure control went from *unable to run* (`closure-norow`) to `planted_ok=True`,
  r74 advanced 52→55, r43/r84 are byte-identically red at B and M. `instruments-*.out`, `other-scorecard-readers.out`.
- DEFECT — the counter pair cannot distinguish the landed reconciliation from information
  destruction. The minimal cheat that deletes the round-85 row and the head `gate-round86-instruments`
  row and re-points one number is green on **all three** available counters (r42 0, r69 0,
  capability-repertoire-audit `met True`) while the row is provably absent. C2's fourth conjunct
  ("moved row present verbatim") is the only thing separating honest from destructive work, and no
  committed instrument checks it — it is asserted only by an ad-hoc line in `measured/c2.out` and by
  my `check-c2.py`. Smallest safe correction for a future round (instruments are frozen now): make
  the row-preservation conjunct a committed check that (i) requires every `| calibration |` row of
  the base outside `## Axes` to appear verbatim under a history heading, and (ii) requires the
  capability multiset of the head table to be non-decreasing across the round, so deletion cannot
  buy a green. Evidence: `cheat-fixture.out`.
- NOTE — `capability-repertoire-audit.py` is *not* an independent count: its `observed` set is text
  derived from "ANY capability-shaped table" in SCORECARD.md (`tools/capability-repertoire-audit.py:11-15,150-156`),
  which the cheat confirms (deleting the head row moves both sides to 52). It was red at B
  (`listed 52 observed 53 missing 1`) purely because the head table carried one row canon lacked, so
  "55 capabilities" rests on two text tables agreeing, not on an inventory. Note also it is the same
  relation r42's `caps` fact already encodes.
- NOTE — `measured/c2.out` line `# moved rows present verbatim at M: [True, True, True]` lists three
  rows, but B has exactly two `| calibration |` rows and I re-derive exactly two. The third element
  has no committed generator and no documented referent; no effect on the verdict (2/2 hold).
- NOTE — at M `round86-rendered-cells` still prints `gate=0 disposition=0`, which is an instrument
  defect, not a false SCORECARD statement: it counts the red round-87 gate receipt
  (`PRE_REPORT round=87 arms=14 failed=4`, gate exit=1) as the newest "terminal" gate, while the
  newest *green* terminal gate is round-86 (`PRE_REPORT round=86 arms=13 failed=0`, exit 0) — the one
  the banner names; and its disposition oracle's `rejected-harmed` expectation is the defect already
  recorded at `corpus/lessons/round-87-verifier-spotcheck.md:70`. C2's "reconciled" scope is the r42
  counter only; two of that neighbouring instrument's three facts remain disputed at M.
- NOTE — `pending` 0 (at I) → 1 (at M) is normal, not harm: `tools/round81-append-debt.py:17-23`
  defines `pending` as the graded round's own record edits awaiting the next round's acceptance, and
  `bad_rows`/`unaccepted` did not move (19/11 at I and M). But the round-88 record never states that
  C2's SCORECARD rewrite added a pending append-only event; Planned item 1 mentions only the carried
  `bad_rows=19`. Evidence: `append-debt-attribution.out`.
- NOTE — the round's own gate at M is red: `PRE_REPORT round=88 arms=14 failed=3 uncommitted=4`
  (round-scope, round-clean, round75-instruments), exit 1 (`.ufo/waves/round-88/measured/gate.out`).
  C2 claims no gate, and the failing arms are the carried debt + receipts untracked at measurement
  time, so this is not a falsification — but "self-description reconciled" is true only of the
  two frozen counters, not of the lane's whole instrument surface.

## Deliverables

`.ufo/waves/round-88/w1/out/CR02ClaimC2/`: `check-c2.py` (re-derives H/V/C, exit 0),
`check-c2.out`, `c2-reconcile-{B,M,TIP}.out`, `c2-newest-{B,M,TIP}.out`, `instruments-{B,M}.out`,
`other-scorecard-readers.out`, `cheat-fixture.out`, `append-debt-attribution.out`.
Scratch removed; lane worktree has no tracked modifications (only sibling wave files untracked).

VERDICT: holds — C2 reproduces exactly at M (and at T) with instruments byte-identical and both rows verbatim; the sole defect is that the counters alone cannot distinguish it from a destructive deletion, which C2's unenforced row-preservation conjunct does satisfy.
