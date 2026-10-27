# R10C2Counter — prereg-check BASE red / frozen-tip green predicate review (incl. missing-file behavior)

Round 56, C2 calibration counter `tools/round56-prereg-check.py`. Seat scope: the gate's
base-red and freeze-green predicates and its missing-file taxonomy. Lane untouched; all
mutations were fixture commits inside one scratch clone
(`/fast/scratch/hyaku/kama-r56/R10C2Counter/clone`, toplevel-guard asserted before first
mutation; scratch removed after evidence copy).

## Axes

- **Operability** — does the gate run and emit the frozen outputs/exit codes at both tips.
- **Calibration** — does the predicate bind exactly (names/designations/expected), does it
  stay red on absence and on one-field designation mutation, is green reachable only via
  exact equality plus 1 kill / 2 controls.

## Verdict: C2 predicates hold; no material defect. Two low-severity robustness findings, one informational, two cosmetic.

## Evidence (all measured this seat; receipts in `receipts/`)

Frozen-byte checks:

- Working-tree counter sha256 `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`
  == frozen C2 digest == `git show efc6b3ec…:tools/round56-prereg-check.py` blob digest.
- Preregistration bytes identical in worktree and freeze blob (`fa4b5a100a9fd6ce…`).
- Base `e10b6d39…` contains none of: preregistration.json, round56-env-leg-battery.py,
  round56-prereg-check.py (`git cat-file -e` all absent). Freeze is one commit
  (`efc6b3ec round-56: freeze LD_AUDIT env leg and prereg roster controls`).
- Battery ROSTER at freeze equals the preregistered roster entry-for-entry
  (base-old-counter control/missed, round56-counter positive-control/detected,
  m-drop-ldaudit kill/missed). Committed receipt `controls/base-c2.out` matches claim.

Gate runs (checker executed from the sha-verified worktree copy against both repos):

| tip | stdout | exit |
|---|---|---|
| lane base `e10b6d39…` | `present=0 roster_match=0 kills=0 controls=0 met=False` | 1 |
| lane freeze `efc6b3ec…` | `present=1 roster_match=1 kills=1 controls=2 met=True` | 0 |
| clone freeze (tree `eda1d40fb9f4` == lane tree) | same green | 0 |
| t1 designation swap (battery `kill`→`control`, prereg frozen) | `present=1 roster_match=0 kills=1 controls=2 met=False` | 1 |
| t2 battery deleted, prereg frozen | `present=0 … met=False` | 1 |
| t3 prereg deleted, battery frozen | `present=0 … met=False` | 1 |
| t4 prereg roster values are strings | empty stdout, `AttributeError: 'str' object has no attribute 'get'` | 1 |
| t5 prereg is JSON array | empty stdout, `AttributeError: 'list' object has no attribute 'get'` | 1 |
| t6 battery appends `ROSTER = UNBOUND_NAME` after main guard | `present=1 roster_match=1 kills=1 controls=2 met=True` | 0 |

Predicate logic cross-check (source read of `tools/round56-prereg-check.py` at the frozen
digest): `met = (battery ROSTER == prereg roster) and kills == 1 and controls == 2`;
absent files short-circuit to `present=0 met=False` exit 1; unparseable prereg JSON or
battery source exits 2 `could-not-evaluate`; kills/controls count prereg-side
designations (`control` and `positive-control` both count as controls).

C2 kill rule exercised: base is red, freeze tip is green, counter digest matches, and the
one-field designation mutation is red (t1: `roster_match=0`). All four falsification
attempts failed → C2 stands.

## Findings by severity

**LOW-1 — crash paths exit 1 with empty stdout, colliding with the red-control exit
code.** t4/t5: a parseable prereg whose root is not an object, or whose roster values are
not dicts, dies on uncaught `AttributeError` in the `kills`/`controls` comprehensions
(roster values `.get`) or `obj.get` (root shape). Python exits 1 — the same code the
legitimate red control uses — with no `present=` line on stdout. Exit-code-only automation
reads "do-nothing control red, as expected" where the gate actually never evaluated.
Evidence: `receipts/t4-malformed-values.out`, `receipts/t5-root-array.out`. Not reachable
from the frozen bytes (prereg is frozen and well-formed); C2's frozen predicates are
unaffected. Proposed fix: shape-check `obj` and roster values in the existing
`could-not-evaluate` path and return 2.

