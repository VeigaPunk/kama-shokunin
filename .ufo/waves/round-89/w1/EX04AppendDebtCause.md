# EX04AppendDebtCause — R4 cause (`round75-instruments` bad_rows=19)

## Scope

Read-only cause analysis of carried defect R4 for lane `kama-shokunin` at committed tip
`c8db858691e883955f10cf9d7e1dec8f8d732bc8`. Read `tools/round81-append-debt.py`,
`tools/append-only-audit.py`, both registers, `plans/round-88/89-claims.md`; ran the R4 command, the audit at
five revisions, the frozen late-row generator and the round-82 delta. Every experiment ran in one
`git clone --shared` under `/fast/scratch/hyaku/kama-r89/EX04AppendDebtCause/wt` with synthetic commits
(throwaway identity); scratch removed. No lane file edited; `PROVINCE.md`/`SCORECARD.md` are dirty from other
seats and were not touched (all measurements read committed objects at the tip). No tool installs, no network,
no server, no model.

## Commands and outputs (exit codes as run)

1. Lane, the R4 command: `python3 tools/round81-append-debt.py --repo . --round 88` → **exit 1**
   `APPEND_DEBT round=88 base=9b4c7af16fdd events=90 accepted=53 late=26 pending=3 unaccepted=11 bad_rows=19
   bad_declarations=0 out_of_population=0`; findings: 7 `hash-mismatch` (late 96-100, 103-104), 12
   `unknown-event` (late 117-128), 27 `count-short` lines (11 events).
2. Closing-round shape: same counter `--round 89` at the tip → **exit 1** `events=93 late=26 pending=0
   unaccepted=14 bad_rows=19` (three round-88 events join the unaccepted set).
