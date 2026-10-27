# X11 — round-42 self-description counter at the round-58 tip

Attacks C2-r58's r42 half and the SCORECARD head edit needed when `## Round 58` lands. Revisions read with `git
cat-file`: base 2f53614e, freeze dcd69473, tip e4891d8a; scratch clone `$S/clone`, fixture `$S/fixture` (throwaway
identity); no lane file written.

## 1. No live mismatch at the frozen tip
`python3 tools/round42-selfdesc-reconcile.py --repo $S/clone --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a` ->
`r41=0 banner=0 planned=0 retired=0 saturation=0 caps=0 receipts=0 readme=0 province=0 rel=0 mismatches=0 maxN=57 met=True` [exit 0]
`python3 tools/round58-c2-counter.py --repo $S/clone --tip e4891d8a --manifest-rev 941acf70...` ->
`claim=N=57 token=rejected-honest-stop maxN=57 manifest=rejected-honest-stop` /
`r42=0 missing=0 stale=0 verdict=0 including=0 mismatches=0 met=True` [exit 0]
At base and freeze: `r41=1 ... mismatches=1 met=False` [exit 1], `detail: r41 calibration run ... no stdout line ==
'43'`; the round-58 row re-anchor (row says `44`, `including round 57`) is what carries r42 to 0.

## 2. Remaining mismatch is latent — three facts keyed to maxN
Fixture `ab62db4c` = tip tree + one `## Round 58 — ...` section:
`r41=0 banner=1 planned=2 ... mismatches=3 maxN=58 met=False` [exit 1]
`detail: banner: head lacks 'Latest measured round: 58'` / `detail: planned: section does not name '### Planned
(round 59)'` / `detail: planned: no line '### Planned (round 59)' followed by a numbered item`
The freeze's "r42 stays 1" under-counts: `planned` grades per fact (pointer sentence, heading line). No other family
moves on a new round section.

## 3. Minimal head edit reaching 0 (scratch commit `6f4f946b`)
`SCORECARD.md | 7 +++++-- 2 deletions`: (1) line 6 `Latest measured round: 57` -> `58`; (2) line 53, the `## Planned`
pointer, `### Planned (round 58)` -> `(round 59)`; (3) append the exact line `### Planned (round 59)` plus numbered
items (5 added lines). Nothing else — not the `| calibration |` row.
`... round42-selfdesc-reconcile.py --repo $S/fixture --tip 6f4f946b` -> `mismatches=0 maxN=58 met=True` [exit 0]
`... round58-c2-counter.py --repo $S/fixture --tip 6f4f946b --manifest-rev 941acf70...` -> `r42=0 missing=0 stale=0
verdict=0 including=0 mismatches=0 met=True` [exit 0]

## 4. Limits (measured)
- L1 token, not authority round: with edit (1) alone line 6 still reads `**Current authority (round 57):**` and the
  counter scores `banner=0`; `grep -rn "Current authority" tools/` finds no checker.
- L2 `planned` accepts any exactly-matching heading line plus a numbered item: renaming the executed `### Planned
  (round 58)` (`b829b07b`, plan text still about round-56 leftovers) gives `mismatches=0 maxN=58 met=True`.
- L3 maxN is fence-blind: `## Round 59` quoted inside a ```text fence (`e7b368d9`) gives `maxN=59 banner=1
  planned=2`; the tip holds no such quote (maxN=57 genuine).
- L4 append-only: both rewritten lines are graded deletions. Squashed fixture (`append-only-audit.py --to
  6f4f946b --files SCORECARD.md`) -> `deleted=2 graded=2 status=unrestored` [exit 1] — over-graded, since a
  one-commit fixture erases line origins and exempt sections cannot shield. Real history at the tip is already red
  (`events=53 restored=12 unrestored=27 regressed=3` [exit 1]), so the edit adds one event rather than breaking a
  green gate. `restored` needs the prior line-6 bytes held verbatim (846 bytes, sha256
  `e83aabb498823ecf0b3a146e200149e5a662ef6d8b378363b10730b71275436f`) as rounds 55/56 did; `--selftest` ->
  `AOA_SELFTEST pass=51 fail=0` exercises that mechanism.

## 5. Ordering trap that can falsify C2 after the section lands
Fixture `ffba0024` = section + head edit + `corpus/lessons/round-58-verifier-spotcheck.md`:
`r42: r41=1 ... no stdout line == '44'` [exit 1] | `c2: claim=N=57 maxN=58 r42=1 stale=1 including=1 mismatches=3
met=False` [exit 1] — `-> 44`, `including round 57` and pointer N=57 are anchored to N=57, so the round-58 lesson
(and any re-anchor, which needs a MANIFEST verdict for N=58) must land after the frozen C2 measurement, or together
with a row re-anchor.

## Files, receipts, risk
Lane files changed: none. Receipts in `.ufo/waves/round-58/w1/out/X11SelfdescCounter/`: `tip-r42.out`, `tip-c2.out`,
`base-r42.out`, `freeze-r42.out`, `a1-section-landed.out`, `b1-head-edit.out`+`.diff`, `b1-c2.out`,
`c1-rename-variant.out`, `e1-{r42,c2}-with-lesson.out`, `f1-fenced-heading.out`, `tip-audit-scorecard.out`,
`audit-selftest.out`, `fixture-commits.out`. Tooling installed: none. Risk: the head edit is a preamble rewrite, so
its append-only event should be restored or disclosed in the landing commit. Blocker: none.