**LOW-2 — an unparsable duplicate `ROSTER` binding leaves the gate green (t6, exit 0).**
The assignment scan keeps the last ROSTER `ast.Assign` whose `literal_eval` succeeds; a
failed parse leaves the earlier value in place, so `ROSTER = UNBOUND_NAME` appended after
the `__main__` guard is invisible to the gate while the battery still executes unchanged.
Similarly, a conditional rebinding (`if X: ROSTER = …`) is a nested `Assign` the top-level
body scan never visits. Bounded in practice: the gate requires exact dict equality with
the frozen prereg, so any *parseable* divergent duplicate turns red, and the frozen
battery carries exactly one top-level ROSTER. Adversarial constructions only; no action
required for round 56. If hardened later: reject batteries containing more than one
top-level `ROSTER` assignment (parsed or not).

**INFO-1 — `kills`/`controls` in the output are prereg-side counts.** t1 prints
`kills=1 controls=2` even though the battery-side mutant has 0 kills / 3 controls; the
battery contributes only through `roster_match`. `met` still requires `roster_match=1`,
so green is correct, but readers should not interpret `kills=`/`controls=` as
battery-verified counts.

**COSMETIC-1 — `BASE` constant is dead code** (`tools/round56-prereg-check.py`, module
top); the base tip is supplied via `--tip`.

**COSMETIC-2 — `--out` is written with `open(a.out, "w")` without creating the parent
directory**; a missing parent crashes after stdout was already emitted. All current
callers pass existing directories.

## Missing-file behavior (explicit seat scope), consolidated

- both files absent → red `present=0 met=False` exit 1 (measured, lane base);
- battery only absent → red exit 1 (measured, t2);
- prereg only absent → red exit 1 (measured, t3);
- prereg present but invalid JSON → exit 2 `could-not-evaluate` (code path: `json.loads`
  ValueError caught);
- battery present but unparseable source → exit 2 `could-not-evaluate` (code path:
  `ast.parse` SyntaxError caught, decode uses `errors="replace"`);
- prereg parseable but wrong shape → uncaught AttributeError exit 1 (LOW-1).

## Residual risk

- LOW-1/LOW-2 are latent robustness gaps, unreachable from the frozen prereg/battery
  bytes; they cannot flip C2's frozen red/green claims.
- The gate reads committed blobs via `git -C repo show` with GIT_* env scrubbed
  (`GIT_CONFIG_GLOBAL=os.devnull`, `GIT_CONFIG_NOSYSTEM=1`) — no repo-config injection
  surface found; `rev-parse --verify tip^{commit}` rejects invalid tips with exit 2
  (code path, not separately executed).
- C2 grades roster fidelity only, per the prereg `limits` field; battery execution
  quality is C1's scope and was not exercised by this seat.

## Verification gaps

- `could-not-evaluate` exit-2 paths (invalid tip, invalid JSON) verified by source read,
  not executed; only the AttributeError paths (t4/t5) were executed crash evidence.
- No jj operations were run or needed; git `show`/`cat-file`/`log`/`diff` reads only
  against the lane; `git add/commit` used exclusively inside the scratch clone.

## Tooling

No installs; stock `python3` and `git` sufficed.

## Artifacts

- Report: .ufo/waves/round-56/w1/out/R10C2Counter.md
- Receipts: .ufo/waves/round-56/w1/out/R10C2Counter/receipts/{lane-base,lane-freeze,clone-freeze,t1-designation-swap,t2-missing-battery,t3-missing-prereg,t4-malformed-values,t5-root-array,t6-duplicate-roster}.out
- Fixture driver (reproducible): .ufo/waves/round-56/w1/out/R10C2Counter/fixture_driver.py
