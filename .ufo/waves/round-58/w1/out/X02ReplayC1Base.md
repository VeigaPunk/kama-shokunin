# X02ReplayC1Base — round-57 checker replayed through the frozen C1 counter
Item: base-checker replay of `2f53614e:tools/round56-prereg-check.py` at tip
`dcd69473dd7e33b316e2ba238a48e5119a6cd809`; list wrongly accepted variants. Lane read-only, no edits.

## Command and result
```
S=/fast/scratch/hyaku/kama-r58/X02ReplayC1Base
TMPDIR="$S" python3 tools/round58-c1-counter.py --repo <lane> \
  --tip dcd69473dd7e33b316e2ba238a48e5119a6cd809 \
  --checker-blob 2f53614e6f5895560edb775cc3e74841aa0dd44c:tools/round56-prereg-check.py \
  --out "$S/c1-base-replay.out"
EXIT=1
tip=dcd69473dd7e33b316e2ba238a48e5119a6cd809
predicate=C1-r58 accept genuine+3/3 benign, reject 11/11 no-op, errors=0
genuine=1/1 benign=1/3 noop_rejected=1/11 errors=0 met=False
```
Confirmed: exactly the frozen base line, byte-identical to committed control
`controls/c1-base-r57-checker.out` (diff empty; `.exit` = `exit=1`). Bytes run: counter `sha256
32f615d8…b411b9` (`dcd69473:tools/round58-c1-counter.py`), checker `sha256 dee6f922…e90ced`
(`2f53614e:tools/round56-prereg-check.py`); two runs identical → deterministic, errors=0 both.

## Wrongly accepted no-ops — 10 of 11 (the whole 8→8 gap)
- `N02-if-false` / `N04-early-return` — call sites parked under `if False:` / after `return 0`
- `N03-unused-function` / `N08-main-not-invoked` — `main` becomes `return 0` (body left in
  `_legacy_main`) / `__main__` guard body becomes `pass`
- `N05-env-guard` / `N09-empty-loop` / `N11-try-else` — calls only reachable under an env guard, a
  `for _leg in []:` loop, or a `try:` branch the design never runs
- `N06-run-body-noop` / `N07-mutant-assert-noop` — `run()` / `assert_mutant_breaks_detection()` bodies
  neutered to `return True`; `N10-run-rebound` rebinds `run = lambda *a, **k: True`

Only `N01-calls-removed` is correctly rejected (label literals deleted from source).

## Also wrongly rejected — benign=1/3 (false negatives, no C1 credit)
`B2-helper-leg` (labels routed through a `_leg` wrapper) and `B3-concat-labels` (`"base-" + "old-counter"`
is a BinOp, not `ast.Constant`); only `B1-rename-comment` passes. Stdout on both: `present=1
roster_match=1 kills=1 controls=2 met=False` — failing conjunct is `executed`, the label test.

## Mechanism (attacks the C1 base row, not the ledger)
`tools/round56-prereg-check.py` is static: `ROSTER` literal equality vs preregistration, then
`executed = expected <= invoked` where `invoked` holds only labels appearing as *constant first
args* of `run(...)`/`assert_mutant_breaks_detection(...)` anywhere in the tree, plus `kills==1` and
`controls==2`. It never runs the battery, so any edit keeping the roster literal and the call shape is
accepted — the 10 survivors above, plus the 2 benign rewrites whose label syntax changed.

## Cross-check, side effect, limits
Same counter at build tip `e4891d8a` with `e4891d8a:tools/round58-battery-exec-check.py` gives
`genuine=1/1 benign=3/3 noop_rejected=11/11 errors=0 met=True`, EXIT=0 — the counter discriminates base
from build on one variant set, so the base number is not a counter artifact.
Side effect: that run executed the battery, whose variants hardcode the real LANE and
`OUT = LANE/.ufo/waves/round-56/measured`, so 4 tracked working-tree files got pid-only churn
(`ld_audit`/`problems` unchanged, e.g. `pid=2361912`→`2532595`). Committed blobs untouched, counter
inputs unaffected; not reverted (git writes forbidden to seats; siblings regenerate these files).
Limit: the variant set is absent at base `2f53614e`, so the "before" line is reproducible only at a tip
carrying the variants — `dcd69473` is correct; nothing here speaks to variants outside the enumerated 11.

**Evidence retained** (no installs were run)
`.ufo/waves/round-58/w1/out/X02ReplayC1Base/receipts/`: `c1-base-replay.out`, `c1-base-replay2.out`,
`c1-build-tip-contrast.out`, `diag-per-variant.txt` (stdout per variant; fixture toplevel asserted),
`diag.py`. Scratch `$S` removed after copying.
