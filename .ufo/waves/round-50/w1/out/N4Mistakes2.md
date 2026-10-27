Verdict: **7 routed items (or sub-items) of the round-45..49 closures have still never become a lesson Mistakes row or a QUALITY criterion**; the dominant defect is a mechanism regression — the `routed`/`carried` block installed by round-48's own fix for this exact problem is absent from the round-49 and round-50 preregistrations, and two carried items (`prerelease`, `b11906` population) fell out of the frozen record this round.

Full ledger, both-side anchors and all seven proposed rows: `.ufo/waves/round-50/w1/out/N4Mistakes2/sweep.md`. Verification receipts: `.ufo/waves/round-50/w1/out/N4Mistakes2/t5-checks-rerun.out`.

## The defect (headline)

`corpus/lessons/round-48.md:31` (Mistakes row 4) fixed "routed items dropped without capture" with a `routed` block in the preregistration naming each closure id one by one. Present at `round-46/47/48/preregistration.json` (r45-D1..D3 / r46-D1..D6+r45-D3 / r47-D1..D9). Absent since:

- `.ufo/waves/round-49/preregistration.json` — keys are `lane, round, attempt, author, frozen_at_utc, base, authority, separability, claims, controls, limits`; routed items survive only as prose inside `authority` (line 8 names "routed R1 and R5") and the claim statements.
- `.ufo/waves/round-50/preregistration.json` — same key set, no `routed`; `authority` (line 8) names only "routed R1, R2 and R3"; `limits` (line 44) names `sub-20` but not `prerelease` or `b11906`, the two other items `round-49-verifier-spotcheck.md:107` carries.

