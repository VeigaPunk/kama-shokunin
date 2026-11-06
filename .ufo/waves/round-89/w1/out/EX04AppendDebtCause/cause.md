# R4 cause — `round75-instruments` red at round 89 (bad_rows=19 + count-short)

Scope: read-only investigation of the carried r87→r88→r89 defect (`plans/round-89-claims.md` "carried
defects" R4). No lane file was edited; every experiment ran in `/fast/scratch/hyaku/kama-r89/EX04AppendDebtCause/wt`
(`git clone --shared`, synthetic commits with a throwaway identity, since removed).

## What the two instruments actually grade

`tools/round81-append-debt.py --round N` builds its population from `tools/append-only-audit.py --json` at the
audited revision `<to>` (= HEAD), keeps events with a non-empty `undisclosed` list (`population()`, counter
lines 88-94), and requires every graded line of every event ancestral to the frozen plan's base to be covered by
one register row. A row is bound to the audit's `undisclosed` entry for the same `(commit, file, line_sha256)`;
the audit's `undisclosed` is **graded lines not held at `<to>`**, not "deleted lines".

The audit's graded/ungraded split is a function of `<to>`:
`tools/append-only-audit.py:649` sets `window = commits[i:]`; :654-656 makes an exempt SCORECARD head title
eligible only when `max(section_counts(title) over window) >= parent count` (the "not gutted" test);
:669 skips a deleted line when its parent section is eligible and the line's origin (union over commits
reachable from `<to>`, :601-632) intersects those titles. Extending `<to>` can therefore only *add* commits to
the window and to the origin union, so eligibility is monotone: **once a deletion becomes ungraded it can never
become graded again**, while a graded deletion can become ungraded at any later commit.

## Class 1 — `hash-mismatch` late lines 96-100, 103-104 (7 rows, event cf28c470)

Rows introduced by `b0064016` ("round-82: … 15 late rows for round 81's five events"); event `cf28c470`
(round-81, `git show --stat cf28c470` → SCORECARD.md 13/13).
At the row-introducing revision the audit's `undisclosed` set for this event was exactly those 9 hashes
(set equality, not just count): audit `to=b0064016` → `cf28c470 SCORECARD.md graded=9 ungraded=4
undisclosed=9`, and `set(undisclosed) == set(register rows for cf28c470)`. The 9 registered deleted lines are
under `## Planned` (7), a dated-round section and the pre-heading banner (the 2 rows that still pass today).
The flip: audit `to=94e8fe7b` (parent of the round-87 commit `3ad2b9e6`) → `graded=9 undisclosed=9`;
audit `to=3ad2b9e6` → `graded=2 ungraded=11 undisclosed=2`. `3ad2b9e6` regrew `## Planned` from 10 to 19
lines; the event's parent had 19, so the title became eligible and the 7 `## Planned` lines that had been graded
turned ungraded (13 deleted lines: 7 Planned + one each under Axes, Capabilities, Retired, Saturation, a dated
round section and the pre-heading banner; the 4 head lines were already ungraded at write time). The 7 stale
rows now name hashes the audit no longer reports for the event (the event itself survives with its 2 graded
lines, both registered).

## Class 2 — `unknown-event` late lines 117-128 (12 rows, event 65665250)

