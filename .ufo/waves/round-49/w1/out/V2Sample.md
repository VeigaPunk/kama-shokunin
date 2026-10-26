# V2Sample — Round 49 seat report: hand-check of C2 (append-only-audit v4) ungraded lines

**Verdict: PASS — all 30 hand-checked ungraded lines (all 17 of event `dd9f5dc6` + 13 of the 65 of event `0718b6ab`, sampled by a stated rule) are genuine re-derived head text under the lane's rule at `SCORECARD.md:6`; every sampled line was born in an exempt `## ` section (v4 origin), and each is either held byte-exact at tip (some under §Historical head sections) or superseded by a regenerated equivalent. No finding in the sampled set; the lane's v4 ungraded counts (17 / 65) hold.**

---

## 1. Assignment and scope

Seat V2Sample (round 49, lane kama, calibration axis): hand-check the lane's ungraded lines under v4 at the frozen build commit
`74558c71c38ceaeace15fd4cf8aa9d84977584b1` for the two SCORECARD.md events:

| Event commit | deleted | graded | ungraded | status |
|---|---|---|---|---|
| `dd9f5dc6c0e63d038bdd070094d7f38290eeee1b` (round-42 claim work) | 31 | 14 | **17** | restored |
| `0718b6abbda6afa6b0ce586f46739fbb92c7cf9c` (round-45 measured results) | 2421 | 2356 | **65** | restored |

Sample: **all 17** of `dd9f5dc6` + **13 of 65** of `0718b6ab`. Stated rule for the 13: the 65 ungraded lines sorted by parent line number, take indices 0, 5, 10, …, 60 (every 5th) → positions {8, 14, 19, 24, 29, 34, 39, 44, 49, 54, 115, 120, 132}, spanning all five head sections.

## 2. Contract and rule under test

- Contract row (`registry/append-only-contract.tsv:3`): `SCORECARD.md` region `exempt=## Axes|## Planned|## Retired|## Saturation|## Capabilities@SCORECARD.md:6`; note: "dated round sections append-only; the five head sections SCORECARD.md:6 names are re-derived in place since round 42 and are ungraded while they are not gutted".
- Lane rule (`SCORECARD.md:6`): the `## Axes` table, §Planned, §Retired, §Saturation, §Capabilities "are re-derived from the tree by `tools/round42-selfdesc-reconcile.py` … the round-5 banner and the head sections they replace are kept verbatim under §Historical head sections, and from round 48 every authority banner this line replaces is appended byte-exact".
- v4 definitions (`tools/append-only-audit.py:6-13`, `tools/round49-append-audit-v4-check.py:15-33`): `origin(l)` = set of `## ` titles holding text at the first commit (rev-list `--topo-order --reverse`) whose blob holds l; `ungraded` ⇔ parent section ∈ eligible exempt title AND `origin(l)` ∩ exempt titles ≠ ∅; quality the tool at tip runs `tools/round42-selfdesc-reconcile.py` checks (banner/planned/retired/saturation/caps/receipts/readme/province/rel) on the same head sections.

## 3. Method and evidence

All runs against a scratch clone of the lane (`git clone --shared`), read-only on the lane itself. No tools installed (stdlib only; tooling-authorization rule not triggered).

1. Tool at tip (frozen v4 build): `python3 tools/append-only-audit.py --repo $S/lane --to 74558c71c38ceaeace15fd4cf8aa9d84977584b1 --json`
   - exit **0**; summary `commits=319 events=5 ungraded_lines=82 restored=5 regressed=0 bad_declarations=0`; events as in §1. (`tool-audit-at-74558c71.json`)
2. C2 counter at tip (the frozen checker, run by me): `python3 tools/round49-append-audit-v4-check.py --repo $S/lane --tip 74558c71… --scratch $S`
   - exit **0**; `fixture=1 lane=1 scenarios=8/8 met=True`; detail lines: `event dd9f5dc6c0e6 SCORECARD.md ungraded 17 <= natively exempt 23` and `event 0718b6abbda6 SCORECARD.md ungraded 65 <= natively exempt 65`. (`c2-counter-run.txt`)
