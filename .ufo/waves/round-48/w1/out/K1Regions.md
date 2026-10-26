# K1Regions — round 48 attack on v3 region semantics (escape hatch)

Verdict: **v3's region exemption is an exploitable escape hatch for dated-section loss — a naive "move/rename under an exempt heading then delete" is caught (graded, exit 1), but every laundering that sustains the exempt section's line count (same-commit filler, or regrowth later in the window) exits 0 with the deletions reported `ungraded`; the exemption is title-based and content-blind, so any dated text relocated under a head title loses its append-only protection. On the lane at 380bcdff9c8af06997c482f6eb03db926a794a2b the 89 ungraded lines are all genuine head text — none is a non-head line riding the exemption (the hole is latent, not exercised).**

## 1. What was tested

Tool: `tools/append-only-audit.py` v3 (frozen), contract shape mirroring the lane's SCORECARD row
(`exempt=## Axes|## Plan@NOTES.md:3`, declaring `NOTES.md:2` binds). Every fixture: `git init` in
`mktemp -d -p $S`, toplevel asserted, throwaway identity, commit history ≤ 3, then
`python3 tools/append-only-audit.py --repo <fx> --to HEAD --json` (verdicts below are its JSON
`summary`/`events` and exit code).

| # | Attack (fixture repo) | v3 verdict | exit | Laundered? |
|---|---|---|---|---|
| A | Move dated block under `## Axes`, then delete it (no filler) | deleted=25 graded=25 unrestored | 1 | **No — caught** |
| B | Rename `## Round 1` → `## Axes`, then delete the 25 lines (no filler) | deleted=25 graded=25 unrestored | 1 | **No — caught** |
| A2 | Move dated block under `## Axes`; delete it while adding 25 filler lines to the section (count 49 → 49) | deleted=25 graded=0 **ungraded=25** status=ungraded | 0 | **Yes** |
| B2 | Rename `## Round 1` → `## Axes`; delete the 25 lines while adding 25 filler lines (count 25 → 25) | deleted=25 graded=0 **ungraded=25** status=ungraded | 0 | **Yes** |
| C | Gut `## Axes` (24 → 1 lines), regrow later in window with 30 unrelated lines | deleted=24 graded=0 **ungraded=24** status=ungraded | 0 | **Yes** |
| D | Delete whole `## Axes` section including its heading (no regrow) | deleted=25 graded=25 unrestored | 1 | **No — caught** |
| D2 | Delete whole `## Axes` section including heading, regrow later with 30 unrelated lines | deleted=25 graded=0 **ungraded=25** status=ungraded | 0 | **Yes** |

Evidence (full JSON): `out/K1Regions/k1-*-audit.json` (7 fixtures).

## 2. Why each works / fails — mechanism

The exemption is computed in `tools/append-only-audit.py` `audit()` (lines 406–419) and
`sections()` (lines 231–238):

- A line's section is the **last `## ` heading text** at or before it; a dated block moved under
  `## Axes` (A) or a dated heading retitled to `## Axes` (B) changes the *label* of append-only
  dated content to a re-derived head label. Content provenance is never consulted.
- Eligibility is **count-only over the window maximum** (line 409–411): an exempt title T is
  eligible when `max over window of count(T, x) >= count(T, parent)`. So:
  - A/B fail because deleting from the enlarged/renamed section drops `count(## Axes)` below the
    parent count (49 → 24, 25 → 0) → ineligible → the dated lines are graded and exit 1.
  - A2/B2 succeed because same-commit filler keeps the count ≥ parent → eligible → the dated
    deletions are `ungraded` and exit 0.
  - C and D2 succeed because eligibility is a **window maximum**, so a later regrowth (30 lines)
    retroactively makes the earlier gutting/wholesale deletion eligible → `ungraded`, exit 0.
  - D fails because the section never comes back → max = 0 < parent count → graded.

C is enshrined in v3's own selftest (`t_exempt_gutted_then_regrown`, lines 774–782: expects
`ungraded`, exit 0). A2/B2/D2 are **not** covered by the selftest (cases in lines 838–849).

## 3. True-loss assessment against the lane's rule

Rule sources: `registry/append-only-contract.tsv` line 3 (SCORECARD row) and `SCORECARD.md:6`
(dated round sections append-only; the five head sections are re-derived in place and ungraded
while not gutted).