3. Audit bracket (`tools/append-only-audit.py --to <rev> --json`, each exit 1 = audit's own unrestored debt):
   `to=94e8fe7b` cf28c470 `graded=9 undisclosed=9`, 65665250 `graded=12 undisclosed=12`;
   `to=3ad2b9e6` cf28c470 `graded=2 ungraded=11 undisclosed=2`, 65665250 `graded=0 ungraded=13
   undisclosed=0 status=ungraded`; `to=HEAD` unchanged since the flip.
4. Historical counter at those revisions (tool bytes of each revision): `--round 86` at `c5d71b7a` **exit 0**
   `late=27 unaccepted=0 bad_rows=0`; `--round 86` at `94e8fe7b` **exit 0** `late=27 unaccepted=0 bad_rows=0`;
   `--round 87` at `3ad2b9e6` **exit 1** `unaccepted=11 bad_rows=19`.
5. Set equality at row-introduction: audit `to=b0064016` `undisclosed(cf28c470)` = the 9 register rows;
   audit `to=c5d71b7a` `undisclosed(65665250)` = the 12 register rows (exact set equality, not just counts).
6. Scratch clone, unchanged (`c8db8586`), `--round 88` → **exit 1** `bad_rows=19 unaccepted=11` (lane reproduced).
7. Clone variant A (drop the 19 stale rows; `38afd3f4`) → **exit 1** `bad_rows=0 unaccepted=11`.
8. Clone variant B (`b19ada1e`: A + 27 generated rows accepting the round-86 events) → `--round 88` **exit 0**
   `late=37 unaccepted=0 bad_rows=0`; `--round 89` **exit 1** `unaccepted=3`.
9. Clone variant C (`969a3a00`: A + 30 generated rows = 27 round-86 + 3 round-88) → `--round 89` **exit 0**
   `APPEND_DEBT round=89 base=56174a1fa6a2 events=93 accepted=53 late=40 pending=0 unaccepted=0 bad_rows=0
   bad_declarations=0 out_of_population=0`; no findings. `--round 88` **exit 1** `out_of_population=3`.
10. Frozen generator cross-check at C: `python3 tools/round82-late-delta.py --repo . --round 89` **exit 0**
    `LATE_DELTA round=89 base=56174a1fa6a2 population=140 carried=110 new=30 bad=0`; at the unchanged tip the
    same live run is **exit 1** `bad=49`.
11. Instrument bytes untouched and self-tested in the clone: `git rev-parse HEAD:tools/round81-append-debt.py`
    = lane tip `bf33dac1e44267641cd64f0a7e3c7c289ae354cb`; audit `aa25456d35138a9df155d0d83c8f6ee09ab70c41`;
    `git diff --stat c8db8586 HEAD` = `registry/append-only-late.tsv` only; `--selftest` **exit 0**
    `APPEND_DEBT_SELFTEST pass=34 fail=0`.

## Findings

- **BLOCKER** — the round-89 close cannot pass arm `round75-instruments` at the tip: exit 1 with
  `bad_rows=19` and, at the closing-round base, `unaccepted=14`. Evidence: `clone-0-control.out`,
  `clone-c8db8586-r89-debt.out`.
- **DEFECT** — root cause is the audit's `<to>`-dependent exempt-region eligibility, not the register author.
  `tools/append-only-audit.py:649-669` makes a SCORECARD head title eligible when `max(section count over
  [event..<to>]) >= parent count`, so a later commit that regrows `## Planned` retroactively turns earlier
  `## Planned` rewrites ungraded; eligibility is monotone in `<to>` (window max and origin union only grow), so
  the flip is permanent. Round-87 commit `3ad2b9e6` regrew `## Planned` 10→19 (event parents 19 and 18):
  green at `94e8fe7b` (`bad_rows=0`) and red at `3ad2b9e6` (`bad_rows=19`) with no register or counter change.
  Evidence: `audit-to-94e8fe7b.json`, `audit-to-3ad2b9e6.json`, `hist-*.out`.
- **NOTE** — the 19 rows were correct when written: `b0064016` (rows 96-104, event `cf28c470`) and
  `c5d71b7a` (rows 117-128, event `65665250`) wrote exactly the audit's then-`undisclosed` sets (9 and 12).
  The 7 `hash-mismatch` rows belong to an event that still exists with 2 undisclosed lines (its dated-round line
  and the pre-heading banner line); the 12 `unknown-event` rows belong to an event the audit now marks
  `ungraded` with `undisclosed=0`, which the counter's `population()` drops. Evidence: `candidate-rows.json`,
  `audit-to-b0064016.json`, `audit-to-c5d71b7a.json`.
- **NOTE** — the 27 `count-short` lines are genuine unaccepted debt, independent of the 19: 11 `(commit,file)`
  events from 7 round-86 commits have zero rows in either register (round 86 accepted rounds 84/85, rounds 87/88
  honest-stopped; `corpus/lessons/round-88.md:101`). Variant A proves independence: `bad_rows=0` but still
  `unaccepted=11`, exit 1.
- **NOTE** — fix needs **register rows only**; a counter change is forbidden for the frozen instrument and
  wrong (the window-wide "not gutted" rule is pinned by selftest arm `exempt-gutted-then-regrown`). Candidate C
  reaches exit 0 at `--round 89` with both instrument blobs byte-identical and the frozen generator re-deriving
  the whole register (`carried=110 new=30 bad=0`). Variant B is the `--round 88` form; C is the closing-round
  form (its 3 round-88 rows are out of population at round 88).
- **NOTE** — residual ratchet: two currently-graded events are close to a re-flip (`latent-headroom.out`):
  `b5743975` ## Axes parent 54 vs max 52 (**2 lines of headroom**, 12 graded lines registered) and `dd9f5dc6`
  ## Retired headroom 5. A round-89 head rewrite that adds two `## Axes` lines reproduces R4 with 12 new
  `hash-mismatch` rows; re-run `--round 89` after the integration commit.
- **NOTE** — the round-82 delta's live mode is already red at the tip (`bad=49` at `--round 89`) and is not a
  gate arm (arm 12 runs only its selftest); C makes it green, so the candidate harms no other instrument.
  No build/lint/test suite was run (not named by the item; parent owns the post-integration gate).

## Deliverables

All under `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-89/w1/out/EX04AppendDebtCause/`:

- `cause.md` — cause per finding class, exact evidence commands and the flip table.
- `append-only-late.minus-spurious.tsv` (A, 110 rows), `append-only-late.corrected-r88.tsv` (B, 137 rows),
  `append-only-late.corrected-r89.tsv` (C, 140 rows) — never applied to the lane.
- `candidate-rows.json` — the 19 dropped and 30 added rows with full cells and note text.
- `make-candidates.py`, `latent-headroom.py` — re-derive the variants and the ratchet headroom.
- `audit-head.json`, `audit-to-b0064016.json`, `audit-to-c5d71b7a.json`, `audit-to-94e8fe7b.json`,
  `audit-to-3ad2b9e6.json` — the `<to>` bracket.
- `lane-round88-r4.out`, `clone-0-control.out`, `clone-A-minus-spurious.out`, `clone-B-r88-debt.out`,
  `clone-B-corrected.out`, `clone-C-r89-debt.out`, `clone-C-r89-delta.out`, `clone-C-r88-debt.out`,
  `clone-C-selftest.out`, `clone-c8db8586-r89-debt.out`, `clone-b19ada1e-r89-debt.out`,
  `clone-0-r82delta.out`, `clone-B-r82delta.out`, `hist-86-c5d71b7a.out`, `hist-86-94e8fe7b.out`,
  `hist-87-3ad2b9e6.out`, `latent-headroom.out` (+ matching `.err` files).

VERDICT: holds — R4 reproduces exactly (`bad_rows=19` = 7 hash-mismatch + 12 unknown-event, plus 27 count-short lines); cause is the audit's monotone `<to>`-dependent exempt-head eligibility, proven by a green→red flip at `3ad2b9e6` with no register change; register-only candidate C is green at `--round 89` (`unaccepted=0 bad_rows=0`, exit 0) with both frozen instruments byte-identical.
