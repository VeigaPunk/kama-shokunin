# X08C2ReplayBase — C2 frozen counter at base 8f7f58cd vs current fleet HEAD

Round 59, kama. Seat: leaf executor/replay. Frozen source:
`.ufo/waves/round-59/controls/freeze.txt` (base `8f7f58cd161f2b7dfa1709450c3ae79599c12833`,
fleet-manifest-rev `c071f0de`, control commit `5d957d24`; all three objects resolve in the lane/fleet repos).

Axis attacked: **calibration 7→7**, C2 clause set only. No source edits, no commits, no sibling/fleet writes.

## Claim/clause attacked

C2 predicate clauses exercised (8 in the counter's `mismatches` dict):

1. `row_missing` — calibration row present in `## Axes`
2. `typed_count` — no literal spotcheck total ("N` (outside closures on record")
3. `pinned_fleet_revision` — no pinned 40-hex in the row
4. `pointer_missing` — `latest outside closure \`corpus/lessons/round-<N>-verifier-spotcheck.md\` (<verdict>)` present
5. `pointer_round` — pointer round == highest-numbered lane spotcheck
6. `pointer_verdict` — pointer token == fleet MANIFEST kama closure verdict for that lane_round
7. `including_round` — `including round <N>` agrees
8. `count_command` — row names `tools/round59-c2-counter.py` with `--fleet-ref`

`--repo` = `/home/vgpnk/Projects/shokunin/kama-shokunin`; `--fleet-repo` defaults to
`/home/vgpnk/Projects/shokunin`; scratch `TMPDIR=/fast/scratch/hyaku/kama-r59/X08C2ReplayBase/tmp`
(created, exported, removed before yield).

## Exact commands and results

Executed tool blob (verified identical across worktree, measured tip, lane HEAD):

```
git -C $LANE hash-object tools/round59-c2-counter.py                      -> 3b80c25845236348a17260883ab60a6093f2ec6c
git -C $LANE rev-parse 2c7443ab...:tools/round59-c2-counter.py            -> 3b80c25845236348a17260883ab60a6093f2ec6c
git -C $LANE rev-parse HEAD:tools/round59-c2-counter.py                   -> 3b80c25845236348a17260883ab60a6093f2ec6c
git -C $LANE rev-parse 8f7f58cd...:tools/round59-c2-counter.py            -> fatal: path ... not in '8f7f58cd...'
git -C $LANE rev-parse HEAD                                               -> 4a541190b6d494a4e99116249632e99aab80adcc
git -C /home/vgpnk/Projects/shokunin rev-parse HEAD                       -> 0f99f606120d0c884656c6e7a290f0e8f33c2181
```

| Run | command | exit | stdout |
|---|---|---|---|
| A measured tip, fleet HEAD | `python3 tools/round59-c2-counter.py --repo $LANE --tip 2c7443ab --fleet-ref HEAD` | **0** | `tip=2c7443abb8d6edb8a5b0f91dfee9f81b824f6d35 fleet=0f99f606120d0c884656c6e7a290f0e8f33c2181 maxN=57 manifest=rejected-honest-stop` / `rows=44 mismatches=0 met=True` / all 8 clauses `=0` |
| B **base 8f7f58cd**, fleet HEAD | `... --tip 8f7f58cd161f2b7dfa1709450c3ae79599c12833 --fleet-ref HEAD` | **1** | `mismatches=3 met=False`; `typed_count=1 pinned_fleet_revision=1 count_command=1`, other five `=0` |
| C measured tip, measurement-time fleet | `... --tip 2c7443ab --fleet-ref 58cffd1f42723048bcfe48eb0bc2f346caa9b77f` | 0 | `fleet=58cffd1f...` `mismatches=0 met=True` |
| D measured tip, ticket-stated fleet | `... --tip 2c7443ab --fleet-ref 3f3dd97345ef1aedfdaec818c9e58675d4f41e3f` | 0 | `fleet=3f3dd973...` `mismatches=0 met=True` |
| E base, measurement-time fleet | `... --tip 8f7f58cd... --fleet-ref 58cffd1f...` | 1 | identical to B: `mismatches=3` (`typed_count`,`pinned_fleet_revision`,`count_command`) |
| H lane HEAD, fleet HEAD | `... --tip HEAD --fleet-ref HEAD` | 0 | `tip=4a541190...` `mismatches=0 met=True` |
| F fail-closed probe (bad tip) | `... --tip deadbeef…×5` | **2** | `could-not-evaluate: unresolvable lane tip or fleet ref` |
| G fail-closed probe (bad fleet ref) | `... --fleet-ref deadbeef…×5` | **2** | `could-not-evaluate: unresolvable lane tip or fleet ref` |

### Base mismatch — confirmed, exact cause

Base SCORECARD calibration row (1355 chars, `git show 8f7f58cd…:SCORECARD.md`) contains, verbatim:

- `44` (outside closures on record, including round 57; ...)` → literal typed count
- `941acf70583a2b3a1d33460b31967e0efd291f3e` → pinned 40-hex fleet MANIFEST revision
- `tools/round58-c2-counter.py --manifest-rev…` → no `tools/round59-c2-counter.py`, no `--fleet-ref`

So base fails exactly the three de-pinning clauses; its pointer clauses pass
(`('57','rejected-honest-stop')`, `including round 57`). Base is a real mismatch, not an
incidental parse failure: 3/8 clauses, exit 1.

Measured-tip row (`2c7443ab…`, 1054 chars) has zero 40-hex, zero typed count, and names
`python3 tools/round59-c2-counter.py --repo <repo> --tip <rev> --fleet-ref HEAD`; pointer
`corpus/lessons/round-57-verifier-spotcheck.md` `(rejected-honest-stop)`, `including round 57`.
8/8 clauses, exit 0. Δ row length 1355→1054 chars is consistent with removal of the pinned
revision + hard-coded count + rc58 counter reference.

### Independent corroboration of the counter's derived fields

```
git -C $LANE show $TIP:corpus/lessons/round-57-verifier-spotcheck.md | head -3
  -> "# Round 57 non-author closure spot-check" / "author: hyaku closure (non-author integrator, @m_opus)"
git -C $LANE ls-tree --name-only $TIP corpus/lessons/ | grep -cE 'round-[0-9]+-verifier-spotcheck\.md$'   -> 44
  (rounds 10-19 and 24-57; highest = 57; no r58/r59 spotcheck file)
git -C /home/vgpnk/Projects/shokunin show HEAD:MANIFEST.json (jq on rounds)
  -> kama closures 50,51,52,53,54,55,56,57; r57 verdict=rejected-honest-stop; no r58 row
```

All 44 matching files carry `author: hyaku closure (non-author integrator, …)`, so the
filename-derived `rows=44` equals the non-author population at this tip.
`maxN=57` identical at base and tip (base tree already contains the r57 spotcheck), so runs B/E
differ from A/C/D only in the three row-content clauses, not in derivation inputs.

## Operability / calibration observations (advisory)

- Counter binds full 40-hex lane tip and resolved fleet revision on stdout; config freezes are
  honoured (no target/counter/fixture edits by this seat).
- Pass is fleet-revision-robust across three distinct fleet commits (58cffd1f, 3f3dd973,
  0f99f606) because the r57 verdict token is unchanged — expected, but it means this counter does
  not currently discriminate fleet-ledger drift for the r57 entry; it only reads the entry.
- Executed counter blob is byte-identical at measured tip and current lane HEAD, and
  `git diff 2c7443ab..HEAD -- SCORECARD.md tools/round59-c2-counter.py corpus/lessons/` is empty:
  no post-measurement drift in the evaluated inputs, so A and H are the same measurement.
- The non-author population is identified by filename regex only; corpus content today satisfies
  it (44/44 `author: hyaku closure (non-author …)`), but an author-produced file named
  `round-N-verifier-spotcheck.md` would be counted. Recorded as calibration nuance, not a kill.
- Latest outside closure resolves to r57 because no r58/r59 external spotcheck exists — matches
  the ticket's "no kama r58 closure row"; no discernment progress is claimed (S517/S518 unrecorded).
- Fail-closed verified for unresolvable tip and unresolvable fleet ref (exit 2, no partial pass).

## Retained evidence

- `/fast/scratch/hyaku/kama-r59/X08C2ReplayBase/{c2-measured-head,c2-base-head,c2-measured-58cffd1f,c2-measured-3f3dd973,c2-base-58cffd1f,c2-lanehead}.txt`, `sc-base.md`, `sc-tip.md` — **removed before yield** per scratch hygiene; all values reproduced verbatim above.
- Tool blob `3b80c25845236348a17260883ab60a6093f2ec6c`; lane HEAD `4a541190`; fleet HEAD `0f99f606`.

## Verdict (falsification, not judgment)

C2 at the frozen base **does not meet** (3/8 clauses, exit 1) and at the measured tip **does
meet** (8/8, exit 0), binding tip `2c7443ab…` and fleet `0f99f606…`. Base mismatch confirmed
and clause counts exact. No install/update performed (no tool needed). No blockers.