- **A2 / B2: true loss, forbidden.** The deleted lines are dated round content (the `## Round 1`
  block), which the rule makes append-only. Retitling or relocating them into a head section does
  not change what they are; the rule's exemption is about *re-derived heads*, not about any text
  an attacker places under a head title. v3 reports them `ungraded` → the rule is evaded.
- **C / D2: head content is lost, but the letter of the rule permits head rewrites** (re-derived
  in place). What is a defect is the test itself: it cannot distinguish regeneration from filler,
  and it hides a *complete, temporary* disappearance of a whole section (D2) if the count
  recovers before the tip. The contract's "ungraded while they are not gutted" is in effect read
  as "never permanently below the parent count in the remaining window", not "not gutted at any
  point".
- **A / B / D naive: correctly caught** — v3 grades and exits 1, so the grant is not trivially
  broken; the escape needs the count to be sustained or later regrown.

## 4. Lane check at 380bcdff9c8af06997c482f6eb03db926a794a2b

Commands:

```
python3 tools/append-only-audit.py --repo $S/lane --to 380bcdff9c8af06997c482f6eb03db926a794a2b --json
  # exit=0; summary: events=5 restored=5 ungraded=0 ungraded_lines=89 regressed=0 vanished=0 bad_declarations=0
python3 tools/round48-append-audit-v3-check.py --repo $S/lane --tip 380bcdff9c8af06997c482f6eb03db926a794a2b --scratch $S
  # selftest=1 contract=1 lane=1 fixture=1 stable=1 rows=9 files=89 lane_events=5
  # lane_failures=0 ungraded_lines=89 fixture_fail=0 met=True  (counter_exit=0)
```

The 89 ungraded lines, per event (computed with the tool's own `deleted_lines`/`sections`
definition — `out/K1Regions/analyze_ungraded.out`):

| event | file | ungraded | sections (ungraded lines) |
|---|---|---|---|
| dd9f5dc6 | SCORECARD.md | 17 | `## Axes` 7, `## Planned` 9, `## Saturation` 1 |
| 0718b6ab | SCORECARD.md | 72 | `## Axes` 42, `## Capabilities` 18, `## Planned` 4, `## Retired` 4, `## Saturation` 4 |

40 ungraded line has a non-head section: `ungraded sections NOT in head titles = {}` for both
events. The graded lines at dd9f5dc6 are 8 pre-heading banner lines (section None) and 6
`## Retired` lines, all held at tip (restored byte-exact by the build's appended r45/r46 banners).
Conclusion: the exemption on the lane does exactly what it declares — no non-head text rides it.

## 5. Findings (defects in the frozen v3 semantics)

1. **Exemption is title-based, not content/purpose-based** (`sections()` 231–238; classification
   412–419). Dated append-only content becomes exempt the moment it sits under a head title
   (A2/B2). This is the primary hole for the lane's rule.
2. **Eligibility is a window maximum of line counts only** (409–411). A section can be gutted —
   even deleted wholesale with its heading (D2) — and laundered by any later regrowth of enough
   lines; the test never looks at what the regrown lines are.
3. The pairing of 1+2 means the *smallest safe correction* is not a single line: grading must
   know provenance. Minimal candidates (proposed text in `out/K1Regions/PROPOSED-FIXES.md`, not
   applied — counter and tool are frozen):
   - replace the window-max test with a **window-min** test: `min over window of count(T,x) >=
     pcount[T]` (kills C/D2; the section must never have been gutted below its parent count);
   - add a **provenance anchor**: a deleted line whose text occurs at any window commit inside a
     non-exempt section is graded regardless of its parent position's section (kills A2/B2;
     false-positive risk only if heads deliberately quote dated lines verbatim, which the lane
     does not).

No tools were installed (stdlib only), so no install record applies. Controls/preregistration
were not touched.

## 6. Evidence written

- `out/K1Regions/lane-v3.json` — v3 JSON on the lane at 380bcdff9c8af06997c482f6eb03db926a794a2b
- `out/K1Regions/analyze_ungraded.py`, `analyze_ungraded.out` — per-event ungraded section analysis
- `out/K1Regions/k1-{move-dated-under-exempt,rename-dated-heading,gut-exempt-regrow-unrelated,delete-whole-exempt-section,move-dated-under-exempt-sustain,rename-dated-heading-sustain,delete-whole-section-then-regrow}-audit.json` — the seven fixture verdicts
- `out/K1Regions/PROPOSED-FIXES.md` — proposed correction (window-min + provenance anchor)
- `out/K1Regions/COUNTER-RUN.txt` — C1 counter run output (met=True)
