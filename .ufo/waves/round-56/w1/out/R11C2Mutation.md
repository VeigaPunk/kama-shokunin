# R11C2Mutation — round-56 falsification seat report

Seat item: "In a private fixture clone, change a roster designation and verify the prereg checker returns met=False."
Axes: operability, calibration. This attack targets **C2 (calibration)**. Leaf member; no subagents dispatched.
Milestone: round-56 falsification. Verdict below is advisory, not a judgment.

## Result

**No defect. The C2 kill-rule condition "a one-field designation mutation remains green" is unreachable.** Every roster-designation mutation path tested returns `met=False` exit 1, via two independent mechanisms: blob-equality break (`roster_match=0`) and the kills/controls arithmetic (`kills=0`/`controls=3` with `roster_match=1`).

## Integrity of the fixture

- Scratch `/fast/scratch/hyaku/kama-r56/R11C2Mutation/` created; `TMPDIR` exported explicitly in every command; `/tmp` never used. Scratch removed before yield.
- One shared clone of the lane: `git clone --no-hardlinks /home/vgpnk/Projects/shokunin/kama-shokunin <scratch>/lane-clone`. The lane tree was never written, no git/jj state touched in the lane.
- Two fixture clones `fixtureA`, `fixtureB` (`git clone --shared` from the private clone). Before every git mutation in a fixture, `git rev-parse --show-toplevel` was asserted to equal that fixture dir; no guard fired.
- Frozen checker bytes extracted from the freeze tip: `git show efc6b3ec6fb6ea308c15855e9b8b62856f4255b7:tools/round56-prereg-check.py` → sha256 `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`, **matches the frozen digest exactly**. All checker runs below used those extracted bytes (`receipts/checker-freeze.py`, copied to the output dir).
- No tooling installs were needed (preexisting python3 + git).

## Baselines (frozen-tip controls reproduced in fixture)

- `python3 checker-freeze.py --repo fixtureA --tip e10b6d39af450e8d652be9ac2986768b531fe13f`
  → `tip=e10b6d39… present=0 roster_match=0 kills=0 controls=0 met=False`, exit **1** (receipt `r56-c2-base.out`). Matches the C2 base control.
- `python3 checker-freeze.py --repo fixtureA --tip efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`
  → `present=1 roster_match=1 kills=1 controls=2 met=True`, exit **0** (receipt `r56-c2-freeze.out`). Matches the C2 freeze control.

## Mutation matrix (one-field designation change `m-drop-ldaudit`: `"kill"` → `"control"`)

| # | commit | battery ROSTER | prereg battery.roster | roster_match | kills | controls | met | exit | receipt |
|---|--------|----------------|----------------------|--------------|-------|----------|-----|------|---------|
| A | `31480baaed0f9885552757ea22f111d3f7b4e238` (fixtureA) | flipped | clean | 0 | 1 | 2 | False | 1 | `r56-c2-mut-a.out` |
| B | `b4a36ade05ac72188af1f9fbf7f44ea41d6cc765` (fixtureB) | flipped | flipped | 1 | 0 | 3 | False | 1 | `r56-c2-mut-b.out` |
| C | `994c50f348cd3768cb733782d1725f16744362ec` (fixtureA) | flipped | flipped (prereg flip stacked on mut-a) | 1 | 0 | 3 | False | 1 | `r56-c2-mut-c.out` |
| D | `a01e9fda10b712802a0602070493e575a906fb65` (fixtureB) | clean | flipped | 0 | 0 | 3 | False | 1 | `r56-c2-mut-d.out` |

- Mutant A proves a battery-side designation edit alone breaks blob equality.
- Mutant B is the strongest probe: the identical edit applied to **both** blobs keeps `roster_match=1`, yet `met=False` because the checker independently requires `kills==1 and controls==2`. The kill rule is not a thin equality wrapper.
- Mutant D is the pure prereg-side mirror of A; also red.
- Mutant C is reported for honesty: it was intended as the prereg-only mirror but landed on mut-a's parent, so it duplicates B's semantics through a different commit path; D supersedes it as the true prereg-only probe.
- Causality check: at fixtureB's clean parent `efc6b3ec` the checker returns `present=1 roster_match=1 kills=1 controls=2 met=True` exit 0 (receipt `r56-c2-mut-b-parent.out`) — the red results are attributable to the designation mutation alone, not fixture drift.
- Diffs of every mutant commit are in `mutant-diffs.txt` (each is exactly the one designation field).

## Mechanism note

In `tools/round56-prereg-check.py`, `kills`/`controls` are counted from the **preregistered** roster (`obj["battery"]["roster"]`), while the AST-parsed battery `ROSTER` participates only in the equality check. Consequence: a designation edit on either side alone lands red via `roster_match=0`, and a coordinated edit on both sides lands red via `kills=0`/`controls=3`. [INFERENCE, not run: a coordinated flip to an unrecognized designation value (neither kill nor control/control-label) would also be red via `kills=0`; the arithmetic path is already demonstrated by mutants B/C.]

## Defects

None found within this seat's scope (C2 one-field designation mutation). Not exercised, out of scope: exit-2 `could-not-evaluate` paths, C1/env-leg behavior, mutant quality of `m-drop-ldaudit` itself.

## Tooling

No installs or upgrades performed; preexisting `git` and `python3` were sufficient.

Report: .ufo/waves/round-56/w1/out/R11C2Mutation.md
