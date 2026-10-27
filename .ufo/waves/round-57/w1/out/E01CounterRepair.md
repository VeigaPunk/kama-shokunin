# E01CounterRepair — round-42 counter stale-count repair (isolated)

Seat: E01CounterRepair, executor, kama round 57 w1. Lane: `/home/vgpnk/Projects/shokunin/kama-shokunin`.
Axes: calibration + operability are the lane's assigned axes (`shokunin.conf`/SCORECARD);
the historical `MISSION.md` conflict is not resolved here. This seat measured the assigned
counter claim only. Scope: private scratch clone; no lane source edits, no commits, no
installs, pacman untouched. Scratch: `/fast/scratch/hyaku/kama-r57/E01CounterRepair`
(removed after receipts were copied). Frozen base: `b89bdab2cc114735ec5d331c6c610134258f7864`.
Live lane HEAD moved during the wave (`89dc4f52` -> `7c873d7b` -> `7b74e2f2` -> `77e7f5ee`
at capture, then `8a7f1976` after this seat's receipts); those commits are the lane's, not
this seat's, and are cited only as context.

## Verdict

1. **No repair to the counter's `maxN` derivation is justified.** At the frozen base the
   derivation is correct: `maxN=56`. The claimed `expected 46` is not derivable from the
   committed tree; it is the literal hardcoded by the do-nothing control
   (`.ufo/waves/round-57/controls/c1-noop.py` prints `mismatches=0 maxN=46 met=True` with
   zero reads). Forcing 46 in a scratch tool copy fails its own banner and planned legs.
2. **The stale datum is the calibration self-description count**, not a capability row
   count: the base mismatch is `r41 calibration run ... no stdout line == '42'` while the
   committed `corpus/lessons/*verifier-spotcheck.md` blob count is 43. At the base the
   `caps`, `retired` and `saturation` legs are all 0.
3. **Smallest isolated repair = one token in SCORECARD.md**: the calibration row's
   `→ \`42\`` becomes `→ \`43\``. Demonstrated in a scratch clone: frozen base
   `mismatches=1 maxN=56 met=False` exit 1 -> repaired `mismatches=0 maxN=56 met=True`
   exit 0, with canonical heading selection and the summary report shape unchanged.
4. The lane integrated an equivalent count repair concurrently at `7b74e2f2` (1 file,
   1 insertion, 1 deletion). At live HEAD the counter reads `mismatches=0 maxN=57 met=True`
   exit 0 (the `## Round 57` section now exists). This seat does not claim that commit.

## Exact evidence (receipts copied to this report's directory)

Fixture fx1: fresh clone, checkout frozen base, identity set locally inside the clone; every
fixture commit confined to `/fast/scratch/.../fx1` after asserting `git rev-parse
--show-toplevel` equals the fixture.

| Step | Receipt | Exact result |
|---|---|---|
| Frozen base, unmodified | `receipts/fx1/base-b89bdab2-repro.out` | `r41=1 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=1 maxN=56 met=False`; detail: calibration run `no stdout line == '42' (exit 0)`; exit 1 |
| One-token repair `42`->`43` | `receipts/fx1/repair-diff.txt` | `1 file changed, 1 insertion(+), 1 deletion(-)`; word-diff is exactly `-`42`` / `+`43`` |
| Same counter after repair | `receipts/fx1/repaired-42to43.out` | `r41=0 ... caps=0 ... mismatches=0 maxN=56 met=True`; exit 0 |
| Selection preserved | `receipts/fx1/canon-selection.out` | `canon_round=49 canon_rows=11`; head names equal; `canonical_firsts=[10,14,16,20,25,30,41,42,43,46,47]`; `max_round_heading=56`; `authority_rounds_max=56` |
| Report output preserved | `receipts/fx1/report-shape.out` | identical field list/order for base and repaired (`r41 ... rel mismatches maxN met`); only values change |
| Wrong count also fails | `receipts/fx2/counter-wrong-count-44.out` | 43->44 fixture: `mismatches=1 met=False`, detail `no stdout line == '44'`, exit 1 (the pass is bound to the true count, not to any edit) |
| Lane HEAD (context) | `receipts/fx2/lane-head.out`, `receipts/fx2/lane-facts.out` | HEAD `77e7f5ee`: `mismatches=0 maxN=57 met=True` exit 0; calibration row now `→ \`43\``; spotcheck blobs 43 |

`maxN` derivation census at the frozen base (`receipts/fx2/derivations.out`):
`max(^## Round N headings)=56`, `max(**Current authority (round N)**)=56`,
`highest canonical-list heading=49`, `canonical firsts max=47`; 46 occurs only in the stale
round-46 canonical table and in the no-op literal. Forcing it (`drivers/round42-selfdesc-reconcile.maxn46.py`,
receipt `receipts/fx2/forced46-tool-on-repaired.out`) gives `banner=1 planned=1 mismatches=2
maxN=46 met=False`, exit 1 — i.e. the claim's expected value is falsified by the claim's own
counter legs.

## No-op discrimination

`receipts/fx2/noop-c1-executed.out`: the control prints `mismatches=0 maxN=46 met=True`,
exit 0, and its source performs no reads. By contrast, the real counter's r41 leg executes
the run fact from SCORECARD in a `git archive` export: the base r41-only run is
`run_bad=1 mismatches=1` exit 1 (`receipts/fx2/r41-base.out`) and flips to `run_bad=0
mismatches=0` exit 0 only after the count token changes (`receipts/fx2/r41-repaired.out`).
A canonical-row rename in the round-49 table also fails the counter (`caps=1`, exit 1,
`receipts/fx2/counter-canonical-row-renamed.out`), and an appended `## Round 57` heading
moves `maxN` to 57 and fails banner/planned (`receipts/fx2/counter-round57-heading.out`).

## Advisory (recorded, not changed)

`canon()` keeps the first table at an equal-numbered canonical marker (`N > best`), so a
duplicate equal-N marker lets a stale table win — reproduced at
`receipts/fx2/canon-duplicate-marker-probe.out` (`(57, [['stale-first','x','1']])`). No
duplicate marker round exists in the live SCORECARD (`duplicate marker rounds: []`), so it
is latent. This seat preserved heading selection as instructed; structural binding of
canonical rows is E02's scope.

## Risks / limits

- The wave's frozen documents disagree on axis labels and expected values
  (`controls/freeze-amendment.txt` says stale count 42 vs actual 43; the seat context says
  `maxN=56` vs `expected 46`). Both were measured; neither is silently reconciled. Only the
  r41 count leg fails at the frozen base, so the 46 target is unsupported (calibration).
- The lane tree changed under the wave (HEAD `89dc4f52` -> `77e7f5ee` at capture, then
  `8a7f1976`), including the equivalent count repair and the round-57 section; fixtures pin
  the frozen base so the before/after is reproducible there.
- `maxN=56` is the correct frozen-base derivation; after round-57 integration it is 57.
  Any integration receipt must state its tip.

Report: .ufo/waves/round-57/w1/out/E01CounterRepair.md
