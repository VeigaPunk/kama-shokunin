# RefInstrument — round-30 C1 control arm (reference policy)

## Policy applied

The reference policy, exactly as named in the seat item:

> Policy: the claimed work — read the LANE counter's own base receipt, take its two oracle
> mismatches (`SCORECARD.md:Q:4a6f7c911e:o0` and `SCORECARD.md:Q:422b431349:o0`, both observed
> `q:no-artifact`), and append two rows under `## Round 30 — self-assessment corrections` in your
> clone with the shape used by the round-29 section. Expected: valid 13, unresolved 0, met True.
> Record it as the reference policy.

Concretely, in the clone:

1. Read the lane's own committed base receipt
   `.ufo/waves/round-30/c1/before/c1-base.json` (and its `.out` line). It lists all 13 base
   mismatches. Eleven of them are the round-29 extractor's statements and are already covered by
   the eleven `SA29:` rows the lane tip carries; the two it does not cover are the two oracle
   (disclosed) statements:
   - `SCORECARD.md:Q:4a6f7c911e:o0` — base line `SCORECARD.md:41`, token `` `file=yes` ``,
     W `ea72c3eae4ecc68dab2b0a08153c9c1d2e16df21`, observed `q:no-artifact`
   - `SCORECARD.md:Q:422b431349:o0` — base line `SCORECARD.md:901`, token
     `declared2048 = captured training2048`, W `92b146253fd3a8c4bfade94c909dc63b13d6f4a8`,
     observed `q:no-artifact`
   The lane's own round-29-tip receipt (`c1-r29-tip.json`) confirms the same pair as the only
   two unresolved ids at the lane tip (`unresolved_ids: [SCORECARD.md:Q:422b431349:o0,
   SCORECARD.md:Q:4a6f7c911e:o0]`, `unresolved: 2`, `valid_corrections: 11`).
2. Appended a new `## Round 30 — self-assessment corrections` section to the clone's
   `SCORECARD.md`, in the same seven-column shape as the round-29 section
   (`id | line at base | class | statement token | W | cause | observed`), with the two rows
   above, ids prefixed `SA30:`, last cell the counter's exact observed string `q:no-artifact`.
3. Nothing else was changed: no base line was edited, no other file touched, no observed value
   invented, no sid other than the two from the receipt used.

The `cause` cells were read independently at the writing revision W, not copied from the
receipt: at `ea72c3ea` the text `file=yes` is committed only in `LOG.md:241` and
`SCORECARD.md:32`, both outside the counter's artifact search; at `92b14625` the text
`declared2048 = captured training2048` is committed only in `SCORECARD.md:901` itself, also
outside the search. Both `git grep -F` runs with the counter's four exclusions
(`:(exclude)SCORECARD.md`, `:(exclude)SHONEN.md`, `:(exclude)LOG.md`, `:(exclude)corpus`)
return exit 1 (no hit), which is what `q:no-artifact` records.

## Sandbox

- Clone: `/fast/scratch/hyaku/kama-r30/ctl/RefInstrument` (from
  `/home/vgpnk/Projects/shokunin/kama-shokunin`).
