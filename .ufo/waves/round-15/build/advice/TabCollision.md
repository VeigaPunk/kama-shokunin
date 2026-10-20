# TabCollision — corpus-guard fixture advice

## Files written
- `tests/ollama-corpus-guard/TabCollision.json` — literal shared-schema matrix (array of scenario objects `{name, names, envelope, expected_rejected}`).

## Scenarios

| name | names | envelope | expected_rejected |
|---|---|---|---|
| `TabCollision-tab-wrapped-duplicate-array` | `n00`–`n15` + `"\tn09\t"` (17 entries) | `array` | `true` |
| `TabCollision-tab-wrapped-unique-array` | `n00`–`n15` + `"\tn16\t"` (17 entries) | `array` | `false` |

## Rationale
- The guard canonicalizes with `str.strip()` (frozen `measure-before.py` lines 352–356: `declared.append(name.strip())`, `unique = len(set(declared))`, reject only when `unique < MINIMUM_UNIQUE_CASES`). `"\tn09\t"` strips to `n09`, colliding with the literal `n09` already present.
- Invalid scenario yields exactly 16 distinct stripped names across 17 entries — the true duplicate collision the current minimum-only guard fails to reject, and one the fixed duplicate guard must catch. It is a genuine duplicate-policy case, not a malformed-schema one (all names non-empty after strip; count ≥ 16).
- Valid counterpart keeps an identical 17-entry shape with every name distinct after stripping (`"\tn16\t"` → `n16`), so a rejection there cannot be blamed on size and proves a correct repair accepts whitespace-padded-but-unique names. "Duplicate removed" applied by swapping the colliding element for a distinct one rather than shrinking below the control size.

## Limitations / bounded findings
- Both fixtures use the `array` envelope; object-envelope coverage is assigned to `ObjectEnvelope.json` (per spec.json sibling assignments) and intentionally not duplicated here.
- Fixture is declarative only; no generator, no execution. Whether `"\tn16\t"`-style padded-unique names are intended to be *accepted* (vs. canonicalized-then-flagged as suspicious) is a repair-semantics decision owned by the L1/GuardRepair lane — schema offers no third verdict, so `false` encodes acceptance after strip-canonicalization.
- No installs or verification runs performed, per assignment.