Rows introduced by `c5d71b7a` ("round-86: … accept the inherited append debt"); event `65665250` is a round-84
commit (`git cat-file -p 65665250` → subject `round-84: retain integrated measurements…`), so the notes'
`round-86 accepts round-84` were right. At `to=c5d71b7a` the audit reported
`65665250 SCORECARD.md graded=12 ungraded=1 undisclosed=12`, again set-equal to the 12 rows.
All 12 registered lines are `## Planned` (the thirteenth deleted line is an `## Axes` line that was already
ungraded; `## Planned`'s parent count is 18). After `3ad2b9e6` (Planned → 19 >= 18) the audit at
any later `<to>` reports `graded=0 ungraded=13 undisclosed=0`, `status=ungraded`; `population()` drops the key, so
the 12 rows fall through `all_events.get(key) is None` → `unknown-event`.

## Class 3 — `count-short` (27 finding lines / 11 events at `--round 88`)

Not a row defect: these are graded events whose `undisclosed` entries are covered by no row at all
(`grep -c` of each commit in both registers = 0). Seven round-86 commits (`079cd67c`, `239a8f39`, `67edda`,
`84e6f4`, `c5a324`, `cef1d7`, `d05f6d`, 11 `(commit,file)` events, 27 lines) were never accepted: round-86's
own commit accepted rounds 84/85 (`c5d71b7a`), and rounds 87/88 honest-stopped without appending acceptance rows
(`corpus/lessons/round-88.md:101` records R4 as carried). The red appeared at round 87, not 86:

| `to` | command | exit | summary |
|---|---|---|---|
| c5d71b7a (rows written) | `round81-append-debt.py --round 86` | 0 | `late=27 unaccepted=0 bad_rows=0` |
| 94e8fe7b (pre-flip) | same | 0 | `late=27 unaccepted=0 bad_rows=0` |
| 3ad2b9e6 (round-87 flip) | `--round 87` | 1 | `unaccepted=11 bad_rows=19` |
| c8db8586 (tip, R4 command) | `--round 88` | 1 | `unaccepted=11 bad_rows=19` |

No register row and no counter byte changed between the green and red runs; only the audited revision advanced.

## Fix — register rows only, no counter change

The counter and audit blobs are byte-identical to the lane tip in every candidate run
(`tools/round81-append-debt.py` bf33dac1…, `tools/append-only-audit.py` aa25456d…; selftest `pass=34 fail=0`).
Changing either is forbidden for a frozen instrument and would be the wrong fix: the window-wide "not gutted"
rule is deliberate (selftest arm `exempt-gutted-then-regrown` pins it). The register must instead carry only
lines the audit at the closing revision reports, and must accept the unregistered events.

Candidates (never applied to the lane; each committed in the scratch clone and graded there):

| variant | file | rows | `--round 88` | `--round 89` |
|---|---|---|---|---|
| A drop 19 stale | `append-only-late.minus-spurious.tsv` | 110 | exit 1 `bad_rows=0 unaccepted=11` | — |
| B A + 27 round-86 rows | `append-only-late.corrected-r88.tsv` | 137 | **exit 0** `late=37 unaccepted=0 bad_rows=0` | exit 1 `unaccepted=3` |
| C A + 30 rows (27 round-86 + 3 round-88) | `append-only-late.corrected-r89.tsv` | 140 | exit 1 `out_of_population=3` | **exit 0** `late=40 unaccepted=0 bad_rows=0 out_of_population=0` |

Variant C is the one the closing round needs (the gate runs `--round <closing round>`; base `56174a1a`, so the
three round-88 events `138a7543`, `eb664062` ×2 are graded and must be accepted too). Cross-check with the
frozen generator: `round82-late-delta.py --round 89` (live mode, not a gate arm) at the tip is red
(`population=140 carried=110 new=30 bad=49`) and at C is `carried=110 new=30 bad=0` exit 0 — C is exactly the
frozen `tools/round81-late-rows.py generate` output for the round-89 population with every carried row
byte-unchanged. C under `--round 88` is red only because its 3 round-88 rows are out of that base's population
(`out_of_population=3`); use B if the arm is ever graded at round 88.

## Residual risk (the same defect will recur)

Eligibility is monotone in `<to>`, so any future commit that regrows an exempt head past a past event's parent
count strands that event's rows. Two currently-graded events are inside the ratchet today
(`latent-headroom.py`): `b5743975` (## Axes, parent 54, current max 52 → **2 lines of headroom**, 12 graded
lines registered) and `dd9f5dc6` (## Retired, parent 9, max 4 → 5 lines). A round-89 head rewrite that adds two
`## Axes` lines reproduces R4 with 12 new `hash-mismatch` rows. Re-run
`python3 tools/round81-append-debt.py --repo . --round 89` after the integration commit; if new
`hash-mismatch`/`unknown-event` findings appear, re-derive the rows against the new tip (never freeze `<to>` in
the counter).

## Evidence commands (lane, read-only; exit codes as run)

```
python3 tools/round81-append-debt.py --repo . --round 88        # exit 1 bad_rows=19 (7 hash-mismatch, 12 unknown-event), 27 count-short lines
python3 tools/append-only-audit.py --repo . --to <rev> --json    # bracket: 94e8fe7b, 3ad2b9e6, b0064016, c5d71b7a
git blame --line-porcelain HEAD -- registry/append-only-late.tsv # rows 96-104 -> b0064016, 117-128 -> c5d71b7a
git show cf28c470 -- SCORECARD.md ; git show --stat 65665250      # the two events
```
