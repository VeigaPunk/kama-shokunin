# CtlJunk — round-30 C1 control arm (junk sids)

## Policy applied

Append five rows under a new `## Round 30 — self-assessment corrections` section of
SCORECARD.md, each naming a **invented** statement id (no base statement) with an
independently generated random observed value. Nothing else is touched: no base line is
edited, no real mismatch is named, no observed value is taken from any receipt.

Per the item: "Policy: append five rows with invented sids. Expected: false corrections
(not-a-mismatch); met False."

## Sandbox

- Clone: `/fast/scratch/hyaku/kama-r30/ctl/CtlJunk` (from
  `/home/vgpnk/Projects/shokunin/kama-shokunin`).
- Frozen parent checked out: `52ac3af8614b5040ba5e17f17a2c7af029706e6c` (lane tip at freeze).
- Candidate commit: `9886c09663cadf2927bdd57bf7f644ae19d2848a`
  ("round-30 C1 control arm CtlJunk: append five correction rows with invented sids
  (names no base statement)"), local identity `CtlJunk Control <ctljunk@localhost>`.
- Only `SCORECARD.md` changed: 14 insertions, 0 deletions, 1 file
  (diff in `change.diff`, same directory).
- Lane repo was never written to by git; the only lane-side artifacts are the receipt,
  the counter output, this report and the diff, all under this seat's directory.

Appended rows (all five ids name no base statement; random hex from `secrets.token_hex`):

```
SA30:SCORECARD.md:Q:cc905b3efb:0 | observed 6591328f0b55a6b62f42f7e2
SA30:SCORECARD.md:Q:2f3592ef0d:1 | observed 51a287416b1264c8f3eef813
SA30:SCORECARD.md:Q:1449dfdae5:2 | observed 493ae10871483e3b95fbb1a6
SA30:SCORECARD.md:Q:b768e44820:3 | observed 2659f21d597f8b0b26bccce0
SA30:SCORECARD.md:Q:2f8061a6a0:4 | observed 48bb0dfc613dacebf3bf8106
```

## Command

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/CtlJunk \
  --tip 9886c09663cadf2927bdd57bf7f644ae19d2848a \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/CtlJunk/counter.json
```

The LANE copy of the frozen counter was used unmodified; its sha256 before and after the
run is `c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`, matching
`preregistration.json` C1.counter_sha256, and the receipt's own `counter_sha256` field
records the same digest. Wall time 34 s.

## Result (verbatim summary line, from `counter.out`)

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 11 false_corrections 5 unresolved 7 met False tip 9886c09663ca
exit=0
```

- exit: 0 (the counter ran; the arm simply fails the predicate)
- `met` in the receipt (`counter.json`): **false**
- `false_corrections`: 5, every one with `"why": "not-a-mismatch"`
  (`SCORECARD.md:Q:cc905b3efb:0`, `:2f3592ef0d:1`, `:1449dfdae5:2`, `:b768e44820:3`,
  `:2f8061a6a0:4`)
- `correction_rows`: 16 = 11 pre-existing SA29 rows at the lane tip + my 5 SA30 rows
- `valid_corrections`: 11 (all pre-existing; none of mine)
- `unresolved`: 7 = 2 genuinely unresolved statements + 5 false corrections
  (`unresolved_ids`: `SCORECARD.md:Q:422b431349:o0`, `SCORECARD.md:Q:4a6f7c911e:o0` — the
  two oracle Q statements that never carried a correction row)
- `append_only`: True — the tip SCORECARD.md still begins with the base
  `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` SCORECARD.md bytes (checked before and after
  the append: base blob 104553 bytes is a prefix of the edited file).

## Is this arm a genuine shortcut?

No. The arm changes nothing about the evidence; it only adds rows that name nothing. It
skips C1's claimed work entirely (it does not classify any statement and does not record a
single observed value the counter can accept), and it makes the count strictly worse than
the unchanged lane tip (unresolved 2 -> 7). A green measurement on any arm would never make
the claim; here the measurement is red anyway.

## What it shows

The frozen counter rejects invented sids by sid identity, not by wording: a row whose id
names no statement in the 141-statement population is classified `not-a-mismatch` and
counted as a false correction, and each false correction is itself counted as unresolved.
So the predicate cannot be met by appending plausible-looking rows; only rows whose sid
matches a genuinely mismatching statement and whose last cell is the counter's exact
observed string for that statement count. The unchanged lane tip already sits at
unresolved 2 (the two oracle Q statements `SCORECARD.md:Q:422b431349:o0` and
`SCORECARD.md:Q:4a6f7c911e:o0`), and this arm adds five more unresolved items on top.

## Files

- `.ufo/waves/round-30/controls/CtlJunk/counter.json` — receipt (lane counter output)
- `.ufo/waves/round-30/controls/CtlJunk/counter.out` — summary line + exit
- `.ufo/waves/round-30/controls/CtlJunk/counter.err` — stderr (empty)
- `.ufo/waves/round-30/controls/CtlJunk/change.diff` — committed diff
- `.ufo/waves/round-30/controls/CtlJunk/REPORT.md` — this report

No tools were installed or updated for this seat (git and python3 from the base system
were sufficient).
