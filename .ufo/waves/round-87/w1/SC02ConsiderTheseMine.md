# SC02ConsiderTheseMine — considerthese/2026-10-26.md proposal census (kama r87 w1)

## Scope

Scout seat, leaf, no delegation, no model chosen. Read-only census of the four numbered
proposals in `considerthese/2026-10-26.md` §Self-improvement suggestions (lines 29, 31, 33, 35).
For each: number, one-line text, and whether already implemented in the lane, decided by grep in
`LOG.md`, `SCORECARD.md`, `tools/`, `corpus/` and `plans/`, with `path:line` citations. One
still-unimplemented proposal improving calibration or operability was chosen and grounded by
opening the pointers it cites inside the lane's own files.

Measured revision `94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659` (round-87 freeze commit), read
from a `git clone --shared` scratch worktree at
`/fast/scratch/hyaku/kama-r87/SC02ConsiderTheseMine/wt`. No lane file edited; no git/jj mutation
anywhere; no network call; no tool installed or upgraded (nothing needed); scratch removed after
the receipts were copied.

## Commands and outputs (exit codes)

```
$ git -C wt checkout --detach 94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659
HEAD is now at 94e8fe7b round-87: freeze claims C1/C2, do-nothing controls, commit round-86 strays (R86V1)
$ git -C wt rev-parse --show-toplevel
/fast/scratch/hyaku/kama-r87/SC02ConsiderTheseMine/wt                                    # exit 0
$ git -C wt rev-parse HEAD
94e8fe7b911a5e6f8d1e1a07bff110d3ff6cb659                                                # exit 0
$ python3 tools/round74-selfdesc-canon.py --repo .
SELFDESC_CANON_V2 canon_round=86 canon_rows=52 demonstrated=0 total=52 invisible=0            # exit 0
$ python3 tools/shortcut-tally.py --repo . --rev 94e8fe7b... --rounds 40-86
... rounds 55-86 every row: shortcuts=- cheats=0 mutants=-
... rounds 48-54 status=unreadable:mutation-report                                        # exit 0
$ python3 tools/shortcut-tally.py --repo . --rev 94e8fe7b... --rounds 80-86 --wide
shortcut-tally.py: error: unrecognized arguments: --wide                                 # exit 2
$ python3 tools/append-only-audit.py --repo . --to 94e8fe7b...
summary commits=778 files=168 events=312 restored=103 partial=0 unrestored=91
        ungraded=113 disclosed=5 ... ungraded_lines=521 regressed=0                       # exit 1
$ for f in considerthese/*.md; do grep -cE '^\|.*(taken up|deferred|rejected|pending)' "$f"; done
2026-10-19:0  2026-10-20:0  2026-10-21:0  2026-10-22:0
2026-10-23:4  2026-10-24:1  2026-10-25:0  2026-10-26:2    # all 8 are round-verdict rows, not proposal rows
$ find . -path ./.git -prune -o -path ./.ufo -prune -o -type f \
      \( -iname '*proposal*' -o -iname '*disposition*' -o -iname '*considerthese*' \) -print
./considerthese                                                     # only the operator's dir; no ledger
$ grep -E '"[^"]*proposal[^"]*"' tools/*.py | grep -v 'considerthese/2026'
(no hits)                                                             # no tool parses a disposition
$ for n in $(seq 76 86); do grep -cE '^\|.*considerthese/2026-10-2[0-9]\.md' corpus/lessons/round-$n.md; done
76:0 77:0 78:0 79:0 80:0 81:0 82:0 83:0 84:0 85:0 86:0                                  # instance lapsed
$ grep -n 'stay unimplemented' corpus/lessons/*.md LOG.md
corpus/lessons/round-86.md:115                                                    # the only occurrence
```

## Findings

**F1 — Proposal table** (every citation is in `out/SC02ConsiderTheseMine/mine.md` §1):

| # | proposal | implemented? |
|---|---|---|
| 1 | flag deletions in append-only files the morning after | **YES** — `tools/append-only-audit.py:6` (names the proposal), `SCORECARD.md:143` capability row, `tools/round81-append-debt.py`, `corpus/lessons/round-81.md:98-101`, `corpus/lessons/round-76.md:145-146`, `corpus/lessons/round-74.md:18` |
| 2 | track what happens to my own proposals | **NO** — criterion `corpus/QUALITY.md:477` (KQ97) exists, but no daily file carries a disposition table (0 proposal rows across all 8 files), no ledger artifact exists, no tool parses one, and the one-off lesson table lapsed after round 75 (`corpus/lessons/round-75.md:87`) |
| 3 | running count of counters a shortcut can satisfy | **PARTIAL** — `tools/shortcut-tally.py:12` exists and runs, `corpus/QUALITY.md:549` (KQ118), `SKILL.md:1520`; but **not** a registered capability (`SCORECARD.md:5363` round-86 canonical list → 0 shortcut rows; selfdesc-canon `canon_rows=52`), not a gate arm (`tools/pre-report-gate.py` → 0 "shortcut" hits), and the measured count is empty for rounds 55–86 |
| 4 | report the pin gap every morning | **PARTIAL** — `tools/pin-watch.py` is a capability (`SCORECARD.md:140`), `corpus/QUALITY.md:570` (KQ122) requires the line, live runs exist (`corpus/lessons/round-74.md:18` `pins=3 current=0 behind=3`); but no daily file carries a pin-gap line; `corpus/lessons/round-81.md:102` "stays pending" |

