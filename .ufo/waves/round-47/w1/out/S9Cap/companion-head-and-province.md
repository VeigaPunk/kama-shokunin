# Companion edits the canonical-list change forces

None of these is cosmetic: `tools/round42-selfdesc-reconcile.py` reads the canonical list for its
`retired`, `saturation`, `caps` and `province` legs, and `tools/round41-scorecard-reconcile.py`
(imported by it) checks the `## Axes` hash anchors. Measured in this seat (scratch clone at
`46a924e0`, synthetic commits, see `../S9Cap/receipt.md`):

| omission | reconcile output | exit |
|---|---|---|
| none (all four edits applied) | `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1` | 1 |
| PROVINCE.md row left alone | `province=3 … mismatches=4` (`lacks registry/append-only-contract.tsv`, `… round47-append-audit-v2-check.py`, `… kama-live-replay.py`) | 1 |
| PROVINCE.md edited but the coverage hash not re-anchored | `r41=2 … mismatches=2`, detail: `coverage sha256 PROVINCE.md cited 659a5101… observed 929f3e3e…` | 1 |
| canonical block added, head mirror / §Retired / §Saturation left alone | `retired=1 saturation=1 caps=1 … mismatches=4` (`does not state '11 capabilities'`, `does not state 'first-working rounds … 47'`, `head names [… 10 names …]`) | 1 |

`r41=1` in every case is the **stale calibration row, not an unrelated red**. Verified at both
`3a09a1d9` and `46a924e0`:

```
git ls-tree --name-only 3a09a1d9 corpus/lessons/ | grep -c 'verifier-spotcheck\.md$'   -> 33
git ls-tree --name-only 46a924e0 corpus/lessons/ | grep -c 'verifier-spotcheck\.md$'   -> 33
```

`SCORECARD.md:18` claims `→ 32`; the tree holds 33 blobs (round-46 closure added
`corpus/lessons/round-46-verifier-spotcheck.md`). Round 47 must repair it (`32` → `33`) for r41 to
be green. **Owned by the §Round 47/head re-anchor deliverable, not by this canon list** — same for
the two moves that only become necessary once a `## Round 47` heading exists:

- `SCORECARD.md:6`: `Current authority (round 46)` → 47 and `Latest measured round: 46.` → 47
  (banner leg);
- `SCORECARD.md:53`: the live-plan pointer `### Planned (round 47)` → `### Planned (round 48)`, and
  a `### Planned (round 48)` heading with a numbered item must exist (planned leg: `maxN+1`).
- `SCORECARD.md:16` `depth` row — **not forced by the canon list**, but forced by the round-47
  SKILL registry rows: it anchors `SKILL.md` sha256 / line count / `grep -c '^## '` run fact.
  Committed tip `46a924e0` matches the row (`1ad95066…`, 1442 lines, 34); the round-47 SKILL.md in
  the working tree is `ddb80f6e…`, 1463 lines, 35 headings, so all three fields move when it lands
  (otherwise `round41-scorecard-reconcile` reads `hash_bad=1 lines_bad=1 run_bad=1`). Re-derive from
  the applied blob at integration.

`S9Scorecard`'s head re-anchor set covers all of these (its `head-reanchors.diff`, including the
depth row) and its merged measurement at commit
`1d910297` reads `r41=0 … province=0 rel=0 mismatches=0 maxN=47 met=True` (exit 0). This seat's
demo tree has no `## Round 47` heading, so `maxN` stays 46 there and `planned`/`banner` read 0 —
that difference is the missing section, not a disagreement.

## 1. SCORECARD.md:57 (`## Retired`)

- now: `None. 6 axes and 10 capabilities remain active.`
- proposed: `None. 6 axes and 11 capabilities remain active.`

## 2. SCORECARD.md:136 (`## Saturation`)

- now: `capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46 (highest canonical list)`
- proposed: `capability first-working rounds 10, 14, 16, 20, 25, 30, 41, 42, 43, 46, 47 (highest canonical list)`
- now: `A capability entered in round 46, so the window is not exhausted either.`
- proposed: `A capability entered in round 47, so the window is not exhausted either.`

## 3. PROVINCE.md:17 (owns table, "lane instruments" row)

Canon evidence cells now cite `registry/append-only-contract.tsv`, `tools/round47-append-audit-v2-check.py`
and `tools/kama-live-replay.py`; the `province` leg requires every `tools/` and `registry/` token of a
canon row to appear in PROVINCE.md.

- replaced:
  `tools/append-only-audit.py` with `tools/round46-append-audit-check.py` (append-only audit of the five append-only self-description files: every commit deleting >= 20 lines from one of them, how many of those lines the file holds again at the audited revision and the commit that restored them; round 46)
- with:
  `tools/append-only-audit.py` with `registry/append-only-contract.tsv` and `tools/round47-append-audit-v2-check.py` (append-only audit of the contract-declared self-description set: every commit deleting >= 20 lines from one of those files, with a deleted count equal to git numstat, the largest share of those lines any commit in the event's window holds again and the commit that restored them; round 46, v2 round 47); `tools/kama-live-replay.py` (re-acquire a live receipt's server archive and model from the URLs its provenance records, verify both sha256 values, re-run the lifecycle and compare every check; round 47)

## 4. SCORECARD.md:17 (`## Axes`, coverage row) - forced by edit 3

The coverage row cites `surface list PROVINCE.md sha256 659a5101ce0a8bc08d2c63a23d52049cd97e183d92f226568607ebf11bc9fc49 (186 lines)`.

- proposed: same row with `sha256 929f3e3eef20fa90429ca0c5a96a63821cff6aeca912ac55bad3a82b4bd3a079`
- the file's line count is unchanged (186): the edit rewrites one table cell inside PROVINCE.md:17.
- the lane's own precedent is round 43 ("re-anchors the `SKILL.md` and `PROVINCE.md` hashes after the round-43 edits").
- both seats computed `929f3e3e…` independently from the edited blob (`S9Scorecard` confirms the same value).

## Placement and de-duplication (settled with S9Scorecard)

`S9Scorecard` carries the 11-row block **inside** `## Round 47` immediately after the claim/controls
prose (round-46 shape), not before the heading as this seat's `canonical-round-47.md` first
proposed. Both placements measure `caps=0` because canonical selection takes the first capability
table after the highest marker, so the choice is cosmetic; the block must be applied **once**. If
the L1 applies `proposed.patch` and then the section draft, the marker and table land twice — apply
the section draft and take only the head/PROVINCE hunks from `proposed.patch`, or apply one and
verify `capability_tables` is 13, not 14.

## Unchanged on purpose

- `**Capabilities — canonical list as of round 46**` and its table stay byte-intact; the round-47
  block supersedes it by number, not by replacement.
- `.ufo/waves/round-47/c2/live/receipt-1.json` is cited as a second evidence pointer for
  `live-receipt-replay`; see the report's limit note on the audit's `unsubstantiated` rule (a row is
  substantiated when *any* one of its path tokens resolves).