3. Per-line reproduction: verbatim copy of `audit()` (`tools/append-only-audit.py:397-507`) instrumented to record each deleted line's (parent position, text, parent section, origin titles, verdict) → reproduced the tool's numbers exactly (17/31 and 65/2421; all other files graded 0 ungraded). (`instrumented-per-line-verdicts.json`)
4. For each ungraded line: origin titles + first commit (rev-list order) from the same blob walk, byte-exact membership at tip and per-section location, and the restore commit `82b5e9d3` membership. (`ungraded-lines-82.json`)

## 4. Hand-check: event `dd9f5dc6` (all 17)

Parent `0bfd47ab` (round-42 freeze). Eligible titles computed by the tool: `## Axes`, `## Capabilities`, `## Planned`, `## Saturation` (`## Retired` ineligible: its line count never again reached the parent's, so its 6 deleted body lines are correctly **graded** — they appear in graded=14 with the 9 head-banner lines, whose parent section is None).

| # | pos | Parent section | Origin titles (first commit) | At tip? | Verdict |
|---|---|---|---|---|---|
| 1 | 17 | ## Axes | ## Axes (24aa1d34, round-41 claim work) | no — superseded | genuine: regenerate-able lead-in; successor line holds the sentence and updates facts |
| 2 | 21 | ## Axes | ## Axes (24aa1d34, round 41) | no — replaced | genuine: regenerable axis row (round-42 values) |
| 3 | 22 | ## Axes | ## Axes (24aa1d34, round 41) | no — replaced | genuine: regenerable axis row |
| 4 | 23 | ## Axes | ## Axes (24aa1d34, round 41) | no — replaced | genuine: regenerable axis row |
| 5 | 24 | ## Axes | ## Axes (24aa1d34, round 41) | no — replaced | genuine: regenerable axis row |
| 6 | 25 | ## Axes | ## Axes (24aa1d34, round 41) | no — replaced | genuine: regenerable axis row |
| 7 | 26 | ## Axes | ## Axes (4fe239a4, round-41 integrate) | no — replaced | genuine: regenerable axis row (adjacency) |
| 8 | 60 | ## Planned | ## Planned (e246c40e, round 5) | **yes** — §Historical head sections | genuine: archived verbatim under `### Planned (round-5 text)` |
| 9 | 61 | ## Planned | ## Planned (e246c40e, round 5) | **yes** — §Historical | genuine: archived verbatim |
| 10 | 62 | ## Planned | ## Planned (e246c40e, round 5) | **yes** — §Historical | genuine: archived verbatim |
| 11 | 63 | ## Planned | ## Planned (e246c40e, round 5) | **yes** — §Historical | genuine: archived verbatim |
| 12 | 64 | ## Planned | ## Planned (e246c40e, round 5) | **yes** — §Historical | genuine: archived verbatim |
| 13 | 65 | ## Planned | mixed incl. None (c6199a25, round 1) | yes (blank) | trivial: blank line, no content |
| 14 | 66 | ## Planned | ## Planned (e246c40e, round 5) | **yes** — §Historical | genuine: archived verbatim |
| 15 | 67 | ## Planned | ## Planned (e246c40e, round 5) | **yes** — §Historical | genuine: archived verbatim |
| 16 | 68 | ## Planned | ## Planned (e246c40e, round 5) | **yes** — §Historical | genuine: archived verbatim |
| 17 | 143 | ## Saturation | ## Saturation (96bbd742, protocol conformance) | **yes** — `## Saturation` | genuine: section heading; relocated/regrown in the re-derived head |

Blob round-42 diff confirms the archival: `### Banner (round-5 text)`, `### Planned (round-5 text)`, `### Retired (round-3 text)`, `### Capabilities (round-10 head table)` under `## Historical head sections (superseded in round 42)` hold the deleted bytes verbatim (spot-checked: planned-body line "After operator-owned route/binding repair…" sits at round-5 commit `e246c40e` under `## Planned`, and byte-exact at tip under §Historical).

## 5. Hand-check: event `0718b6ab` (13 of 65)

Parent `21945c61` (round 45). This event gutted the whole file (2429 → 17 lines) and the very next commit `82b5e9d3` restored it (holds 74 of the 82 ungraded texts byte-exact; the rest return in regenerated form). Eligible: all five titles. All 65 ungraded lines have parent section ∈ exempt titles AND origin ∩ exempt ≠ ∅ (v4 condition); 57 of 65 exist byte-exact at tip under the same/§Historical section; the 8 absent at tip (`pos 14,16,17,18,53,57,117,135`) are regenerable values whose successors are present at tip (e.g. old operability row → current row with re-anchored hash and `45/45` selftest count; `None. 6 axes and 9 capabilities…` → `6 axes and 11 capabilities…`; `Saturation line **8/10** …` → same opening with current derived sentence; `### Planned (round 46)` → `round 49`).

Sampled 13 (indices 0,5,…,60 of the 65 by parent position):

| # | pos | Parent section | Origin titles (first commit) | At tip? | Verdict |
|---|---|---|---|---|---|
| 1 | 8 | ## Axes | ## Axes (c6199a25, round 1) | yes — `## Axes` | genuine: heading of re-derived head |
| 2 | 14 | ## Axes | ## Axes (dd9f5dc6, round 42) | no — superseded | genuine: regenerable operability row (successor holds current values) |
| 3 | 19 | ## Axes | ## Axes (2793eb51, round-42 fixes) | yes — `## Axes` | genuine: regenerable row, held |
| 4 | 24 | ## Axes | ## Axes (c6199a25, round 1) | yes — `## Axes` | genuine: table separator, structural |
| 5 | 29 | ## Axes | ## Axes (83bee7fa, round 2) | yes — `## Axes` | genuine: historical-axes-table row, held verbatim |
| 6 | 34 | ## Axes | ## Axes (83bee7fa, round 2) | yes — `## Axes` | genuine: "Why operability stops at 8…" paragraph, held |
| 7 | 39 | ## Axes | ## Axes (ea72c3ea, round 3) | yes — `## Axes` | genuine: Round-3 verdicts paragraph, held |
| 8 | 44 | ## Axes | ## Axes (ea72c3ea, round 3) | yes — `## Axes` | genuine: verdicts paragraph, held |
| 9 | 49 | ## Axes | ## Axes (ea72c3ea, round 3) | yes — `## Axes` | genuine: "Carried debt" paragraph, held |
| 10 | 54 | ## Planned | mixed incl. None (c6199a25, round 1) | yes (blank) | trivial: blank line |
| 11 | 115 | ## Capabilities | ## Capabilities (96bbd742) | yes — `## Capabilities` | genuine: section heading |
| 12 | 120 | ## Capabilities | ## Axes (c6199a25, round 1) | yes — `## Capabilities` | genuine: table separator; born as the Axes-table separator (exempt-title birth per v4) |
| 13 | 132 | ## Capabilities | mixed incl. None (c6199a25, round 1) | yes (blank) | trivial: blank line |

## 6. Conclusion

- All 30 sampled lines are genuine re-derived head text per `SCORECARD.md:6`: they belong to one of the five declared re-derived head sections, their v4 origin contains an exempt title (none was laundered from a dated section into an exempt one), and each is either preserved byte-exact (held at tip, incl. §Historical archival) or is regenerable content superseded by the corresponding current value.
- The tool's v4 counts (17 and 65) match the C2 counter's bound (`ungraded <= natively exempt`: 17 ≤ 23, 65 ≤ 65) and the instrumented per-line reproduction.
- **No finding** in the sampled set. No defect observed in the frozen counter/tool/controls (out of scope; nothing to fix in place).
- Residual risk: the un-sampled 52 lines of `0718b6ab` were verified programmatically only (v4 condition, at-tip/§Historical membership, structural classification), not row-by-row hand-read; the 8 regenerated-missing lines' successors were checked by prefix/structure, not full-text diff.

## 7. Files written

- Report: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V2Sample.md`
- Deliverables: `/home/vgpnk/Projects/shokunin/kama-shokunin/.ufo/waves/round-49/w1/out/V2Sample/`
  - `tool-audit-at-74558c71.json` (tool JSON at tip, exit 0)
  - `c2-counter-run.txt` (C2 run, `fixture=1 lane=1 scenarios=8/8 met=True`, exit 0)
  - `instrumented-per-line-verdicts.json` (per-line verdicts for all events)
  - `ungraded-lines-82.json` (the 82 ungraded lines: parent pos, text, parent section, origin titles, first commit, tip presence)