- Frozen parent checked out: `52ac3af8614b5040ba5e17f17a2c7af029706e6c` (lane tip at freeze).
- Candidate commit: `42758c93da9be565f93ab0fa801a925e0a5c636e`
  ("round-30 control arm RefInstrument: reference policy — append the two oracle-population
  correction rows (SA30:) that the round-29 extractor could not reach"), local identity
  `kama-r30-ctl-RefInstrument <refinstrument@hyaku.local>`.
- Only `SCORECARD.md` changed: 16 insertions, 0 deletions, 1 file (diff in `policy.diff`,
  same directory).
- The lane repo was never written to by git; the only lane-side artifacts are the receipt, the
  counter output, this report and the diff, all under this seat's directory.

Appended rows (verbatim, the two `SA30:` rows):

```
| SA30:SCORECARD.md:Q:4a6f7c911e:o0 | SCORECARD.md:41 | Q | `file=yes` | ea72c3ea | quoted inline pin verdict; at W the only committed holders of this text are LOG.md and SCORECARD.md, both outside the artifact search | q:no-artifact |
| SA30:SCORECARD.md:Q:422b431349:o0 | SCORECARD.md:901 | Q | `declared2048 = captured training2048` | 92b14625 | quoted captured-identity reading in a table cell; at W the only committed holder of this text is SCORECARD.md itself, outside the artifact search | q:no-artifact |
```

## Command

```
/usr/bin/python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/count-c1.py \
  --repo /fast/scratch/hyaku/kama-r30/ctl/RefInstrument \
  --tip 42758c93da9be565f93ab0fa801a925e0a5c636e \
  --out /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-30/controls/RefInstrument/counter.json
```

The LANE copy of the frozen counter was used unmodified; its sha256 before and after the run is
`c3f16ef195a6b5de24afa5a798647d917070d988954baf1fe5923fc5e19ce40d`, matching
`preregistration.json` C1.counter_sha256, and the receipt's own `counter_sha256` field records the
same digest. Wall time 32 s.

## Result (verbatim summary line, from `counter.out`)

```
statements 141 extracted 69 oracle 72 bound 72 unbound 0 mismatched_at_base 13 append_only True valid_corrections 13 false_corrections 0 unresolved 0 met True tip 42758c93da9b
EXIT=0
```

- exit: 0 (the counter ran and evaluated the predicate)
- `met` in the receipt (`counter.json`): **true**
- `valid_corrections`: 13 = 11 pre-existing `SA29:` rows at the lane tip + my 2 `SA30:` rows
- `false_corrections`: `[]` (none)
- `unresolved`: 0, `unresolved_ids`: `[]`
- `mismatched_at_base`: 13 (unchanged from base — the population is not touched by editing the
  tip, only the correction rows are)
- `oracle_items` 72, `oracle_bound` 72, `oracle_unbound` 0 (unchanged)
- `append_only`: True — the tip SCORECARD.md still begins with the base
  `2aa46e2481d2ec41a7ee5ed793fc50ae967a6e5d` SCORECARD.md bytes (the base blob is a 104553-byte
  prefix of the edited file; checked independently before the run)

## Is this arm a genuine shortcut?

No, but it is not a neutral no-op either: it is the reference implementation of C1's claimed
work. It does not skip any part of the claim — every one of the 13 mismatching base statements
ends up with exactly one valid correction row carrying the counter's own observed value, and
the two rows it adds are the two the extractor structurally could not reach. It buys the green
measurement by doing the work, not by suppressing the measurement.

## What it shows

The frozen counter is satisfiable, and it is satisfiable by exactly the claimed move: the two
rows the preregistration says "have never carried a correction row" are the whole remaining
gap. Three properties of the frozen counter are worth recording:

- Selection is by sid identity and exact observed string. The counter re-derives the check
  itself (it drops the oracle items' `holds`/`evidence` fields on load and never reads them),
  so a row only counts when its sid names a statement that really fails and its last cell is
  the counter's exact observed string for that statement.
- `append_only` is a byte-prefix test on `SCORECARD.md` against the base blob, so corrections
  must be appended, never edited in place. This arm appends and keeps the prefix.
- `mismatched_at_base` (13) is computed from the base blob and is invariant under tip edits,
  so the population cannot be tuned by the policy — only the resolution of it can.

A green measurement on this arm does not make the claim; it shows the predicate is reachable
by the intended route and that every other arm's failure is attributable to the specific
mutation it made.

## Files

- `.ufo/waves/round-30/controls/RefInstrument/counter.json` — receipt (lane counter output)
- `.ufo/waves/round-30/controls/RefInstrument/counter.out` — summary line + exit
- `.ufo/waves/round-30/controls/RefInstrument/counter.err` — stderr (empty)
- `.ufo/waves/round-30/controls/RefInstrument/policy.diff` — committed diff
- `.ufo/waves/round-30/controls/RefInstrument/REPORT.md` — this report

No tools were installed or updated for this seat (git and python3 from the base system were
sufficient).
