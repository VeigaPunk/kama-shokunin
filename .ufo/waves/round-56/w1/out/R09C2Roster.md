# R09C2Roster — C2 roster comparison

Compared the frozen preregistration `battery.roster` with the top-level AST-literal `ROSTER` in `tools/round56-env-leg-battery.py` at freeze tip `efc6b3ec6fb6ea308c15855e9b8b62856f4255b7`.

**Result: no mismatch.** Both contain exactly the same three names, designations, expected outcomes, and insertion order:

| Name | Designation | Expected |
|---|---|---|
| `base-old-counter` | `control` | `missed` |
| `round56-counter` | `positive-control` | `detected` |
| `m-drop-ldaudit` | `kill` | `missed` |

The frozen battery blob matches the worktree byte-for-byte (SHA-256 `79b19596c475863dbd5fe5c03511996b050a69d500f2671385069c02d17c335c`). AST inspection found one top-level `ROSTER` assignment and no other assignment anywhere in the AST. The prereg JSON has no duplicate keys; all roster keys/string values are ASCII and exact. Parsed dict equality, insertion order, scalar UTF-8 bytes, canonical sorted JSON bytes, and insertion-order compact JSON bytes all match.

**Checker receipts** (Python 3.14.8; `TMPDIR=/fast/scratch/hyaku/kama-r56/R09C2Roster`):

- `python3 tools/round56-prereg-check.py --repo /home/vgpnk/Projects/shokunin/kama-shokunin --tip efc6b3ec6fb6ea308c15855e9b8b62856f4255b7` → exit 0; `present=1 roster_match=1 kills=1 controls=2 met=True`.
- Same command with `--tip e10b6d39af450e8d652be9ac2986768b531fe13f` → exit 1; `present=0 roster_match=0 kills=0 controls=0 met=False`.

The checker’s SHA-256 is the frozen `c7b0d787f348691bbc057114b455545f5abfb0c70ec497e1ad695591f1489853`. No defect or proposed fix identified within this roster-comparison scope. No tools installed.