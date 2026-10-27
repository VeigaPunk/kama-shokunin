# X02ReplayC2 — C2 replay at the freeze tip

Seat scope: run `tools/round56-prereg-check.py` against the frozen freeze tip and report exact
stdout and exit code. Advisory only; no judgement, no lane mutation.

- Lane (read-only): `/home/vgpnk/Projects/shokunin/kama-shokunin`
- Freeze tip: `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` (parent `e10b6d39af450e8d652be9ac2986768b531fe13f`)
- Interpreter: Python 3.14.8
- Scratch: `/fast/scratch/hyaku/kama-r56/X02ReplayC2` (`TMPDIR` set explicitly), removed at end.

## 1. Required run — freeze tip

Command:

```
python3 tools/round56-prereg-check.py \
  --repo /home/vgpnk/Projects/shokunin/kama-shokunin \
  --tip efc6b3ec6fb6ea308c15855e9b8b62856f4255b7 \
  --out freeze-c2.out
```

Exact stdout (2 lines, trailing newline, no stderr):

```
tip=efc6b3ec6fb6ea308c15855e9b8b62856f4255b7
present=1 roster_match=1 kills=1 controls=2 met=True
```

Exit code: **0**. Matches the frozen C2 target (`present=1 roster_match=1 kills=1 controls=2 met=True`).
Re-run produced byte-identical stdout and exit 0 (deterministic; receipt `freeze-c2.run2.out` diff-empty).

## 2. Base control (corroborating, not the assigned run)

```
--tip e10b6d39af450e8d652be9ac2986768b531fe13f
```

Exact stdout:

```
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
present=0 roster_match=0 kills=0 controls=0 met=False
```

Exit code: **1**. Red baseline reproduces the preregistered target (`present=0 ... met=False`).

## 3. Kill leg — one-field designation mutation (corroborating)

Isolated clone at `/fast/scratch/.../clone-c2` (`git rev-parse --show-toplevel` asserted = the clone
before any commit). Single-field edit `"m-drop-ldaudit": designation "kill" -> "positive-control"`,
committed as `6566afebe5b232dfcd3973db7612006dc81b7bdd` (1 file, 1 insertion, 1 deletion):

```
tip=6566afebe5b232dfcd3973db7612006dc81b7bdd
present=1 roster_match=0 kills=1 controls=2 met=False
```

Exit code: **1**. The one-field designation mutation does not stay green (`roster_match=0`), so the
C2 kill rule's "mutation remains green" leg does not fire. Note the mutation is caught by exact
roster equality, not by the kill/control tallies: `positive-control` is still counted as a control,
so `kills=1 controls=2` are unchanged. A mutation to an uncounted label would additionally move the
tallies. No predicate change proposed — the frozen rule is satisfied by `met=False`.

## 4. Digests observed

| artifact | sha256 | frozen? |
|---|---|---|
| `tools/round56-prereg-check.py` | `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853` | yes — equals frozen checker digest |
| `tools/round56-replay-code-audit.py` | `fc3d4b63a3020cf37e6f4080e25c9d693a8b177c4f84cae6688b2e445444ff6f` | yes — equals frozen C1 counter digest |
| `tools/round56-env-leg-battery.py` | `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c` | n/a (not frozen) |
| `.ufo/waves/round-56/preregistration.json` | `fa4b5a100a9fd6ceaec93c537f3d9264a0883fac873368243ff1ae041d82ee68` | n/a |

Worktree hashes equal the blobs at the freeze tip for preregistration and battery (checked with
`git show efc6b3ec:<path> | sha256sum`), so the tip under test and the checked-out lane agree.

## 5. Defect / fidelity observation (non-blocking, no artifact changed)

Committed `.ufo/waves/round-56/controls/base-c2.out` ends with a third line `exit=1`:

```
tip=e10b6d39af450e8d652be9ac2986768b531fe13f
present=0 roster_match=0 kills=0 controls=0 met=False
exit=1
```

The live checker writes only the first two lines to stdout and to `--out`; `exit=1` is not part of
its output. Values agree with the live run above (no contradiction of the frozen target), but the
control receipt is not byte-reproducible from the frozen counter alone — it carries an
operator-appended line. Proposed fix for a later round (do not touch frozen artifacts now): have the
counter emit its own `exit=<code>` line before `return`, or capture exit status in a separate wrapper
receipt so committed control receipts are byte-reproducible from the counter.

Second, smaller observation: `kills`/`controls` tallies are derived from the *parsed* roster, so a
designation mutation between two counted labels is only witnessed by `roster_match`. This is
sufficient for the frozen predicate; recording it so no seat reads `kills=1 controls=2` on the
mutant leg as "the mutation was seen by the tallies".

## 6. Risks and blockers

- None for the assigned check; freeze-tip run and base control both reproduce their frozen targets.
- Scope limits inherited: this grades roster fidelity, not mutant quality beyond the one frozen C1
  control (preregistration `limits`). C1 (env leg) was not re-run by this seat.
- No tool installs or upgrades (none needed).
- Lane, jj state and fleet-root files untouched; only this report and `out/X02ReplayC2/` receipts written.

## Receipts

`out/X02ReplayC2/`: `transcript.txt` (commands, exact stdout, exits, digests, mutant diff),
`freeze-c2.out`, `base-c2.out`, `mutant-designation-c2.out`.