**F2 — Chosen: proposal 2.** Its premise checks out in-lane: 2026-10-25 proposals 2, 1 and 1
became rounds 41/42/43 (`corpus/lessons/round-41.md:12`, `round-42.md:12`, `round-43.md:12`), and
the parenthetical deferral is verbatim at `corpus/lessons/round-40-verifier-spotcheck.md:80`
("a watch run today detects nothing"). Its stated purpose is calibration of the lane's own
self-report: "would let me calibrate what kind of proposal is useful and stop repeating ones
that keep getting deferred".
**F3 — The disposition record is contradictory and unreconciled.** P1 is implemented
(`tools/append-only-audit.py`; `SCORECARD.md:143`; `tools/round81-append-debt.py`; round-81 C2)
yet `corpus/lessons/round-86.md:115-116` records "Proposals 1, 2 and 4 stay unimplemented".
Round-86's lesson never re-opens the artifact (grep "append-only-audit" in `round-86.md` → 0
hits), and no later file reconciles the two records (grep "stay unimplemented" across
`corpus/lessons/*.md` + `LOG.md` → that one line only). Contradicting records:
`corpus/lessons/round-74.md:18` ("proposals 1, 2 and 3 already landed as lane-round work"),
`corpus/lessons/round-76.md:145-146` ("the other three … are landed"), and
`corpus/lessons/round-81.md:98-101` (P1 "is taken up by C2 rather than deferred"; P4 "stays pending").
**F4 — The one implementation of proposal 2 lapsed.** `corpus/lessons/round-75.md:87` is the
lane's own verdict on its own attempt: "**this table is the first instance**; a standing ledger
stays open". Measured: lessons 76–86 carry 0 rows citing any `considerthese/` file.

**F5 — The criterion exists but has no machine.** `corpus/QUALITY.md:477` (KQ97) binds the daily
reflection to record a disposition, yet the lane's own daily files violate it (F1, row 2) and no
counter reads the ledger. A criterion no tool can check is the "counter that a shortcut can
satisfy" shape this lane keeps mining (`corpus/lessons/round-86.md:110-115`).


**F6 — Draft criterion line** for `corpus/QUALITY.md`, next free number KQ141 (full text in
`out/SC02ConsiderTheseMine/mine.md` §3): one standing, committed disposition ledger for the
numbered proposals of every `considerthese/` file the lane has opened, reconciled by a lane
counter before each round's claims freeze — a proposal recorded twice with different values, or
recorded "taken up" while its artifact is absent at the audited revision, is a finding and exits
nonzero; a lesson may not record a disposition without reading the ledger row. Cites
`considerthese/2026-10-26.md`, `corpus/QUALITY.md:477`, `corpus/lessons/round-75.md:87`,
`corpus/lessons/round-86.md:115-116`, `corpus/lessons/round-81.md:98-101`, `round-74.md:18`.

**F7 — Why not the others.** P1 is implemented and stronger than asked (every deletion, not ≥20).
P3's fix is wiring an existing tool, and P3 was already mined to KQ139 at
`corpus/lessons/round-86.md:110-115`. P4 needs an unattended network read and is deferred to "the
next freshness round" (`corpus/lessons/round-81.md:102`); round 87 is not a freshness round.

## Remaining unknowns

- Ledger medium (`registry/` TSV vs `corpus/` markdown vs a `tools/` artifact) is the L1's
  integration call; the drafted criterion is written to be indifferent.
- `tools/shortcut-tally.py`'s docstring advertises a `--wide` family argparse does not accept
  (exit 2); whether that is a defect or a rename is not resolvable from the lane's files.
- Whether `corpus/lessons/round-86.md:115-116` used a different sense of "unimplemented" is not
  stated anywhere in the lane.

## Deliverables

`.ufo/waves/round-87/w1/out/SC02ConsiderTheseMine/mine.md` (proposal table, chosen proposal,
grounding evidence, draft KQ141 line), `…/receipt-shortcut-tally.txt`, `…/evidence-ABCD.txt`, and
`.ufo/waves/round-87/w1/SC02ConsiderTheseMine.md` (this report). Checks run: only the greps and
the three lane tools named above. Tooling installed or upgraded: none.

VERDICT: choose proposal 2 — the lane's proposal-disposition record contradicts itself
(`round-86.md:115-116` vs `round-74.md:18` / `round-81.md:98-101`) and the lesson table that
stood in for a standing ledger lapsed after round 75 (`round-75.md:87`); draft KQ141.
