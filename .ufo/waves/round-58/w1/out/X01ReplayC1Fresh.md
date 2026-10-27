# X01ReplayC1Fresh — round-58 C1 replay from a fresh shared clone

Attacks: claim C1, counter `tools/round58-c1-counter.py`, checker `tools/round58-battery-exec-check.py`,
variant set `tests/round58-battery-variants/`, base/do-nothing receipts (cb1ef102). Clone `git clone
--shared <lane> $S/clone`, toplevel = `$S/clone`; clone HEAD e4f207f5, yet every blob is read at `--tip
e4891d8a`, so HEAD drift is irrelevant. Checker at HEAD and e4891d is one blob 02616f0f (sha256
89ad4e5d…) and the genuine variant equals lane `tools/round56-env-leg-battery.py` (1f4ebff0, 69b77a6a…).

## 1. Prescribed counter run — exit 0
```
cd $S/clone && TMPDIR=$S python3 tools/round58-c1-counter.py --repo $S/clone \
  --tip e4891d8a4c9c70e97124980c2ec9aee5762a7f0a --checker tools/round58-battery-exec-check.py
tip=e4891d8a4c9c70e97124980c2ec9aee5762a7f0a
predicate=C1-r58 accept genuine+3/3 benign, reject 11/11 no-op, errors=0
genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True                     EXIT=0
```
Detail (`c1-counter-prescribed.stdout`): genuine accept 0, B1/B2/B3 accept 0, N01–N11 reject exit=1 each; identical with the checker pinned to the tip (`--checker-blob e4891d8a…:tools/round58-battery-exec-check.py`, exit 0, `c1-counter-blob.out`).

## 2. Checker against the lane's real round-56 battery — exit 0
```
python3 tools/round58-battery-exec-check.py --repo $S/clone --tip e4891d8a…
present=1 roster_match=1 kills=1 controls=2 executed=1 legs=3/3 mutant_assert=1 met=True   EXIT=0
```
(`checker-real-battery.out`) Roster literal equals `.ufo/waves/round-56/preregistration.json` `battery.roster` exactly.

## 3. Base and do-nothing controls reproduced — exit 1 each
`--checker-blob 2f53614e…:tools/round56-prereg-check.py`: `genuine=1/1 benign=1/3 noop_rejected=1/11 errors=0 met=False`, exit 1 = freeze base text. At tip: always-accept `benign=3/3 noop_rejected=0/11`, always-reject `genuine=0/1 benign=0/3`, hash-only `benign=0/3 noop_rejected=11/11`; all met=False, exit 1, matching the committed `.out` numbers (only the tip line differs; those receipts record dcd6947). The 8→8 delta is the checker, not the variants: `git diff dcd6947 e4891d8a -- tests/round58-battery-variants` is empty.

## 4. LIMITS — survivors outside the 11 enumerated variants (no C1 credit claimed)
Driver `x01-limits-probes.py`, receipt `x01-limits-probes.out`; each variant went into its own throwaway fixture (toplevel asserted equal to the fixture dir) and was scored by the real checker:
```
P0-genuine-as-fixture:                    exit=0 met=True   (fixture-validity control)
P1-decoy-counter-not-invoked:            exit=0 met=True   LIMIT
P2-assertion-always-true:                exit=0 met=True   LIMIT
P3-positive-control-expectation-flipped: exit=0 met=True   LIMIT
P4-exit-zero-unconditional:              exit=0 met=True   LIMIT
P5-empty-battery:                        exit=1 met=False  (rejection control)
```
- P1 — `subprocess.run(["true","--counter","decoy"])` replaces both real invocations: the counter
  under test never runs, yet the `--counter` argv token satisfies the frame predicate; the checker
  binds that token, not the executable, paths, or `--expect` value.
- P2 — `exact_field_match` returns True unconditionally (vacuous leg verdicts) while subprocess calls
  still fire; N06/N07 short-circuit *before* the subprocess, so they miss this shape.
- P3 — positive control called with `"missed"` not `"detected"`, roster literal intact, so the leg's
  discriminating expectation is never checked. P4 — `main` returns 0 unconditionally; the battery's
  own exit code is not bound.
C1 as frozen is met (the kill rule scores only genuine, the 3 benign and the 11 enumerated no-ops);
the four shapes above are LIMITS for a later round, not retroactive predicate changes.

## 5. Hygiene
No tool installed or upgraded (system python3 only; pacman paused, untouched). `TMPDIR=$S` for every
run; fixtures and counter work dirs removed by their own finally blocks; `$S` deleted after receipts
were copied here. Writes confined to this directory plus `X01ReplayC1Fresh.md`; no git
add/commit/reset/checkout/push in lane or clone; fleet root, sibling lanes and shokuknow untouched;
the parent re-runs §1 and §2 for the post-integration gate.