Verified (my own run of seat T5Mistakes' committed check, which independently reaches the same finding):

```
S=/fast/scratch/hyaku/kama-r50/N4Mistakes2
git clone --shared /home/vgpnk/Projects/shokunin/kama-shokunin "$S/lane"
python3 /home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/T5Mistakes/checks.py --repo "$S/lane"
→ exit 1
  check B routed-block: FAIL — round-49: no routed/carried block, round-48 closure routed 3 lane item(s); round-50: no routed/carried block, round-49 closure routed 5 lane item(s)
  check D carried-limits: FAIL — round-50 limits do not name 'prerelease' or 'b11906' (round-49 closure R5)
  check C sweep-consumed: FAIL — round-49 N5Mistakes/sweep.md cited by no committed corpus/ or registry/ file
```

Proposed fix: land `checks.py`'s B and D legs as a committed `tools/routed-block-check.py` run at every freeze (it already fails correctly: exit 1 on r49/r50, would pass on r48). Proposed Mistakes row class: `carrier-loss` — a fix without a persistent carrier is dead on arrival; this is the second instance of the same class (r45-D1's carrier died at r47; the fix's own carrier died at r49).

## The six remaining uncaptured items (summary; proposed rows in sweep.md)

| # | Item | Routed at | Never-captured evidence | Class proposed |
|---|---|---|---|---|
| B | sub-20-line deletions unwatched; `ed135b3c` LOG.md loss (7 del, restored_max 2) still partial | `round-48-verifier-spotcheck.md:119`; carried `round-49-verifier-spotcheck.md:107`; disclosed `round-50/preregistration.json:44` | event gate `tools/append-only-audit.py:91,520` (threshold 20); grep `sub-20|threshold` over `round-4[5-9].md`+`QUALITY.md` → no row/KQ | `graded-below-threshold` — commit a `--threshold 1` census receipt per round; fails today (66 graded partial/unrestored events at `w1/out/L1Lowthr/audit-threshold1.json`) |
| C | r45-D1 deferred→dropped (claim-outcome reader re-freeze) | `round-45-verifier-spotcheck.md:146` | deferred `round-46.md:12`; absent every routing since; `round-48.md:31` names it only as a dropped example; `grep r45-D1` → 0 | `dropped-deferred` — a `deferred` disposition without re-arm expires; KQ65 (`QUALITY.md:380`) lacks the known-data constraint |
| D | r46-D3 named sub-gaps: reworded witnesses auto-pickable; V1Code F1–F4 | `round-46-verifier-spotcheck.md:139` ("write it as a lesson row … or drop it with a reason") | family rowed `round-47.md:45`; named items in no lesson/QUALITY (`grep V1Code|auto-pick` → only `round-46.md:91` roster) | `sub-item drop` — next freshness claim's limits must name them or drop with reason |
| E | r47-D2 multi-receipt replay closed in code, not in rule | `round-47-verifier-spotcheck.md:98` | `replayed=3/3` exists (r48-spotcheck:49); KQ69/KQ75 (`QUALITY.md:396,411`) never require set coverage; no row | `closed-without-capture` — KQ amend: replay claims cover all N receipts; fails on r47's 1/3 |
| F | r48-R5 record-time fetch (K2Record): settled disclosed limit, wave-output only | `round-48-verifier-spotcheck.md:116` | no Mistakes row, no KQ scope clause; grep `record.time.*fetch` → 0 | `accepted-limit unrowed` — a `disclosed-limit` row or one KQ74 scope sentence |
| G | per-mutant dispositions (r47 13/44; r48 21/52+15/55+6/27; r49 11/20+10/23+16/49+8/29) | `round-47-verifier-spotcheck.md:101`; `round-48-verifier-spotcheck.md:117`; `round-49-verifier-spotcheck.md:106` | counts disclosed in SCORECARD; per-mutant disposition exists only in seat wave output | `per-mutant undispositioned` — `registry/mutant-dispositions.tsv`, not a kill threshold (KQ20's round-20 no-universal-policy caveat honored); low priority |

## Staleness correction to the round-49 sweep (N5Mistakes F9)

`w1/out/N5Mistakes/sweep.md` claimed `tools/sources-append-only.py` "exits 2 on every revision since round 45 … parser fix pending". Resolved: the pre-repair tool at `c4b2175d^` exits 2 on the r45 failing pair while the tip tool exits 0 (`added S496/S497/S498 (allowed)`; selftest 45/45). Committed receipts: `w1/out/T5Mistakes/sources-guard{,-pre-repair}.out`. Its F10/F11a/F11d are likewise captured now (round-49 row 4; KQ76; KQ77/KQ78). Correcting the standing record is cheap and prevents a third seat from re-reporting it.

## Disagreements

None uncaptured: every closure step-3 discernment table ends `agree` on all sampled admits/rejects (r45:124-130, r46:117-121, r47:75-81, r48:88-93, r49:81-86). The one closure-to-closure disagreement (r48-R4 correcting r47's "quoted map matches" conformance row, `round-48-verifier-spotcheck.md:113`) is operator-side — the prompt addendum is not a lane file — carried open as r49-R6 (`round-49-verifier-spotcheck.md:108`); its lane-side shadow is already `round-49.md` Mistakes row 3.

## Operator-owned inventory (for the integrator's operator route; not lane defects)

Planner-seat impossibility (`kama | round-39`), MISSION axes pair (`kama | round-35`), parked worktree (`kama | round-41..43`), r46-D6 sibling-lane truncation census (aggregator), r48-R4→r49-R6 prompt route map (includes the r47 closure doc correction), SHONEN promotion boxes. Sources: r45:150, r46:142-149, r47:106-107, r48:121-127, r49:108-115.

## Caveat on sibling evidence

T5Mistakes' check C ("a sweep must be cited by a committed corpus/registry file") cannot be satisfied by the sweep itself — a sweep cannot cite itself in the same commit it lands; keep check B+D for Row A and treat check C as advisory for the *next* round's lesson.

## Commands run

- `git clone --shared` of the lane into `$S/lane`; `python3 …/T5Mistakes/checks.py --repo "$S/lane"` → exit 1, output committed at `t5-checks-rerun.out`.
- `git show --numstat ed135b3c` → `0 12 HOURS.md`, `1 7 LOG.md` (7 deleted, under the threshold-20 event rule).
- `python3 -c json` dumps of `round-{46..50}/preregistration.json` → `routed` present 46/47/48, absent 49/50.
- greps for `r45-D1`, `prerelease`, `sub-20|threshold`, `V1Code|auto-pick`, `record.time.*fetch` across `corpus/lessons/round-4[5-9].md`, `corpus/QUALITY.md`, `.ufo/waves/round-{49,50}/preregistration.json` → outputs quoted in `sweep.md`.
- Lane, fleet repo and sibling lanes untouched; no counters executed (read-only analysis); no installs (no tool needed).

Files written:
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/N4Mistakes2.md` (this report)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/N4Mistakes2/sweep.md` (full routing ledger + proposed rows)
- `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-50/w1/out/N4Mistakes2/t5-checks-rerun.out` (verification receipt, exit 1)
