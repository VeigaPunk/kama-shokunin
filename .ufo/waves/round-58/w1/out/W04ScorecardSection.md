# W04ScorecardSection — Round 58 finding

Axes: calibration (r42/C2 self-description), operability (the section must not disturb the counters).

## Result
Drafted `## Round 58` in the exact `## Round 57` shape — heading, freeze/controls/base prose, 4-column claims table
(C1 operability 8→8, C2 calibration 7→7) with measured cells marked `PENDING`, the held-scores/limits sentence, and
`### Planned (round 59)` with numbered items — and tested it in a scratch clone.

The section alone is not enough: adding `## Round 58` raises r42's `maxN` 57→58, so the draft also carries the two
head edits that forces — line 6 rewritten for round 58 (`Latest measured round: 58`, `operability + calibration`,
derivations promise kept) and the `## Planned` pointer moved 58→59. Those two are the C2 dependency, not cosmetics.

Placements (3 hunks, `draft-round58.patch`, 50 lines):
1. line 6 — new authority banner; the old banner is preserved verbatim in the appended fenced block.
2. line 53 — `The live plan is \`### Planned (round 59)\` at the end of this file`.
3. EOF — `## Historical authority text — round 57` (old banner, `cmp` byte-identical to `e4891d8a:SCORECARD.md:6`) then the `## Round 58 …` section (`draft-round58-section.md`, byte-extracted from the tested commit).

## Measurements
Scratch clone `/fast/scratch/hyaku/kama-r58/W04ScorecardSection/lane` (toplevel verified, `--shared` clone of the lane),
base `e4891d8a`, draft commit `3e2526153f24033e60ec5ca381d35b5e395103f2`; receipts in this directory.
- `python3 tools/round42-selfdesc-reconcile.py --repo . --tip <rev>`: base `r41=0 banner=0 planned=0 retired=0
  saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=57 met=True` exit 0; draft identical with
  `maxN=58` and `mismatches=0 met=True` exit 0 (`r42-base.out`, `r42-draft.out`).
- `python3 tools/round58-c2-counter.py --repo . --tip <rev> --manifest-rev 941acf70583a2b3a1d33460b31967e0efd291f3e`:
  base `claim=N=57 token=rejected-honest-stop` / `r42=0 missing=0 stale=0 verdict=0 including=0 mismatches=0 met=True`
  exit 0 (`c2-base-buildtip.out`); draft same with the draft tip, met=True exit 0 (`c2-draft.out`).
- `python3 tools/append-only-audit.py --repo . --to <rev> --json`: exit 1 both tips on pre-existing
  `bad_declarations=4 unrestored=8`; draft delta `regressed=0 → 0`, `unrestored=8 → 8`. The draft commit's SCORECARD
  event is `deleted=2 graded=1 ungraded=1 held_at_to=1 status=restored` — the replaced banner is held verbatim.
- `python3 tools/round54-cited-path-check.py --repo . --tip <rev> --fleet /home/vgpnk/Projects/shokunin`: base
  `cited=715 unresolved=14 disclosed=14 undisclosed=0 bad=1 stale=0 dropped=0 met=False` exit 1; draft `cited=717
  unresolved=14 disclosed=14 undisclosed=0 bad=1 stale=0 dropped=0 met=False` exit 1 (`cited54-*.out`) — same
  pre-existing `bad=1` (`corpus/lessons/round-52-verifier-spotcheck.md` superseded → `round-53-…` not cited in
  SCORECARD), and `dropped=0`, so the draft adds only resolving citations.
- `python3 tools/planned-pointer-check.py <SCORECARD>`: exit 1 at both tips on one pre-existing dangling
  `§Round-53 measured results`; the pointer line itself prints `ok (The live plan is \`### Planned (round 59)\` …)`.
- Patch applicability: second `--shared` fixture at `e4891d8a` + `git apply --check draft-round58.patch` → exit 0.
- `python3 tools/shortcut-tally.py --repo . --rev <rev>`: exit 0, identical detail at both tips (population 40-47).

## Findings
1. The live lane working tree (uncommitted, mirrored 2026-10-27T20:00Z) already carries hunks 1–2 plus the historical
   block but no `## Round 58` section. Mirrored into a scratch commit (`7bd0771`, `r42-live-mirror-interim.out`) it scores `banner=1 planned=1
   mismatches=2 met=False maxN=57` (head lacks 'Latest measured round: 57'; `## Planned` does not name `### Planned
   (round 58)`). Appending the drafted section to that same mirror scores `mismatches=0 maxN=58 met=True` exit 0
   (`r42-live-mirror-draft.out`). The missing piece is exactly `draft-round58-section.md`; all three hunks must land in
   one commit.
2. r42's `banner` and `planned` facts are keyed to `maxN`; landing the section without the line-6 banner and the
   pointer scores `banner=1 planned=1` and C2 fails. The draft holds both at 0 with `maxN=58`.
3. Frozen C2's "r42 stays 1 until the L1 lands the round-58 SCORECARD section" is not what the tree shows at the
   build tip: r42 is already `mismatches=0 maxN=57` at `e4891d8a`. The `r42=1` belongs to `bfaea953` (receipt
   `.ufo/waves/round-58/measured/c2-build.out`). C2 can therefore be met before the section exists; the section must
   not break it. Attack target: C2's before/after narrative, not its predicate.
4. `PENDING` cells deliberately avoid backticked receipt paths: `.ufo/waves/round-58/measured/` is uncommitted at
   `e4891d8a`, and the cited-path counter scores unresolved SCORECARD citations. Fill `PENDING` and cite the receipts
   in the same commit that writes them.
5. Pre-existing and untouched by the draft: cited-path `bad=1`, planned-pointer round-53 dangling reference,
   append-only `bad_declarations=4` / `unrestored=8`.

Out of scope: C1's own measurement (not this seat) and the round-44/45 ledger audits; the C1 counter was not run. Scratch roots removed after copying receipts. No lane file touched, no tool installed.
